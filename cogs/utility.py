
# =========================================================
# MISUKI - UTILITY
# =========================================================

import discord

from discord.ext import commands


# =========================================================
# UTILITY COG
# =========================================================

class Utility(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    # =====================================================
    # /PING
    # =====================================================

    @discord.app_commands.command(
        name="ping",
        description="Check if the bot is online."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        try:

            latency = round(
                self.bot.latency * 1000
            )

            await interaction.response.send_message(
                f"🏓 **Pong!**\n"
                f"📡 Latency: `{latency}ms`"
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error executing /ping: {error}"
            )


    # =====================================================
    # /HELP
    # =====================================================

    @discord.app_commands.command(
        name="help",
        description="Show available commands."
    )
    async def help_command(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="🤖 Misuki Bot — Commands",
            description=(
                "`/ping` — Check if the bot is online.\n"
                "`/help` — Show this message."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Misuki Bot"
        )

        try:

            await interaction.response.send_message(
                embed=embed
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error executing /help: {error}"
            )


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    await bot.add_cog(
        Utility(bot)
    )

    print(
        "🛠️ Utility cog loaded."
    )

