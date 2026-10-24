# =========================================================
# MISUKI ONBOARDING
# Automatic welcome DM + one-time 30-day free license
# =========================================================

import asyncio

import discord
from discord.ext import commands


class Onboarding(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def find_installer(self, guild):
        try:
            async for entry in guild.audit_logs(
                limit=20,
                action=discord.AuditLogAction.bot_add
            ):
                target = getattr(entry, "target", None)

                if target and getattr(target, "id", None) == self.bot.user.id:
                    user = getattr(entry, "user", None)
                    if user is not None:
                        return user
        except Exception as error:
            print(
                f"Could not read installer audit log for "
                f"{guild.name} ({guild.id}): {error}"
            )

        return guild.owner

    async def send_welcome_dm(self, guild, user, license_key, expires_at):
        expiration = (
            f"<t:{int(expires_at.timestamp())}:F>"
            if expires_at
            else "30 days after activation"
        )

        embed = discord.Embed(
            title="Welcome to Misuki",
            description=(
                f"Thank you for adding Misuki to **{guild.name}**.\n\n"
                "Your server has received **30 days of Misuki Premium completely free**."
            ),
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Quick Start Guide",
            value=(
                "1. Configure your server settings.\n"
                "2. Set up the verification system.\n"
                "3. Configure tickets and support channels.\n"
                "4. Configure moderation features.\n"
                "5. Check your license and Premium features."
            ),
            inline=False
        )

        embed.add_field(
            name="Your Free 30-Day License",
            value=(
                f"License key: `{license_key}`\n"
                f"Expires: {expiration}\n\n"
                "No funds will be charged when your free license expires. "
                "There are no automatic charges, renewals, or payments after "
                "the free period. When the license expires, your Premium "
                "benefits will simply end."
            ),
            inline=False
        )

        embed.add_field(
            name="Need Help?",
            value=(
                "You can use the Misuki dashboard to manage your server and "
                "license. Make sure Misuki has the permissions required by "
                "the features you enable."
            ),
            inline=False
        )

        embed.set_footer(text="Misuki • Premium License")

        try:
            await user.send(embed=embed)
            print(
                f"Sent onboarding DM to {user} for "
                f"{guild.name} ({guild.id})."
            )
        except Exception as error:
            print(
                f"Could not send onboarding DM to {user} "
                f"for {guild.name} ({guild.id}): {error}"
            )

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await asyncio.sleep(3)

        license_manager = self.bot.get_cog("LicenseManager")

        if license_manager is None:
            print(
                f"LicenseManager is unavailable; onboarding skipped for "
                f"{guild.name} ({guild.id})."
            )
            return

        if not license_manager.database_ready():
            print(
                f"License database is unavailable; onboarding skipped for "
                f"{guild.name} ({guild.id})."
            )
            return

        installer = await self.find_installer(guild)

        if installer is None:
            print(
                f"Could not determine installer for "
                f"{guild.name} ({guild.id})."
            )
            return

        license_key = await license_manager.create_license(
            guild.id,
            30
        )

        if license_key is None:
            print(
                f"No new free license created for {guild.name} ({guild.id}); "
                "the server already has a license."
            )
            return

        license_data = await license_manager.get_license(guild.id)

        if license_data is None:
            print(
                f"Free license was created but could not be read for "
                f"{guild.name} ({guild.id})."
            )
            return

        await self.send_welcome_dm(
            guild,
            installer,
            license_key,
            license_data["expires_at"]
        )


async def setup(bot):
    await bot.add_cog(Onboarding(bot))
    print("Onboarding loaded.")
