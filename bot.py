# =========================================================
# MISUKI BOT
# Main Bot File
# =========================================================

import os
import asyncio
import json
import time

import discord

from discord.ext import commands

from dotenv import load_dotenv


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BOT_STATS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "bot_stats.json"
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# UPTIME
# =========================================================

BOT_START_TIME = time.time()


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()

intents.members = True
intents.message_content = True


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# COMMAND COUNT
# =========================================================

def count_commands(commands_list):

    total = 0

    for command in commands_list:

        if isinstance(
            command,
            discord.app_commands.Group
        ):

            total += count_commands(
                command.commands
            )

        else:

            total += 1

    return total


# =========================================================
# UPTIME FORMAT
# =========================================================

def get_uptime():

    elapsed = max(
        0,
        int(
            time.time()
            - BOT_START_TIME
        )
    )

    days, remainder = divmod(
        elapsed,
        86400
    )

    hours, remainder = divmod(
        remainder,
        3600
    )

    minutes, seconds = divmod(
        remainder,
        60
    )

    parts = []

    if days:

        parts.append(
            f"{days}d"
        )

    if hours:

        parts.append(
            f"{hours}h"
        )

    if minutes:

        parts.append(
            f"{minutes}m"
        )

    if not parts:

        parts.append(
            f"{seconds}s"
        )

    return " ".join(
        parts
    )


# =========================================================
# WRITE STATISTICS
# =========================================================

async def update_stats_snapshot():

    try:

        # -------------------------------------------------
        # CREATE DATA DIRECTORY
        # -------------------------------------------------

        data_directory = os.path.dirname(
            BOT_STATS_FILE
        )

        os.makedirs(
            data_directory,
            exist_ok=True
        )


        # -------------------------------------------------
        # COMMANDS
        # -------------------------------------------------

        commands_count = count_commands(
            bot.tree.get_commands()
        )


        # -------------------------------------------------
        # ADMIN SERVER INFORMATION
        # -------------------------------------------------

        admin_servers = []

        for guild in bot.guilds:

            icon = None

            try:

                if guild.icon:

                    icon = str(
                        guild.icon.url
                    )

            except Exception:

                icon = None


            admin_servers.append({

                "name": guild.name,

                "id": str(
                    guild.id
                ),

                "icon": icon,

                "members": (
                    guild.member_count
                    or 0
                ),
            })


        # -------------------------------------------------
        # SNAPSHOT
        # -------------------------------------------------

        snapshot = {

            "servers": len(
                bot.guilds
            ),

            "users": sum(
                guild.member_count or 0
                for guild in bot.guilds
            ),

            "channels": sum(
                len(guild.channels)
                for guild in bot.guilds
            ),

            "latency": round(
                bot.latency * 1000
            ),

            "commands": commands_count,

            "bot_status": (
                "Online"
                if bot.is_ready()
                else "Offline"
            ),

            "uptime": get_uptime(),

            "version": os.getenv(
                "MISUKI_VERSION",
                "1.0.0"
            ),

            "admin_servers": admin_servers,
        }


        # -------------------------------------------------
        # TEMPORARY FILE
        # -------------------------------------------------

        temporary_file = (
            BOT_STATS_FILE
            + ".tmp"
        )


        # -------------------------------------------------
        # WRITE
        # -------------------------------------------------

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                snapshot,
                file,
                ensure_ascii=False,
                indent=2
            )


        # -------------------------------------------------
        # REPLACE
        # -------------------------------------------------

        os.replace(
            temporary_file,
            BOT_STATS_FILE
        )


        print(
            "📊 Bot statistics updated:"
        )

        print(
            f"   Servers: {snapshot['servers']}"
        )

        print(
            f"   Users: {snapshot['users']}"
        )

        print(
            f"   Channels: {snapshot['channels']}"
        )

        print(
            f"   Commands: {snapshot['commands']}"
        )

        print(
            f"   Latency: {snapshot['latency']}ms"
        )

        print(
            f"   Uptime: {snapshot['uptime']}"
        )

        print(
            f"   Status: {snapshot['bot_status']}"
        )

    except Exception as error:

        print(
            f"❌ Error updating bot statistics: {error}"
        )


# =========================================================
# STATISTICS LOOP
# =========================================================

async def statistics_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        await update_stats_snapshot()

        await asyncio.sleep(
            30
        )


statistics_task = None


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    global statistics_task


    # =====================================================
    # PRESENCE
    # =====================================================

    await bot.change_presence(

        status=discord.Status.online,

        activity=discord.Game(
            name="Misuki Server"
        )
    )


    print(
        f"🤖 Bot connected as {bot.user}"
    )

    print(
        f"🟢 Bot status: {bot.status}"
    )


    # =====================================================
    # REGISTERED COMMANDS
    # =====================================================

    print(
        "📋 Comandos registados:"
    )


    for command in bot.tree.get_commands():

        print(
            f"   /{command.name}"
        )


        if isinstance(
            command,
            discord.app_commands.Group
        ):

            for subcommand in command.commands:

                print(
                    f"      /{command.name} "
                    f"{subcommand.name}"
                )


    # =====================================================
    # INITIAL STATISTICS
    # =====================================================

    # Criar o bot_stats.json imediatamente
    # quando o bot fica online.

    await update_stats_snapshot()


    # =====================================================
    # SYNC
    # =====================================================

    try:

        synced = await bot.tree.sync()


        print(
            f"⚡ {len(synced)} command(s) synced"
        )


        print(
            "📋 Comandos sincronizados:"
        )


        for command in synced:

            print(
                f"   /{command.name}"
            )


            if isinstance(
                command,
                discord.app_commands.Group
            ):

                for subcommand in command.commands:

                    print(
                        f"      /{command.name} "
                        f"{subcommand.name}"
                    )


        # Atualizar novamente depois do sync,
        # garantindo que o número de comandos
        # está atualizado.

        await update_stats_snapshot()


        # =================================================
        # START STATISTICS LOOP
        # =================================================

        if (
            statistics_task is None
            or statistics_task.done()
        ):

            statistics_task = asyncio.create_task(
                statistics_loop()
            )


    except Exception as error:

        print(
            f"❌ Error syncing commands: {error}"
        )

        # Mesmo que o sync falhe, manter
        # as estatísticas atualizadas.

        await update_stats_snapshot()


        if (
            statistics_task is None
            or statistics_task.done()
        ):

            statistics_task = asyncio.create_task(
                statistics_loop()
            )


# =========================================================
# LOAD EXTENSIONS
# =========================================================

async def load_extensions():

    extensions = [

        "cogs.config",

        "cogs.tickets",

        "cogs.stats",

        "cogs.verification",

        "cogs.jail",

        "cogs.moderation",

        "cogs.announcements",

        "cogs.utility",

        "cogs.licenses",

        "cogs.triggers",

        "cogs.impersonate",
    ]


    for extension in extensions:

        try:

            await bot.load_extension(
                extension
            )


            print(
                f"Loaded: {extension}"
            )


        except Exception as error:

            print(
                f"❌ Failed to load "
                f"{extension}: {error}"
            )


# =========================================================
# MAIN
# =========================================================

async def main():

    token = os.getenv(
        "DISCORD_BOT_TOKEN"
    )

    database_url = os.getenv(
        "DATABASE_URL"
    )


    if not token:

        print(
            "❌ DISCORD_BOT_TOKEN não está configurado."
        )

        return


    if not database_url:

        print(
            "❌ DATABASE_URL não está configurado."
        )

        return


    print(
        "🗄️ DATABASE_URL encontrada."
    )


    # =====================================================
    # LOAD EXTENSIONS
    # =====================================================

    await load_extensions()


    # =====================================================
    # START BOT
    # =====================================================

    print(
        "🚀 Starting Discord bot..."
    )


    print(
        f"🧪 Message Content Intent: "
        f"{bot.intents.message_content}"
    )


    await bot.start(
        token
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )