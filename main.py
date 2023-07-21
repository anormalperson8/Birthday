# Packages
import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
import datetime
import calendar
import asyncio

# Self .py files
import birthday

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, activity=nextcord.Game(name="Happy Birthday...?"))

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
    await ctx.send(f"Oi")


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
async def get_birthday(interaction: nextcord.Interaction, user: nextcord.User = None):
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
async def set_birthday(interaction: nextcord.Interaction, day: int, month: int, year: int = 1):
    await set_user_birthday(interaction, None, day, month, year)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set another user's birthday. Mods only")
async def set_user_birthday(interaction: nextcord.Interaction, user: nextcord.User, day: int, month: int,
                            year: int = 1):
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
async def delete_user_birthday(interaction: nextcord.Interaction, user: nextcord.User):
    if user is not None:  # Check if it is a mod call or not
        if user.id == interaction.user.id:  # Wrong call
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="Wrong command. Use /delete_birthday to set your own!")
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
async def add_emote(interaction: nextcord.Interaction, message_id: int, emote: str):
    await interaction.response.defer(ephemeral=True)
    if not check_mod(interaction):
        await interaction.edit_original_message(content="Mods only.")
        return
    try:
        message = await interaction.channel.fetch_message(message_id)
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
async def edit(interaction: nextcord.Interaction, message_id: int, content: str):
    await interaction.response.defer(ephemeral=True)
    if not check_mod(interaction):
        await interaction.edit_original_message(content="Mods only.")
        return
    try:
        message = await interaction.channel.fetch_message(message_id)
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
    schedule_time = datetime.datetime.now()
    schedule_time = schedule_time.replace(hour=3, minute=30, second=0, microsecond=0)
    # DEBUG TIME PRINT COMMANDS
    # print(schedule_time)
    # print(f"Now: {datetime.datetime.now()}")
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        if schedule_time <= now:
            await bday_announcement()
            # add one day to schedule_time to repeat on next day
            schedule_time += datetime.timedelta(days=1)
        await asyncio.sleep(200)


async def bday_announcement():
    user_id = birthday.get_user()
    if user_id is not None:
        await announce(user_id)
    else:
        print("no message.")


async def announce(user_id):
    for i in user_id:
        if not client.get_guild(int(os.getenv('OUTLET'))).get_member(i):
            user_id.remove(i)
    channel_test = client.get_guild(int(os.getenv('TEST_GUILD'))).get_channel(int(os.getenv('TEST_CHANNEL')))
    channel = client.get_guild(int(os.getenv('OUTLET'))).get_channel(int(os.getenv('AN_ID')))
    # DEBUG PURPOSES ONLY
    # channel = channel_test
    if len(user_id) == 1:
        if user_id[0] == client.user.id:
            await channel.send(f"It's my birthday today hehe <:EeveeLurk:991271779735719976>")
        else:
            await channel.send(f"It's <@{user_id[0]}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@&{community}>")
        await channel_test.send(f"{client.get_user(int(user_id[0])).name}'s birthday message is sent.")
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
                                f"{client.get_user(int(user_id[1])).name}'s birthday message is sent.")
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
        await channel_test.send(debug)


# Easter eggs I guess
@client.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return
    if "i don't like birthdays" in message.content.lower():
        name = message.author.nick
        if name is None:
            name = message.author.name
        await message.channel.send(f"You're mean, {name}. <:EeveeMegaSob:1084890813902884994>")
    elif "birthday eevee" in message.content.lower():
        await message.add_reaction("<:EeveeLurk:991271779735719976>")


client.run(token)
