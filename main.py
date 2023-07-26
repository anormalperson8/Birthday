# Packages
import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
import datetime
import calendar
import asyncio
import random

# Self .py files
import birthday

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents,
                      activity=nextcord.Game(name="Happy Birthday...?"), help_command=None)

path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
data_path = f"{path}/data"
load_dotenv(f"{data_path}/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))
mod_role_id = [int(os.getenv('MOD_ID')), int(os.getenv('ADMIN_TEST_ID'))]
community = int(os.getenv('COM_ID'))
guilds_list = []
for guild in client.guilds:
    guilds_list.append(int(guild.id))
perm = birthday.get_perm()


@client.event
async def on_ready():
    await client.wait_until_ready()
    client.loop.create_task(ann())
    print('We have logged in as {0.user}'.format(client))


# Response-testing command
@client.command()
async def boo(ctx):
    if ctx.author.bot:
        await ctx.send("You're not a user :P")
        return
    await ctx.send(f"Oi.")


def timestamp():
    now = datetime.datetime.now()
    a = f"Today is {now.date().day} {calendar.month_name[now.date().month]}, {now.date().year}\n" \
        f"The time (hh/mm/ss) now is {now.time().hour:02}:{now.time().minute:02}:{now.time().second:02}."
    return a


@client.command()
async def time(ctx):
    if ctx.author.id != owner_id:
        return
    await ctx.send(f"Time check!\n{timestamp()}")


@commands.guild_only()
@client.command()
async def echo(ctx, *, arg):
    await ctx.message.delete()
    for role in ctx.message.author.roles:
        if role.id in mod_role_id:
            await ctx.send(arg)
            return


# Check whether the member is in the server, and whether the channel is allowed to use the command
def check_user(user_id, interaction):
    # Block users not in server
    if interaction.guild.get_member(user_id) is None:
        return 0
    # Only allow specific channels
    if interaction.channel_id not in perm:
        return 1
    return None


# Check whether a user is mod
def check_mod(interaction: nextcord.Interaction):
    for role in interaction.user.roles:
        if role.id in mod_role_id:
            return True
    return False


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="test")
async def test(interaction: nextcord.Interaction, stat: int = 1):
    if interaction.user.id != owner_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(
            content="This is for the owner not you <:sunnyyBleh:1055108393372749824>")
        return
    if interaction.channel_id not in perm:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content=f"<@{interaction.user.id}> This is the wrong test channel!")
        return
    if stat:
        await interaction.response.defer()
        await interaction.edit_original_message(content="test done <:EeveeUwU:965977552067899482>")
    else:
        await interaction.response.defer()
        await bday_announcement()
        await interaction.edit_original_message(content="test (status: 1) done <:EeveeUwU:965977552067899482>")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Checkers. Not the board game one.")
async def checkers(interaction: nextcord.Interaction):
    if interaction.user.id != owner_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(
            content="This is for the owner not you <:sunnyyBleh:1055108393372749824>")
        return
    bday_list = birthday.get_user()
    if bday_list is None:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="No bdays today.")
        return
    message = "It's the bday of "
    for i in range(len(bday_list)):
        if i != 0:
            message += ", "
        message += client.get_user(int(bday_list[i])).name
    message += "."
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_message(content=f"{message}")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.defer()
    await interaction.edit_original_message(content="Pong!")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Get a member's birthday! You can even get mine!")
async def get_birthday(interaction: nextcord.Interaction,
                       user: nextcord.User = nextcord.SlashOption(required=False,
                                                                  description="The user whose birthday "
                                                                              "you want to know.",
                                                                  default=None)):
    if user is None:
        user = interaction.user
    stat = check_user(user.id, interaction)
    if stat == 0 or stat == 1:
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content=f"This is the wrong channel!")
            return
        await interaction.edit_original_message(content="Member is not in server.")
        return
    await interaction.response.defer()
    date = birthday.get_date(user.id)
    if date is not None:
        day = int(date.day)
        month = date.strftime("%B")
        year = int(date.strftime("%Y"))
    else:
        await interaction.edit_original_message(
            content=f"{user.display_name}'s birthday does not exist in the system. <:EeveeCry:965985819057848320>")
        return
    postfix = 'th'
    if (day % 10 == 1) and (day // 10 != 1):
        postfix = 'st'
    elif (day % 10 == 2) and (day // 10 != 1):
        postfix = 'nd'
    elif (day % 10 == 3) and (day // 10 != 1):
        postfix = 'rd'
    year_phrase = ""
    if year != 1:
        year_phrase = ", " + str(year)
    await interaction.edit_original_message(
        content=f"{user.display_name}'s birthday is on {day}{postfix} {month}{year_phrase}.")


def valid_date(year, month, day):
    if year < 1 or month < 1 or month > 12 or year > 2023 or day < 1 or day > 31:
        return False
    if month == 2 and day > 28:
        if calendar.isleap(year) or year == 1:
            return True
        return False
    if month % 2 == 0 and month <= 7 and day > 30:
        return False
    if month % 2 == 1 and month > 7 and day > 30:
        return False
    if datetime.datetime.now() < datetime.datetime(year=year, month=month, day=day):
        return False
    return True


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set your own birthday!")
async def set_birthday(interaction: nextcord.Interaction,
                       day: int = nextcord.SlashOption(required=True, description="The day."),
                       month: int = nextcord.SlashOption(required=True, description="The month."),
                       year: int = nextcord.SlashOption(required=False, description="The year.", default=1)):
    await set_user_birthday(interaction, None, day, month, year)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set another user's birthday. Mods only")
async def set_user_birthday(interaction: nextcord.Interaction,
                            user: nextcord.User = nextcord.SlashOption(required=True,
                                                                       description="The member whose birthday "
                                                                                   "you want to set."),
                            day: int = nextcord.SlashOption(required=True, description="The day."),
                            month: int = nextcord.SlashOption(required=True, description="The month."),
                            year: int = nextcord.SlashOption(required=False, description="The year.", default=1)):
    if user is not None:  # Check if it is a mod call or not
        if user.id == interaction.user.id:  # Wrong call
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="Wrong command. Use /set_birthday to set your own!")
            return
        elif not check_mod(interaction):  # Not a mod
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="You do not have the permission to add others' birthdays!")
            return
    if user is None:
        user = interaction.user
    stat = check_user(user.id, interaction)
    if stat == 0 or stat == 1:  # Wrong channel or member not in server
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content="This is the wrong channel!")
            return
        await interaction.edit_original_message(content="Member is not in server.")
        return
    await interaction.response.defer()
    if not valid_date(year, month, day):
        await interaction.edit_original_message(content="Invalid Birthday! <:EeveeOwO:965977455791857695>")
        return
    birthday.set_date(user.id, year, month, day)
    await interaction.edit_original_message(content="Birthday updated! <:EeveeCool:1007625997719449642>")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Delete your own birthday entry.")
async def delete_birthday(interaction: nextcord.Interaction):
    await delete_user_birthday(interaction, None)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Delete another user's birthday entry. Mods only.")
async def delete_user_birthday(interaction: nextcord.Interaction,
                               user: nextcord.User = nextcord.SlashOption(required=True,
                                                                          description="The member whose birthday "
                                                                                      "you want to delete.")):
    if user is not None:  # Check if it is a mod call or not
        if user.id == interaction.user.id:  # Wrong call
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="Wrong command. Use /delete_birthday to delete your own!")
            return
        elif not check_mod(interaction):  # Not a mod
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(
                content="You do not have the permission to delete others' birthdays!")
            return
    if user is None:
        user = interaction.user
    stat = check_user(user.id, interaction)
    if stat == 0 or stat == 1:  # Wrong channel or member not in server
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content="This is the wrong channel!")
            return
        await interaction.edit_original_message(content="Member is not in server.")
        return
    await interaction.response.defer()
    stat = birthday.remove_date(user.id)
    if stat:
        await interaction.edit_original_message(content="Birthday deleted.")
    else:
        await interaction.edit_original_message(
            content=f"{user.display_name}'s birthday does not exist in the system. <:EeveeCry:965985819057848320>")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Add a reaction to a message. Must be used in the same "
                                                         "channel as the target message. Mods only.")
async def add_emote(interaction: nextcord.Interaction,
                    message_id: str = nextcord.SlashOption(required=True, description="The ID of the message."),
                    emote: str = nextcord.SlashOption(required=True, description="The emoji you want to add.")):
    await interaction.response.defer(ephemeral=True)
    if not check_mod(interaction):
        await interaction.edit_original_message(content="Mods only.")
        return
    try:
        if message_id.isnumeric():
            message = await interaction.channel.fetch_message(message_id)
        else:
            await interaction.edit_original_message(content="Not a valid id.")
            return
    except nextcord.NotFound or nextcord.HTTPException or nextcord.InvalidArgument:
        await interaction.edit_original_message(content="Message not found./Emote does not exist")
        return
    await message.add_reaction(emote)
    await interaction.edit_original_message(content="Done.")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Secret Command. Owner only.")
async def secret(interaction: nextcord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyyBleh:1055108393372749824>")
        return
    await interaction.edit_original_message(file=nextcord.File(r"./data/bday.json"))


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Edits a message Eevee sent. Mods only.")
async def edit(interaction: nextcord.Interaction,
               message_id: str= nextcord.SlashOption(required=True, description="The ID of the message."),
               content: str = nextcord.SlashOption(required=True, description="The new content of the message.")):
    await interaction.response.defer(ephemeral=True)
    if not check_mod(interaction):
        await interaction.edit_original_message(content="Mods only.")
        return
    try:
        if message_id.isnumeric():
            message = await interaction.channel.fetch_message(message_id)
        else:
            await interaction.edit_original_message(content="Not a valid id.")
            return
    except:
        await interaction.edit_original_message(content="Message not found.")
        return
    if message.author.id == client.user.id:
        await message.edit(content=content)
        await interaction.edit_original_message(content="Done.")
    else:
        await interaction.edit_original_message(content="That message is not mine!")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Changes Eevee's activity. "
                                                         "Add url only when streaming. Owner only.")
async def activity(interaction: nextcord.Interaction, activity_name: str, verb: str = nextcord.SlashOption(
    required=True,
    choices={"Play": "Playing", "Stream": "Streaming", "Listen": "Listening", "Watch": "Watching"}),
                   url: str = None):
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyyBleh:1055108393372749824>")
        return
    verb_dict = {"Playing": nextcord.Game(name=activity_name),
                 "Streaming": nextcord.Streaming(name=activity_name, url=url),
                 "Listening": nextcord.Activity(type=nextcord.ActivityType.listening, name=activity_name),
                 "Watching": nextcord.Activity(type=nextcord.ActivityType.watching, name=activity_name)}
    await interaction.response.defer(ephemeral=True)
    await client.change_presence(activity=verb_dict[verb])
    await interaction.edit_original_message(content=f"Done. Activity is changed to \"{verb} {activity_name}\".")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Changes Eevee's status. "
                                                         "Add url only when streaming. Owner only.")
async def status(interaction: nextcord.Interaction, stat: str = nextcord.SlashOption(
    required=True,
    choices={"Online": "Online", "Idle": "Idle",
             "Do Not Disturb": "DND", "Offline": "Offline"})):
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyyBleh:1055108393372749824>")
        return
    status_dict = {"Online": nextcord.Status.online, "Idle": nextcord.Status.idle,
                   "DND": nextcord.Status.dnd, "Offline": nextcord.Status.offline}
    await interaction.response.defer(ephemeral=True)
    await client.change_presence(status=status_dict[stat])
    await interaction.edit_original_message(content=f"Done.")


async def ann():
    schedule_time = datetime.datetime.now().replace(hour=2, minute=0, second=0, microsecond=0)
    # DEBUG PRINTING COMMANDS
    # print(schedule_time)
    # print(timestamp())
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        if schedule_time <= now:
            await bday_announcement()
            # add one day to schedule_time to repeat on next day
            schedule_time += datetime.timedelta(days=1)
        await asyncio.sleep(10)


async def bday_announcement():
    user_id = birthday.get_user()
    if user_id is not None:
        await announce(user_id)
    else:
        channel_test = client.get_guild(int(os.getenv('TEST_GUILD'))).get_channel(int(os.getenv('TEST_CHANNEL')))
        await channel_test.send(f"No message today.\n{timestamp()}")
        print("no message.")


async def announce(user_id):
    for i in user_id:
        if not client.get_guild(int(os.getenv('OUTLET'))).get_member(i):
            user_id.remove(i)
    channel_test = client.get_guild(int(os.getenv('TEST_GUILD'))).get_channel(int(os.getenv('TEST_CHANNEL')))
    channel = client.get_guild(int(os.getenv('OUTLET'))).get_channel(int(os.getenv('AN_ID')))
    # DEBUG PURPOSES ONLY
    # channel = channel_test
    if len(user_id) == 0:
        await channel_test.send(
            f"No message today.\n{timestamp()}\nThere is at least one birthday today")
        print(f"no message. yes birthday.")
        return
    elif len(user_id) == 1:
        if user_id[0] == client.user.id:
            await channel.send(f"It's my birthday today hehe <:EeveeLurk:991271779735719976>")
        else:
            await channel.send(f"It's <@{user_id[0]}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@&{community}>")
        await channel_test.send(f"{client.get_user(int(user_id[0])).name}'s birthday message is sent.\n{timestamp()}")
    elif len(user_id) == 2:
        if client.user.id in user_id:
            a = 1
            if user_id[0] == client.user.id:
                a = 0
            await channel.send(f"It's <@{user_id[(a + 1) % 2]}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@&{community}>")
            await channel.send(f"It's also my birthday today hehe <:EeveeLurk:991271779735719976>")
        else:
            await channel.send(f"It's the birthday of <@{user_id[0]}> and <@{user_id[1]}>, "
                               f"everyone wish them a happy birthday!\nHave a great day birthday stars! "
                               f"<:EeveeHeart:977982162303324190> \n<@&{community}>")
        await channel_test.send(f"{client.get_user(int(user_id[0])).name} and "
                                f"{client.get_user(int(user_id[1])).name}'s birthday message is sent.\n{timestamp()}")
    else:
        stat = False
        message = f"It's the birthday of "
        for i in range(len(user_id) - 1):
            if user_id[i] == client.user.id:
                stat = True
                continue
            message += f"<@{user_id[i]}>"
            if i != len(user_id) - 2:
                message += ", "
        message += (f" and <@{user_id[len(user_id) - 1]}>! Happy Birthday to all of them!"
                    f"<:EeveeHeart:977982162303324190> \n<@&{community}>")
        await channel.send(message)
        if stat:
            await channel.send(
                f"I guess I should also mention it's my birthday today as well <:EeveeLurk:991271779735719976>")
        debug = "bday message of "
        for j in range(len(user_id)):
            if j != 0:
                debug += ", "
            debug += f"{client.get_user(int(user_id[j])).name}"
        debug += " sent."
        debug += f"\n{timestamp()}"
        await channel_test.send(debug)


def check_tomorrow(month, day, year):
    today = datetime.datetime.now().date()
    date = datetime.date(year, month, day)
    if (date - today).days == 1:
        return True
    return False


def random_colour():
    colours = {1: nextcord.Colour.red(),
               2: nextcord.Colour.orange(),
               3: nextcord.Colour.yellow(),
               4: nextcord.Colour.green(),
               5: nextcord.Colour.blue(),
               6: nextcord.Colour.purple(),
               7: nextcord.Colour.dark_purple()}
    random.seed(datetime.datetime.now().timestamp())
    return colours[random.randint(1, 7)]


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Lists out future birthdays.")
async def coming_birthdays(interaction: nextcord.Interaction):
    if interaction.channel_id not in perm:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="This is the wrong channel!")
        return
    await interaction.response.defer()
    coming = birthday.coming_birthdays()
    des = f""
    today = datetime.datetime.now()
    for i in coming:
        if today.month == i['month'] and today.day == i['day']:
            des += f"**Today**\n" + f"<@{i['id']}>\n\n"
            continue
        if check_tomorrow(i['month'], i['day'], today.year):
            des += f"**Tomorrow**\n" + f"<@{i['id']}>\n\n"
            continue
        des += f"**{i['day']} {calendar.month_name[i['month']]}**\n" + f"<@{i['id']}>\n\n"
    await interaction.edit_original_message(embeds=[
        nextcord.Embed(title="Upcoming Birthdays <:EeveeUwU:965977552067899482>",
                       description=des,
                       colour=random_colour())])


class Pages(nextcord.ui.View):

    def __init__(self, *, timeout=180, pages=None, page_number=0, ctx=None):
        super().__init__(timeout=timeout)
        if pages is None:
            pages = []
        self.pages = pages
        self.page_number = page_number
        self.ctx = ctx

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, emoji="⬅️", disabled=False)
    async def previous_button(self, button: nextcord.ui.button, interaction):
        if self.page_number <= 0:
            await interaction.response.send_message("You are already at the first page! <:EeveeOwO:965977455791857695>",
                                                    ephemeral=True)
        else:
            self.page_number -= 1
        await interaction.response.edit_message(view=self, content="",
                                                embed=self.pages[self.page_number])

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, emoji="➡️", disabled=False)
    async def next_button(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if self.page_number >= 2:
            await interaction.response.send_message("You are already at the last page! <:EeveeOwO:965977455791857695>",
                                                    ephemeral=True)
        else:
            self.page_number += 1
        await interaction.response.edit_message(view=self, content="",
                                                embed=self.pages[self.page_number])


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="My info!")  # Create a slash command
async def info(ctx):
    if ctx.channel_id not in perm:
        await ctx.response.defer(ephemeral=True)
        await ctx.edit_original_message(content="This is the wrong channel!")
        return
    title = "Birthday Eevee <:EeveeWave:1062326395935674489>"
    url = "https://github.com/anormalperson8/Birthday"
    colour = random_colour()
    page1 = nextcord.Embed(title=title,
                           description="# Server Global Commands\n"
                                       "The following commands can be used by all users of Outlet.\n"
                                       "## Slash Commands\n"
                                       "**coming_birthdays**\nThis command shows future birthdays of the server.\n"
                                       "(At most 8.)\n"
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
                           colour=colour, url=url)
    page2 = nextcord.Embed(title=title,
                           description="# Moderator Commands\n"
                                       "The following commands can only be used by moderators of Outlet.\n"
                                       "## Slash Commands\n"
                                       "**set_user_birthday**\nThis command sets a user's birthday to the bot.\n"
                                       "Same as **set_birthday**, but cannot be used to set your own.\n"
                                       "**delete_user_birthday**\nThis command deletes a user's birthday.\n"
                                       "Same as **delete_birthday**, but cannot be used to delete your own.\n"
                                       "**add_reaction**\nThis commands lets "
                                       "Birthday Eevee add a reaction to a message.\n"
                                       "(Only accepts default emojis or emojis of Outlet.)\n"
                                       "Message ID and emotes are required for the command.\n"
                                       "**edit**\nThis commands edits a message Birthday Eevee sent.\n"
                                       "Message ID and content are requried for the command.\n"
                                       "## Text Commands (Prefix: `.`)\n"
                                       "**echo**\nBirthday Eevee echos what you say.",
                           colour=colour, url=url)
    page3 = nextcord.Embed(title=title,
                           description="# Owner Commands\n"
                                       "Don't try it. They can only be used by the owner.\n"
                                       "## Slash Commands\n"
                                       "**test**\nDon't try it.\n"
                                       "**checkers**\nDon't try it.\n"
                                       "**status**\nDon't try it.\n"
                                       "**activity**\nDon't try it.\n"
                                       "**secret**\nIt *literally* says secret.\n"
                                       "## Text Commands (prefix: `.`)\n"
                                       "**time**\nYou won't get any response if you're not the owner.",
                           colour=colour, url=url)
    pages = [page1, page2, page3]
    image = "https://cdn.discordapp.com/attachments/1117033415305347073/1133685861318414497/BdayEevee.png"
    for i in range(len(pages)):
        pages[i].set_thumbnail(image)
        pages[i].set_footer(text=f"Page {i+1}/3")
    await ctx.response.send_message(content="", embed=page1, view=Pages(pages=pages))


# Easter eggs I guess
@client.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return
    if "i don't like birthdays" in message.content.lower() or "i dont like birthdays" in message.content.lower():
        name = message.author.nick
        if name is None:
            name = message.author.name
        await message.channel.send(f"You're mean, {name}. <:EeveeMegaSob:1084890813902884994>")
    elif "birthday eevee" in message.content.lower():
        await message.add_reaction("<:EeveeLurk:991271779735719976>")


client.run(token)
