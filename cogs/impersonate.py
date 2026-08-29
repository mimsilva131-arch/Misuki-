import discord
from discord import app_commands
from discord.ext import commands


class Impersonate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="impersonate",
        description="Envia uma mensagem de paródia usando o perfil visual de um utilizador."
    )
    @app_commands.describe(
        user="Utilizador a representar",
        message="Mensagem"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def impersonate(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: str
    ):

        channel = interaction.channel

        if not isinstance(
            channel,
            discord.TextChannel
        ):
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado num canal de texto.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:

            webhook = await channel.create_webhook(
                name="Misuki Parody"
            )

            avatar_url = str(
                user.display_avatar.replace(
                    size=1024,
                    format="png"
                ).url
            )

            username = (
                f"{user.display_name} [PARÓDIA]"
            )

            await webhook.send(
                content=message,
                username=username,
                avatar_url=avatar_url,
                allowed_mentions=discord.AllowedMentions.none()
            )

            await webhook.delete(
                reason="Temporary Misuki parody webhook"
            )

            await interaction.followup.send(
                "✅ Paródia enviada.",
                ephemeral=True
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ O Misuki não tem permissão para gerir webhooks neste canal.",
                ephemeral=True
            )

        except discord.HTTPException as error:

            print(
                f"❌ Impersonate webhook error: {error}"
            )

            await interaction.followup.send(
                "❌ Não foi possível enviar a paródia.",
                ephemeral=True
            )

        except Exception as error:

            print(
                f"❌ Impersonate error: {error}"
            )

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

            await interaction.response.send_message(
                "❌ Apenas Staff pode utilizar este comando.",
                ephemeral=True
            )

            return

        print(
            f"❌ Impersonate command error: {error}"
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                "❌ Ocorreu um erro.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Ocorreu um erro.",
                ephemeral=True
            )


async def setup(bot):

    await bot.add_cog(
        Impersonate(bot)
    )