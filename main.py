import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_FILE = "welcome.json"
WELCOME_CH = None
if os.path.exists(WELCOME_FILE):
    try:
        WELCOME_CH = json.load(open(WELCOME_FILE)).get("channel_id")
    except:
        WELCOME_CH = None

TICKET_FILE = "ticket.json"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ===== TICKET SYSTEM - PICHLA WALA =====
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket 5 sec me band ho jayega...", ephemeral=True)
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        # Agar ticket pehle se hai to nahi banega
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
        embed = discord.Embed(title="GHOSTMC SUPPORT", description=f"{interaction.user.mention} Support team jaldi aayegi, apna issue batao!", color=0x00FF00)
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"Ticket bana {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticketpanel", description="Ticket panel bheje")
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👻 GHOSTMC - SUPPORT TICKET",
        description="**Koi problem hai?**\n\n> 📦 Buy related issue\n> ⛏️ SMP me problem\n> 👤 Player report\n\nNiche button dabao aur apna ticket kholo!",
        color=0x00FF00
    )
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    await interaction.response.send_message(embed=embed, view=TicketView())
    bot.add_view(TicketView()) # restart pe bhi kaam karega

# ===== WELCOME SET =====
@bot.tree.command(name="welcomeset", description="Welcome yaha ayega")
async def welcomeset(interaction: discord.Interaction):
    global WELCOME_CH
    WELCOME_CH = interaction.channel.id
    json.dump({"channel_id": WELCOME_CH}, open(WELCOME_FILE, "w"))
    await interaction.response.send_message(f"Welcome set {interaction.channel.mention} pe", ephemeral=True)

@bot.event
async def on_member_join(member):
    if not WELCOME_CH:
        return
    ch = member.guild.get_channel(WELCOME_CH)
    if not ch:
        return
    desc = f"""
╔════════════════════╗
   👻 WELCOME TO GHOSTMC 👻
╚════════════════════╝

Hey {member.mention} ! Welcome to the most haunted & powerful SMP! ⛏️

> 🌍 **IP:** `upcomming`
> 📌 **Version:** 1.21.11 | Crossplay 
> 🔗 **Store:** #buy-here
> 🎫 **Support:** #🎫・tickets

━━━━━━━━━━━━━━━━━━━━━━━━
**🔥 KYA TUM APNA DOSTO KO INVITE KAROGA?**



Members: {member.guild.member_count} 👻
"""
    embed = discord.Embed(description=desc, color=0x00FF00)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ch.send(embed=embed)

# ===== SAY CMD =====
@bot.tree.command(name="say", description="Bot se kuch bulwao")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Bhej diya", ephemeral=True)
    await interaction.channel.send(message)

TOKEN = os.environ.get("TOKEN") or "APNA_TOKEN_YAHA_DALO"
bot.run(TOKEN)
