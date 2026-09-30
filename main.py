import discord
from discord.ext import commands
from discord import app_commands
import asyncio, os, yt_dlp

TOKEN = os.getenv("TOKEN")
SONG_URL = "https://www.youtube.com/watch?v=AbkEmIgJMcU"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="-", intents=intents)
ytdl = yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True})
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
autorespond = {}

class CloseTicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_bh")
    async def close(self, interaction, button):
        await interaction.response.send_message("Closing...", ephemeral=True)
        await asyncio.sleep(2)
        await interaction.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="BUY", emoji="🛒"),
            discord.SelectOption(label="CLAIM", emoji="🎁"),
            discord.SelectOption(label="REWARDS", emoji="💰"),
            discord.SelectOption(label="REPORT", emoji="🚨"),
            discord.SelectOption(label="APPLY", emoji="📝"),
        ]
        super().__init__(placeholder="Ticket Select Karo...", options=options, custom_id="ticket_bh")
    async def callback(self, interaction):
        guild = interaction.guild
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
        channel = await guild.create_text_channel(name=f"{self.values[0].lower()}-{interaction.user.name}", overwrites=overwrites)
        await channel.send(f"{interaction.user.mention} Staff wait karo", view=CloseTicketView())
        await interaction.response.send_message(f"Ban gaya {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

async def play_loop(vc):
    while True:
        try:
            if not vc.is_connected(): break
            if not vc.is_playing() and not vc.is_paused():
                info = ytdl.extract_info(SONG_URL, download=False)
                vc.play(discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS))
            await asyncio.sleep(10)
        except: await asyncio.sleep(5)

@bot.event
async def on_ready():
    print(f"Online: {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    await bot.tree.sync()

@bot.tree.command(name="ticketpanel", description="Ticket panel bhejo")
async def ticketpanel(interaction):
    embed = discord.Embed(title="GHOSTMC SUPPORT", description="🛒 BUY\n🎁 CLAIM\n💰 REWARDS\n🚨 REPORT\n📝 APPLY", color=0x00ff00)
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Done ✅", ephemeral=True)

@bot.tree.command(name="join", description="24/7 Music VC")
async def join_cmd(interaction):
    if not interaction.user.voice: return await interaction.response.send_message("VC me jaa pehle!", ephemeral=True)
    vc = interaction.guild.voice_client
    if not vc: vc = await interaction.user.voice.channel.connect()
    else: await vc.move_to(interaction.user.voice.channel)
    await interaction.response.send_message(f"Join ho gaya {interaction.user.voice.channel.mention}")
    bot.loop.create_task(play_loop(vc))

@bot.tree.command(name="leave", description="VC se nikal")
async def leave_cmd(interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Nikal gaya 👋")
    else: await interaction.response.send_message("Me VC me nahi hu", ephemeral=True)

@bot.tree.command(name="say", description="Bot se bulwao")
async def say_cmd(interaction, message: str):
    await interaction.response.send_message("Bhej diya", ephemeral=True)
    await interaction.channel.send(message)

@bot.tree.command(name="autoresponder", description="Auto reply")
async def auto_cmd(interaction, word: str, reply: str):
    autorespond[word.lower()] = reply
    await interaction.response.send_message(f"Set: {word} -> {reply} ✅", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if message.content.lower() in autorespond: await message.channel.send(autorespond[message.content.lower()])
    await bot.process_commands(message)

bot.run(TOKEN)
