# =========================================================
# MISUKI LICENSE SYSTEM
# PostgreSQL / Neon
# =========================================================

import os
import secrets

from datetime import datetime, timedelta, timezone

import asyncpg

import discord

from discord import app_commands

from discord.ext import commands


# =========================================================
# ENVIRONMENT
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# =========================================================
# OWNER
# =========================================================

OWNER_ID = 1146083816503529545


# =========================================================
# LICENSE MANAGER
# =========================================================

class LicenseManager(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.pool = None


    # =====================================================
    # DATABASE
    # =====================================================

    async def create_database(self):

        if not DATABASE_URL:

            raise RuntimeError(
                "DATABASE_URL não está configurado."
            )

        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=5
        )

        async with self.pool.acquire() as connection:

            await connection.execute("""
                CREATE TABLE IF NOT EXISTS licenses (

                    guild_id BIGINT PRIMARY KEY,

                    license_key TEXT UNIQUE NOT NULL,

                    status TEXT NOT NULL
                    DEFAULT 'active',

                    expires_at TIMESTAMPTZ,

                    created_at TIMESTAMPTZ NOT NULL

                )
            """)


    # =====================================================
    # COG LOAD
    # =====================================================

    async def cog_load(self):

        await self.create_database()

        print(
            "🗄️ LicenseManager conectado ao Neon."
        )


    # =====================================================
    # COG UNLOAD
    # =====================================================

    async def cog_unload(self):

        if self.pool:

            await self.pool.close()


    # =====================================================
    # GENERATE KEY
    # =====================================================

    async def generate_license_key(self):

        while True:

            parts = [

                secrets.token_hex(4).upper(),

                secrets.token_hex(4).upper(),

                secrets.token_hex(4).upper(),

                secrets.token_hex(4).upper()

            ]

            key = (
                "MISUKI-"
                + "-".join(parts)
            )

            async with self.pool.acquire() as connection:

                result = await connection.fetchrow(
                    """
                    SELECT 1
                    FROM licenses
                    WHERE license_key = $1
                    """,
                    key
                )

            if result is None:

                return key


    # =====================================================
    # GET LICENSE
    # =====================================================

    async def get_license(
        self,
        guild_id
    ):

        async with self.pool.acquire() as connection:

            return await connection.fetchrow(
                """
                SELECT
                    guild_id,
                    license_key,
                    status,
                    expires_at,
                    created_at
                FROM licenses
                WHERE guild_id = $1
                """,
                guild_id
            )


    # =====================================================
    # ACTIVE LICENSE
    # =====================================================

    async def has_active_license(
        self,
        guild_id
    ):

        license_data = await self.get_license(
            guild_id
        )

        if license_data is None:

            return False

        status = license_data["status"]

        expires_at = license_data["expires_at"]

        if status != "active":

            return False

        if expires_at is None:

            return True

        now = datetime.now(
            timezone.utc
        )

        if now >= expires_at:

            await self.set_expired(
                guild_id
            )

            return False

        return True


    # =====================================================
    # EXPIRE
    # =====================================================

    async def set_expired(
        self,
        guild_id
    ):

        async with self.pool.acquire() as connection:

            await connection.execute(
                """
                UPDATE licenses
                SET status = 'expired'
                WHERE guild_id = $1
                """,
                guild_id
            )


    # =====================================================
    # CREATE
    # =====================================================

    async def create_license(
        self,
        guild_id,
        days
    ):

        existing = await self.get_license(
            guild_id
        )

        if existing:

            return None

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(days=days)
        )

        license_key = await self.generate_license_key()

        async with self.pool.acquire() as connection:

            await connection.execute(
                """
                INSERT INTO licenses
                (
                    guild_id,
                    license_key,
                    status,
                    expires_at,
                    created_at
                )

                VALUES ($1, $2, $3, $4, $5)
                """,

                guild_id,
                license_key,
                "active",
                expires_at,
                now
            )

        return license_key


    # =====================================================
    # REVOKE
    # =====================================================

    async def revoke_license(
        self,
        guild_id
    ):

        existing = await self.get_license(
            guild_id
        )

        if existing is None:

            return False

        async with self.pool.acquire() as connection:

            await connection.execute(
                """
                UPDATE licenses
                SET status = 'revoked'
                WHERE guild_id = $1
                """,
                guild_id
            )

        return True


    # =====================================================
    # EXTEND
    # =====================================================

    async def extend_license(
        self,
        guild_id,
        days
    ):

        existing = await self.get_license(
            guild_id
        )

        if existing is None:

            return False

        status = existing["status"]

        expires_at = existing["expires_at"]

        if status != "active":

            return False

        if expires_at is None:

            return False

        now = datetime.now(
            timezone.utc
        )

        if now >= expires_at:

            await self.set_expired(
                guild_id
            )

            return False

        new_expiration = (
            expires_at
            + timedelta(days=days)
        )

        async with self.pool.acquire() as connection:

            await connection.execute(
                """
                UPDATE licenses
                SET expires_at = $1
                WHERE guild_id = $2
                """,
                new_expiration,
                guild_id
            )

        return True


    # =====================================================
    # DELETE
    # =====================================================

    async def delete_license(
        self,
        guild_id
    ):

        existing = await self.get_license(
            guild_id
        )

        if existing is None:

            return False

        async with self.pool.acquire() as connection:

            await connection.execute(
                """
                DELETE FROM licenses
                WHERE guild_id = $1
                """,
                guild_id
            )

        return True


    # =====================================================
    # OWNER
    # =====================================================

    def is_owner(
        self,
        interaction
    ):

        return (
            interaction.user.id
            == OWNER_ID
        )


    # =====================================================
    # LICENSE EMBED
    # =====================================================

    async def build_license_embed(
        self,
        guild_id
    ):

        license_data = await self.get_license(
            guild_id
        )

        if license_data is None:

            embed = discord.Embed(
                title="🔐 Misuki License",
                description=(
                    "This server does not have "
                    "a Misuki license."
                ),
                color=discord.Color.red()
            )

            embed.add_field(
                name="Server ID",
                value=f"`{guild_id}`",
                inline=False
            )

            return embed

        status = license_data["status"]

        expires_at = license_data["expires_at"]

        created_at = license_data["created_at"]

        license_key = license_data["license_key"]


        # -------------------------------------------------
        # CHECK EXPIRATION
        # -------------------------------------------------

        if (
            status == "active"
            and expires_at
        ):

            now = datetime.now(
                timezone.utc
            )

            if now >= expires_at:

                await self.set_expired(
                    guild_id
                )

                status = "expired"


        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        if status == "active":

            status_text = "🟢 Active"

            color = discord.Color.green()

        elif status == "expired":

            status_text = "🔴 Expired"

            color = discord.Color.red()

        elif status == "revoked":

            status_text = "⛔ Revoked"

            color = discord.Color.red()

        else:

            status_text = (
                f"⚪ {status.title()}"
            )

            color = discord.Color.orange()


        # -------------------------------------------------
        # EXPIRATION
        # -------------------------------------------------

        if expires_at:

            expiration_text = (
                f"<t:{int(expires_at.timestamp())}:F>"
            )

        else:

            expiration_text = "Never"


        # -------------------------------------------------
        # EMBED
        # -------------------------------------------------

        embed = discord.Embed(
            title="🔐 Misuki License",
            color=color
        )

        embed.add_field(
            name="Status",
            value=status_text,
            inline=True
        )

        embed.add_field(
            name="Expires",
            value=expiration_text,
            inline=True
        )

        embed.add_field(
            name="Server ID",
            value=f"`{guild_id}`",
            inline=False
        )

        embed.add_field(
            name="License Key",
            value=f"`{license_key}`",
            inline=False
        )

        embed.add_field(
            name="Created",
            value=(
                f"<t:{int(created_at.timestamp())}:F>"
            ),
            inline=False
        )

        embed.set_footer(
            text="Misuki • License System"
        )

        return embed


    # =====================================================
    # /LICENSE
    # =====================================================

    @app_commands.command(
        name="license",
        description="View the license of this server."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def license(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        embed = await self.build_license_embed(
            interaction.guild.id
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # =====================================================
    # /CREATELICENSE
    # =====================================================

    @app_commands.command(
        name="createlicense",
        description="Create a license for a server."
    )
    @app_commands.describe(
        server_id="ID of the server receiving the license.",
        days="Number of days the license remains active."
    )
    async def createlicense(
        self,
        interaction: discord.Interaction,
        server_id: str,
        days: app_commands.Range[int, 1, 3650]
    ):

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You are not authorized to create licenses.",
                ephemeral=True
            )

            return

        try:

            guild_id = int(
                server_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid Server ID.",
                ephemeral=True
            )

            return

        license_key = await self.create_license(
            guild_id,
            days
        )

        if license_key is None:

            await interaction.response.send_message(
                "❌ This server already has a license.",
                ephemeral=True
            )

            return

        guild = self.bot.get_guild(
            guild_id
        )

        server_name = (
            guild.name
            if guild
            else "Unknown / Bot not in server"
        )

        license_data = await self.get_license(
            guild_id
        )

        expiration = license_data["expires_at"]

        embed = discord.Embed(
            title="✅ License Created",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Server",
            value=server_name,
            inline=True
        )

        embed.add_field(
            name="Server ID",
            value=f"`{guild_id}`",
            inline=True
        )

        embed.add_field(
            name="Duration",
            value=f"{days} day(s)",
            inline=True
        )

        embed.add_field(
            name="License Key",
            value=f"`{license_key}`",
            inline=False
        )

        embed.add_field(
            name="Expires",
            value=(
                f"<t:{int(expiration.timestamp())}:F>"
            ),
            inline=False
        )

        embed.set_footer(
            text="Misuki • License System"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # =====================================================
    # /REVOKELICENSE
    # =====================================================

    @app_commands.command(
        name="revokelicense",
        description="Revoke a server license."
    )
    @app_commands.describe(
        server_id="ID of the server."
    )
    async def revokelicense(
        self,
        interaction: discord.Interaction,
        server_id: str
    ):

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You are not authorized to revoke licenses.",
                ephemeral=True
            )

            return

        try:

            guild_id = int(
                server_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid Server ID.",
                ephemeral=True
            )

            return

        success = await self.revoke_license(
            guild_id
        )

        if not success:

            await interaction.response.send_message(
                "❌ This server does not have a license.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "⛔ **License revoked.**\n\n"
                f"Server ID: `{guild_id}`\n\n"
                "All premium functionality is now blocked."
            ),
            ephemeral=True
        )


    # =====================================================
    # /EXTENDLICENSE
    # =====================================================

    @app_commands.command(
        name="extendlicense",
        description="Extend a server license."
    )
    @app_commands.describe(
        server_id="ID of the server.",
        days="Number of days to add."
    )
    async def extendlicense(
        self,
        interaction: discord.Interaction,
        server_id: str,
        days: app_commands.Range[int, 1, 3650]
    ):

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You are not authorized to extend licenses.",
                ephemeral=True
            )

            return

        try:

            guild_id = int(
                server_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid Server ID.",
                ephemeral=True
            )

            return

        success = await self.extend_license(
            guild_id,
            days
        )

        if not success:

            await interaction.response.send_message(
                (
                    "❌ The license cannot be extended.\n\n"
                    "It may be missing, expired, or revoked."
                ),
                ephemeral=True
            )

            return

        license_data = await self.get_license(
            guild_id
        )

        expiration = license_data["expires_at"]

        await interaction.response.send_message(
            (
                f"✅ License extended by **{days} days**.\n\n"
                f"Server ID: `{guild_id}`\n"
                f"New expiration: "
                f"<t:{int(expiration.timestamp())}:F>"
            ),
            ephemeral=True
        )


    # =====================================================
    # /DELETELICENSE
    # =====================================================

    @app_commands.command(
        name="deletelicense",
        description="Delete a server license completely."
    )
    @app_commands.describe(
        server_id="ID of the server."
    )
    async def deletelicense(
        self,
        interaction: discord.Interaction,
        server_id: str
    ):

        if not self.is_owner(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You are not authorized to delete licenses.",
                ephemeral=True
            )

            return

        try:

            guild_id = int(
                server_id
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ Invalid Server ID.",
                ephemeral=True
            )

            return

        success = await self.delete_license(
            guild_id
        )

        if not success:

            await interaction.response.send_message(
                "❌ This server does not have a license.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "🗑️ **License deleted.**\n\n"
                f"Server ID: `{guild_id}`\n\n"
                "A completely new license can now "
                "be created for this server."
            ),
            ephemeral=True
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot):

    cog = LicenseManager(
        bot
    )

    await bot.add_cog(
        cog
    )

    print(
        "🔐 LicenseManager carregado."
    )

    commands_list = (
        cog.get_app_commands()
    )

    print(
        f"🔐 Comandos do LicenseManager: "
        f"{len(commands_list)}"
    )

    for command in commands_list:

        print(
            f"   /{command.name}"
        )