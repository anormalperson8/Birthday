# Packages
import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands
import datetime
import calendar
import asyncio

# Self .py files
import birthday
import info_command
import server_info

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, help_command=None,
                      activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="The Passage of Time"))

path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)
data_path = f"{path}/data"
load_dotenv(f"{data_path}/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))
guilds_list = []
for guild in client.guilds:
    guilds_list.append(int(guild.id))
servers = server_info.get_servers()


@client.event
async def on_ready():
    await client.wait_until_ready()
    client.loop.create_task(ann())
    print('We have logged in as {0.user}'.format(client))
    test_server = server_info.get_servers()[0]
    channel_test = client.get_guild(test_server.serverID).get_channel(test_server.allowedChannels[0])
    await channel_test.send("Bot is on.")


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
        f"The time (hh/mm/ss) now is {now.time().hour:02}:{now.time().minute:02}:{now.time().second:02}.\n" \
        f"Today is {calendar.day_name[now.weekday()]}."
    return a


@client.command()
async def time(ctx):
    if ctx.author.id != owner_id:
        return
    await ctx.send(f"Time check!\n{timestamp()}")


async def echo_content(ctx, arg, ping: bool):
    # Owner Privileges
    if ctx.author.id == owner_id:
        if ctx.message.reference is not None and ctx.message.reference.resolved is not None:
            await ctx.message.reference.resolved.reply(arg, mention_author=ping)
        else:
            await ctx.send(arg)
        return
    # Check Mod
    for role in ctx.message.author.roles:
        if role.id in server_info.search_for_server(servers, ctx.message.guild.id).moderatorRoles:
            if ctx.message.reference is not None and ctx.message.reference.resolved is not None:
                await ctx.message.reference.resolved.reply(arg, mention_author=ping)
            else:
                await ctx.send(arg)
            return


@commands.guild_only()
@client.command()
async def echo(ctx, *, arg):
    await ctx.message.delete()
    await echo_content(ctx, arg, True)


@commands.guild_only()
@client.command()
async def echo2(ctx, *, arg):
    await ctx.message.delete()
    await echo_content(ctx, arg, False)


# Check whether the member is in the server, and whether users are allowed to use commands in the channel
def check_user(user_id, interaction):
    # Block users not in server
    if interaction.guild.get_member(user_id) is None:
        return 0
    # Only allow specific channels
    server = server_info.search_for_server(servers, interaction.guild_id)
    if interaction.channel_id not in server.allowedChannels:
        return 1
    return None


# Check whether a user is mod
def check_mod(interaction: nextcord.Interaction):
    for role in interaction.user.roles:
        if role.id in server_info.search_for_server(servers, interaction.guild_id).moderatorRoles:
            return True
    return False


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Test command. Owner only")
async def test(interaction: nextcord.Interaction,
               stat: int = nextcord.SlashOption(default=1, required=False,
                                                description="0 to forcefully start announcing birthday. 1 otherwise.")):
    # Owner only
    if interaction.user.id != owner_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(
            content="This is for the owner not you <:sunnyyBleh:1134343350133202975>")
        return
    # Check channel
    if interaction.channel_id not in server_info.search_for_server(servers, interaction.guild_id).allowedChannels:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content=f"<@{interaction.user.id}> This is the wrong test channel!")
        return

    # Force announce?
    if stat:
        await interaction.response.defer()
        await interaction.edit_original_message(content="test done <:EeveeUwU:965977552067899482>")
    else:
        await interaction.response.defer()
        await bday_announcement()
        await interaction.edit_original_message(content="test (status: 0) done <:EeveeUwU:965977552067899482>")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Checkers. Not the board game one. Owner only.")
async def checkers(interaction: nextcord.Interaction):
    # Owner
    if interaction.user.id != owner_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(
            content="This is for the owner not you <:sunnyBleh:1134343350133202975>")
        return

    bday_list = birthday.get_user()
    # No birthdays
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


@client.slash_command(guild_ids=guilds_list, description="Pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.edit_original_message(content="Pong!")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Get a member's birthday! You can even get mine!")
async def get_birthday(interaction: nextcord.Interaction,
                       user: nextcord.User = nextcord.SlashOption(required=False,
                                                                  description="The user whose birthday "
                                                                              "you want to know.",
                                                                  default=None)):
    # Default option of user
    if user is None:
        user = interaction.user

    stat = check_user(user.id, interaction)

    # 0 means user is not in server, 1 means wrong channel
    if stat == 0 or stat == 1:
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content=f"This is the wrong channel!")
            return
        await interaction.edit_original_message(content="Member is not in server.")
        return

    await interaction.response.defer()
    date, allow = birthday.get_date(user.id)

    if date is None:
        await interaction.edit_original_message(
            content=f"{user.global_name}'s birthday does not exist in the system. <:EeveeCry:965985819057848320>")
        return

    # Generate the date string if date exists
    day = int(date.day)
    month = date.strftime("%B")
    year = int(date.strftime("%Y"))

    # Generate postfix of the date
    postfix = 'th'
    if day // 10 != 1:
        if day % 10 == 1:
            postfix = 'st'
        elif day % 10 == 2:
            postfix = 'nd'
        elif day % 10 == 3:
            postfix = 'rd'

    phrase = f"on **{day}{postfix} {month}**"

    # If the user included the year
    if year != 1 and allow:
        phrase += f"\nThey were born in {year}."

    # Calculate date difference
    now = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
    if (date.month >= now.month) and (date.day >= now.day):
        next_bday = (datetime.datetime(now.year, date.month, date.day) - now).days
    else:
        next_bday = (datetime.datetime(now.year + 1, date.month, date.day) - now).days

    if next_bday == 0:
        await interaction.edit_original_message(
            content=f"It is {user.global_name}'s birthday today, {phrase}")
    elif next_bday == 1:
        await interaction.edit_original_message(
            content=f"Tomorrow is {user.global_name}'s next birthday, {phrase}")
    else:
        await interaction.edit_original_message(
            content=f"{user.global_name}'s next birthday is in **{next_bday}** days, {phrase}")


def valid_date(year, month, day):
    if year < 1 or month < 1 or month > 12 or year > 2023 or day < 1 or day > 31:
        return False

    # Check for 29th Feb in leap years
    if month == 2 and day > 28:
        if calendar.isleap(year) and day == 29:
            return True
        return False

    # On or before July, odd-numbered months have 31 days
    if month <= 7 and month % 2 == 0 and day > 30:
        return False
    # After July, even-numbered months have 31 days
    if month > 7 and month % 2 == 1 and day > 30:
        return False

    # Birthday in the future?
    if datetime.datetime.now() < datetime.datetime(year=year, month=month, day=day):
        return False

    return True


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set your own birthday!")
async def set_birthday(interaction: nextcord.Interaction,
                       day: int = nextcord.SlashOption(required=True, description="The day."),
                       month: int = nextcord.SlashOption(required=True, description="The month."),
                       year: int = nextcord.SlashOption(required=False, description="The year.", default=1),
                       disclose: bool = nextcord.SlashOption(required=False,
                                                             description="Whether your birth year would be disclosed "
                                                                         "in get_birthday().",
                                                             default=False)):
    await set_user_birthday(interaction, None, day, month, year, disclose)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set another user's birthday. Mods only")
async def set_user_birthday(interaction: nextcord.Interaction,
                            user: nextcord.User = nextcord.SlashOption(required=True,
                                                                       description="The member whose birthday "
                                                                                   "you want to set."),
                            day: int = nextcord.SlashOption(required=True, description="The day."),
                            month: int = nextcord.SlashOption(required=True, description="The month."),
                            year: int = nextcord.SlashOption(required=False, description="The year.", default=1),
                            disclose: bool = nextcord.SlashOption(required=False,
                                                                  description="Whether your birth year would be disclosed "
                                                                              "in get_birthday().",
                                                                  default=False)):
    # Check if it is a mod call or not
    if user is not None and not check_mod(interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="You do not have the permission to add others' birthdays!")
        return

    # Setting own birthday
    if user is None:
        user = interaction.user

    stat = check_user(user.id, interaction)

    # Wrong channel or member not in server
    if stat == 0 or stat == 1:
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

    birthday.set_date(user.id, year, month, day, disclose)
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
    # Check if it is a mod call or not
    if user is not None and not check_mod(interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="You do not have the permission to delete others' birthdays!")
        return

    if user is None:
        user = interaction.user

    stat = check_user(user.id, interaction)
    if stat == 0 or stat == 1:
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content="This is the wrong channel!")
            return
        await interaction.edit_original_message(content="You cannot delete a member's birthday "
                                                        "if the member not in this server.")
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
        await interaction.edit_original_message(content="Message not found./Emote does not exist.")
        return
    await message.add_reaction(emote)
    await interaction.edit_original_message(content="Done.")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Secret Command. Owner only.")
async def secret(interaction: nextcord.Interaction,
                 number: int = nextcord.SlashOption(required=False, description="A number.", default=1)):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            embed=nextcord.Embed(colour=info_command.random_colour(), title="This is a secret🤫",
                                 url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                 description="There is totally not a link at the title."))
        return
    if number:
        await interaction.edit_original_message(files=[nextcord.File(r"./data/bday.json"),
                                                       nextcord.File(r"./data/server.json"),
                                                       nextcord.File(r"./data/day.txt")])
    else:
        await interaction.edit_original_message(files=[nextcord.File(r"./data/bday.json"),
                                                       nextcord.File(r"./data/server.json"),
                                                       nextcord.File(r"./data/day.txt"),
                                                       nextcord.File(r"./data/data.env")])


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Edits a message Eevee sent. Mods only.")
async def edit(interaction: nextcord.Interaction,
               message_id: str = nextcord.SlashOption(required=True, description="The ID of the message."),
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
    except nextcord.NotFound or nextcord.HTTPException or nextcord.InvalidArgument:
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
async def activity(interaction: nextcord.Interaction,
                   activity_name: str = nextcord.SlashOption(required=True, description="The name of the application. "
                                                                                        "Put anything when deleting."),
                   verb: str = nextcord.SlashOption(
                       required=True,
                       choices={"Play": "Playing", "Stream": "Streaming",
                                "Listen": "Listening", "Watch": "Watching", "Delete": "None"},
                       description="The action."),
                   url: str = nextcord.SlashOption(
                       required=False,
                       description="The url. Add only when streaming.",
                       default=None)):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyBleh:1134343350133202975>")
        return
    verb_dict = {"Playing": nextcord.Game(name=activity_name),
                 "Streaming": nextcord.Streaming(name=activity_name, url=url),
                 "Listening": nextcord.Activity(type=nextcord.ActivityType.listening, name=activity_name),
                 "Watching": nextcord.Activity(type=nextcord.ActivityType.watching, name=activity_name),
                 "None": None}
    await client.change_presence(activity=verb_dict[verb])
    if verb == "None":
        await interaction.edit_original_message(content=f"Done. Activity is deleted.")
    elif verb == "Listening":
        await interaction.edit_original_message(content=f"Done. Activity is changed to \"{verb} to {activity_name}\".")
    else:
        await interaction.edit_original_message(content=f"Done. Activity is changed to \"{verb} {activity_name}\".")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Changes Eevee's status. "
                                                         "Add url only when streaming. Owner only.")
async def status(interaction: nextcord.Interaction,
                 stat: str = nextcord.SlashOption(
                     required=True,
                     choices={"Online": "Online", "Idle": "Idle",
                              "Do Not Disturb": "DND", "Offline": "Offline"},
                     description="The status.")):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyBleh:1134343350133202975>")
        return
    status_dict = {"Online": nextcord.Status.online, "Idle": nextcord.Status.idle,
                   "DND": nextcord.Status.dnd, "Offline": nextcord.Status.offline}
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
            day = now.weekday()
            # Read day.txt
            if os.path.isfile(data_path + "/day.txt"):
                weekday_file = open(data_path + "/day.txt", "r")
                day_in_file = weekday_file.read()
                weekday_file.close()
            else:
                # Previous day
                day_in_file = (day + 6) % 7
            # Announce if the day in txt does not match
            if int(day_in_file) != day:
                weekday_file = open(data_path + "/day.txt", "w")
                weekday_file.write(str(day))
                weekday_file.close()
                await bday_announcement()
            # add one day to schedule_time to repeat on next day
            schedule_time += datetime.timedelta(days=1)
        await asyncio.sleep(10)


async def bday_announcement():
    user_id = birthday.get_user()
    if user_id is not None:
        for server in servers:
            await announce(list(user_id), server)
    else:
        # Test server is hard-coded as the first server and only 1 allowed channel
        test_server = server_info.get_servers()[0]
        channel_test = client.get_guild(test_server.serverID).get_channel(test_server.allowedChannels[0])
        await channel_test.send(f"No message for all servers today.\n{timestamp()}")
        print("No message.")


async def announce(user_id: list, server: server_info.Server):
    # No announcement channel
    if server.announcementChannel == 1:
        return

    # Remove all members not in the server
    for i in user_id:
        if client.get_guild(server.serverID).get_member(i) is None:
            user_id.remove(i)

    # Create the role string
    role = f"<@&{server.role_to_ping}>"
    # No role to ping
    if server.role_to_ping == 1:
        role = f":D"

    # Test server is hard-coded as the first server and only 1 allowed channel
    test_server = server_info.get_servers()[0]
    channel_test = client.get_guild(test_server.serverID).get_channel(test_server.allowedChannels[0])
    channel = client.get_guild(server.serverID).get_channel(server.announcementChannel)
    # DEBUG PURPOSES ONLY
    # channel = channel_test
    # print(f"for channel {server.serverID} {role}")
    if len(user_id) == 0:
        await channel_test.send(
            f"For server {server.serverID}:\n"
            f"No message today.\n{timestamp()}\nThere is at least one birthday today though.")
        return
    # 1 user
    elif len(user_id) == 1:
        # The bot itself
        if user_id[0] == client.user.id:
            await channel.send(f"It's my birthday today hehe <:EeveeLurk:991271779735719976>")
        else:
            await channel.send(f"It's <@{user_id[0]}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n"
                               f"{role}")
        # Test server
        await channel_test.send(f"For server {server.serverID}:\n"
                                f"{client.get_user(int(user_id[0])).name}'s birthday message is sent.\n{timestamp()}")
    # 2 users
    elif len(user_id) == 2:
        # If one of them is the bot itself
        if client.user.id in user_id:
            a = 1
            if user_id[0] == client.user.id:
                a = 0
            await channel.send(f"It's <@{user_id[(a + 1) % 2]}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n{role}")
            await channel.send(f"It's also my birthday today hehe <:EeveeLurk:991271779735719976>")
        else:
            await channel.send(f"It's the birthday of <@{user_id[0]}> and <@{user_id[1]}>, "
                               f"everyone wish them a happy birthday!\nHave a great day birthday stars! "
                               f"<:EeveeHeart:977982162303324190> \n{role}")
        # Test server
        await channel_test.send(f"For server {server.serverID}:\n"
                                f"{client.get_user(int(user_id[0])).name} and "
                                f"{client.get_user(int(user_id[1])).name}'s birthday message is sent.\n{timestamp()}")
    else:
        stat = False
        message = f"It's the birthday of "
        for i in range(len(user_id) - 1):
            # If the bot is in the list, it will not be added to the bday message
            if user_id[i] == client.user.id:
                stat = True
                continue
            message += f"<@{user_id[i]}>"
            # Second last uses "and"
            if i != len(user_id) - 2:
                message += ", "
        message += (f" and <@{user_id[len(user_id) - 1]}>! Happy Birthday to all of them!"
                    f"<:EeveeHeart:977982162303324190> \n{role}")
        await channel.send(message)
        if stat:
            await channel.send(
                f"I guess I should also mention it's my birthday today as well <:EeveeLurk:991271779735719976>")
        # Test server
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


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Lists out future birthdays.")
async def upcoming_birthdays(interaction: nextcord.Interaction):
    server = server_info.search_for_server(servers, interaction.guild_id)
    if interaction.channel_id not in server.allowedChannels:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="This is the wrong channel!")
        return
    await interaction.response.defer()
    dummy_coming = birthday.coming_birthdays()
    temp_coming = []
    for i in dummy_coming:
        # Remove the bot itself
        if i["id"] == client.user.id:
            continue
        # Not in server
        if not (client.get_guild(server.serverID).get_member(i["id"]) is None):
            temp_coming.append(i)

    des = f""
    today = datetime.datetime.now()
    length = 10
    if len(temp_coming) < 10:
        length = len(temp_coming)
    if length == 0:
        des += "No birthdays :("
    coming = [temp_coming[i] for i in range(length)]
    for i in coming:
        if today.month == i['month'] and today.day == i['day']:
            des += f"**Today**\n" + f"<@{i['id']}>\n\n"
            continue
        if check_tomorrow(i['month'], i['day'], today.year):
            des += f"**Tomorrow**\n" + f"<@{i['id']}>\n\n"
            continue
        des += f"**{i['day']:02} {calendar.month_name[i['month']]}**\n" + f"<@{i['id']}>\n\n"
    await interaction.edit_original_message(embeds=[
        nextcord.Embed(title="Upcoming Birthdays <:EeveeUwU:965977552067899482>",
                       description=des,
                       colour=info_command.random_colour())])


class Pages(nextcord.ui.View):

    def __init__(self, *, timeout=90, pages=None, page_number=0, ctx=None):
        super().__init__(timeout=timeout)
        if pages is None:
            pages = []
        self.pages = pages
        self.page_number = page_number
        self.ctx = ctx

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, emoji="⬅️", disabled=True)
    async def previous_button(self, button: nextcord.ui.button, interaction):
        if self.page_number <= 0:
            await interaction.response.send_message("You are already at the first page! <:EeveeOwO:965977455791857695>",
                                                    ephemeral=True)
        else:
            self.page_number -= 1
            await self.update_button(self.page_number)
            await interaction.response.edit_message(view=self, content="",
                                                    embed=self.pages[self.page_number])

    @nextcord.ui.button(label="", style=nextcord.ButtonStyle.gray, emoji="➡️", disabled=False)
    async def next_button(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
        if self.page_number >= len(self.pages) - 1:
            await interaction.response.send_message("You are already at the last page! <:EeveeOwO:965977455791857695>",
                                                    ephemeral=True)
        else:
            self.page_number += 1
            await self.update_button(self.page_number)
            await interaction.response.edit_message(view=self, content="",
                                                    embed=self.pages[self.page_number])

    async def update_button(self, page: int):
        self.previous_button.disabled = page == 0
        self.next_button.disabled = page == len(self.pages) - 1

    async def on_timeout(self) -> None:
        await self.disable_button()
        og = await self.ctx.original_message()
        await og.edit(view=self, content="", embed=self.pages[self.page_number])

    async def disable_button(self):
        self.previous_button.disabled = True
        self.next_button.disabled = True


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="My info!")
async def info(interaction):
    server = server_info.search_for_server(servers, interaction.guild_id)
    if interaction.channel_id not in server.allowedChannels:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(content="This is the wrong channel!")
        return
    title = "Birthday Eevee <:EeveeWave:1062326395935674489>"
    url = "https://github.com/anormalperson8/Birthday"
    pages = [info_command.create_page(title, url, i + 1) for i in range(3)]
    image = "https://github.com/anormalperson8/Birthday/blob/master/image/BdayEevee.png?raw=true"
    for i in range(len(pages)):
        pages[i].set_thumbnail(image)
        pages[i].set_footer(text=f"Page {i + 1}/3")
    await interaction.response.send_message(content="", embed=pages[0], view=Pages(pages=pages, ctx=interaction))


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Changes server information. Owner only.")
async def modify(interaction: nextcord.Interaction,
                 server_id: str = nextcord.SlashOption(required=True, description="The server to edit."),
                 action: int = nextcord.SlashOption(required=True,
                                                    choices={"Add": 1,
                                                             "Remove": 0},
                                                    description="Add or remove an attribute."),
                 thing_to_modify: int = nextcord.SlashOption(required=True,
                                                             choices={"Announcement Channel": 1,
                                                                      "Moderator Role": 2, "Allowed Channel": 3,
                                                                      "Role to Ping": 4},
                                                             description="The attribute you want to edit."),
                 change: str = nextcord.SlashOption(required=False,
                                                    description="The ID you want to add/remove. "
                                                                "Write any number when removing ann/role",
                                                    default=None)):
    await interaction.response.defer(ephemeral=True)
    if interaction.user.id != owner_id:
        await interaction.edit_original_message(
            content="Did you not read the description? This is for the owner not you <:sunnyBleh:1134343350133202975>")
        return
    # Changing data types
    action = bool(action)
    try:
        server_id = int(server_id)
    except ValueError:
        await interaction.edit_original_message(content="Invalid server ID")
        return
    try:
        change = int(change)
    except ValueError:
        await interaction.edit_original_message(content="Invalid channel/role ID")
        return

    stat = False
    message = ""
    match thing_to_modify:
        case 1:
            if action and change is None:
                await interaction.edit_original_message(content=f"Problem: You forgot to include the ID.")
                return
            if change is None:
                change = 1
            stat, message = server_info.modify(server_id, action, announcement_channel=change)
        case 2:
            if change is None:
                await interaction.edit_original_message(content=f"Problem: You forgot to include the ID.")
                return
            stat, message = server_info.modify(server_id, action, moderator_role=change)
        case 3:
            if change is None:
                await interaction.edit_original_message(content=f"Problem: You forgot to include the ID.")
                return
            stat, message = server_info.modify(server_id, action, allowed_channel=change)
        case 4:
            if action and change is None:
                await interaction.edit_original_message(content=f"Problem: You forgot to include the ID.")
                return
            if change is None:
                change = 1
            stat, message = server_info.modify(server_id, action, role_to_ping=change)

    if stat:
        global servers
        servers = server_info.get_servers()
        await interaction.edit_original_message(content=f"Your modification is done!\n{message}")
        return
    await interaction.edit_original_message(content=f"Your modification was not completed.\n{message}")


# Easter eggs I guess
@client.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return
    if "i don't like birthdays" in message.content.lower() or "i dont like birthdays" in message.content.lower():
        name = message.author.nick
        if name is None:
            name = message.author.global_name
        await message.channel.send(f"<:EeveeMegaSob:1084890813902884994> You're mean, {name}.")
    elif "birthday eevee" in message.content.lower():
        await message.add_reaction("<:EeveeLurk:991271779735719976>")


client.run(token)
