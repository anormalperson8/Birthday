import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands, tasks
import datetime
import birthday
import calendar

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, activity=nextcord.Game(name="Happy Birthday...?"))

load_dotenv("/home/sunny/PythonBday/data/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))
mod_role_id = int(os.getenv('MOD_ID'))
outlet = int(os.getenv('OUTLET'))
announcement = int(os.getenv('AN_ID'))
community = int(os.getenv('COM_ID'))
ann_time = datetime.time(hour=17, minute=20, tzinfo=datetime.timezone.utc),
guilds_list = []
for guild in client.guilds:
    guilds_list += guild.id
perm = -1


@client.event
async def on_ready():
    await client.wait_until_ready()
    print('We have logged in as {0.user}'.format(client))
    bday_annoucement.start()


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
    if interaction.channel_id != perm:
        return 1
    return None


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="test")
async def test(interaction: nextcord.Interaction):
    if interaction.user.id != owner_id:
        await interaction.response.defer(ephemeral=True)
        await interaction.edit_original_message(
            content="This is for the owner not you <:sunnyyBleh:1055108393372749824>")
    if interaction.channel_id != perm:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(content=f"<@{interaction.user.id}> This is the wrong test channel!",
                                        delete_after=180)
        return
    await interaction.response.defer()
    await interaction.edit_original_message(content="test done <:EeveeUwU:965977552067899482>")


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
    await set_user_birthday(interaction, day, month, year, interaction.user)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set a user's birthday. Mods only")
async def set_user_birthday(interaction: nextcord.Interaction, day: int, month: int,
                            year: int = 1, user: nextcord.User = None):
    if user is None:
        user = interaction.user
    # Owner privileges
    elif interaction.user.id == owner_id:
        print('', end='')
    else:
        if not interaction.guild.get_role(mod_role_id) in interaction.user.roles:
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="You do not have the permission to add others' birthdays!")
            return
    stat = check_user(user.id, interaction)
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
    birthday.set_date(user.id, year, month, day)
    await interaction.edit_original_message(content="Birthday added/edited! <:EeveeCool:1007625997719449642>")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Delete your own birthday entry.")
async def delete_birthday(interaction: nextcord.Interaction):
    await delete_user_birthday(interaction, interaction.user)


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Delete a user's birthday entry. Mods only.")
async def delete_user_birthday(interaction: nextcord.Interaction, user: nextcord.User = None):
    if user is None:
        user = interaction.user
    # Owner privileges
    elif interaction.user.id == owner_id:
        print('', end='')
    else:
        if not interaction.guild.get_role(mod_role_id) in interaction.user.roles:
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_message(content="You do not have the permission to delete others' birthdays!")
            return
    stat = check_user(user.id, interaction)
    if stat == 0 or stat == 1:
        await interaction.response.defer(ephemeral=True)
        if stat:
            await interaction.edit_original_message(content=f"This is the wrong channel!")
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
async def bday_annoucement():
    # Testing purposes:
    channel = client.get_guild(949627365816958976).get_channel(1117033415305347073)
    # Outlet:
    # channel = client.get_guild(outlet).get_channel(announcement)
    user_id = birthday.get_user()
    if user_id is not None:
        await channel.send(f"It's <@{user_id}>'s birthday, everyone wish them a happy birthday! "
                           f"Have a great day birthday star! <:EeveeHeart:977982162303324190> \n<@{community}>")


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
