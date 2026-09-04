# =========================================================
# MISUKI BOT
# Main Bot File
# =========================================================

import os
import asyncio
import json
import time

import discord
import psycopg2

from discord.ext import commands

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


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
# DATABASE CONNECTION
# =========================================================

def get_database_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL não está configurado."
        )

    return psycopg2.connect(
        DATABASE_URL,
        connect_timeout=10
    )


# =========================================================
# CREATE STATISTICS TABLE
# =========================================================

def initialize_statistics_database():

    connection = None

    try:

        connection = get_database_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS bot_statistics (

                    id INTEGER PRIMARY KEY,

                    servers INTEGER NOT NULL DEFAULT 0,

                    users INTEGER NOT NULL DEFAULT 0,

                    channels INTEGER NOT NULL DEFAULT 0,

                    latency INTEGER NOT NULL DEFAULT 0,

                    commands INTEGER NOT NULL DEFAULT 0,

                    bot_status TEXT NOT NULL DEFAULT 'Offline',

                    uptime TEXT NOT NULL DEFAULT '0s',

                    version TEXT NOT NULL DEFAULT '1.0.0',

                    last_seen DOUBLE PRECISION,

                    admin_servers JSONB NOT NULL DEFAULT '[]'::jsonb,

                    updated_at DOUBLE PRECISION NOT NULL
                )
                """
            )

            cursor.execute(
                """
                INSERT INTO bot_statistics (
                    id,
                    servers,
                    users,
                    channels,
                    latency,
                    commands,
                    bot_status,
                    uptime,
                    version,
                    last_seen,
                    admin_servers,
                    updated_at
                )

                VALUES (
                    1,
                    0,
                    0,
                    0,
                    0,
                    0,
                    'Offline',
                    '0s',
                    %s,
                    NULL,
                    '[]'::jsonb,
                    %s
                )

                ON CONFLICT (id)
                DO NOTHING
                """,
                (
                    os.getenv(
                        "MISUKI_VERSION",
                        "1.0.0"
                    ),
                    time.time()
                )
            )

        connection.commit()

        print(
            "🗄️ Statistics database initialized."
        )

    except Exception as error:

        if connection:

            connection.rollback()

        print(
            f"❌ Error initializing statistics database: {error}"
        )

        raise

    finally:

        if connection:

            connection.close()


# =========================================================
# WRITE STATISTICS
# =========================================================

async def update_stats_snapshot():

    connection = None

    try:

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
        # HEARTBEAT
        # -------------------------------------------------

        last_seen = time.time()


        # -------------------------------------------------
        # SNAPSHOT VALUES
        # -------------------------------------------------

        latency = round(
            bot.latency * 1000
        )

        bot_status = (
            "Online"
            if bot.is_ready()
            else "Offline"
        )

        uptime = get_uptime()

        version = os.getenv(
            "MISUKI_VERSION",
            "1.0.0"
        )


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_database_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE bot_statistics

                SET
                    servers = %s,
                    users = %s,
                    channels = %s,
                    latency = %s,
                    commands = %s,
                    bot_status = %s,
                    uptime = %s,
                    version = %s,
                    last_seen = %s,
                    admin_servers = %s::jsonb,
                    updated_at = %s

                WHERE id = 1
                """,
                (
                    len(
                        bot.guilds
                    ),

                    sum(
                        guild.member_count or 0
                        for guild in bot.guilds
                    ),

                    sum(
                        len(guild.channels)
                        for guild in bot.guilds
                    ),

                    latency,

                    commands_count,

                    bot_status,

                    uptime,

                    version,

                    last_seen,

                    json.dumps(
                        admin_servers,
                        ensure_ascii=False
                    ),

                    time.time()
                )
            )

        connection.commit()


        # -------------------------------------------------
        # LOG
        # -------------------------------------------------

        print(
            "📊 Bot statistics updated:"
        )

        print(
            f"   Servers: {len(bot.guilds)}"
        )

        print(
            f"   Users: {sum(guild.member_count or 0 for guild in bot.guilds)}"
        )

        print(
            f"   Channels: {sum(len(guild.channels) for guild in bot.guilds)}"
        )

        print(
            f"   Commands: {commands_count}"
        )

        print(
            f"   Latency: {latency}ms"
        )

        print(
            f"   Uptime: {uptime}"
        )

        print(
            f"   Status: {bot_status}"
        )

        print(
            f"   Heartbeat: {last_seen}"
        )


    except Exception as error:

        print(
            f"❌ Error updating bot statistics: {error}"
        )


    finally:

        if connection:

            connection.close()


# =========================================================
# STATISTICS LOOP
# =========================================================

async def statistics_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        await update_stats_snapshot()

        await asyncio.sleep(
            10
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


        # Atualizar depois do sync.

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


        # Mesmo que o sync falhe,
        # continuar com o heartbeat.

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
    # INITIALIZE STATISTICS DATABASE
    # =====================================================

    initialize_statistics_database()


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