# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!movie')

@bot.command(name='wednesday', help='When it is wednesday')
async def wednesday(ctx):
    #if message.author == client.user:
    #    return

    response = 'It is Wednesday my dudes'
    await ctx.send(response)
    
bot.run(TOKEN)
