# remoteDiscordShell
remoteDiscordShell is a remote shell for Linux that makes use of Discord's conection to send commands and receive their output from the computer.
This tool is specially useful if you want to connect to a computer that is behind a private network without opening ports or just want to control your computer through Discord, without using any ssh client.

Check [remoteTelegramShell](https://github.com/EnriqueMoran/remoteTelegramShell) out for a similar solution working in Telegram.


![alt tag](/readme_images/readme_img_1.gif)


## Features
- Control your computer even if its within a private network.
- Send and download any file to/from your computer.
- All Linux distros supported.
- Login system and root restriction to avoid malicious connections from other users.
- Log system to register every sent command.
- Configure the server channels you want the bot to write in.
- Update/upgrade your system remotely.
- Install/remove any package remotely.
- Ban any command you don't want to be sent to the computer.


![alt tag](/readme_images/readme_img_2.gif)


## How it works
Through the configuration file, you can chose which Discord server and channels will be accessible for the bot. To access to the computer control, Discord users must log into the system, the password will be asked through DM to any unregistered user who sends a command.

Once the user is logged in, all (allowed) commands sent will be processed by the computer and the generated output will be sent back to the user in real time.

There is a configurable list of forbidden commands that shouldn't be used due to unexpected behaviour (e.g. non generating output commands such nano or vim).

There is a set of special commands for specific actions such update or upgrade the system, the list of avaliable special commands is the following:
- **/update:** Update system.
- **/upgrade:** Upgrade system.
- **/install:** Ask for a package and install it.
- **/uninstall:** Ask for a package, then remove and purge it.
- **/help:** Show help message.
- **/reload:** Load config again.
- **/stop:** Send CTRL+C signal to current running process.
- **/forbidden:** Show forbidden command list.
- **/getfile:** Download the specified file (absolute path).


## Installation guide
First step is downloading this project using the following command:
```
git clone https://github.com/EnriqueMoran/remoteDiscordShell.git
```

After cloning the repository in your own computer (it should be Linux OS), the following step is installing discord library (notice that this bot is compatible with python 3.7+, so pip3 might be necessary to use):
```
pip install discord
```

After this, we need to create a new bot and add it to our server.
1. Access to [Discord's developer portal](https://discord.com/developers/applications) and click on *New Application*.

2. Click on *Bot*, at left side menu and add a new bot.

![alt tag](/readme_images/image1.png)

3. Add the bot to your server. Go to *Oauth2* on left side menu and check **bot** and **administrator** options in *SCOPES* and *BOT PERMISSIONS*.

![alt tag](/readme_images/image2.png)

4. Access to generated url on your browser and select the server you want to add the bot in.

5. In your bot page, copy the token. Open *config.txt* file and fill the blanks (file paths MUST be absolute). 

![alt tag](/readme_images/image3.png)

Depending on the chosen directory and if sudo parameter is active, it might be necessary to change access permissions of files, this can be done with chmod command.

6. Last step is executing .py script and start using our computer through Discord.
```
python3 pyDiscordShellBot.py
python3 pyDiscordShellBot.py &              (this will run the script in background)
```


## Sending and receiving files
To send files just drag and drop them on the chat, they will be stored in configured shared folder.

![alt tag](/readme_images/readme_img_4.gif)


To download files from the computer use "/getfile + path" (e.g. /getfile /home/user/Desktop/test-file.txt).

![alt tag](/readme_images/readme_img_3.gif)


## TODO
- Clean code and use decorators for user checking.
- Parallelize loading messages (update, upgrade, install, remove) to avoid max edition limit.
- Add configurable ignore key to avoid processing messages starting with that character.


## Version history
Check [project releases](https://github.com/EnriqueMoran/remoteDiscordShell/releases) for more info.

- **v0.0.1:** (06/29/20) Basic functionalities added.
- **v0.0.2:** (07/02/20) Update/upgrade system and package installation features added.
- **v1.0.0:** (07/07/20) Upload/download files features added, log is working now.
- **v1.1.0:** (10/27/21) Major changes. Specific channels usage implemented, multiple distro support added.