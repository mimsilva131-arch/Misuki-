
import os
import asyncio
import discord
from discord.ext import commands


# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.all()


# =========================================================
# BOT
# =========================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
print(
    "Message Content Intent:",
    bot.intents.message_content
)

# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

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

    except Exception as error:

        print(
            f"❌ Error syncing commands: {error}"
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
        "DISCORD_TOKEN"
    )

    if not token:

        print(
            "❌ DISCORD_TOKEN não está configurado."
        )

        return

    await load_extensions()

    print(
        "🚀 Starting Discord bot..."
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

