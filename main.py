import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands
import json
import datetime

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
@client.slash_command(guild_ids=guilds_list, description="Get a member's birthday")
async def get_birthday(interaction: nextcord.Interaction, arg: nextcord.User):
    await interaction.response.defer()
    await interaction.edit_original_message(content=f"Pong!")


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
