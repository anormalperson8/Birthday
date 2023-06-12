import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands
import datetime
import birthday
import calendar

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents, activity=nextcord.Game(name="Happy Birthday...?"))

load_dotenv("/home/sunny/PythonBday/data/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))
guilds_list = []
for guild in client.guilds:
    guilds_list += guild.id


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# Response-testing command
@client.command()
async def boo(ctx):
    if ctx.author.bot:
        await ctx.send("You're not a user :P")
        return
    await ctx.send("Oi")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Pong!")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.defer()
    await interaction.edit_original_message(content="Pong!")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Get a member's birthday! You can even get mine!")
async def get_birthday(interaction: nextcord.Interaction, user: nextcord.User):
    await interaction.response.defer()
    # TO BE REMOVED
    if interaction.user.id != owner_id and interaction.user.id != int("805783359610552380"):
        await interaction.edit_original_message(content="You don't have permission yet! Stay tuned.")
        return
    # TODO: ADD BLOCKING OF MEMBERS NOT IN THE SERVER
    if interaction.guild.get_member(user.id) is None:
        await interaction.edit_original_message(content="Member is not in server.")
        return
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
        if not calendar.isleap(year):
            return False
        return True
    if month % 2 == 0 and month <= 7 and day > 30:
        return False
    if month % 2 == 1 and month > 7 and day > 30:
        return False
    if datetime.datetime.now() < datetime.datetime(year=year, month=month, day=day):
        return False
    return True


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set your own birthday!")
async def set_birthday(interaction: nextcord.Interaction, user: nextcord.User, day: int, month: int, year: int = 1):
    # TODO: SETUP THE SET BIRTHDAY
    # TODO: CHECK INTERACTION CHANNELS
    await interaction.response.defer()
    if not valid_date(year, month, day):
        await interaction.edit_original_message(content="Invalid Birthday! <:EeveeOwO:965977455791857695>")
        return
    await interaction.edit_original_message(content=f"This hasn't been implemented yet. Stay tuned!")


@commands.guild_only()
@client.slash_command(guild_ids=guilds_list, description="Set your own birthday")
async def set_user_birthday(interaction: nextcord.Interaction, user: nextcord.User, day: int, month: int,
                            year: int = 1):
    # TODO: SETUP THE SET BIRTHDAY (MOD'S VERSION)
    # TODO: CHECK INTERACTION CHANNEL
    await interaction.response.defer()
    if not valid_date(year, month, day):
        await interaction.edit_original_message(content="Invalid Birthday! <:EeveeOwO:965977455791857695>")
        return
    await interaction.edit_original_message(content=f"This hasn't been implemented yet. Stay tuned!")


@client.listen('on_message')
async def on_message(message):
    if message.author.bot:
        return
    name = message.author.nick
    if name is None:
        name = message.author.name
    if message.content == "Hi Bday":
        await message.channel.send(f"Hello {name}!")


client.run(token)
