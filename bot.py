import discord
import asyncio
import random
from discord.ext import commands

import os
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_message_time = None

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(check_inactive())

@bot.event
async def on_message(message):
    global last_message_time
    if message.author == bot.user:
        return
    
    last_message_time = asyncio.get_event_loop().time()
    await bot.process_commands(message)

async def check_inactive():
    global last_message_time
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        await asyncio.sleep(60)  # check every 1 min
        
        if last_message_time is None:
            continue
        
        now = asyncio.get_event_loop().time()
        
        if now - last_message_time > 1800:  # 30 mins inactive
            channel = discord.utils.get(bot.get_all_channels(), name="general")
            
            if channel:
                messages = [
                    "Server is quiet 😶 anyone alive?",
                    "Yo 👀 let's chat!",
                    "Drop a random thought 💭",
                    "Who’s online right now?"
                ]
                await channel.send(random.choice(messages))

bot.run(TOKEN)