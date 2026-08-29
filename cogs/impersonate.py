import discord
from discord import app_commands
from discord.ext import commands


class Impersonate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="impersonate",
        description="Pretends to be an user, by sending the wished message."
    )
    @app_commands.describe(
        user="The user to impersonate",
        message="Message"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def impersonate(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: str
    ):

        await interaction.response.defer()

        webhook = await interaction.channel.create_webhook(
            name="Misuki Parody"
        )

        try:

            display_name = user.display_name
            avatar_url = user.display_avatar.url

            await webhook.send(
                content=message,
                username=f"{display_name}",
                avatar_url=avatar_url,
                wait=True
            )

        finally:

            await webhook.delete()


    @impersonate.error
    async def impersonate_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):

            await interaction.response.send_message(
                "❌ Apenas Staff pode usar este comando.",
                ephemeral=True
            )

            return

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ Ocorreu um erro ao executar o comando.",
                ephemeral=True
            )


async def setup(bot):

    await bot.add_cog(
        Impersonate(bot)
    )