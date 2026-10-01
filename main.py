import discord
from discord.ext import commands
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
@bot.event
async def on_ready():
    print(f"Online {bot.user}")
    await bot.tree.sync()
@bot.tree.command(name="say")
async def say(interaction, message: str):
    await interaction.response.send_message("Done", ephemeral=True)
    await interaction.channel.send(message)
import os
bot.run(os.environ.get("TOKEN"))
