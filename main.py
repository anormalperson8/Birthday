import nextcord
import os
from dotenv import load_dotenv
from nextcord.ext import commands

intents = nextcord.Intents.all()
client = commands.Bot(command_prefix='$', intents=intents, activity=nextcord.Game(name="Suffering"))

load_dotenv("/home/sunny/SuneBot/data/data.env")

token = os.getenv('TOKEN')
owner_id = int(os.getenv('ID'))

