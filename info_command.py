import nextcord
import datetime
import random


def random_colour():
    colours = [nextcord.Colour.red(),
               nextcord.Colour.orange(),
               nextcord.Colour.yellow(),
               nextcord.Colour.green(),
               nextcord.Colour.blue(),
               nextcord.Colour.purple(),
               nextcord.Colour.dark_purple()]
    random.seed(datetime.datetime.now().timestamp())
    return colours[random.randint(0, 6)]


def create_page(title: str, url: str, page: int):
    if page == 1:
        return nextcord.Embed(title=title,
                              description="# Info about me!\n"
                                          "I am Birthday Eevee!\n"
                                          "I am a bot that stores and announces server members' birthdays.\n"
                                          "Read the other pages to see what commands I have to offer.",
                              colour=random_colour(), url=url)
    if page == 2:
        return nextcord.Embed(title=title,
                              description="# Server Global Commands\n"
                                          "The following commands can be used by all users of the server.\n"
                                          "## Slash Commands\n"
                                          "**upcoming_birthdays**\nThis command shows future birthdays of the server.\n"
                                          "(At most 10.)\n"
                                          "**set_birthday**\nThis command adds your own birthday to the bot.\n"
                                          "Requires at least your birth month and birth day.\n"
                                          "**delete_birthday**\nThis command removes your own birthday from the bot.\n"
                                          ""
                                          "**get_birthday**\nThis command allows you to get a user's birthday.\n"
                                          "The bot assumes your own if no user is given.\n"
                                          "**ping**\nTest command.\n"
                                          "**info**\nThis command.\n"
                                          "## Text Commands (Prefix: `.`)\n"
                                          "**boo**\nOi.",
                              colour=random_colour(), url=url)
    if page == 3:
        return nextcord.Embed(title=title,
                              description="# Moderator Commands\n"
                                          "The following commands can only be used by moderators of the server.\n"
                                          "Note that moderator is custom-set, "
                                          "and not someone who has \"Manage Messages\" permissions.\n"
                                          "## Slash Commands\n"
                                          "**set_user_birthday**\nThis command sets a user's birthday to the bot.\n"
                                          "Same as **set_birthday**.\n"
                                          "**delete_user_birthday**\nThis command deletes a user's birthday.\n"
                                          "Same as **delete_birthday**.\n"
                                          "**add_emote**\nThis commands lets "
                                          "Birthday Eevee add a reaction to a message.\n"
                                          "(Only accepts default emojis or emojis of servers Eevee is in.)\n"
                                          "Message ID and emotes are required for the command.\n"
                                          "**edit**\nThis commands edits a message Birthday Eevee sent.\n"
                                          "Message ID and content are required for the command.\n"
                                          "## Text Commands (Prefix: `.`)\n"
                                          "**echo**\nBirthday Eevee echos what you say.\n"
                                          "If you are replying to a message, the message author is pinged.\n"
                                          "You won't get any response if you're not a moderator.\n"
                                          "However your message will be deleted.\n"
                                          "**echo2**\nBirthday Eevee echos what you say.\n"
                                          "If you are replying to a message, the message author is *not* pinged.\n"
                                          "You won't get any response if you're not a moderator.\n"
                                          "However your message will be deleted.",
                              colour=random_colour(), url=url)
    if page == 4:
        return nextcord.Embed(title=title,
                              description="# Owner Commands\n"
                                          "Don't try it. They can only be used by the owner.\n"
                                          "## Slash Commands\n"
                                          "**test**\nDon't try it.\n"
                                          "**checkers**\nDon't try it.\n"
                                          "**status**\nDon't try it.\n"
                                          "**activity**\nDon't try it.\n"
                                          "**modify**\nDon't try it.\n"
                                          "**add_server**\nDon't try it.\n"
                                          "**secret**\nIt *literally* says secret.\n"
                                          "## Text Commands (Prefix: `.`)\n"
                                          "**time**\nYou won't get any response if you're not the owner.",
                              colour=random_colour(), url=url)
    if page == 5:
        return nextcord.Embed(title=title,
                              description="# Unused page\n"
                                          "You should not be seeing this page.\n"
                                          "If you are seeing this, contact the owner.\n",
                              colour=random_colour(), url=url)
