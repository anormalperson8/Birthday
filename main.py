import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents, activity=nextcord.Game(name="Suffering"))

load_dotenv("/home/sunny/SuneBot/data/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))

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
@client.command()
async def sync(ctx):
    if ctx.author.id == owner_id:
        await client.tree.sync()
        await ctx.send("Commands synced!")
    else:
        await ctx.send("You're not the owner")


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
