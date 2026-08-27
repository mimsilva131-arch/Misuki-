
import os
import sqlite3
import secrets

from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

DATABASE = os.path.join(
    DATA_DIR,
    "misuki.db"
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

        self.create_database()

    # =====================================================
    # DATABASE
    # =====================================================

    def create_database(self):

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS licenses (

                    guild_id INTEGER PRIMARY KEY,

                    license_key TEXT UNIQUE NOT NULL,

                    status TEXT NOT NULL
                    DEFAULT 'active',

                    expires_at TEXT,

                    created_at TEXT NOT NULL

                )
            """)

            connection.commit()

    # =====================================================
    # GENERATE KEY
    # =====================================================

    def generate_license_key(self):

        while True:

            parts = [
                secrets.token_hex(4).upper(),
                secrets.token_hex(4).upper(),
                secrets.token_hex(4).upper(),
                secrets.token_hex(4).upper()
            ]

            key = "MISUKI-" + "-".join(parts)

            with sqlite3.connect(DATABASE) as connection:

                result = connection.execute(
                    """
                    SELECT 1
                    FROM licenses
                    WHERE license_key = ?
                    """,
                    (key,)
                ).fetchone()

            if result is None:

                return key

    # =====================================================
    # GET LICENSE
    # =====================================================

    def get_license(self, guild_id):

        with sqlite3.connect(DATABASE) as connection:

            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    guild_id,
                    license_key,
                    status,
                    expires_at,
                    created_at
                FROM licenses
                WHERE guild_id = ?
            """, (
                guild_id,
            ))

            return cursor.fetchone()

    # =====================================================
    # ACTIVE LICENSE
    # =====================================================

    def has_active_license(self, guild_id):

        license_data = self.get_license(
            guild_id
        )

        if license_data is None:
            return False

        status = license_data[2]
        expires_at = license_data[3]

        if status != "active":
            return False

        if not expires_at:
            return True

        try:

            expiration = datetime.fromisoformat(
                expires_at
            )

        except ValueError:

            return False

        if datetime.now() >= expiration:

            self.set_expired(
                guild_id
            )

            return False

        return True

    # =====================================================
    # EXPIRE
    # =====================================================

    def set_expired(self, guild_id):

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                UPDATE licenses
                SET status = 'expired'
                WHERE guild_id = ?
            """, (
                guild_id,
            ))

            connection.commit()

    # =====================================================
    # CREATE
    # =====================================================

    def create_license(
        self,
        guild_id,
        days
    ):

        existing = self.get_license(
            guild_id
        )

        if existing:

            return None

        created_at = datetime.now()

        expires_at = (
            created_at
            + timedelta(days=days)
        )

        license_key = (
            self.generate_license_key()
        )

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                INSERT INTO licenses
                (
                    guild_id,
                    license_key,
                    status,
                    expires_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                guild_id,
                license_key,
                "active",
                expires_at.isoformat(),
                created_at.isoformat()
            ))

            connection.commit()

        return license_key

    # =====================================================
    # REVOKE
    # =====================================================

    def revoke_license(self, guild_id):

        existing = self.get_license(
            guild_id
        )

        if existing is None:
            return False

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                UPDATE licenses
                SET status = 'revoked'
                WHERE guild_id = ?
            """, (
                guild_id,
            ))

            connection.commit()

        return True

    # =====================================================
    # EXTEND
    # =====================================================

    def extend_license(
        self,
        guild_id,
        days
    ):

        existing = self.get_license(
            guild_id
        )

        if existing is None:
            return False

        status = existing[2]
        expires_at = existing[3]

        if status != "active":
            return False

        if not expires_at:
            return False

        try:

            expiration = datetime.fromisoformat(
                expires_at
            )

        except ValueError:

            return False

        if datetime.now() >= expiration:

            self.set_expired(
                guild_id
            )

            return False

        new_expiration = (
            expiration
            + timedelta(days=days)
        )

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                UPDATE licenses
                SET expires_at = ?
                WHERE guild_id = ?
            """, (
                new_expiration.isoformat(),
                guild_id
            ))

            connection.commit()

        return True

    # =====================================================
    # DELETE
    # =====================================================

    def delete_license(self, guild_id):

        existing = self.get_license(
            guild_id
        )

        if existing is None:
            return False

        with sqlite3.connect(DATABASE) as connection:

            connection.execute("""
                DELETE FROM licenses
                WHERE guild_id = ?
            """, (
                guild_id,
            ))

            connection.commit()

        return True

    # =====================================================
    # OWNER
    # =====================================================

    def is_owner(self, interaction):

        return (
            interaction.user.id
            == OWNER_ID
        )

    # =====================================================
    # LICENSE EMBED
    # =====================================================

    def build_license_embed(
        self,
        guild_id
    ):

        license_data = self.get_license(
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

        (
            stored_guild_id,
            license_key,
            status,
            expires_at,
            created_at
        ) = license_data

        # -------------------------------------------------
        # CHECK EXPIRATION
        # -------------------------------------------------

        if status == "active" and expires_at:

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                if datetime.now() >= expiration:

                    self.set_expired(
                        guild_id
                    )

                    status = "expired"

            except ValueError:

                status = "invalid"

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

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

                expiration_text = (
                    f"<t:{int(expiration.timestamp())}:F>"
                )

            except ValueError:

                expiration_text = expires_at

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
            value=created_at,
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

        embed = self.build_license_embed(
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

        license_key = self.create_license(
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

        license_data = self.get_license(
            guild_id
        )

        expiration = datetime.fromisoformat(
            license_data[3]
        )

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

        success = self.revoke_license(
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

        success = self.extend_license(
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

        license_data = self.get_license(
            guild_id
        )

        expiration = datetime.fromisoformat(
            license_data[3]
        )

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

        success = self.delete_license(
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

