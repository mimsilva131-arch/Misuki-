# =========================================================
# MISUKI - VERIFICATION SYSTEM
# =========================================================

import os
import time
import asyncio

import discord
import psycopg2

from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

SITE_URL = os.getenv(
    "MISUKI_SITE_URL"
)


# =========================================================
# DATABASE
# =========================================================

def get_database_connection():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL não está configurado."
        )

    return psycopg2.connect(
        DATABASE_URL,
        connect_timeout=10
    )


# =========================================================
# VERIFICATION COG
# =========================================================

class Verification(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.verification_task = None

        self.initialize_database()

    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    def initialize_database(self):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_requests (

                        id BIGSERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        user_id BIGINT NOT NULL,

                        username TEXT,

                        status TEXT NOT NULL DEFAULT 'pending',

                        created_at DOUBLE PRECISION NOT NULL,

                        processed_at DOUBLE PRECISION,

                        UNIQUE (
                            guild_id,
                            user_id
                        )
                    )
                    """
                )

            connection.commit()

            print(
                "🔐 Verification database initialized."
            )

        except Exception as error:

            if connection:
                connection.rollback()

            print(
                f"❌ Error initializing verification database: {error}"
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # CONFIG HELPERS
    # =====================================================

    def get_config_cog(self):

        return self.bot.get_cog(
            "Config"
        )

    # =====================================================
    # GET VERIFIED ROLE
    # =====================================================

    def get_verified_role(
        self,
        guild
    ):

        config = self.get_config_cog()

        if config is None:

            return None

        role_ids = config.get_roles(
            guild.id,
            "verified"
        )

        if not role_ids:

            return None

        # -------------------------------------------------
        # The existing config system allows multiple roles.
        # Verification uses the first configured role.
        # -------------------------------------------------

        role_id = role_ids[0]

        return guild.get_role(
            int(role_id)
        )

    # =====================================================
    # GET VERIFICATION CHANNEL
    # =====================================================

    def get_verification_channel(
        self,
        guild
    ):

        config = self.get_config_cog()

        if config is None:

            return None

        channel_id = config.get_channel_value(
            guild.id,
            "verification_channel_id"
        )

        if not channel_id:

            return None

        return guild.get_channel(
            int(channel_id)
        )

    # =====================================================
    # GET VERIFIED LOG CHANNEL
    # =====================================================

    def get_verified_log_channel(
        self,
        guild
    ):

        config = self.get_config_cog()

        if config is None:

            return None

        channel_id = config.get_channel_value(
            guild.id,
            "verified_log_channel_id"
        )

        if not channel_id:

            return None

        return guild.get_channel(
            int(channel_id)
        )

    # =====================================================
    # GET UNVERIFIED LOG CHANNEL
    # =====================================================

    def get_unverified_log_channel(
        self,
        guild
    ):

        config = self.get_config_cog()

        if config is None:

            return None

        channel_id = config.get_channel_value(
            guild.id,
            "unverified_log_channel_id"
        )

        if not channel_id:

            return None

        return guild.get_channel(
            int(channel_id)
        )

    # =====================================================
    # BUILD VERIFICATION URL
    # =====================================================

    def get_verification_url(
        self,
        guild_id
    ):

        if not SITE_URL:

            return None

        return (
            f"{SITE_URL.rstrip('/')}"
            f"/verify?guild_id={guild_id}"
        )

    # =====================================================
    # BUILD PANEL
    # =====================================================

    def create_verification_embed(
        self,
        guild
    ):

        embed = discord.Embed(

            title="🔐 Server Verification",

            description=(
                "To access this server, "
                "you must verify your Discord account.\n\n"
                "Click the button below to begin "
                "the verification process."
            ),

            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Misuki Verification"
        )

        return embed

    # =====================================================
    # SEND VERIFICATION PANEL
    # =====================================================

    async def send_verification_panel(
        self,
        guild
    ):

        channel = self.get_verification_channel(
            guild
        )

        if channel is None:

            return (
                False,
                "❌ No Verification Channel is configured."
            )

        if not SITE_URL:

            return (
                False,
                "❌ MISUKI_SITE_URL is not configured."
            )

        verification_url = self.get_verification_url(
            guild.id
        )

        if not verification_url:

            return (
                False,
                "❌ Could not create the verification URL."
            )

        embed = self.create_verification_embed(
            guild
        )

        view = VerificationPanelView(
            verification_url
        )

        try:

            message = await channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            return (
                False,
                "❌ I don't have permission to send messages in the Verification Channel."
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error sending verification panel: {error}"
            )

            return (
                False,
                "❌ Discord rejected the verification panel."
            )

        # -------------------------------------------------
        # Store panel message ID
        # -------------------------------------------------

        self.save_panel_message(
            guild.id,
            channel.id,
            message.id
        )

        return (
            True,
            message
        )

    # =====================================================
    # PANEL MESSAGE DATABASE
    # =====================================================

    def create_panel_table(self):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS verification_panels (

                        guild_id BIGINT PRIMARY KEY,

                        channel_id BIGINT NOT NULL,

                        message_id BIGINT NOT NULL,

                        updated_at DOUBLE PRECISION NOT NULL
                    )
                    """
                )

            connection.commit()

        except Exception as error:

            if connection:
                connection.rollback()

            print(
                f"❌ Error creating verification panel table: {error}"
            )

        finally:

            if connection:
                connection.close()

    def save_panel_message(
        self,
        guild_id,
        channel_id,
        message_id
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO verification_panels (
                        guild_id,
                        channel_id,
                        message_id,
                        updated_at
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    )

                    ON CONFLICT (guild_id)
                    DO UPDATE SET
                        channel_id = EXCLUDED.channel_id,
                        message_id = EXCLUDED.message_id,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        guild_id,
                        channel_id,
                        message_id,
                        time.time()
                    )
                )

            connection.commit()

        except Exception as error:

            if connection:
                connection.rollback()

            print(
                f"❌ Error saving verification panel: {error}"
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # GET PENDING VERIFICATIONS
    # =====================================================

    def get_pending_verifications(self):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        guild_id,
                        user_id,
                        username
                    FROM verification_requests
                    WHERE status = 'pending'
                    ORDER BY id ASC
                    LIMIT 25
                    """
                )

                rows = cursor.fetchall()

            return rows

        except Exception as error:

            print(
                f"❌ Error reading verification requests: {error}"
            )

            return []

        finally:

            if connection:
                connection.close()

    # =====================================================
    # MARK VERIFICATION AS PROCESSED
    # =====================================================

    def update_verification_status(
        self,
        request_id,
        status
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE verification_requests

                    SET
                        status = %s,
                        processed_at = %s

                    WHERE id = %s
                    """,
                    (
                        status,
                        time.time(),
                        request_id
                    )
                )

            connection.commit()

        except Exception as error:

            if connection:
                connection.rollback()

            print(
                f"❌ Error updating verification request: {error}"
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # VERIFICATION LOG
    # =====================================================

    async def send_verification_log(
        self,
        guild,
        member,
        username,
        success=True,
        reason=None
    ):

        if success:

            channel = self.get_verified_log_channel(
                guild
            )

            if channel is None:

                return

            embed = discord.Embed(

                title="✅ User Verified",

                description=(
                    f"{member.mention} has successfully "
                    "completed verification."
                ),

                color=discord.Color.green(),

                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="User",
                value=(
                    f"{member.mention}\n"
                    f"`{member.id}`"
                ),
                inline=True
            )

            embed.add_field(
                name="Username",
                value=(
                    username
                    or member.name
                ),
                inline=True
            )

            role = self.get_verified_role(
                guild
            )

            if role:

                embed.add_field(
                    name="Role",
                    value=role.mention,
                    inline=True
                )

            embed.set_footer(
                text="Misuki Verification"
            )

        else:

            channel = self.get_unverified_log_channel(
                guild
            )

            if channel is None:

                return

            embed = discord.Embed(

                title="❌ Verification Failed",

                description=(
                    f"Verification failed for "
                    f"<@{member.id}>."
                ),

                color=discord.Color.red(),

                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="User",
                value=(
                    f"<@{member.id}>\n"
                    f"`{member.id}`"
                ),
                inline=True
            )

            if reason:

                embed.add_field(
                    name="Reason",
                    value=reason,
                    inline=False
                )

            embed.set_footer(
                text="Misuki Verification"
            )

        try:

            await channel.send(
                embed=embed
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error sending verification log: {error}"
            )

    # =====================================================
    # PROCESS VERIFICATION
    # =====================================================

    async def process_verification(
        self,
        request_id,
        guild_id,
        user_id,
        username
    ):

        guild = self.bot.get_guild(
            int(guild_id)
        )

        if guild is None:

            self.update_verification_status(
                request_id,
                "guild_unavailable"
            )

            return

        member = guild.get_member(
            int(user_id)
        )

        if member is None:

            try:

                member = await guild.fetch_member(
                    int(user_id)
                )

            except discord.NotFound:

                self.update_verification_status(
                    request_id,
                    "member_not_found"
                )

                return

            except discord.HTTPException as error:

                print(
                    f"❌ Error fetching member {user_id}: {error}"
                )

                return

        role = self.get_verified_role(
            guild
        )

        if role is None:

            print(
                f"❌ No Verified Role configured in {guild.name}."
            )

            await self.send_verification_log(
                guild,
                member,
                username,
                success=False,
                reason="No Verified Role is configured."
            )

            self.update_verification_status(
                request_id,
                "no_role"
            )

            return

        # -------------------------------------------------
        # Already verified
        # -------------------------------------------------

        if role in member.roles:

            self.update_verification_status(
                request_id,
                "already_verified"
            )

            return

        # -------------------------------------------------
        # Check bot permissions / hierarchy
        # -------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            self.update_verification_status(
                request_id,
                "bot_member_unavailable"
            )

            return

        if not bot_member.guild_permissions.manage_roles:

            print(
                f"❌ Missing Manage Roles permission in {guild.name}."
            )

            await self.send_verification_log(
                guild,
                member,
                username,
                success=False,
                reason="The bot does not have Manage Roles permission."
            )

            self.update_verification_status(
                request_id,
                "missing_manage_roles"
            )

            return

        if role >= bot_member.top_role:

            print(
                f"❌ Verified Role is above the bot's highest role "
                f"in {guild.name}."
            )

            await self.send_verification_log(
                guild,
                member,
                username,
                success=False,
                reason=(
                    "The Verified Role is above or equal to "
                    "the bot's highest role."
                )
            )

            self.update_verification_status(
                request_id,
                "role_hierarchy"
            )

            return

        # -------------------------------------------------
        # Add role
        # -------------------------------------------------

        try:

            await member.add_roles(
                role,
                reason="Miskui verification completed."
            )

        except discord.Forbidden:

            await self.send_verification_log(
                guild,
                member,
                username,
                success=False,
                reason=(
                    "Discord denied the role assignment."
                )
            )

            self.update_verification_status(
                request_id,
                "forbidden"
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error assigning verification role: {error}"
            )

            self.update_verification_status(
                request_id,
                "discord_error"
            )

            return

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        self.update_verification_status(
            request_id,
            "verified"
        )

        await self.send_verification_log(
            guild,
            member,
            username,
            success=True
        )

        print(
            f"✅ Verified {member} in {guild.name}"
        )

    # =====================================================
    # VERIFICATION WORKER
    # =====================================================

    async def verification_worker(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            try:

                requests = (
                    self.get_pending_verifications()
                )

                for request in requests:

                    (
                        request_id,
                        guild_id,
                        user_id,
                        username
                    ) = request

                    await self.process_verification(
                        request_id,
                        guild_id,
                        user_id,
                        username
                    )

            except Exception as error:

                print(
                    f"❌ Verification worker error: {error}"
                )

            await asyncio.sleep(
                5
            )

    # =====================================================
    # START WORKER
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(self):

        if self.verification_task is None:

            self.verification_task = (
                asyncio.create_task(
                    self.verification_worker()
                )
            )

            print(
                "🔐 Verification worker started."
            )

    # =====================================================
    # /VERIFY
    # =====================================================

    @app_commands.command(
        name="verify",
        description="Send the verification panel."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def verify_command(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # Configuration
        # -------------------------------------------------

        config = self.get_config_cog()

        if config is None:

            await interaction.response.send_message(
                "❌ The configuration system is unavailable.",
                ephemeral=True
            )

            return

        verification_channel = (
            self.get_verification_channel(
                interaction.guild
            )
        )

        verified_role = (
            self.get_verified_role(
                interaction.guild
            )
        )

        if verification_channel is None:

            await interaction.response.send_message(
                (
                    "❌ **Verification Channel** is not configured.\n\n"
                    "Go to `/setup` → **Verification** "
                    "and select the channel."
                ),
                ephemeral=True
            )

            return

        if verified_role is None:

            await interaction.response.send_message(
                (
                    "❌ **Verified Role** is not configured.\n\n"
                    "Go to `/setup` → **Verification** "
                    "and select the role."
                ),
                ephemeral=True
            )

            return

        if not SITE_URL:

            await interaction.response.send_message(
                (
                    "❌ `MISUKI_SITE_URL` is not configured "
                    "on the bot."
                ),
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        success, result = (
            await self.send_verification_panel(
                interaction.guild
            )
        )

        if not success:

            await interaction.followup.send(
                result,
                ephemeral=True
            )

            return

        await interaction.followup.send(
            (
                "✅ Verification panel sent to "
                f"{verification_channel.mention}."
            ),
            ephemeral=True
        )


# =========================================================
# VERIFICATION PANEL VIEW
# =========================================================

class VerificationPanelView(
    discord.ui.View
):

    def __init__(
        self,
        verification_url
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            VerificationButton(
                verification_url
            )
        )


# =========================================================
# VERIFICATION BUTTON
# =========================================================

class VerificationButton(
    discord.ui.Button
):

    def __init__(
        self,
        verification_url
    ):

        super().__init__(
            label="Verify",
            emoji="🔐",
            style=discord.ButtonStyle.link,
            url=verification_url
        )


# =========================================================
# LOAD COG
# =========================================================

async def setup(
    bot
):

    cog = Verification(
        bot
    )

    cog.create_panel_table()

    await bot.add_cog(
        cog
    )