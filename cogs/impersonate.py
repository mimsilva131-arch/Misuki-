import discord
from discord import app_commands
from discord.ext import commands


class Impersonate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="impersonate",
        description="Send a message as another user"
    )
    @app_commands.describe(
        user="User you want to impersonate",
        message="Message to send"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def impersonate(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: str
    ):

        if not isinstance(
            interaction.channel,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                "❌ This command can only be used in a text channel.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        webhook = None

        try:

            display_name = (
                user.display_name
                or user.name
                or "Discord User"
            )

            avatar_url = str(
                user.display_avatar.replace(
                    size=1024,
                    format="png"
                ).url
            )

            webhook = await interaction.channel.create_webhook(
                name="Misuki Parody"
            )

            await webhook.send(
                content=message,
                username=f"{display_name}",
                avatar_url=avatar_url,
                allowed_mentions=discord.AllowedMentions.none()
            )

            await webhook.delete(
                reason="Temporary Misuki parody webhook"
            )

            webhook = None

            await interaction.followup.send(
                "✅ Paródia enviada.",
                ephemeral=True
            )

        except discord.Forbidden:

            if webhook:
                try:
                    await webhook.delete()
                except Exception:
                    pass

            await interaction.followup.send(
                "❌ O Misuki não tem permissão para gerir webhooks neste canal.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"❌ Discord API error: {error}"
            )

            if webhook:
                try:
                    await webhook.delete()
                except Exception:
                    pass

            await interaction.followup.send(
                "❌ O Discord rejeitou a operação.",
                ephemeral=True
            )

        except Exception as error:

            print(
                f"❌ Impersonate error: {error}"
            )

            if webhook:
                try:
                    await webhook.delete()
                except Exception:
                    pass

            await interaction.followup.send(
                "❌ Ocorreu um erro inesperado.",
                ephemeral=True
            )

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

            message = (
                "❌ Apenas Staff pode utilizar este comando."
            )

        else:

            print(
                f"❌ Impersonate command error: {error}"
            )

            message = (
                "❌ Ocorreu um erro ao executar o comando."
            )

        if interaction.response.is_done():

            await interaction.followup.send(
                message,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                message,
                ephemeral=True
            )


async def setup(bot):

    await bot.add_cog(
        Impersonate(bot)
    )