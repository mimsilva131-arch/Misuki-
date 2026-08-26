import discord
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="ping",
        description="Check if the bot is online."
    )
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong! 🏓")

    @discord.app_commands.command(
        name="help",
        description="Show available commands."
    )
    async def help_command(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "**🤖 Misuki Bot — Commands**\n\n"
            "`/ping` — Check if the bot is online.\n"
            "`/help` — Show this message."
        )


async def setup(bot):
    await bot.add_cog(Utility(bot))