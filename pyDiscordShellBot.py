import configparser
import datetime
import discord
import hashlib
import json
import os
import re
import requests
import subprocess
import tempfile
import time


__author__ = "EnriqueMoran"

__version__ = "v1.1.0"


TOKEN = None
GUILD_NAME = None          # Server's name
CHANNELS_NAME = []         # Server's channels
PASSWORD = None
SHARED_FOLDER = None       # Shared files storage folder path
USERS_FILE = None          # users.txt path
LOG_FILE = None            # log.txt path
LOG_LIMIT = None           # Max number of lines to register in log
ENABLE_ROOT = False
FORBIDDEN_COMMANDS = []    # Non working / disabled commands

CLIENT = discord.Client()  # Discord client
IN_GUILD = False           # Is bot running in configured server?
LOG_LINES = 0              # Current lines of log.txt
COMMANDS_QUEUE = {}        # Used for updating and upgrading the system
AUTHENTIFIED_USERS = {}    # Users allowed to send commands
CUSTOM_COMMANDS = []       # Bot custom commands
FORBIDDEN_COMMANDS = []    # Non working commands
SUDOERS = {}               # Users with root access


def load_config(config_file):
    global TOKEN, GUILD_NAME, CHANNELS_NAME, PASSWORD, SHARED_FOLDER, \
           USERS_FILE, LOG_FILE, LOG_LIMIT, ENABLE_ROOT, FORBIDDEN_COMMANDS
    config = configparser.ConfigParser()
    config.read(config_file)
    TOKEN = config.get('GENERAL', 'token')
    GUILD_NAME = config.get('GENERAL', 'guild_name')
    CHANNELS_NAME = json.loads(config.get('GENERAL', 'channels_name'))
    PASSWORD = config.get('GENERAL', 'password')
    SHARED_FOLDER = config.get('FILES', 'shared_folder')
    USERS_FILE = config.get('FILES', 'users_file')
    LOG_FILE = config.get('FILES', 'log_file')
    LOG_LIMIT = int(config.get('FILES', 'log_limit'))
    ENABLE_ROOT = bool(config.get('PERMISSIONS', 'enable_root'))
    FORBIDDEN_COMMANDS = json.loads(config.get('USAGE', 'forbidden_commands'))

def initialize():
    """
    Read config and create configured files and folders.
    """
    global COMMANDS_QUEUE, CUSTOM_COMMANDS, CLIENT

    config_path = os.getcwd() + "/config.txt"
    load_config(config_path)
    error, error_msg = check_config()

    CUSTOM_COMMANDS = ["/update", "/upgrade", "/install",
                          "/uninstall", "/forbidden","/help",
                          "/reload_config"]
    COMMANDS_QUEUE = {
                      'update': set(),
                      'upgrade': set(),
                      'install': set(),
                      'uninstall': set()
    }
    if not error:
        f1 = open(LOG_FILE, "a+")
        f1.close
        f2 = open(USERS_FILE, "a+")
        f2.close

        with open(LOG_FILE) as f:
            LOG_LINES = sum(1 for _ in f)
        os.makedirs(SHARED_FOLDER, exist_ok=True)
    else:
        print(error_msg)
        exit()


def check_config():
    global TOKEN, GUILD_NAME, CHANNELS_NAME, PASSWORD, SHARED_FOLDER, \
           USERS_FILE, LOG_FILE, LOG_LIMIT, ENABLE_ROOT, FORBIDDEN_COMMANDS

    error = False
    error_msg = "Config file not properly filled, errors:"
    if not CHANNELS_NAME or len(CHANNELS_NAME) <= 0:
            error = True
            error_msg += "\n- Channel name field is empty."
    if not PASSWORD or len(PASSWORD) <= 0:
            error = True
            error_msg += "\n- Password field is empty."
    if not SHARED_FOLDER or len(SHARED_FOLDER) <= 0:
        error = True
        error_msg += "\n- Shared folder field is empty."
    if "./" in SHARED_FOLDER:
        error = True
        error_msg += "\n- Shared folder path is relative."
    if not USERS_FILE or len(USERS_FILE) <= 0:
        error = True
        error_msg += "\n- Users file field is empty."
    if "./" in USERS_FILE:
        error = True
        error_msg += "\n- Users file field is relative."
    if not LOG_FILE or len(LOG_FILE) <= 0:
        error = True
        error_msg += "\n- Log file field is empty."
    if "./" in LOG_FILE:
        error = True
        error_msg += "\n- Log file path is relative."
    if not LOG_LIMIT or LOG_LIMIT < 0:
        error = True
        error_msg += "\n- Log limit wrong value."
    if not ENABLE_ROOT:
        error = True
        error_msg += "\n- Enable root field is empty."
    if not FORBIDDEN_COMMANDS:
        FORBIDDEN_COMMANDS = []
    return error, error_msg


def in_guild(func):
    """
    Check whether bot is running in configured server
    """
    def wrapper(*args, **kwargs):
        if IN_GUILD:
            return func(*args, **kwargs)
        return wrapper


def in_channel(message):
    """
    Check whether message comes from configured channels
    """
    return True if message.channel in CHANNELS_NAME else False


def encrypt(id):
    """
    Cipher user id using SHA256
    """
    m = hashlib.sha256()
    m.update(str(id).encode())
    return m.hexdigest()


def register_user(user_id):
    """
    Add user to users.txt
    """
    encrypted_user = encrypt(user_id)
    f = open(USERS_FILE, "a+")
    content = f.readlines()
    content = [x.strip() for x in content]
    if encrypted_user not in content:
        f.write(str(encrypted_user) + "\n")
    f.close()


def check_user(id):
    """
    Check if user ID is registered in users.txt
    """
    global AUTHENTIFIED_USERS

    encrypted_id = encrypt(id)
    check = False
    with open(USERS_FILE) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        if encrypted_id in content:
            check = True
    return check


def allow_user(user_id):
    """
    Add user to authentified users set
    """
    global AUTHENTIFIED_USERS

    AUTHENTIFIED_USERS.add(user_id)


def register_log(message):
    """
    Register message in log.txt
    """
    global LOG_LIMIT, LOG_FILE, LOG_LINES
    LOG_LINES += 1
    with open(LOG_FILE, 'a+') as f:
        now = datetime.datetime.now().strftime("%m-%d-%y %H:%M:%S ")
        f.write(now + "[" + str(message.author.name) + " (" +
                str(message.author.id) + ")]: " + str(message.content) + "\n")
    if LOG_LIMIT > 0 and LOG_LINES > LOG_LIMIT:
        with open(LOG_FILE) as f:
            lines = f.read().splitlines(True)
        with open(LOG_FILE, 'w+') as f:
            f.writelines(lines[abs(LOG_LINES - LOG_LIMIT):])


async def ask_password(channel):
    await message.author.create_dm()
    response = "Enter sudo password."
    await message.author.dm_channel.send(response)


async def update_system(channel):
    """
    Run update command depending on SO distro
    """
    # TODO: add distro support and ask for password through dm
    # TODO: paralellize loading message to avoid discord edit limit
    output_text = "Updating system"
    loading_items = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
    i = 0
    msg_output = await channel.send(output_text)
    try:
        command = 'sudo apt-get update -y'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            await msg_output.edit(content=
                                  loading_items[i%(len(loading_items))] +
                                  output_text)
            i += 1
        proc.wait()
        if proc.poll() == 0:
            output = "System updated sucessfully."
            await msg_output.edit(content=output)
        else:
            output = "System not updated, error code: " + str(proc.poll())
            await msg_output.edit(content=output)
    except Exception as e:
        error = "Error ocurred: " + str(e)
        error_type = "Error type: " + str((e.__class__.__name__))
        await channel.send(str(error))
        await channel.send(str(error_type))


async def upgrade_system(channel):
    """
    Run upgrade command depending on SO distro
    """
    # TODO: add distro support and ask for password through dm
    # TODO: paralellize loading message to avoid discord edit limit
    try:
        command = 'sudo apt-get upgrade -y'
        proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            if output:
                await channel.send(output.decode('utf-8'))
        proc.wait()

        if proc.poll() == 0:
            await channel.send("System upgraded sucessfully.")
        else:
            await channel.send("System not upgraded" +
                                       ", error code: " + str(proc.poll()))
    except Exception as e:
        error = "Error ocurred: " + str(e)
        error_type = "Error type: " + str((e.__class__.__name__))
        await channel.send(str(error))
        await channel.send(str(error_type))


async def install_package(message):
    """
    Run install package command depending on SO distro
    """
    # TODO: add distro support and ask for password through dm
    # TODO: paralellize loading message to avoid discord edit limit
    try:
        command = 'sudo apt-get install -y' + message.content
        proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
        already_installed = False

        while True:
            output = proc.stdout.readline()
            already_installed = (already_installed or
                                 "0 newly installed" in str(output))
            if output == b'' and proc.poll() is not None:
                break
            if output:
                await message.channel.send(output.decode('utf-8'))
        proc.wait()

        if already_installed:
                    return    # Dont send any message
        if proc.poll() == 0:
            await message.channel.send(f"Package {message.content} " +
                                       "sucessfully installed.")
        else:
            await message.channel.send(f"Package {message.content} " +
                                       "not installed. Error code: " +
                                       str(proc.poll()))
    except Exception as e:
        error = "Error ocurred: " + str(e)
        error_type = "Error type: " + str((e.__class__.__name__))
        await message.channel.send(str(error))
        await message.channel.send(str(error_type))


async def remove_package(message):
    """
    Run remove package command depending on SO distro
    """
    # TODO: add distro support and ask for password through dm
    # TODO: paralellize loading message to avoid discord edit limit
    try:
        command = 'sudo apt-get --purge remove -y' + message.content
        proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
        already_removed = False

        while True:
            output = proc.stdout.readline()
            already_removed = (already_removed or
                               "0 to remove" in str(output))
            if output == b'' and proc.poll() is not None:
                break
            if output:
                await message.channel.send(output.decode('utf-8'))
        proc.wait()

        if already_removed:
                    return    # Dont send any message
        if proc.poll() == 0:
            await message.channel.send(f"Package {message.content} " +
                                       "sucessfully removed.")
        else:
            await message.channel.send(f"Package {message.content} " +
                                       "not removed. Error code: " +
                                       str(proc.poll()))
    except Exception as e:
        error = "Error ocurred: " + str(e)
        error_type = "Error type: " + str((e.__class__.__name__))
        await message.channel.send(str(error))
        await message.channel.send(str(error_type))


async def show_forbidden_commands(channel):
    res = ""
    for element in FORBIDDEN_COMMANDS:
        res += element + ", "
    await channel.send(res[:-2])


async def show_help(message):
    message_one = "Current version: " + VERSION
    message_two = "Welcome to remoteDiscordShell, this bot allows users " + \
        "to remotely control a computer terminal. Current commands: "
    await message.channel.send(message_one)
    await message.channel.send(message_two)
    res = ""
    for element in CUSTOM_COMMANDS:
        res += element + ", "
    await message.channel.send(res[:-2])


@CLIENT.event
async def on_ready():
    """
    Search for configured server through discord
    """
    global IN_GUILD

    guild = discord.utils.get(CLIENT.guilds, name=GUILD_NAME)
    if guild:
        IN_GUILD = True
        print(f"Server {GUILD_NAME} found! running...")
        await send_welcome_msg(guild)
        return
    print(f"Server {GUILD_NAME} not found...")
    exit()


async def send_welcome_msg(guild):
    """
    Send welcome message to first configured channel
    """
    global CUSTOM_COMMANDS, CHANNELS_NAME, __version__, SHARED_FOLDER

    msg_zero = f"---- pyDiscordShellBot version: {__version__} ----"
    msg_one = "\n\nWelcome to pyDiscordShellBot, this bot allows " + \
               "you to remotely control a computer through shell commands."
    
    msg_two = f"\nList of avaliable commands: {', '.join(CUSTOM_COMMANDS)}"
    msg_three = "\nSent files to the computer will be saved in" + \
                f" configured shared folder: *{SHARED_FOLDER}*"
    msg_four = "\nYou can download files by using getfile + path " + \
               "(*e.g. getfile /home/user/Desktop/file.txt*)."
    channel = discord.utils.get(guild.channels, name=CHANNELS_NAME[0],
                                type=discord.ChannelType.text)
    welcome_msg = msg_zero + msg_one + msg_two + msg_three + msg_four
    await channel.send(welcome_msg)


async def send_message(command, channel):
    """
    Send an empty message to user and edit it with command output
    """
    output = "ㅤ"    # Invisible character
    msg_output = await channel.send(output)
    output = ""
    try:
        proc = subprocess.Popen(command, shell=True, stdin=None,
                            stdout=subprocess.PIPE, executable="/bin/bash")
        for line in iter(proc.stdout.readline, b''):
            decoded = line.decode('windows-1252').strip()
            if len(re.sub('[^A-Za-z0-9]+', '', decoded)) <= 0:
                # Empty message that raises api 400 error
                # Send special blank character
                output += "\n"
                await msg_output.edit(content=output)
            else:
                try:
                    output += line.decode('utf-8')
                    await msg_output.edit(content=output)
                except Exception as e:
                    print("te")
                    await msg_output.edit(content=e)
        error = proc.communicate()
        proc.wait()
    except Exception as e:
        error = "Error: Command not found"
        await msg_output.edit(content=error)
    return proc.returncode, msg_output


@in_guild
@CLIENT.event
async def on_message(message):
    """
    Send command to computer and return the output
    """
    global USERS_FILELOGIN, VERSION, FORBIDDEN_COMMANDS, ENABLE_ROOT, \
           AUTHENTIFIED_USERS, COMMANDS_QUEUE

    if message.author == CLIENT.user:  # Ignore self messages
        return

    register_log(message)

    if message.author.id not in AUTHENTIFIED_USERS:
        if message.content == PASSWORD:
            if isinstance(message.channel, discord.channel.DMChannel):
                register_user(message.author.id)    # Register in users.txt
                allow_user(message.author.id)    # Grant access to user
                response = "Logged in, you can use commands now."
                await message.author.dm_channel.send(response)
            return
        if not check_user(message.author.id):
            await message.author.create_dm()
            response = "Please log in, insert a valid password."
            await message.author.dm_channel.send(response)
            return

    if message.author.id in COMMANDS_QUEUE['update']:
        # User must reply whether update system or not
        if message.content.strip().lower() == 'yes':
            COMMANDS_QUEUE['update'].remove(message.author.id)
            await update_system(message.channel)
        elif message.content.lower() == 'no':
            COMMANDS_QUEUE['update'].remove(message.author.id)
            response = "System won't update."
            await message.channel.send(response)
        else:
            response = "Please reply 'yes' or 'no'."
            await message.channel.send(response)
        return

    if message.author.id in COMMANDS_QUEUE['upgrade']:
        # User must reply wether upgrade system or not
        if message.content.lower() == 'yes':
            COMMANDS_QUEUE['upgrade'].remove(message.author.id)
            response = "System upgrading..."
            await message.channel.send(response)
            await upgrade_system(message.channel)
        elif message.content.lower() == 'no':
            COMMANDS_QUEUE['upgrade'].remove(message.author.id)
            response = "System won't upgrade."
            await message.channel.send(response)
        else:
            response = "Please reply 'yes' or 'no'."
            await message.channel.send(response)
        return

    if message.author.id in COMMANDS_QUEUE['install']:
        # User must reply which package to install
        if message.content.lower() == 'cancel':
            COMMANDS_QUEUE['install'].remove(message.author.id)
            response = "No package will be installed."
            await message.channel.send(response)
        else:
            COMMANDS_QUEUE['install'].remove(message.author.id)
            response = "Trying to install package..."
            await message.channel.send(response)
            await install_package(message)
        return

    if message.author.id in COMMANDS_QUEUE['uninstall']:
        # User must reply which package to install
        if message.content.lower() == 'cancel':
            COMMANDS_QUEUE['uninstall'].remove(message.author.id)
            response = "No package will be removed."
            await message.channel.send(response)
        else:
            COMMANDS_QUEUE['uninstall'].remove(message.author.id)
            response = "Trying to remove package..."
            await message.channel.send(response)
            await remove_package(message)
        return

    if len(message.attachments) > 0:    # A file is sent
        file_path = SHARED_FOLDER + message.attachments[0].filename
        r = requests.get(message.attachments[0].url)
        with open(file_path, 'wb') as file:
            file.write(r.content)
        await message.channel.send(f"File saved as {file_path}")

    else:
        if message.content.lower() == '/update':    # Update system
            await message.channel.send("Update system? (Write yes/no): ")
            COMMANDS_QUEUE['update'].add(message.author.id)
        elif message.content.lower() == '/upgrade':    # Upgrade system
            await message.channel.send("Upgrade system? (Write yes/no): ")
            COMMANDS_QUEUE['upgrade'].add(message.author.id)
        elif message.content.lower() == '/install':    # Install package
            await message.channel.send("Write package name to install or " +
                                       "'cancel' to exit: ")
            COMMANDS_QUEUE['install'].add(message.author.id)
        elif message.content.lower() == '/uninstall':    # Remove package
            await message.channel.send("Write package name to uninstall or " +
                                       "'cancel' to exit: ")
            COMMANDS_QUEUE['uninstall'].add(message.author.id)
        elif message.content.lower() == '/forbidden':    # Forbidden commands
            await message.channel.send("Currently forbidden commands:")
            await show_forbidden_commands(message)
        elif message.content.lower() == '/help':    # Show help message
            await show_help(message)
        else:
            if message.content[0:2] == 'cd':
                try:
                    os.chdir(message.content[3:])
                    await message.channel.send("Changed directory to " +
                                               str(os.getcwd()))
                except Exception as e:
                    await message.channel.send(str(e))

            elif message.content.split()[0] in FORBIDDEN_COMMANDS:
                await message.channel.send(f"{message.content.split()[0]} is"\
                                            " a forbidden command.")

            elif message.content[0:4] == "sudo" and not ENABLE_ROOT:
                await message.channel.send("root commands are disabled.")

            elif message.content[0:4] == "ping" and \
                 len(message.content.split()) == 2:
                # Default ping, without arguments
                ip = str(message.content).split()[1]
                com = "ping " + str(ip) + " -c 4"    # Infinite ping fix
                try:
                    code, msg = await send_message(com, message.channel)
                    if code != 0:
                        text = " Name or service not known"
                        await msg.edit(content=text)
                except Exception as e:
                    error = "Error ocurred: " + str(e)
                    error_type = "Error type: " + str((e.__class__.__name__))
                    await message.channel.send(str(error))
                    await message.channel.send(str(error_type))
            elif message.content[0:3] == "top":
                try:
# TODO: En vez de mandar com, a message quitarle top y añadirle top -b y que mande top -b + message
                    msg_text = "."
                    msg_edit = await message.channel.send(msg_text)

                    while True:
                        com = "top -b -n 1 -o +%CPU | head -n 10 | awk '{OFS=\"\\t\"}; {print $1, $2, $5, $8, $9, $10, $NF}'"

                        p = subprocess.Popen(com, stdout=subprocess.PIPE,
                                         shell=True, cwd=os.getcwd(),
                                         bufsize=1)
                        try:
                            top_msg = ""
                            for line in iter(p.stdout.readline, b''):
                                decoded = line.decode('windows-1252').strip()
                                if len(re.sub('[^A-Za-z0-9]+', '', decoded)) <= 0:
                                    top_msg += "\n"
                                else:
                                    try:
                                        top_msg += line.decode('utf-8')
                                    except Exception as e:
                                        await message.channel.send(str(e))
                            #await message.channel.send(top_msg)
                            print(top_msg)
                            top_msg = "```PID\tUSER\tVIRT\tS\t%CPU\t%MEM\tCOMMAND\n" +\
                            "1\troot\t185108\tS\t0,0\t0,3\tsystemd\n" + \
                            "2\troot\t0\tS\t0,0\t0,0\tkthreadd\n" + \
                            "3\troot\t0\tI\t0,0\t0,0\trcu_gp```"
                            await msg_edit.edit(content=top_msg)
                        except:
                            break
                except Exception as e:
                    error = "Error ocurred: " + str(e)
                    error_type = "Error type: " + str((e.__class__.__name__))
                    await message.channel.send(str(error))
                    await message.channel.send(str(error_type))

            elif message.content[0:7] == "getfile":
                file_path = os.path.join(message.content[7:].strip())
                if os.path.isfile(file_path):
                    await message.channel.send("Sending file.")
                    file = discord.File(file_path)
                    await message.channel.send(files=[file])
                else:
                    await message.channel.send("File doesn't exists.")

            else:
                try:
                    pass
                    await send_message(message.content, message.channel)
                except Exception as e:
                    error = "Error: Command not found"
                    await message.channel.send(error, e)
    return

def main():
    global CLIENT, TOKEN

    initialize()
    CLIENT.run(TOKEN)

if __name__ == "__main__":
    main()
