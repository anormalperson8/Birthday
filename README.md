# Birthday Eevee

A Discord bot for storing birthdays, and announces when the date matches.<br/>
Written specifically for friends' Discord servers.

Also used as an exercise to familiarise myself with the syntax of Python programming language.

This project contains a lot of spaghetti codes.


## Version 2.0
Just like the first version, the bot is based mostly on slash commands.

The bot has been updated to accommodate multiple servers!

This bot remembers birthdays of users in a Discord server, and announces them on the relevant day.


#### Version 2.0.0
- Added support to multiple servers.
- Tried (Keyword: Tried) to make the code a little bit nicer to read. Just a *tiny little bit*. Still very spaghetti.

#### Version 2.0.1
- The `echo` text command has been updated!
- The `echo` text command has now been split into `echo` and `echo2`.
- The only difference is if the message is replying another one, `echo` pings the author while `echo2` does not.

#### Version 2.0.2
- Owner can now modify server information.
- The code is now slightly more readable. (It is still far from actually readable)

## Version 2.1

#### Version 2.1.0
- Changed get_birthday so that whether a user's birth year is displayed depends on the `allow` 
attribute on their birthday entries.
- Changed all past users' entries' `allow` attribute to `false` (Except for itself).

#### Version 2.1.1
- Added the ability for the owner to add/delete server from the server data file.

#### Version 2.1.2
- The info command now has a cover page briefly introducing Eevee.

## Main files

### [main.py](/main.py)
The file that stores all the commands and interactions.

### [birthday.py](/birthday.py)
The file that stores all the code that is used to read/write data.

### [info_command.py](/info_command.py)
The file that stores contents of the `info` slash command, as there are a lot of text in that.

### [server_info.py](/server_info.py)
The file that stores all the code that is used to retrieve server data, such as its ID of the announcement channel.

### [Requirements](/requirements.txt)
This file lists packages one needs to additionally install to host this bot.

## FAQ
#### Can I host this bot myself?
- Yes, but please contact me for permission if you do.

#### How do I host this bot myself?
- To be added.

#### Is the code really spaghetti?
- Yes, absolutely!

