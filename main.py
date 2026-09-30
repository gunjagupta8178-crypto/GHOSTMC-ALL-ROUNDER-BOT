import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_FILE = "welcome.json"
TICKET_FILE = "ticket.json"
AUTO_FILE = "autoresponder.json"

WELCOME_CH = None
if os.path.exists(WELCOME_FILE):
    try:
        WELCOME_CH = json.load(open(WELCOME_FILE)).get("channel_id")
    except:
        WELCOME_CH = None

# Load autoresponder
AUTORESP = {}
if os.path.exists(AUTO_FILE):
    try:
        AUTORESP = json.load(open(AUTO_FILE))
    except:
        AUTORESP = {}

def save_auto():
    json.dump(AUTORESP, open(AUTO_FILE, "w"), indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(TicketView())
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ===== TICKET SYSTEM =====
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket 5 sec me band ho jayega...", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing:
            await interaction.response.send_message(f"Tera ticket pehle se hai {existing.mention}", ephemeral=True)
            return
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="GHOSTMC SUPPORT", description=f"{interaction.user.mention} Support team jaldi aayegi!", color=0x00FF00)
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"Ticket bana {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticketpanel", description="Ticket panel bheje")
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(title="👻 GHOSTMC - SUPPORT TICKET", description="**Koi problem hai?**\n\n> 📦 Buy related\n> ⛏️ SMP problem\n> 👤 Report\n\nNiche button dabao!", color=0x00FF00)
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=embed, view=TicketView())

# ===== WELCOME =====
@bot.tree.command(name="welcomeset", description="Welcome yaha ayega")
async def welcomeset(interaction: discord.Interaction):
    global WELCOME_CH
    WELCOME_CH = interaction.channel.id
    json.dump({"channel_id": WELCOME_CH}, open(WELCOME_FILE, "w"))
    await interaction.response.send_message(f"Welcome set {interaction.channel.mention} pe", ephemeral=True)

@bot.event
async def on_member_join(member):
    if not WELCOME_CH: return
    ch = member.guild.get_channel(WELCOME_CH)
    if not ch: return
    desc = f"""
╔════════════════════╗
   👻 WELCOME TO GHOSTMC 👻
╚════════════════════╝
Hey {member.mention} !
> 🌍 **IP:** `upcomming`
> 📌 **Version:** 1.20+
Members: {member.guild.member_count} 👻
"""
    embed = discord.Embed(description=desc, color=0x00FF00)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ch.send(embed=embed)

# ===== SAY =====
@bot.tree.command(name="say", description="Bot se kuch bulwao")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Bhej diya", ephemeral=True)
    await interaction.channel.send(message)

# ===== AUTORESPONDER COMMAND SE =====
@bot.tree.command(name="autoresponder", description="Auto reply set karo")
@app_commands.describe(action="add / remove / list", trigger="Kis word pe reply kare", response="Kya reply de")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list")
])
async def autoresponder(interaction: discord.Interaction, action: str, trigger: str = None, response: str = None):
    global AUTORESP
    if action == "add":
        if not trigger or not response:
            await interaction.response.send_message("Add ke liye trigger aur response dono do! Ex: `/autoresponder add ip IP hai play.ghostmc.in`", ephemeral=True)
            return
        AUTORESP[trigger.lower()] = response
        save_auto()
        await interaction.response.send_message(f"✅ Autoresponder set: `{trigger.lower()}` -> {response}", ephemeral=True)
    
    elif action == "remove":
        if not trigger:
            await interaction.response.send_message("Remove ke liye trigger naam do", ephemeral=True)
            return
        if trigger.lower() in AUTORESP:
            del AUTORESP[trigger.lower()]
            save_auto()
            await interaction.response.send_message(f"🗑️ Hata diya `{trigger.lower()}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"Nahi mila `{trigger.lower()}`", ephemeral=True)

    elif action == "list":
        if not AUTORESP:
            await interaction.response.send_message("Koi autoresponder nahi hai abhi", ephemeral=True)
            return
        text = "\n".join([f"`{k}` -> {v}" for k,v in AUTORESP.items()])
        embed = discord.Embed(title="Autoresponder List", description=text, color=0x00FF00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ===== AUTO REPLY LOGIC =====
@bot.event
async def on_message(message):
    if message.author.bot: return
    # check autoresponder
    content = message.content.lower()
    for trig, resp in AUTORESP.items():
        if trig in content:
            await message.channel.send(resp)
            break
    await bot.process_commands(message)

TOKEN = os.environ.get("TOKEN") or "APNA_TOKEN_YAHA_DALO"
bot.run(TOKEN)
