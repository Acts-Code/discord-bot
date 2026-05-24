import discord
print("discord is good")
import random
print("random good")
import asyncio
print("asyncio good")
import datetime
print("datetime good")
import aiohttp
print("aiohttp good")
import os
print("os good")
from discord.ext import commands
print("discord.ext- commands good")
from discord import app_commands
print("discord- app_commands good")
from ai import ask_ai
print("ai-ask ai good")
from urllib.parse import quote_plus
print("urllib.parse-quote_plus")
#============FIREBASE====================#
from firebase import db

def add_rep(user_id, amount):

    ref = db.collection("reputation").document(str(user_id))

    doc = ref.get()

    if doc.exists:
        current = doc.to_dict().get("rep", 0)
    else:
        current = 0

    ref.set({
        "rep": current + amount
    })

print("Firebase connected!")
# ================= TOKENS ================= #
TOKEN = os.getenv("TOKEN")
# ================= SETTINGS ================= #
MONITORED_CHANNEL_ID = 1481723127703797793
WELCOME_CHANNEL_ID = 1502928422438178856
INACTIVE_TIME = 2700  # 45 minutAes
BANNED_USER_IDS = set()
OWNER_ID =1407707442569285858
REPORT_CHANNEL_ID = 1502949484445958174
# ================= ADMIN ROLES ================= #
ADMIN_ROLE_IDS = [
    1489157059487334482,
    1489156996421914808,
    1485995037509812324,
    1484279764922667008,
    1492620579713323070
]

#=============OWNERONLY HELPER============#
def is_owner(interaction: discord.Interaction):
    return interaction.user.id == OWNER_ID
# ================= INTENTS ================= #
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

last_message_time = None
#=============HEROS===================#
@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command):
    try:
        user_id = str(interaction.user.id)
        command_name = command.name

        ref = db.collection("command_logs").document(user_id)

        doc = ref.get()
        data = doc.to_dict() if doc.exists else {
            "total_commands": 0,
            "commands": {}
        }

        commands = data.get("commands", {})
        commands[command_name] = commands.get(command_name, 0) + 1

        ref.set({
            "username": str(interaction.user),
            "total_commands": data.get("total_commands", 0) + 1,
            "commands": commands,
            "last_command": command_name,
            "last_used": datetime.datetime.utcnow().isoformat()
        })

    except Exception as e:
        print("TRACK ERROR:", e)
#===============ADMIN CHECK===================#
def is_admin(interaction: discord.Interaction):
    if not interaction.guild:
        return False

    return any(
        role.id in ADMIN_ROLE_IDS
        for role in interaction.user.roles
    )
#====================BLOCK CHECK================#
def not_blocked():

    async def predicate(interaction: discord.Interaction):

        if interaction.user.id in BANNED_USER_IDS:

            await interaction.response.send_message(
                "🚫 You are blocked from using Actor.",
                ephemeral=True
            )

            return False

        return True

    return app_commands.check(predicate)
    
#=========OWNER ONLY COMMANDS===========#
#=============OWNER ONLY DECORATOR============#
def owner_only():

    async def predicate(interaction: discord.Interaction):

        if interaction.user.id != OWNER_ID:

            await interaction.response.send_message(
                "❌ Owner only.",
                ephemeral=True
            )

            return False

        return True

    return app_commands.check(predicate)
@bot.tree.command(
    name="block",
    description="Block a user from using the bot (Owner only)."
)
async def block(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not is_owner(interaction):
        return await interaction.response.send_message(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )

    BANNED_USER_IDS.add(member.id)

    await interaction.response.send_message(
        f"🚫 {member.mention} has been blocked from using Actor."
    )
@bot.tree.command(
    name="unblock",
    description="Unblock a user from the bot (Owner only)."
)
async def unblock(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not is_owner(interaction):
        return await interaction.response.send_message(
            "❌ Only the bot owner can use this command.",
            ephemeral=True
        )

    BANNED_USER_IDS.discard(member.id)

    await interaction.response.send_message(
        f"✅ {member.mention} has been unblocked."
    )
@bot.tree.command(
    name="track_view",
    description="View command usage stats."
)
@owner_only()
async def track_view(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    ref = db.collection("command_logs").document(str(member.id))

    doc = ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            "❌ No tracking data found."
        )

    data = doc.to_dict()

    commands = data.get("commands", {})

    cmd_text = "\n".join(
        [f"`{cmd}` → {count}" for cmd, count in commands.items()]
    )

    if not cmd_text:
        cmd_text = "No commands used."

    embed = discord.Embed(
        title=f"📊 {member.name}'s Command Stats",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📦 Total Commands",
        value=data.get("total_commands", 0),
        inline=False
    )

    embed.add_field(
        name="🕒 Last Command",
        value=data.get("last_command", "None"),
        inline=False
    )

    embed.add_field(
        name="📜 Command Usage",
        value=cmd_text[:1000],
        inline=False
    )

    await interaction.response.send_message(
        embed=embed
    )
# ================= FACT ================= #
async def get_fact():
    try:
        url = "https://uselessfacts.jsph.pl/random.json?language=en"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return data["text"]

    except Exception as e:
        print("Fact error:", e)
        return "⚠️ Couldn't fetch fact."

# ================= JOKE ================= #
async def get_joke():
    try:
        url = "https://official-joke-api.appspot.com/random_joke"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

                return f"{data['setup']} - {data['punchline']}"

    except Exception as e:
        print("Joke error:", e)
        return "⚠️ Couldn't fetch joke."

# ================= READY ================= #
@bot.event
async def on_ready():
    global last_message_time

    print(f"✅ Logged in as {bot.user}")

    last_message_time = asyncio.get_event_loop().time()

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")

    except Exception as e:
        print("Sync error:", e)

    # FIX: safe task start (no bot.loop)
    if not hasattr(bot, "inactive_task_started"):
        bot.inactive_task_started = True
        asyncio.create_task(check_inactive())
# ================= MESSAGE TRACKING ================= #

last_message_time = None

@bot.event
async def on_message(message):
    global last_message_time

    if message.author.bot:
        return

    if message.channel.id == 1481723127703797793:
        last_message_time = asyncio.get_event_loop().time()

    await bot.process_commands(message)


# ================= INACTIVE CHAT ================= #

async def check_inactive():
    global last_message_time
    await bot.wait_until_ready()
    

    msgs = [
        "😶 Dead chat",
        "👀 Anyone here?",
        "💀 Silent mode",
        "📢 Wake up",
        "👻 Ghost town",
        "😎 First person to talk is the coolest",
        "⏱️ Waiting for a response",
        "💀 Imagine if you guys are talking in other channel"
    ]

    while not bot.is_closed():

        await asyncio.sleep(60)

        if last_message_time is None:
            continue

        inactive_for = (
            asyncio.get_event_loop().time()
            - last_message_time
        )

        if inactive_for > INACTIVE_TIME:

            channel = bot.get_channel(1481723127703797793)

            if channel:
                await channel.send(random.choice(msgs))

                # RESET TIMER
                last_message_time = asyncio.get_event_loop().time()
# ================= BASIC COMMANDS ================= #

@bot.tree.command(
    name="ping",
    description="Shows the bot latency."
)
@not_blocked()
  
async def ping(interaction: discord.Interaction):

    await interaction.response.send_message(
        f"🏓 {round(bot.latency * 1000)}ms"
    )
@bot.tree.command(
    name="ai",
    description="Ask Actor anything"
)
@not_blocked()
  
async def ai(interaction: discord.Interaction, question: str):

    await interaction.response.defer()

    reply = await ask_ai(interaction.user.id, question)

    await interaction.followup.send(reply)
@bot.tree.command(
    name="coin",
    description="Flip a coin."
)
@not_blocked()
  
async def coin(interaction: discord.Interaction):

    await interaction.response.send_message(
        random.choice(["🪙 Heads", "🪙 Tails"])
    )

@bot.tree.command(
    name="dice",
    description="Roll a dice from 1 to 6."
)
@not_blocked()
  
async def dice(interaction: discord.Interaction):

    await interaction.response.send_message(
        f"🎲 {random.randint(1,6)}"
    )

@bot.tree.command(
    name="8ball",
    description="Ask the magic 8ball a question."
)
@not_blocked()
  
async def ball(interaction: discord.Interaction, question: str):

    answers = [
        "✅ Yes",
        "❌ No",
        "🤔 Maybe",
        "⏳ Ask later"
    ]

    await interaction.response.send_message(
        random.choice(answers)
    )
@bot.tree.command(
    name="embed",
    description="Send a custom embed message."
)
async def embed(
    interaction: discord.Interaction,
    title: str,
    message: str,
    color: str = "blue"
):

    colors = {
        "red": discord.Color.red(),
        "blue": discord.Color.blue(),
        "green": discord.Color.green(),
        "gold": discord.Color.gold(),
        "purple": discord.Color.purple(),
        "pink": discord.Color.magenta(),
        "black": discord.Color.default()
    }

    embed = discord.Embed(
        title=title,
        description=message,
        color=colors.get(color.lower(), discord.Color.blue())
    )

    embed.set_footer(
        text=f"Sent by {interaction.user}",
        icon_url=interaction.user.display_avatar.url
    )

    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(embed=embed)
@bot.tree.command(
    name="random",
    description="Randomly pick something from a list.(Separate iteams using comma)"
)
@not_blocked()
  
async def random_pick(interaction: discord.Interaction, items: str):

    choices = [
        x.strip()
        for x in items.split(",")
        if x.strip()
    ]

    if not choices:
        return await interaction.response.send_message(
            "❌ No items provided."
        )

    await interaction.response.send_message(
        f"🎯 {random.choice(choices)}"
    )
@bot.tree.command(
    name="say",
    description="Make the bot say something."
)
  
@not_blocked()
async def say(interaction: discord.Interaction, message: str):

    await interaction.response.send_message(message)
@bot.tree.command(
    name="act_point",
    description="Give act points to a user (Owner only)."
)
async def rep(
    interaction: discord.Interaction,
    member: discord.Member,
    amount: int,
    reason: str
):
    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message(
            "❌ Owner only.",
            ephemeral=True
        )

    # 🔥 IMPORTANT: prevent interaction timeout
    await interaction.response.defer()

    try:
        add_rep(member.id, amount)

        await interaction.followup.send(
            f"⭐ Added {amount} act points to {member.mention}\n"
            f"📝 Reason: {reason}"
        )

    except Exception as e:
        await interaction.followup.send(
            f"❌ Error: {e}"
        )
@bot.tree.command(
    name="act_point_view",
    description="Check a user's act points."
)
@not_blocked()
async def reputation(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    ref = db.collection("reputation").document(str(member.id))

    doc = ref.get()

    rep = 0

    if doc.exists:
        rep = doc.to_dict().get("rep", 0)

    await interaction.response.send_message(
        f"⭐ {member.mention} has {rep} act points."
    )
@bot.tree.command(
    name="announcement",
    description="Send an announcement to the server."
)
@not_blocked()
  
async def announcement(
    interaction: discord.Interaction,
    title: str,
    message: str,
    channel: discord.TextChannel = None
):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    target_channel = channel or interaction.channel

    embed = discord.Embed(
        title=f"📢 {title}",
        description=message,
        color=discord.Color.blurple()
    )

    embed.set_footer(text=f"Announced by {interaction.user}")

    await target_channel.send(embed=embed)

    await interaction.response.send_message(
        f"✅ Announcement sent to {target_channel.mention}",
        ephemeral=True
    )
        
@bot.tree.command(
    name="avatar",
    description="Show a user's avatar."
)
@not_blocked()
  
async def avatar(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.blurple()
    )

    if member.avatar:
        embed.set_image(url=member.avatar.url)
    else:
        return await interaction.response.send_message(
            "❌ No avatar found."
        )

    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(
    name="fact",
    description="Get a random fact."
)
@not_blocked()
  
async def fact(interaction: discord.Interaction):

    await interaction.response.send_message(
        await get_fact()
    )

@bot.tree.command(
    name="joke",
    description="Get a random joke."
)
@not_blocked()
  
async def joke(interaction: discord.Interaction):

    await interaction.response.send_message(
        await get_joke()
    )

@bot.tree.command(
    name="time",
    description="Shows the current server time."
)
@not_blocked()
  
async def time_cmd(interaction: discord.Interaction):

    current = datetime.datetime.now().strftime("%H:%M:%S")

    await interaction.response.send_message(
        f"🕒 {current}"
    )
@bot.tree.command(
    name="fhaa",
    description="Play the legendary FHAA sound in VC"
)
async def fhaa(interaction: discord.Interaction):

    if not interaction.user.voice:
        return await interaction.response.send_message(
            "❌ You must be in a voice channel first!",
            ephemeral=True
        )

    channel = interaction.user.voice.channel

    voice = await channel.connect()  # ✅ INSIDE async function

    await interaction.response.send_message("fahh🔥 (playing in VC)")

    audio_file = discord.FFmpegPCMAudio("Fahhh - QuickSounds.com.mp3")
    voice.play(audio_file)

    while voice.is_playing():
        await asyncio.sleep(1)

    await voice.disconnect()
# ================= ADMIN COMMANDS ================= #
@bot.tree.command(
    name="ban",
    description="Ban a member from the server."
)
@not_blocked()
  
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "No reason"
):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    try:
        await member.ban(reason=reason)

        await interaction.response.send_message(
            f"🔨 Banned {member.mention}\nReason: {reason}"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed: {e}",
            ephemeral=True
        )
        
@bot.tree.command(
    name="lock",
    description="Lock the current channel."
)
@not_blocked()
  
async def lock(interaction: discord.Interaction):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = False

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔒 Channel locked."
    )
     
@bot.tree.command(
    name="unlock",
    description="Unlock the current channel."
)
@not_blocked()
  
async def unlock(interaction: discord.Interaction):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    overwrite = interaction.channel.overwrites_for(
        interaction.guild.default_role
    )

    overwrite.send_messages = True

    await interaction.channel.set_permissions(
        interaction.guild.default_role,
        overwrite=overwrite
    )

    await interaction.response.send_message(
        "🔓 Channel unlocked."
    )   


@bot.tree.command(
    name="warn",
    description="Warn a member."
)
@not_blocked()
  
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    embed = discord.Embed(
        title="⚠️ Warning Issued",
        color=discord.Color.orange()
    )

    embed.add_field(name="User", value=member.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)

    await interaction.response.send_message(embed=embed)    
@bot.tree.command(
    name="clear",
    description="Delete a number of messages."
)
@not_blocked()
  
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Amount must be greater than 0.",
            ephemeral=True
        )

    try:

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Deleted {len(deleted)} messages.",
            ephemeral=True
        )

    except Exception as e:

        await interaction.followup.send(
            f"❌ Failed: {e}",
            ephemeral=True
        )

@bot.tree.command(
    name="unban",
    description="Unban a user using their ID."
)
@not_blocked()
  
async def unban(
    interaction: discord.Interaction,
    user_id: str
):

    if not is_admin(interaction):

        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    try:

        user = await bot.fetch_user(int(user_id))

        await interaction.guild.unban(user)

        await interaction.response.send_message(
            f"✅ Unbanned {user}"
        )

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Failed: {e}",
            ephemeral=True
        )

@bot.tree.command(
    name="mute",
    description="Timeout a member for a specific amount of time."
)
@not_blocked()
  
async def mute(
    interaction: discord.Interaction,
    member: discord.Member,
    minutes: int
):

    if not is_admin(interaction):

        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    try:

        await member.timeout(
            datetime.timedelta(minutes=minutes)
        )

        await interaction.response.send_message(
            f"🔇 Muted {member.mention} for {minutes} minutes"
        )

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Failed to mute: {e}",
            ephemeral=True
        )
        
@bot.tree.command(
    name="report",
    description="Report a user to the staff team."
)
@not_blocked()
  
async def report(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str
):

    if member == interaction.user:
        return await interaction.response.send_message(
            "❌ You cannot report yourself.",
            ephemeral=True
        )

    channel = bot.get_channel(REPORT_CHANNEL_ID)

    if not channel:
        return await interaction.response.send_message(
            "❌ Report channel not found.",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🚨 New Report",
        color=discord.Color.red()
    )

    embed.add_field(
        name="Reported User",
        value=member.mention,
        inline=False
    )

    embed.add_field(
        name="Reported By",
        value=interaction.user.mention,
        inline=False
    )

    embed.add_field(
        name="Reason",
        value=reason,
        inline=False
    )

    embed.timestamp = datetime.datetime.utcnow()

    await channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Report sent to staff.",
        ephemeral=True
    )
    # ================= ADMIN CHECK ================= #
    if not is_admin(interaction):
        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    # prevent warning yourself
    if member == interaction.user:
        return await interaction.response.send_message(
            "❌ You cannot warn yourself.",
            ephemeral=True
        )

    try:

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=interaction.user.mention,
            inline=False
        )

        embed.timestamp = datetime.datetime.utcnow()

        # send in current channel
        await interaction.response.send_message(
            embed=embed
        )

        # optional DM to warned user
        try:
            await member.send(
                f"⚠️ You were warned in **{interaction.guild.name}**\nReason: {reason}"
            )
        except:
            pass

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Failed: {e}",
            ephemeral=True
        )

@bot.tree.command(
    name="unmute",
    description="Remove timeout from a member."
)
@not_blocked()
  
async def unmute(
    interaction: discord.Interaction,
    member: discord.Member
):

    if not is_admin(interaction):

        return await interaction.response.send_message(
            "❌ Admin only",
            ephemeral=True
        )

    try:

        await member.timeout(None)

        await interaction.response.send_message(
            f"🔊 Unmuted {member.mention}"
        )

    except Exception as e:

        await interaction.response.send_message(
            f"❌ Failed to unmute: {e}",
            ephemeral=True
        )

# ================= INFO COMMANDS ================= #

@bot.tree.command(
    name="serverinfo",
    description="Shows information about the server."
)
@not_blocked()
  
async def serverinfo(interaction: discord.Interaction):

    guild = interaction.guild

    embed = discord.Embed(
        title=guild.name,
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="👥 Members",
        value=guild.member_count
    )

    embed.add_field(
        name="🆔 Server ID",
        value=guild.id
    )

    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

    await interaction.response.send_message(embed=embed)
    
@bot.tree.command(
    name="help_act",
    description="Shows all Actor commands."
)
@not_blocked()
  
async def help_act(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🤖 Actor Help Menu",
        description="Here are all available commands:",
        color=discord.Color.blurple()
    )

    # ===== FUN =====
    embed.add_field(
        name="🎮 Fun Commands",
        value=(
            "`/ping` - Show bot latency\n"
            "`/coin` - Flip a coin\n"
            "`/dice` - Roll a dice\n"
            "`/8ball` - Ask the magic 8ball\n"
            "`/random` - Randomly pick an item\n"
            "`/say` - Make Actor say something"
        ),
        inline=False
    )

    # ===== AI & UTILITY =====
    embed.add_field(
        name="🧠 AI & Utility",
        value=(
            "`/ai` - Ask Actor anything\n"
            "`/fact` - Random fact\n"
            "`/joke` - Random joke\n"
            "`/time` - Current server time\n"
            "`/timer` - Start a countdown timer\n"
            "`/remind` - Set a reminder"
        ),
        inline=False
    )

    # ===== USER INFO =====
    embed.add_field(
        name="👤 User Commands",
        value=(
            "`/avatar` - Show avatar\n"
            "`/profile` - Show profile picture\n"
            "`/userinfo` - Show user info\n"
            "`/serverinfo` - Show server info"
        ),
        inline=False
    )

    # ===== MODERATION =====
    embed.add_field(
        name="🛡️ Moderation",
        value=(
            "`/ban` - Ban a member\n"
            "`/unban` - Unban a user\n"
            "`/mute` - Timeout a member\n"
            "`/unmute` - Remove timeout\n"
            "`/warn` - Warn a member\n"
            "`/clear` - Delete messages\n"
            "`/lock` - Lock a channel\n"
            "`/unlock` - Unlock a channel\n"
            "`/announcement` - Send announcement\n"
            "`/report` - Report a user"
        ),
        inline=False
    )

    # ===== OWNER =====
    embed.add_field(
        name="👑 Owner Commands",
        value=(
            "`/block` - Block a user from Actor\n"
            "`/unblock` - Unblock a user"
        ),
        inline=False
    )

    # ===== TOTAL =====
    embed.add_field(
        name="📦 Total Commands",
        value="28 Commands Available",
        inline=False
    )

    embed.set_footer(
        text="Actor • Simple • Fast • Human-like"
    )

    embed.timestamp = datetime.datetime.utcnow()

    await interaction.response.send_message(
        embed=embed
    )
@bot.tree.command(
    name="userinfo",
    description="Shows information about a user."
)
@not_blocked()
  
async def userinfo(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"{member}",
        color=discord.Color.green()
    )

    embed.add_field(
        name="🆔 User ID",
        value=member.id
    )

    embed.add_field(
        name="📅 Joined",
        value=member.joined_at.strftime("%Y-%m-%d")
    )

    embed.set_thumbnail(
        url=member.avatar.url if member.avatar else None
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="profile",
    description="Shows a user's profile picture."
)
@not_blocked()
  
async def profile(
    interaction: discord.Interaction,
    member: discord.Member = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"{member.name}'s Profile",
        color=discord.Color.orange()
    )

    if member.avatar:
        embed.set_image(url=member.avatar.url)

    await interaction.response.send_message(embed=embed)
    
    
@bot.tree.command(
    name="timer",
    description="Start a countdown timer."
)
@not_blocked()
  
async def timer(
    interaction: discord.Interaction,
    seconds: int
):

    if seconds <= 0:
        return await interaction.response.send_message(
            "❌ Time must be more than 0."
        )

    await interaction.response.send_message(
        f"⏳ {interaction.user.mention} Timer started for {seconds} seconds."
    )

    await asyncio.sleep(seconds)

    await interaction.followup.send(
        f"⏰ {interaction.user.mention} Your timer ended!"
    )
    
@bot.tree.command(
    name="remind",
    description="Set a reminder."
)
@not_blocked()
  
async def remind(
    interaction: discord.Interaction,
    seconds: int,
    reminder: str
):

    if seconds <= 0:
        return await interaction.response.send_message(
            "❌ Time must be more than 0."
        )

    await interaction.response.send_message(
        f"🔔 {interaction.user.mention} Reminder set for {seconds} seconds."
    )

    await asyncio.sleep(seconds)

    await interaction.followup.send(
        f"📝 {interaction.user.mention} Reminder:\n{reminder}"
    )
    
@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if not channel:
        return

    try:

        welcome_url = (
            f"https://api.popcat.xyz/welcomecard?"
            f"background=https://i.imgur.com/5FL6qEm.png"
            f"&text1={quote_plus(member.name)}"
            f"&text2={quote_plus(f'Welcome to {member.guild.name}')}"
            f"&text3={quote_plus(f'Member #{member.guild.member_count}')}"
            f"&avatar={quote_plus(member.display_avatar.url)}"
        )

        print(welcome_url)

        embed = discord.Embed(
            title="👋 Welcome!",
            description=f"{member.mention} joined the server.",
            color=discord.Color.blurple()
        )

        embed.set_image(url=welcome_url)

        await channel.send(embed=embed)

    except Exception as e:
        print("Welcome error:", e)
print("yah running")
# ================= RUN ================= #
bot.run(TOKEN)
