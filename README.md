# remoteDiscordShell
remoteDiscordShell is a remote shell for Linux that makes use of Discord's conection to send commands and receive messages from the computer. It has an user login system and root restriction in order to avoid malicious connections from other Discord users. _"discord"_ module is needed. This tool is specially useful if you want to connect to a computer that is behind a private network without opening ports or just want to control your computer through Discord, without using any other ssh client.

It also has a log file for tracking users input, that registers the date, command and user ID.

![alt tag](/readme_images/gif1.gif)


## How it works
Through the configuration file, you can chose which Discord server will are accessible for the bot (non registered servers won't get any reply from the bot). To access to the computer control, Discord users must log into the system, the password will be asked by DM to any unregistered user that send any command.

Once the user is logged in, all (avaliable) commands sent will be processed by the computer and the generated output will be sent back to the user in real time.

There is a list of forbidden commands that can't be used due to unexpected behaviour (for example non generating output commands such nano or vim), if you find any allowed command that causes any error, please report it. To check the forbidden commands list use **/forbidden**.

There is a set of special commands for specific actions such update or upgrade the system, the list of avaliable special commands is the following:
- **/start:** Send initial message with useful information about this bot.
- **/update:** Update system (might need root permission).
- **/upgrade:** Upgrade system (might need root permission).
- **/install:** Ask for a package and install it (might need root permission).
- **/uninstall:** Ask for a package, then remove and purge it (migth need root permission).
- **/forbidden:** Show forbidden command list.
- **/help:** Show useful information about this bot.


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
To send files just drag and drop on the chat, they will be stored in configured shareFolder.
To download files from the computer use "getfile + path" (e.g. getfile /home/user/Desktop/test-file.txt).

![alt tag](/readme_images/gif2.gif)



![alt tag](/readme_images/image5.png)


## Supported distros
Debian and Ubuntu based distros can be updated and upgraded, install and uninstall packages aswell (because apt-get is used). I am currently working on adding support for the rest of package managers and distros.


## Roadmap
Future changes and features:
* Improve compatibility with Linux distros (currently, install/uninstall commands uses apt-get).
* Test and improve root option.
* Improve security.
* Improve Windows compatibility.
* Add parameter to allow file sending.
* Add ctrl+c command.
* Add multiple servers usage support.
* Add welcome message for the first time this bot is used in a server.
* Check wether the bot has permission to write in channels.


## Version history
Check [project releases](https://github.com/EnriqueMoran/remoteDiscordShell/releases) for more info.
- **v0.0.1:** (06/29/20) Basic functionalities added.
- **v0.0.2:** (07/02/20) Update/upgrade system and package installation features added.
- **v1.0.0:** (07/07/20) Upload/download files features added, log is working now.
