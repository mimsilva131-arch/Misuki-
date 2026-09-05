import asyncio
import json
import re
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks


# =========================================================
# DATABASE
# =========================================================

DATABASE = "data/misuki.db"


# =========================================================
# JAIL
# =========================================================

class Jail(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.create_database()

        self.jail_expiration_worker.start()

    def cog_unload(self):

        self.jail_expiration_worker.cancel()

    # =====================================================
    # DATABASE
    # =====================================================

    def create_database(self):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jail_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id INTEGER NOT NULL,

                user_id INTEGER NOT NULL,

                moderator_id INTEGER NOT NULL,

                reason TEXT,

                jailed_at TEXT NOT NULL,

                expires_at TEXT,

                previous_roles TEXT NOT NULL,

                active INTEGER NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_jail_active
            ON jail_records (
                guild_id,
                user_id,
                active
            )
        """)

        connection.commit()

        connection.close()

    # =====================================================
    # CONFIG
    # =====================================================

    def get_config_cog(self):

        return self.bot.get_cog(
            "Config"
        )

    def get_jailed_role_ids(
        self,
        guild_id
    ):

        config = self.get_config_cog()

        if config is None:
            return []

        return config.get_roles(
            guild_id,
            "jailed"
        )

    def get_jail_log_channel_id(
        self,
        guild_id
    ):

        config = self.get_config_cog()

        if config is None:
            return None

        return config.get_channel_value(
            guild_id,
            "jail_log_channel_id"
        )

    # =====================================================
    # ACTIVE RECORD
    # =====================================================

    def get_active_record(
        self,
        guild_id,
        user_id
    ):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                guild_id,
                user_id,
                moderator_id,
                reason,
                jailed_at,
                expires_at,
                previous_roles,
                active

            FROM jail_records

            WHERE guild_id = ?
            AND user_id = ?
            AND active = 1

            ORDER BY id DESC

            LIMIT 1
        """, (
            guild_id,
            user_id
        ))

        result = cursor.fetchone()

        connection.close()

        return result

    # =====================================================
    # SAVE RECORD
    # =====================================================

    def create_jail_record(
        self,
        guild_id,
        user_id,
        moderator_id,
        reason,
        expires_at,
        previous_roles
    ):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO jail_records
            (
                guild_id,
                user_id,
                moderator_id,
                reason,
                jailed_at,
                expires_at,
                previous_roles,
                active
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            guild_id,
            user_id,
            moderator_id,
            reason,
            datetime.now(
                timezone.utc
            ).isoformat(),
            (
                expires_at.isoformat()
                if expires_at
                else None
            ),
            json.dumps(
                previous_roles
            )
        ))

        record_id = cursor.lastrowid

        connection.commit()

        connection.close()

        return record_id

    # =====================================================
    # CLOSE RECORD
    # =====================================================

    def close_record(
        self,
        record_id
    ):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE jail_records

            SET active = 0

            WHERE id = ?
        """, (
            record_id,
        ))

        connection.commit()

        connection.close()

    # =====================================================
    # PARSE DURATION
    # =====================================================

    def parse_duration(
        self,
        value
    ):

        if not value:
            return None

        value = value.lower().strip()

        if value in (
            "permanent",
            "perm",
            "perma",
            "forever"
        ):
            return None

        match = re.fullmatch(
            r"(\d+)\s*(s|m|h|d|w)",
            value
        )

        if not match:
            return False

        amount = int(
            match.group(1)
        )

        unit = match.group(2)

        if amount <= 0:
            return False

        if unit == "s":
            delta = timedelta(
                seconds=amount
            )

        elif unit == "m":
            delta = timedelta(
                minutes=amount
            )

        elif unit == "h":
            delta = timedelta(
                hours=amount
            )

        elif unit == "d":
            delta = timedelta(
                days=amount
            )

        elif unit == "w":
            delta = timedelta(
                weeks=amount
            )

        else:
            return False

        return datetime.now(
            timezone.utc
        ) + delta

    # =====================================================
    # PERMISSION CHECK
    # =====================================================

    def has_staff_role(
        self,
        member
    ):

        config = self.get_config_cog()

        if config is None:
            return False

        staff_roles = config.get_roles(
            member.guild.id,
            "staff"
        )

        if not staff_roles:
            return False

        return any(
            role.id in staff_roles
            for role in member.roles
        )

    # =====================================================
    # HIERARCHY
    # =====================================================

    def can_manage_member(
        self,
        interaction,
        member
    ):

        guild = interaction.guild

        if guild is None:
            return False

        moderator = interaction.user

        if member.id == moderator.id:
            return False

        if member.id == guild.owner_id:
            return False

        if moderator.id != guild.owner_id:

            if member.top_role >= moderator.top_role:
                return False

        bot_member = guild.me

        if bot_member is None:
            return False

        if member.top_role >= bot_member.top_role:
            return False

        return True

    # =====================================================
    # GET JAILED ROLE
    # =====================================================

    def get_jailed_role(
        self,
        guild
    ):

        role_ids = self.get_jailed_role_ids(
            guild.id
        )

        if not role_ids:
            return None

        for role_id in role_ids:

            role = guild.get_role(
                int(role_id)
            )

            if role:
                return role

        return None

    # =====================================================
    # REMOVE MANAGEABLE ROLES
    # =====================================================

    def get_previous_roles(
        self,
        guild,
        member,
        jailed_role
    ):

        bot_member = guild.me

        if bot_member is None:
            return []

        previous_roles = []

        for role in member.roles:

            if role.is_default():
                continue

            if role.id == jailed_role.id:
                continue

            if role >= bot_member.top_role:
                continue

            previous_roles.append(
                role.id
            )

        return previous_roles

    # =====================================================
    # APPLY JAIL
    # =====================================================

    async def apply_jail(
        self,
        member,
        jailed_role
    ):

        guild = member.guild

        bot_member = guild.me

        if bot_member is None:
            return False, []

        previous_roles = self.get_previous_roles(
            guild,
            member,
            jailed_role
        )

        roles_to_remove = []

        for role in member.roles:

            if role.is_default():
                continue

            if role.id == jailed_role.id:
                continue

            if role >= bot_member.top_role:
                continue

            roles_to_remove.append(
                role
            )

        if roles_to_remove:

            try:

                await member.remove_roles(
                    *roles_to_remove,
                    reason="Misuki Jail"
                )

            except discord.HTTPException:

                return False, previous_roles

        if jailed_role not in member.roles:

            try:

                await member.add_roles(
                    jailed_role,
                    reason="Misuki Jail"
                )

            except discord.HTTPException:

                return False, previous_roles

        return True, previous_roles

    # =====================================================
    # RESTORE ROLES
    # =====================================================

    async def restore_roles(
        self,
        member,
        role_ids
    ):

        guild = member.guild

        bot_member = guild.me

        if bot_member is None:
            return []

        roles = []

        for role_id in role_ids:

            role = guild.get_role(
                int(role_id)
            )

            if role is None:
                continue

            if role.is_default():
                continue

            if role >= bot_member.top_role:
                continue

            roles.append(
                role
            )

        restored = []

        if roles:

            try:

                await member.add_roles(
                    *roles,
                    reason="Misuki Unjail"
                )

                restored = [
                    role.id
                    for role in roles
                ]

            except discord.HTTPException:
                pass

        return restored

    # =====================================================
    # REMOVE JAIL ROLE
    # =====================================================

    async def remove_jail_role(
        self,
        member,
        jailed_role
    ):

        if jailed_role not in member.roles:
            return True

        try:

            await member.remove_roles(
                jailed_role,
                reason="Misuki Unjail"
            )

            return True

        except discord.HTTPException:

            return False

    # =====================================================
    # LOG
    # =====================================================

    async def send_jail_log(
        self,
        guild,
        title,
        color,
        member,
        moderator=None,
        reason=None,
        duration=None,
        action=None
    ):

        channel_id = self.get_jail_log_channel_id(
            guild.id
        )

        if not channel_id:
            return

        channel = guild.get_channel(
            int(channel_id)
        )

        if channel is None:
            return

        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.add_field(
            name="User",
            value=(
                f"{member.mention}\n"
                f"`{member.id}`"
            ),
            inline=False
        )

        if moderator:

            embed.add_field(
                name="Moderator",
                value=(
                    f"{moderator.mention}\n"
                    f"`{moderator.id}`"
                ),
                inline=True
            )

        if action:

            embed.add_field(
                name="Action",
                value=action,
                inline=True
            )

        if duration:

            embed.add_field(
                name="Duration",
                value=duration,
                inline=True
            )

        if reason:

            embed.add_field(
                name="Reason",
                value=reason[:1024],
                inline=False
            )

        embed.set_footer(
            text="Misuki • Jail System"
        )

        try:

            await channel.send(
                embed=embed
            )

        except discord.HTTPException:

            pass

    # =====================================================
    # /JAIL
    # =====================================================

    @app_commands.command(
        name="jail",
        description="Jail a member."
    )
    @app_commands.describe(
        member="The member to jail.",
        duration="Duration: 10m, 1h, 1d, 7d or permanent.",
        reason="Reason for the jail."
    )
    async def jail_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: str = "permanent",
        reason: str = "No reason provided."
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # STAFF
        # -------------------------------------------------

        if not self.has_staff_role(
            interaction.user
        ) and interaction.user.id != guild.owner_id:

            await interaction.followup.send(
                "❌ You do not have the configured Staff Role.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # JAILED ROLE
        # -------------------------------------------------

        jailed_role = self.get_jailed_role(
            guild
        )

        if jailed_role is None:

            await interaction.followup.send(
                "❌ No Jailed Role is configured. "
                "Use `/setup` → Jail → Jailed Role.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # BOT HIERARCHY
        # -------------------------------------------------

        bot_member = guild.me

        if bot_member is None:

            await interaction.followup.send(
                "❌ I could not determine my server permissions.",
                ephemeral=True
            )

            return

        if jailed_role >= bot_member.top_role:

            await interaction.followup.send(
                "❌ My highest role must be above the Jailed Role.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # MEMBER HIERARCHY
        # -------------------------------------------------

        if not self.can_manage_member(
            interaction,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot jail this member because of the role hierarchy.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # ALREADY JAILED
        # -------------------------------------------------

        existing = self.get_active_record(
            guild.id,
            member.id
        )

        if existing:

            await interaction.followup.send(
                "❌ This member is already jailed.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # DURATION
        # -------------------------------------------------

        expires_at = self.parse_duration(
            duration
        )

        if expires_at is False:

            await interaction.followup.send(
                "❌ Invalid duration.\n\n"
                "Examples: `10m`, `1h`, `6h`, `1d`, `7d`, `2w`, `permanent`.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        success, previous_roles = await self.apply_jail(
            member,
            jailed_role
        )

        if not success:

            await interaction.followup.send(
                "❌ I could not apply the Jail Role. "
                "Check my permissions and role hierarchy.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        record_id = self.create_jail_record(
            guild.id,
            member.id,
            interaction.user.id,
            reason,
            expires_at,
            previous_roles
        )

        # -------------------------------------------------
        # DURATION TEXT
        # -------------------------------------------------

        if expires_at:

            duration_text = (
                f"<t:{int(expires_at.timestamp())}:R>"
            )

        else:

            duration_text = "Permanent"

        # -------------------------------------------------
        # LOG
        # -------------------------------------------------

        await self.send_jail_log(
            guild,
            "⛓️ Member Jailed",
            discord.Color.red(),
            member,
            interaction.user,
            reason,
            duration_text,
            "Jail"
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        embed = discord.Embed(
            title="⛓️ Member Jailed",
            description=(
                f"{member.mention} has been jailed."
            ),
            color=discord.Color.red()
        )

        embed.add_field(
            name="Reason",
            value=reason[:1024],
            inline=False
        )

        embed.add_field(
            name="Duration",
            value=duration_text,
            inline=True
        )

        embed.add_field(
            name="Moderator",
            value=interaction.user.mention,
            inline=True
        )

        embed.set_footer(
            text=f"Jail ID: {record_id}"
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # /UNJAIL
    # =====================================================

    @app_commands.command(
        name="unjail",
        description="Release a member from jail."
    )
    @app_commands.describe(
        member="The member to release."
    )
    async def unjail_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # STAFF
        # -------------------------------------------------

        if not self.has_staff_role(
            interaction.user
        ) and interaction.user.id != guild.owner_id:

            await interaction.followup.send(
                "❌ You do not have the configured Staff Role.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # RECORD
        # -------------------------------------------------

        record = self.get_active_record(
            guild.id,
            member.id
        )

        if record is None:

            await interaction.followup.send(
                "❌ This member is not currently jailed.",
                ephemeral=True
            )

            return

        (
            record_id,
            guild_id,
            user_id,
            moderator_id,
            reason,
            jailed_at,
            expires_at,
            previous_roles_json,
            active
        ) = record

        # -------------------------------------------------
        # JAILED ROLE
        # -------------------------------------------------

        jailed_role = self.get_jailed_role(
            guild
        )

        if jailed_role:

            removed = await self.remove_jail_role(
                member,
                jailed_role
            )

            if not removed:

                await interaction.followup.send(
                    "❌ I could not remove the Jailed Role. "
                    "Check my permissions and role hierarchy.",
                    ephemeral=True
                )

                return

        # -------------------------------------------------
        # RESTORE
        # -------------------------------------------------

        try:

            previous_roles = json.loads(
                previous_roles_json
            )

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError
        ):

            previous_roles = []

        await self.restore_roles(
            member,
            previous_roles
        )

        # -------------------------------------------------
        # CLOSE
        # -------------------------------------------------

        self.close_record(
            record_id
        )

        # -------------------------------------------------
        # LOG
        # -------------------------------------------------

        await self.send_jail_log(
            guild,
            "🔓 Member Unjailed",
            discord.Color.green(),
            member,
            interaction.user,
            reason,
            None,
            "Unjail"
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        embed = discord.Embed(
            title="🔓 Member Unjailed",
            description=(
                f"{member.mention} has been released from jail."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="Original Reason",
            value=(
                reason[:1024]
                if reason
                else "No reason provided."
            ),
            inline=False
        )

        embed.add_field(
            name="Moderator",
            value=interaction.user.mention,
            inline=True
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # /JAILINFO
    # =====================================================

    @app_commands.command(
        name="jailinfo",
        description="View information about a member's jail."
    )
    @app_commands.describe(
        member="The member to inspect."
    )
    async def jailinfo_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        record = self.get_active_record(
            interaction.guild.id,
            member.id
        )

        if record is None:

            await interaction.response.send_message(
                f"ℹ️ {member.mention} is not currently jailed.",
                ephemeral=True
            )

            return

        (
            record_id,
            guild_id,
            user_id,
            moderator_id,
            reason,
            jailed_at,
            expires_at,
            previous_roles_json,
            active
        ) = record

        embed = discord.Embed(
            title="⛓️ Jail Information",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="User",
            value=(
                f"{member.mention}\n"
                f"`{member.id}`"
            ),
            inline=False
        )

        embed.add_field(
            name="Moderator",
            value=f"<@{moderator_id}>",
            inline=True
        )

        embed.add_field(
            name="Reason",
            value=(
                reason[:1024]
                if reason
                else "No reason provided."
            ),
            inline=False
        )

        if expires_at:

            try:

                expiry = datetime.fromisoformat(
                    expires_at
                )

                expiry_timestamp = int(
                    expiry.timestamp()
                )

                expiration_text = (
                    f"<t:{expiry_timestamp}:F>\n"
                    f"<t:{expiry_timestamp}:R>"
                )

            except ValueError:

                expiration_text = expires_at

        else:

            expiration_text = "Permanent"

        embed.add_field(
            name="Expires",
            value=expiration_text,
            inline=True
        )

        embed.add_field(
            name="Jail ID",
            value=f"`{record_id}`",
            inline=True
        )

        try:

            previous_roles = json.loads(
                previous_roles_json
            )

            role_count = len(
                previous_roles
            )

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError
        ):

            role_count = 0

        embed.add_field(
            name="Saved Roles",
            value=str(role_count),
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # EXPIRATION WORKER
    # =====================================================

    @tasks.loop(seconds=15)
    async def jail_expiration_worker(
        self
    ):

        await self.bot.wait_until_ready()

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                guild_id,
                user_id,
                reason,
                expires_at,
                previous_roles

            FROM jail_records

            WHERE active = 1
            AND expires_at IS NOT NULL
        """)

        records = cursor.fetchall()

        connection.close()

        now = datetime.now(
            timezone.utc
        )

        for record in records:

            (
                record_id,
                guild_id,
                user_id,
                reason,
                expires_at,
                previous_roles_json
            ) = record

            try:

                expiry = datetime.fromisoformat(
                    expires_at
                )

            except ValueError:

                continue

            if expiry > now:
                continue

            guild = self.bot.get_guild(
                int(guild_id)
            )

            if guild is None:
                continue

            member = guild.get_member(
                int(user_id)
            )

            if member is None:

                self.close_record(
                    record_id
                )

                continue

            jailed_role = self.get_jailed_role(
                guild
            )

            if jailed_role:

                await self.remove_jail_role(
                    member,
                    jailed_role
                )

            try:

                previous_roles = json.loads(
                    previous_roles_json
                )

            except (
                TypeError,
                ValueError,
                json.JSONDecodeError
            ):

                previous_roles = []

            await self.restore_roles(
                member,
                previous_roles
            )

            self.close_record(
                record_id
            )

            await self.send_jail_log(
                guild,
                "⏰ Jail Expired",
                discord.Color.green(),
                member,
                None,
                reason,
                None,
                "Automatic Unjail"
            )

    @jail_expiration_worker.before_loop
    async def before_jail_expiration_worker(
        self
    ):

        await self.bot.wait_until_ready()


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    await bot.add_cog(
        Jail(bot)
    )