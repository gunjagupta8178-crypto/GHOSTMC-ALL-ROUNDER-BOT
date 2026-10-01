import discord, os, asyncio
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CH = None
AUTORESP = {}

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing in 3 sec...", ephemeral=True)
        await asyncio.sleep(3)
        await interaction.channel.delete()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}")
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.send(f"{interaction.user.mention} Support will be here soon!", view=CloseView())
        await interaction.response.send_message(f"Created {channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"Online {bot.user}")
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    await bot.tree.sync()
    print("Ready - All commands synced")

@bot.tree.command(name="ticketpanel", description="Send ticket panel")
async def ticketpanel(interaction: discord.Interaction):
    embed = discord.Embed(title="Support Ticket", description="Click below to create a ticket", color=discord.Color.green())
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Panel sent", ephemeral=True)

@bot.tree.command(name="welcomeset", description="Set welcome channel")
async def welcomeset(interaction: discord.Interaction):
    global WELCOME_CH
    WELCOME_CH = interaction.channel.id
    await interaction.response.send_message(f"Welcome channel set to {interaction.channel.mention}", ephemeral=True)

@bot.tree.command(name="say", description="Make bot say something")
async def say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Done", ephemeral=True)
    await interaction.channel.send(message)

@bot.tree.command(name="autoresponder", description="Auto reply setup")
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list")
])
async def autoresponder(interaction: discord.Interaction, action: str, trigger: str = None, response: str = None):
    if action == "add":
        if not trigger or not response:
            await interaction.response.send_message("Use: trigger and response both needed", ephemeral=True)
            return
        AUTORESP[trigger.lower()] = response
        await interaction.response.send_message(f"Added autoresponder for `{trigger}`", ephemeral=True)
    elif action == "remove":
        AUTORESP.pop(trigger.lower(), None)
        await interaction.response.send_message(f"Removed `{trigger}`", ephemeral=True)
    else:
        if not AUTORESP:
            await interaction.response.send_message("No autoresponders", ephemeral=True)
        else:
            text = "\n".join([f"{k} -> {v}" for k,v in AUTORESP.items()])
            await interaction.response.send_message(f"**List:**\n{text}", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if WELCOME_CH and message.channel.id == WELCOME_CH:
        pass
    for k, v in AUTORESP.items():
        if k in message.content.lower():
            await message.channel.send(v)
            break
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if WELCOME_CH:
        ch = bot.get_channel(WELCOME_CH)
        if ch:
            await ch.send(f"Welcome {member.mention} to {member.guild.name}!")

bot.run(os.environ.get("TOKEN"))
