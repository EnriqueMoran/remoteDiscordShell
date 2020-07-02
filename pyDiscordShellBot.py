import subprocess
import os
import re
import datetime
import hashlib
import time
import discord


__author__ = "EnriqueMoran"

__version__ = "v0.0.2"


TOKEN = None
VERSION = None
PASSWORD = None
USERS = None    # users.txt path
LOG = None    # log.txt path
LOGLINES = 0    # Current lines of log.txt
SHAREFOLDER = None    # Shared files storage folder path
LOGLIMIT = None    # Max number of lines to register in log
GUILD = None    # Server's name
INGUILD = False    # Is this bot running in configured server?
USERSLOGIN = []    # List of users id waiting for pass to be added
USERSUPDATE = []   # List of users id waiting to update system's response
USERSUPGRADE = []   # List of users id waiting to upgrade system's response
USERSINSTALL = []   # List of users id waiting to install a package
USERSUNINSTALL = []   # List of users id waiting to uninstall a package
FORBIDDENCOMMANDS = [
    "wait", "exit", "clear", "aptitude", "raspi-config",
    "nano", "dc", "htop", "ex", "expand", "vim", "man", "apt-get", "poweroff",
    "reboot", "ssh", "scp", "wc"
    ]    # non working commands due to API error or output eror


def load_config(configFile):
    global VERSION, TOKEN, PASSWORD, USERS, LOG, LOGLIMIT, ROOT, \
        SHAREFOLDER, LOGLINES, GUILD, INGUILD

    file = open(configFile, "r")
    lines = file.read().splitlines()
    cont = 0
    read = False

    for line in lines:
        if cont == 5 and line[:1] != "" and read is True:
            VERSION = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 6 and line[:1] != "" and read is True:
            TOKEN = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 8 and line[:1] != "" and read is True:
            GUILD = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 11 and line[:1] != "" and read is True:
            PASSWORD = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 14 and line[:1] != "" and read is True:
            SHAREFOLDER = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 18 and line[:1] != "" and read is True:
            USERS = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 21 and line[:1] != "" and read is True:
            LOG = [file.strip() for file in line.split('=')][1]
            read = False
        if cont == 22 and line[:1] != "" and read is True:
            LOGLIMIT = int([file.strip() for file in line.split('=')][1])
            read = False
        if cont == 25 and line[:1] != "" and read is True:
            ROOT = bool([file.strip() for file in line.split('=')][1])
            read = False
        if line[:1] == "#":
            cont += 1
            read = True

config_path = os.getcwd() + "/config.txt"
load_config(config_path)

f1 = open(LOG, "a+")
f1.close
f2 = open(USERS, "a+")
f2.close

with open(LOG) as f:
    LOGLINES = sum(1 for _ in f)

os.makedirs(SHAREFOLDER, exist_ok=True)

client = discord.Client()


async def check_config(message):
    # TODO: CURRENTLY NOT USED, USE IT ON WELCOME MESSAGE
    error = False
    error_msg = "Config file not properly filled, errors:"
    if "./" in SHAREFOLDER:
        error = True
        error_msg += "\n- Share Folder path field is empty."
    if PASSWORD == "":
        error = True
        error_msg += "\n- Password field is empty."
    if USERS == "":
        error = True
        error_msg += "\n- Users File path field is empty."
    if "./" in USERS:
        error = True
        error_msg += "\n- Users File path is relative."
    if LOG == "":
        error = True
        error_msg += "\n- Log File path field is empty."
    if "./" in LOG:
        error = True
        error_msg += "\n- Log File path is relative."
    if LOGLIMIT == "":
        error = True
        error_msg += "\n- Log limit field is empty."
    if ROOT == "":
        error = True
        error_msg += "\n- Root field is empty."
    if error:
        await message.channel.send(error_msg)
    return error


def in_guild(func):    # Check if bot is in configured server
    def wrapper(*args, **kwargs):
        if INGUILD:
            return func(*args, **kwargs)
        return wrapper


def encrypt(id):    # Cipher users.txt content using SHA256
    m = hashlib.sha256()
    m.update(str(id).encode())
    return m.hexdigest()


def register(user):    # Register user and allow him to access
    encrypted_user = encrypt(user)
    f = open(USERS, "a+")
    content = f.readlines()
    content = [x.strip() for x in content]
    if encrypted_user not in content:
        f.write(str(encrypted_user) + "\n")
    f.close


def check_user_login(login):    # Check if user ID is on users.txt
    encrypted_login = encrypt(login)
    check = False
    with open(USERS) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        if encrypted_login in content:
            check = True
    return check


async def updateSystem(message):
    try:
        proc = subprocess.Popen('sudo apt-get update -y', shell=True,
                                stdin=None, stdout=subprocess.PIPE,
                                executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            if output:
                await message.channel.send(output.decode('utf-8'))
        proc.wait()

        if proc.poll() == 0:
            await message.channel.send("System updated sucessfully.")
        else:
            await message.channel.send("System not updated" +
                                       ", error code: " + str(proc.poll()))
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        await message.channel.send(str(error))
        await message.channel.send(str(errorType))


async def upgradeSystem(message):
    try:
        proc = subprocess.Popen('sudo apt-get upgrade -y', shell=True,
                                stdin=None, stdout=subprocess.PIPE,
                                executable="/bin/bash")
        while True:
            output = proc.stdout.readline()
            if output == b'' and proc.poll() is not None:
                break
            if output:
                await message.channel.send(output.decode('utf-8'))
        proc.wait()

        if proc.poll() == 0:
            await message.channel.send("System upgraded sucessfully.")
        else:
            await message.channel.send("System not upgraded" +
                                       ", error code: " + str(proc.poll()))
    except Exception as e:
        error = "Error ocurred: " + str(e)
        errorType = "Error type: " + str((e.__class__.__name__))
        await message.channel.send(str(error))
        await message.channel.send(str(errorType))


async def installPackage(message):
    try:
        proc = subprocess.Popen('sudo apt-get install -y ' + message.content,
                                shell=True, stdin=None,
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
        errorType = "Error type: " + str((e.__class__.__name__))
        await message.channel.send(str(error))
        await message.channel.send(str(errorType))


@client.event
async def on_ready():
    global TOKEN, GUILD, INGUILD
    guild = discord.utils.get(client.guilds, name=GUILD)
    if guild:
        INGUILD = True
        print("Server found! running...")
        return
    print("No server found... Press ctrl+c to exit.")


@in_guild
@client.event
async def on_message(message):
    global USERSLOGIN, VERSION, FORBIDDENCOMMANDS, ROOT, USERSUPDATE, \
        USERSUPGRADE, USERSINSTALL, USERSUNINSTALL
    if message.author == client.user:
        return
    if message.author.id in USERSLOGIN:    # User must add password to access
        if message.content == PASSWORD:
            register(message.author.id)    # Grant access to user
            USERSLOGIN.remove(message.author.id)
            response = "Logged in, you can use commands now."
            await message.author.dm_channel.send(response)
            return
    if message.author.id in USERSUPDATE:
        # User must reply wether update system or not
        if message.content.lower() == 'yes':
            USERSUPDATE.remove(message.author.id)
            response = "System updating..."
            await message.channel.send(response)
            await updateSystem(message)
        elif message.content.lower() == 'no':
            USERSUPDATE.remove(message.author.id)
            response = "System won't update."
            await message.channel.send(response)
        else:
            response = "Please reply 'yes' or 'no'."
            await message.channel.send(response)
        return
    if message.author.id in USERSUPGRADE:
        # User must reply wether upgrade system or not
        if message.content.lower() == 'yes':
            USERSUPGRADE.remove(message.author.id)
            response = "System upgrading..."
            await message.channel.send(response)
            await upgradeSystem(message)
        elif message.content.lower() == 'no':
            USERSUPGRADE.remove(message.author.id)
            response = "System won't upgrade."
            await message.channel.send(response)
        else:
            response = "Please reply 'yes' or 'no'."
            await message.channel.send(response)
        return
    if not check_user_login(message.author.id):
        USERSLOGIN.append(message.author.id)  # Waiting for pass to be written
        await message.author.create_dm()
        response = "Please log in, insert password:"
        await message.author.dm_channel.send(response)
        return
    if message.author.id in USERSINSTALL:
        # User must reply which package to install
        if message.content.lower() == 'cancel':
            USERSINSTALL.remove(message.author.id)
            response = "No package will be installed."
            await message.channel.send(response)
        else:
            USERSINSTALL.remove(message.author.id)
            response = "Trying to install package..."
            await message.channel.send(response)
            await installPackage(message)
        return
    if not check_user_login(message.author.id):
        USERSLOGIN.append(message.author.id)  # Waiting for pass to be written
        await message.author.create_dm()
        response = "Please log in, insert password:"
        await message.author.dm_channel.send(response)
        return
    else:
        if message.content.lower() == '/start':    # TODO: TMP welcome message
            welcome_one = "Welcome to discordShell, this bot allows " + \
                          "you to remotely control a computer terminal."
            welcome_two = "List of avaliable commands: \n- To " + \
                "install packages use /install \n- To update system " + \
                "use /update \n- To upgrade system use /upgrade \n- To " + \
                "view forbidden commands use /forbidden."
            welcome_three = "You can send files to the computer, " + \
                "also download them by using getfile + path (e.g. getfile " + \
                "/home/user/Desktop/file.txt)."
            await message.channel.send(f"Current version: {VERSION}")
            await message.channel.send(welcome_one)
            await message.channel.send(welcome_two)
            await message.channel.send(welcome_three)
        elif message.content.lower() == '/update':    # Update system
            await message.channel.send("Update system? (Write yes/no): ")
            USERSUPDATE.append(message.author.id)  # Waiting for response
        elif message.content.lower() == '/upgrade':    # Upgrade system
            await message.channel.send("Upgrade system? (Write yes/no): ")
            USERSUPGRADE.append(message.author.id)  # Waiting for response
        elif message.content.lower() == '/install':    # Install package
            await message.channel.send("Write package name to install or " +
                                       "'cancel' to exit: ")
            USERSINSTALL.append(message.author.id)  # Waiting for response
        elif message.content.lower() == '/uninstall':    # Remove package
            pass    # TODO
        elif message.content.lower() == '/forbidden':    # Forbidden commands
            pass    # TODO
        elif message.content.lower() == '/help':    # Show help message
            pass    # TODO
        else:    # Linux command
            if message.content[0:2] == 'cd':
                try:
                    os.chdir(message.content[3:])
                    await message.channel.send("Current directory: " +
                                               str(os.getcwd()))
                except Exception as e:
                    await message.channel.send(str(e))
            elif message.content.split()[0] in FORBIDDENCOMMANDS:
                await message.channel.send("Forbidden command.")
            elif message.content[0:4] == "sudo" and not ROOT:
                await message.channel.send("root commands are disabled.")
            elif (
                    message.content[0:4] == "ping" and
                    len(message.content.split()) == 2
                 ):
                ip = str(message.content).split()[1]
                com = "ping " + str(ip) + " -c 4"    # Infinite ping fix
                try:
                    p = subprocess.Popen(com, stdout=subprocess.PIPE,
                                         shell=True, cwd=os.getcwd(),
                                         bufsize=1)
                    for line in iter(p.stdout.readline, b''):
                        try:
                            await message.channel.send(line.decode('utf-8'))
                        except:
                            pass
                    p.communicate()
                    if p.returncode != 0:
                        await message.channel.send(" Name or " +
                                                   "service not known")
                except Exception as e:
                    error = "Error ocurred: " + str(e)
                    errorType = "Error type: " + str((e.__class__.__name__))
                    await message.channel.send(str(error))
                    await message.channel.send(str(errorType))
            elif message.content[0:3] == "top":
                pass    # TODO
            elif message.content[0:7] == "getfile":
                pass    # TODO
            else:
                try:
                    p = subprocess.Popen(message.content,
                                         stdout=subprocess.PIPE,
                                         shell=True, cwd=os.getcwd(),
                                         bufsize=1)
                    for line in iter(p.stdout.readline, b''):
                        decoded = line.decode('windows-1252').strip()
                        if len(re.sub('[^A-Za-z0-9]+', '', decoded)) <= 0:
                            # Empty message that raises api 400 error
                            # Send special blank character (U+0701)
                            await message.channel.send("܁")
                        else:
                            try:
                                await message.channel.send(
                                    line.decode('utf-8'))
                            except Exception as e:
                                await message.channel.send(str(e))
                    error = p.communicate()
                    p.wait()
                    if p.returncode != 0:
                        pass
                except Exception as e:
                    error = "Error: Command not found"
                    await message.channel.send(error)
    return


if __name__ == "__main__":
    client.run(TOKEN)
