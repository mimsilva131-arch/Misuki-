import discord
from discord import app_commands
from discord.ext import commands


class Impersonate(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="impersonate",
        description="Cria uma paródia visual do perfil de um utilizador."
    )
    @app_commands.describe(
        user="Utilizador que queres representar",
        message="Mensagem a enviar"
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
                "❌ Este comando só pode ser usado num canal de texto.",
                ephemeral=True
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        webhook = None

        try:
            # =====================================================
            # PERFIL
            # =====================================================

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

            # =====================================================
            # EMBED
            # =====================================================

            embed = discord.Embed(
                description=message,
                color=discord.Color.blurple()
            )

            embed.set_author(
                name=f"{display_name} [PARÓDIA]",
                icon_url=avatar_url
            )

            # =====================================================
            # AVATAR
            # =====================================================

            embed.set_thumbnail(
                url=avatar_url
            )

            # =====================================================
            # PERFIL
            # =====================================================

            embed.add_field(
                name="👤 Utilizador representado",
                value=f"{user.mention}",
                inline=False
            )

            # =====================================================
            # USERNAME
            # =====================================================

            embed.add_field(
                name="🏷️ Username",
                value=f"`@{user.name}`",
                inline=True
            )

            # =====================================================
            # ID
            # =====================================================

            embed.add_field(
                name="🆔 ID",
                value=f"`{user.id}`",
                inline=True
            )

            # =====================================================
            # BANNER
            # =====================================================
            #
            # Member normalmente não fornece o banner.
            # Tentamos obter o User completo através da API
            # oficial da discord.py.
            #

            try:
                full_user = await self.bot.fetch_user(
                    user.id
                )

            except discord.HTTPException:
                full_user = user

            banner_url = None

            if getattr(
                full_user,
                "banner",
                None
            ):

                try:
                    banner_url = str(
                        full_user.banner.replace(
                            size=1024,
                            format="png"
                        ).url
                    )

                except Exception:
                    banner_url = None

            if banner_url:

                embed.set_image(
                    url=banner_url
                )

            # =====================================================
            # FOOTER
            # =====================================================

            embed.set_footer(
                text="⚠️ PARÓDIA • Misuki"
            )

            # =====================================================
            # WEBHOOK
            # =====================================================

            webhook = await interaction.channel.create_webhook(
                name="Misuki Parody"
            )

            await webhook.send(
                username=f"{display_name} [PARÓDIA]",
                avatar_url=avatar_url,
                embed=embed,
                allowed_mentions=discord.AllowedMentions.none()
            )

            # =====================================================
            # DELETE WEBHOOK
            # =====================================================

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
                "❌ O Misuki não tem permissão para criar ou gerir webhooks neste canal.",
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

    # =========================================================
    # PERMISSION ERROR
    # =========================================================

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

            if interaction.response.is_done():

                await interaction.followup.send(
                    "❌ Apenas Staff pode utilizar este comando.",
                    ephemeral=True
                )

            else:

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
                "❌ Ocorreu um erro ao executar o comando.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                "❌ Ocorreu um erro ao executar o comando.",
                ephemeral=True
            )


# =============================================================
# SETUP
# =============================================================

async def setup(bot):

    await bot.add_cog(
        Impersonate(bot)
    )