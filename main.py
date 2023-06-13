# Packages
import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
import datetime
import calendar
# Self .py files
import birthday

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, activity=nextcord.Game(name="Happy Birthday...?"))

load_dotenv("/home/sunny/PythonBday/data/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))
mod_role_id = [int(os.getenv('MOD_ID'))]
outlet = int(os.getenv('OUTLET'))
announcement = int(os.getenv('AN_ID'))
community = int(os.getenv('COM_ID'))
guilds_list = []
for guild in client.guilds:
    guilds_list += guild.id
perm = birthday.get_perm()


@client.event
async def on_ready():
    await client.wait_until_ready()
    print('We have logged in as {0.user}'.format(client))
    bday_announcement.start()


# Response-testing command
@client.command()
async def boo(ctx):
    if ctx.author.bot:
        await ctx.send("You're not a user :P")
        return
    await ctx.send(f"Oi")


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
        for role2 in mod_role_id:
            if role.id == role2:
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
        channel = client.get_guild(outlet).get_channel(announcement)
        user_id = birthday.get_user()
        if user_id is not None:
            await channel.send(f"It's <@{user_id}>'s birthday, everyone wish them a happy birthday! "
                               f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@{community}>")


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
    if stat == 0 or stat == 1: # Wrong channel or member not in server
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
    await interaction.edit_original_message(content="Birthday added/edited! <:EeveeCool:1007625997719449642>")


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


@tasks.loop(hours=23, minutes=59, seconds=30.0)
async def bday_announcement():
    # Testing purposes:
    channel_test = client.get_guild(int(os.getenv('TEST_GUILD'))).get_channel(int(os.getenv('TEST_CHANNEL')))
    # Outlet:
    channel = client.get_guild(outlet).get_channel(announcement)
    user_id = birthday.get_user()
    if user_id is not None:
        await channel.send(f"It's <@{user_id}>'s birthday, everyone wish them a happy birthday! "
                           f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@{community}>")

        await channel_test.send(f"{nextcord.Client.get_user(int(user_id)) .name}'s birthday message is sent.")

# Easter egg I guess
@client.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return
    name = message.author.nick
    if name is None:
        name = message.author.name
    if "I don't like birthdays" in message.content:
        await message.channel.send(f"You're mean, {name}. <:EeveeMegaSob:1084890813902884994>")


client.run(token)
