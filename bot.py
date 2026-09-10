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


load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_START_TIME = time.time()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


def count_commands(commands_list):
    total = 0
    for command in commands_list:
        if isinstance(command, discord.app_commands.Group):
            total += count_commands(command.commands)
        else:
            total += 1
    return total


def is_human_member(member):
    """Discord's authoritative bot flag: human accounts only."""
    return not bool(getattr(member, "bot", False))


BOT_INSTALLERS = {}


async def refresh_bot_installers():
    """Find who actually added Misuki in each guild using Discord's audit log."""
    if not bot.user:
        return

    for guild in bot.guilds:
        try:
            async for entry in guild.audit_logs(
                limit=50,
                action=discord.AuditLogAction.bot_add
            ):
                target = getattr(entry, "target", None)
                target_id = getattr(target, "id", None)
                if target_id == bot.user.id:
                    actor = getattr(entry, "user", None)
                    actor_id = getattr(actor, "id", None)
                    if actor_id:
                        BOT_INSTALLERS[str(guild.id)] = str(actor_id)
                    break
        except Exception as error:
            print(f"⚠️ Could not read installer audit log for {guild.name} ({guild.id}): {error}")


async def count_statistics_users():
    """Count unique human Discord users across all guilds."""
    user_ids = set()
    scanned = 0
    excluded_bots = 0

    for guild in bot.guilds:
        guild_seen = set()
        try:
            async for member in guild.fetch_members(limit=None, cache=True):
                member_id = getattr(member, "id", None)
                if member_id is None or member_id in guild_seen:
                    continue

                guild_seen.add(member_id)
                scanned += 1

                if not is_human_member(member):
                    excluded_bots += 1
                    continue

                user_ids.add(member_id)

        except Exception as error:
            print(
                f"⚠️ Could not fetch members for {guild.name} ({guild.id}): {error}"
            )

            for member in guild.members:
                member_id = getattr(member, "id", None)
                if member_id is None or member_id in guild_seen:
                    continue

                guild_seen.add(member_id)
                scanned += 1

                if not is_human_member(member):
                    excluded_bots += 1
                    continue

                user_ids.add(member_id)

    print(f"   Members scanned: {scanned}")
    print(f"   Bots excluded: {excluded_bots}")
    print(f"   Unique human users: {len(user_ids)}")

    return len(user_ids)


def count_verified_users():
    connection = None
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id)
                FROM verification_requests
                WHERE status = 'verified'
            """)
            result = cursor.fetchone()
            return int(result[0] or 0) if result else 0
    except Exception as error:
        print(f"⚠️ Could not read verification statistics: {error}")
        return 0
    finally:
        if connection:
            connection.close()


def get_uptime():
    elapsed = max(0, int(time.time() - BOT_START_TIME))
    days, remainder = divmod(elapsed, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def get_database_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não está configurado.")
    return psycopg2.connect(DATABASE_URL, connect_timeout=10)


def initialize_statistics_database():
    connection = None
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_statistics (
                    id INTEGER PRIMARY KEY,
                    servers INTEGER NOT NULL DEFAULT 0,
                    users INTEGER NOT NULL DEFAULT 0,
                    channels INTEGER NOT NULL DEFAULT 0,
                    latency INTEGER NOT NULL DEFAULT 0,
                    commands INTEGER NOT NULL DEFAULT 0,
                    tickets BIGINT NOT NULL DEFAULT 0,
                    moderation_actions BIGINT NOT NULL DEFAULT 0,
                    announcements BIGINT NOT NULL DEFAULT 0,
                    verifications INTEGER NOT NULL DEFAULT 0,
                    bot_status TEXT NOT NULL DEFAULT 'Offline',
                    uptime TEXT NOT NULL DEFAULT '0s',
                    version TEXT NOT NULL DEFAULT '1.0.0',
                    last_seen DOUBLE PRECISION,
                    admin_servers JSONB NOT NULL DEFAULT '[]'::jsonb,
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
            migrations = [
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS verifications INTEGER NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS tickets BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS moderation_actions BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS announcements BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS admin_servers JSONB NOT NULL DEFAULT '[]'::jsonb",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS last_seen DOUBLE PRECISION",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS updated_at DOUBLE PRECISION NOT NULL DEFAULT 0",
            ]
            for migration in migrations:
                cursor.execute(migration)
            cursor.execute("""
                INSERT INTO bot_statistics (
                    id, servers, users, channels, latency, commands, tickets,
                    moderation_actions, announcements, verifications, bot_status,
                    uptime, version, last_seen, admin_servers, updated_at
                ) VALUES (
                    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Offline', '0s', %s,
                    NULL, '[]'::jsonb, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (os.getenv("MISUKI_VERSION", "1.0.0"), time.time()))
        connection.commit()
        print("🗄️ Statistics database initialized.")
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"❌ Error initializing statistics database: {error}")
        raise
    finally:
        if connection:
            connection.close()


def get_detected_servers():
    servers = []
    for guild in bot.guilds:
        icon = None
        try:
            if guild.icon:
                icon = str(guild.icon.url)
        except Exception:
            icon = None
        installer_id = BOT_INSTALLERS.get(str(guild.id))
        servers.append({
            "name": guild.name,
            "id": str(guild.id),
            "icon": icon,
            # Kept for compatibility with the existing dashboard backend.
            # This is the actual installer, never the current guild owner.
            "owner_id": installer_id,
            "installer_id": installer_id,
            "server_owner_id": str(guild.owner_id) if guild.owner_id else None,
            "members": sum(
                1 for member in guild.members if is_human_member(member)
            )
        })
    return servers


def print_detected_servers():
    detected_servers = get_detected_servers()
    print("🔎 Discord guilds detected:")
    if not detected_servers:
        print("   ⚠️ No guilds detected.")
        return
    for server in detected_servers:
        print(
            f"   • {server['name']} ({server['id']}) "
            f"— {server['members']} members"
        )


async def update_stats_snapshot():
    connection = None
    try:
        await refresh_bot_installers()
        users_count = await count_statistics_users()
        detected_servers = get_detected_servers()
        servers_count = len(detected_servers)
        commands_count = count_commands(bot.tree.get_commands())
        verifications_count = count_verified_users()
        last_seen = time.time()
        latency = round(bot.latency * 1000)
        bot_status = "Online" if bot.is_ready() else "Offline"
        uptime = get_uptime()
        version = os.getenv("MISUKI_VERSION", "1.0.0")
        channels_count = sum(len(guild.channels) for guild in bot.guilds)
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # IMPORTANT: activity counters are maintained by their cogs.
            # Do not overwrite tickets/moderation/announcements here.
            cursor.execute("""
                UPDATE bot_statistics
                SET
                    servers = %s,
                    users = %s,
                    channels = %s,
                    latency = %s,
                    commands = %s,
                    verifications = %s,
                    bot_status = %s,
                    uptime = %s,
                    version = %s,
                    last_seen = %s,
                    admin_servers = %s::jsonb,
                    updated_at = %s
                WHERE id = 1
            """, (
                servers_count, users_count, channels_count, latency,
                commands_count, verifications_count, bot_status, uptime,
                version, last_seen, json.dumps(detected_servers, ensure_ascii=False),
                last_seen
            ))
        connection.commit()
        print("📊 Bot statistics updated:")
        print(f"   Servers: {servers_count}")
        print(f"   Users: {users_count}")
        print(f"   Verifications: {verifications_count}")
        print(f"   Channels: {channels_count}")
        print(f"   Commands: {commands_count}")
        print(f"   Latency: {latency}ms")
        print(f"   Uptime: {uptime}")
        print(f"   Status: {bot_status}")
        print(f"   Heartbeat: {last_seen}")
        print_detected_servers()
    except Exception as error:
        print(f"❌ Error updating bot statistics: {error}")
    finally:
        if connection:
            connection.close()


async def statistics_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await update_stats_snapshot()
        await asyncio.sleep(10)


statistics_task = None


@bot.event
async def on_guild_join(guild):
    print("➕ Bot joined a new server:")
    print(f"   Name: {guild.name}")
    print(f"   ID: {guild.id}")
    print(f"   Members: {sum(1 for member in guild.members if is_human_member(member))}")
    await asyncio.sleep(2)
    await refresh_bot_installers()
    await update_stats_snapshot()


@bot.event
async def on_guild_remove(guild):
    BOT_INSTALLERS.pop(str(guild.id), None)
    print("➖ Bot left a server:")
    print(f"   Name: {guild.name}")
    print(f"   ID: {guild.id}")
    await update_stats_snapshot()


@bot.event
async def on_ready():
    global statistics_task
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Misuki Server"))
    print(f"🤖 Bot connected as {bot.user}")
    print(f"🟢 Bot status: {bot.status}")
    print(f"🏠 Discord guild count: {len(bot.guilds)}")
    await refresh_bot_installers()
    print_detected_servers()
    print("📋 Comandos registados:")
    for command in bot.tree.get_commands():
        print(f"   /{command.name}")
        if isinstance(command, discord.app_commands.Group):
            for subcommand in command.commands:
                print(f"      /{command.name} {subcommand.name}")
    await update_stats_snapshot()
    try:
        synced = await bot.tree.sync()
        print(f"⚡ {len(synced)} command(s) synced")
        print("📋 Comandos sincronizados:")
        for command in synced:
            print(f"   /{command.name}")
    except Exception as error:
        print(f"❌ Command sync error: {error}")
    if statistics_task is None or statistics_task.done():
        statistics_task = asyncio.create_task(statistics_loop())


EXTENSIONS = [
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


async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            print(f"🧩 Loaded extension: {extension}")
        except Exception as error:
            print(f"❌ Failed to load extension {extension}: {error}")


async def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN não está configurado.")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não está configurado.")
    initialize_statistics_database()
    await load_extensions()
    await bot.start(token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped.")
