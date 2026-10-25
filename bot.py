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


load_dotenv(override=False)

DATABASE_URL = os.getenv("DATABASE_URL")
MISUKI_VERSION = os.getenv("MISUKI_VERSION", "").strip()
BOT_START_TIME = time.time()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


PREMIUM_COMMANDS = {
    "ticket", "verify", "warn", "warnings", "unwarn", "clearwarnings",
    "clear", "timeout", "untimeout", "kick", "ban", "unban", "softban",
    "jail", "unjail", "jailinfo", "announce", "trigger", "impersonate"
}


async def global_license_check(interaction: discord.Interaction):
    """Block premium application commands when the guild has no active license."""
    if interaction.guild is None:
        return True

    command = getattr(interaction, "command", None)
    command_name = getattr(command, "qualified_name", None) or getattr(command, "name", None)
    if command_name:
        command_name = str(command_name).split()[-1].lower()

    if command_name not in PREMIUM_COMMANDS:
        return True

    license_manager = bot.get_cog("LicenseManager")
    if license_manager is None:
        await interaction.response.send_message(
            "❌ Premium functionality is temporarily unavailable. Please try again later.",
            ephemeral=True
        )
        return False

    try:
        active = await license_manager.has_active_license(interaction.guild.id)
    except Exception as error:
        print(f"⚠️ Could not verify license for /{command_name}: {error}")
        await interaction.response.send_message(
            "❌ The license could not be verified. Please try again later.",
            ephemeral=True
        )
        return False

    if active:
        return True

    await interaction.response.send_message(
        "🔒 This command requires an active Misuki license for this server.",
        ephemeral=True
    )
    return False


bot.tree.interaction_check = global_license_check


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
BOT_GUILD_HUMAN_COUNTS = {}


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


BOT_ADMIN_USERS = []

async def populate_member_cache():
    """Populate Discord member caches so statistics can use real member data."""
    for guild in bot.guilds:
        try:
            await guild.chunk(cache=True)
        except Exception as error:
            print(
                f"⚠️ Could not populate members for {guild.name} "
                f"({guild.id}): {error}"
            )


async def count_statistics_users():
    """Count unique human Discord users from the bot's populated member cache."""
    global BOT_ADMIN_USERS

    BOT_GUILD_HUMAN_COUNTS.clear()

    users_by_id = {}

    for guild in bot.guilds:
        guild_humans = set()

        for member in guild.members:
            member_id = getattr(member, "id", None)

            if member_id is None:
                continue

            if not is_human_member(member):
                continue

            member_id = str(member_id)
            guild_humans.add(member_id)

            username = str(
                getattr(member, "name", "")
                or ""
            )

            display_name = str(
                getattr(member, "display_name", "")
                or username
                or "Discord User"
            )

            avatar_url = None

            try:
                avatar = getattr(member, "display_avatar", None)
                if avatar:
                    avatar_url = str(avatar.url)
            except Exception:
                avatar_url = None

            user = users_by_id.get(member_id)

            if user is None:
                user = {
                    "id": member_id,
                    "name": display_name,
                    "username": username,
                    "avatar": avatar_url,
                    "servers_count": 0,
                    "created_at": None,
                    "added_bot": False
                }
                users_by_id[member_id] = user

            user["servers_count"] += 1

            if avatar_url:
                user["avatar"] = avatar_url

            if display_name:
                user["name"] = display_name

            if username:
                user["username"] = username

        BOT_GUILD_HUMAN_COUNTS[str(guild.id)] = len(guild_humans)

    installer_ids = {
        str(value)
        for value in BOT_INSTALLERS.values()
        if value
    }

    for user in users_by_id.values():
        try:
            discord_id = int(user["id"])
            timestamp = (
                (discord_id >> 22) + 1420070400000
            ) / 1000

            user["created_at"] = time.strftime(
                "%d/%m/%Y",
                time.gmtime(timestamp)
            )
        except Exception:
            user["created_at"] = None

        user["added_bot"] = user["id"] in installer_ids

    BOT_ADMIN_USERS = sorted(
        users_by_id.values(),
        key=lambda user: (
            str(user.get("name") or "").lower(),
            str(user.get("id") or "")
        )
    )

    print(f"   Unique human users: {len(BOT_ADMIN_USERS)}")

    return len(BOT_ADMIN_USERS)

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
                    version TEXT NOT NULL DEFAULT '',
                    last_seen DOUBLE PRECISION,
                    admin_servers JSONB NOT NULL DEFAULT '[]'::jsonb,
                    admin_users JSONB NOT NULL DEFAULT '[]'::jsonb,
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
            migrations = [
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS verifications INTEGER NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS tickets BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS moderation_actions BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS announcements BIGINT NOT NULL DEFAULT 0",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS admin_servers JSONB NOT NULL DEFAULT '[]'::jsonb",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS admin_users JSONB NOT NULL DEFAULT '[]'::jsonb",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS last_seen DOUBLE PRECISION",
                "ALTER TABLE bot_statistics ADD COLUMN IF NOT EXISTS updated_at DOUBLE PRECISION NOT NULL DEFAULT 0",
            ]
            for migration in migrations:
                cursor.execute(migration)
            cursor.execute("""
                INSERT INTO bot_statistics (
                    id, servers, users, channels, latency, commands, tickets,
                    moderation_actions, announcements, verifications, bot_status,
                    uptime, version, last_seen, admin_servers, admin_users, updated_at
                ) VALUES (
                    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'Offline', '0s', %s,
                    NULL, '[]'::jsonb, '[]'::jsonb, %s
                ) ON CONFLICT (id) DO NOTHING
            """, (MISUKI_VERSION, time.time()))
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
            "members": BOT_GUILD_HUMAN_COUNTS.get(
                str(guild.id),
                sum(1 for member in guild.members if is_human_member(member))
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
        version = MISUKI_VERSION
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
                    admin_users = %s::jsonb,
                    updated_at = %s
                WHERE id = 1
            """, (
                servers_count, users_count, channels_count, latency,
                commands_count, verifications_count, bot_status, uptime,
                version, last_seen, json.dumps(detected_servers, ensure_ascii=False),
                json.dumps(BOT_ADMIN_USERS, ensure_ascii=False), last_seen
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


async def sync_owner_license_command_permissions():
    """Make license-management commands visible only to the bot owner in each guild."""
    if not OWNER_ID:
        return

    commands_to_restrict = {"createlicense", "revokelicense"}

    for guild in bot.guilds:
        try:
            for command in bot.tree.get_commands():
                if command.name not in commands_to_restrict:
                    continue

                await bot.tree.set_permissions(
                    guild,
                    command,
                    permissions=[
                        discord.app_commands.CommandPermission(
                            id=OWNER_ID,
                            type=discord.app_commands.AppCommandPermissionType.user,
                            permission=True,
                        )
                    ],
                )
        except Exception as error:
            print(
                f"⚠️ Could not restrict license command permissions in "
                f"{guild.id}: {error}"
            )


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
    await populate_member_cache()
    print_detected_servers()
    print("📋 Comandos registados:")
    registered_count = 0

    for command in bot.tree.get_commands():
        if isinstance(
            command,
            discord.app_commands.Group
        ):
            print(f"   /{command.name}")

            for subcommand in command.commands:
                registered_count += 1
                print(
                    f"      /{command.name} "
                    f"{subcommand.name}"
                )
        else:
            registered_count += 1
            print(f"   /{command.name}")

    print(
        f"📊 Total de comandos registados: "
        f"{registered_count}"
    )

    await update_stats_snapshot()

    try:
        synced = await bot.tree.sync()

        # Discord returns top-level commands/groups from sync().
        # Group subcommands are contained inside their parent group,
        # so they must not be counted recursively for sync verification.
        registered_top_level_count = len(bot.tree.get_commands())
        synced_top_level_count = len(synced)

        print(
            f"⚡ {synced_top_level_count} top-level command(s)/group(s) synced"
        )

        print("📋 Comandos sincronizados:")

        for command in synced:
            if isinstance(
                command,
                discord.app_commands.Group
            ):
                print(f"   /{command.name}")

                for subcommand in command.commands:
                    print(
                        f"      /{command.name} "
                        f"{subcommand.name}"
                    )
            else:
                print(f"   /{command.name}")

        if synced_top_level_count != registered_top_level_count:
            raise RuntimeError(
                "Discord command sync mismatch: "
                f"top_level_registered={registered_top_level_count}, "
                f"top_level_synced={synced_top_level_count}"
            )

        print(
            "✅ All registered commands/groups were "
            "successfully synchronised with Discord."
        )

        await sync_owner_license_command_permissions()
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
    "cogs.onboarding",
    "cogs.triggers",
    "cogs.impersonate",
]


async def load_extensions():
    failed_extensions = []

    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            print(f"🧩 Loaded extension: {extension}")
        except Exception as error:
            failed_extensions.append(
                (extension, error)
            )

            print(
                f"❌ Failed to load extension "
                f"{extension}: {error}"
            )

    # Do not start a partially loaded bot.
    # A missing cog means its commands would not be
    # registered/synchronised with Discord.
    if failed_extensions:
        print(
            "❌ Bot startup aborted: "
            f"{len(failed_extensions)} extension(s) failed."
        )

        for extension, error in failed_extensions:
            print(
                f"   • {extension}: {error}"
            )

        raise RuntimeError(
            "One or more Discord extensions failed to load."
        )

    loaded_count = len(EXTENSIONS)

    print(
        f"🧩 All Discord extensions loaded "
        f"successfully ({loaded_count}/{len(EXTENSIONS)})."
    )


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
