import sqlite3
from datetime import datetime
import os

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
# ROLE OPTIONS
# =========================================================

ROLE_OPTIONS = [
    ("Staff Role", "staff", "👮"),
    ("Moderator Role", "moderator", "🛡️"),
    ("Jailed Role", "jailed", "⛓️"),
    ("Verified Role", "verified", "✅"),
]


# =========================================================
# CHANNEL OPTIONS
# =========================================================

CHANNEL_OPTIONS = [
    (
        "Configuration Logs",
        "configuration_log_channel_id",
        "📋"
    ),
    (
        "Transcript Channel",
        "transcript_log_channel_id",
        "🧾"
    ),
    (
        "Jail Logs",
        "jail_log_channel_id",
        "⛓️"
    ),
    (
        "Moderation Logs",
        "moderation_log_channel_id",
        "🛡️"
    ),
    (
        "Welcome Channel",
        "welcome_channel_id",
        "👋"
    ),
    (
        "Verification Channel",
        "verification_channel_id",
        "🔐"
    ),
    (
        "Verified Logs",
        "verified_log_channel_id",
        "✅"
    ),
    (
        "Unverified Logs",
        "unverified_log_channel_id",
        "❌"
    ),
]


# =========================================================
# CONFIG
# =========================================================

class Config(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.create_database()

    # =====================================================
    # DATABASE
    # =====================================================

    def create_database(self):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,

                configuration_log_channel_id INTEGER,

                transcript_log_channel_id INTEGER,

                jail_log_channel_id INTEGER,

                moderation_log_channel_id INTEGER,

                welcome_channel_id INTEGER,

                verification_channel_id INTEGER,

                verified_log_channel_id INTEGER,

                unverified_log_channel_id INTEGER,

                ticket_category_id INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id INTEGER NOT NULL,

                setting TEXT NOT NULL,

                role_id INTEGER NOT NULL,

                UNIQUE(
                    guild_id,
                    setting,
                    role_id
                )
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                guild_id INTEGER NOT NULL,

                user_id INTEGER NOT NULL,

                setting TEXT NOT NULL,

                old_value TEXT,

                new_value TEXT,

                timestamp TEXT NOT NULL
            )
        """)

        # -------------------------------------------------
        # MIGRATIONS
        # -------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(guild_config)"
        )

        columns = {
            row[1]
            for row in cursor.fetchall()
        }

        migrations = {
            "transcript_log_channel_id": "INTEGER",
            "verified_log_channel_id": "INTEGER",
            "unverified_log_channel_id": "INTEGER",
            "ticket_category_id": "INTEGER",
        }

        for column, data_type in migrations.items():

            if column not in columns:

                cursor.execute(
                    f"""
                    ALTER TABLE guild_config
                    ADD COLUMN {column} {data_type}
                    """
                )

        connection.commit()

        connection.close()

    # =====================================================
    # GUILD ROW
    # =====================================================

    def ensure_guild(
        self,
        guild_id
    ):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO guild_config
            (guild_id)
            VALUES (?)
        """, (
            guild_id,
        ))

        connection.commit()

        connection.close()

    # =====================================================
    # ROLES
    # =====================================================

    def get_roles(
        self,
        guild_id,
        setting
    ):

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT role_id
            FROM role_permissions

            WHERE guild_id = ?
            AND setting = ?

            ORDER BY id
        """, (
            guild_id,
            setting
        ))

        roles = [
            row[0]
            for row in cursor.fetchall()
        ]

        connection.close()

        return roles

    async def add_roles(
        self,
        guild_id,
        user_id,
        setting,
        roles
    ):

        old_roles = self.get_roles(
            guild_id,
            setting
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        for role in roles:

            cursor.execute("""
                INSERT OR IGNORE INTO role_permissions
                (
                    guild_id,
                    setting,
                    role_id
                )

                VALUES (?, ?, ?)
            """, (
                guild_id,
                setting,
                role.id
            ))

        connection.commit()

        connection.close()

        new_roles = self.get_roles(
            guild_id,
            setting
        )

        await self.add_history(
            guild_id,
            user_id,
            setting,
            old_roles,
            new_roles
        )

        await self.send_config_log(
            guild_id,
            user_id,
            setting,
            old_roles,
            new_roles
        )

    async def remove_role(
        self,
        guild_id,
        user_id,
        setting,
        role_id
    ):

        old_roles = self.get_roles(
            guild_id,
            setting
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM role_permissions

            WHERE guild_id = ?
            AND setting = ?
            AND role_id = ?
        """, (
            guild_id,
            setting,
            role_id
        ))

        connection.commit()

        connection.close()

        new_roles = self.get_roles(
            guild_id,
            setting
        )

        await self.add_history(
            guild_id,
            user_id,
            setting,
            old_roles,
            new_roles
        )

        await self.send_config_log(
            guild_id,
            user_id,
            setting,
            old_roles,
            new_roles
        )

    async def clear_roles(
        self,
        guild_id,
        user_id,
        setting
    ):

        old_roles = self.get_roles(
            guild_id,
            setting
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM role_permissions

            WHERE guild_id = ?
            AND setting = ?
        """, (
            guild_id,
            setting
        ))

        connection.commit()

        connection.close()

        await self.add_history(
            guild_id,
            user_id,
            setting,
            old_roles,
            []
        )

        await self.send_config_log(
            guild_id,
            user_id,
            setting,
            old_roles,
            []
        )

    # =====================================================
    # CHANNELS
    # =====================================================

    def get_channel_value(
        self,
        guild_id,
        setting
    ):

        allowed_settings = {
            option[1]
            for option in CHANNEL_OPTIONS
        }

        if setting not in allowed_settings:

            return None

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(
            f"""
            SELECT {setting}

            FROM guild_config

            WHERE guild_id = ?
            """,
            (
                guild_id,
            )
        )

        result = cursor.fetchone()

        connection.close()

        if result is None:

            return None

        return result[0]

    # =====================================================
    # TICKET CATEGORY
    # =====================================================

    def get_ticket_category(
        self,
        guild_id
    ):

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            SELECT ticket_category_id

            FROM guild_config

            WHERE guild_id = ?
        """, (
            guild_id,
        ))

        result = cursor.fetchone()

        connection.close()

        if result is None:

            return None

        return result[0]

    async def save_ticket_category(
        self,
        guild_id,
        user_id,
        category_id
    ):

        old_value = self.get_ticket_category(
            guild_id
        )

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE guild_config

            SET ticket_category_id = ?

            WHERE guild_id = ?
        """, (
            category_id,
            guild_id
        ))

        connection.commit()

        connection.close()

        await self.add_history(
            guild_id,
            user_id,
            "ticket_category_id",
            old_value,
            category_id
        )

        await self.send_config_log(
            guild_id,
            user_id,
            "ticket_category_id",
            old_value,
            category_id
        )

    async def remove_ticket_category(
        self,
        guild_id,
        user_id
    ):

        old_value = self.get_ticket_category(
            guild_id
        )

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE guild_config

            SET ticket_category_id = NULL

            WHERE guild_id = ?
        """, (
            guild_id,
        ))

        connection.commit()

        connection.close()

        await self.add_history(
            guild_id,
            user_id,
            "ticket_category_id",
            old_value,
            None
        )

        await self.send_config_log(
            guild_id,
            user_id,
            "ticket_category_id",
            old_value,
            None
        )

    # =====================================================
    # SAVE CHANNEL
    # =====================================================

    async def save_channel(
        self,
        guild_id,
        user_id,
        setting,
        channel_id
    ):

        allowed_settings = {
            option[1]
            for option in CHANNEL_OPTIONS
        }

        if setting not in allowed_settings:

            return

        old_value = self.get_channel_value(
            guild_id,
            setting
        )

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(
            f"""
            UPDATE guild_config

            SET {setting} = ?

            WHERE guild_id = ?
            """,
            (
                channel_id,
                guild_id
            )
        )

        connection.commit()

        connection.close()

        await self.add_history(
            guild_id,
            user_id,
            setting,
            old_value,
            channel_id
        )

        await self.send_config_log(
            guild_id,
            user_id,
            setting,
            old_value,
            channel_id
        )

    async def remove_channel(
        self,
        guild_id,
        user_id,
        setting
    ):

        allowed_settings = {
            option[1]
            for option in CHANNEL_OPTIONS
        }

        if setting not in allowed_settings:

            return

        old_value = self.get_channel_value(
            guild_id,
            setting
        )

        self.ensure_guild(
            guild_id
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(
            f"""
            UPDATE guild_config

            SET {setting} = NULL

            WHERE guild_id = ?
            """,
            (
                guild_id,
            )
        )

        connection.commit()

        connection.close()

        await self.add_history(
            guild_id,
            user_id,
            setting,
            old_value,
            None
        )

        await self.send_config_log(
            guild_id,
            user_id,
            setting,
            old_value,
            None
        )

    # =====================================================
    # HISTORY
    # =====================================================

    async def add_history(
        self,
        guild_id,
        user_id,
        setting,
        old_value,
        new_value
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO config_history
            (
                guild_id,
                user_id,
                setting,
                old_value,
                new_value,
                timestamp
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            guild_id,
            user_id,
            setting,
            str(old_value),
            str(new_value),
            timestamp
        ))

        connection.commit()

        connection.close()

    # =====================================================
    # CONFIG LOG
    # =====================================================

    async def send_config_log(
        self,
        guild_id,
        user_id,
        setting,
        old_value,
        new_value
    ):

        log_channel_id = self.get_channel_value(
            guild_id,
            "configuration_log_channel_id"
        )

        if not log_channel_id:

            return

        channel = self.bot.get_channel(
            int(log_channel_id)
        )

        if channel is None:

            return

        guild = self.bot.get_guild(
            guild_id
        )

        if guild is None:

            return

        def format_value(value):

            # ---------------------------------------------
            # LIST OF ROLES
            # ---------------------------------------------

            if isinstance(value, list):

                if not value:

                    return "None"

                mentions = []

                for role_id in value:

                    try:

                        role = guild.get_role(
                            int(role_id)
                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        continue

                    if role:

                        mentions.append(
                            role.mention
                        )

                return (
                    "\n".join(mentions)
                    if mentions
                    else "None"
                )

            # ---------------------------------------------
            # NONE
            # ---------------------------------------------

            if value is None:

                return "None"

            # ---------------------------------------------
            # INTEGER
            # ---------------------------------------------

            try:

                value = int(value)

            except (
                TypeError,
                ValueError
            ):

                return str(value)

            # ---------------------------------------------
            # CATEGORY
            # ---------------------------------------------

            category = guild.get_channel(
                value
            )

            if isinstance(
                category,
                discord.CategoryChannel
            ):

                return f"**{category.name}**"

            # ---------------------------------------------
            # ROLE
            # ---------------------------------------------

            role = guild.get_role(
                value
            )

            if role:

                return role.mention

            # ---------------------------------------------
            # CHANNEL
            # ---------------------------------------------

            channel_obj = guild.get_channel(
                value
            )

            if channel_obj:

                return channel_obj.mention

            # ---------------------------------------------
            # UNKNOWN ID
            # ---------------------------------------------

            return f"`{value}`"

        embed = discord.Embed(
            title="⚙️ Configuration Changed",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="Administrator",
            value=f"<@{user_id}>",
            inline=False
        )

        embed.add_field(
            name="Setting",
            value=setting,
            inline=False
        )

        embed.add_field(
            name="Previous",
            value=format_value(old_value),
            inline=True
        )

        embed.add_field(
            name="New",
            value=format_value(new_value),
            inline=True
        )

        try:

            await channel.send(
                embed=embed
            )

        except discord.HTTPException:

            pass

    # =====================================================
    # /SETUP
    # =====================================================

    @app_commands.command(
        name="setup",
        description="Configure the Misuki Bot."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def setup_command(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="⚙️ Misuki Bot Setup",
            description=(
                "Configure Misuki for this server.\n\n"
                "Choose a category below."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed,
            view=MainSetupView(self)
        )


# =========================================================
# MAIN SETUP
# =========================================================

class MainSetupView(discord.ui.View):

    def __init__(self, config):

        super().__init__(
            timeout=600
        )

        self.add_item(
            RolesButton(config)
        )

        self.add_item(
            ChannelsButton(config)
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Tickets",
                "🎫",
                discord.ButtonStyle.success,
                "tickets"
            )
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Moderation",
                "🛡️",
                discord.ButtonStyle.danger,
                "moderation"
            )
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Verification",
                "🔐",
                discord.ButtonStyle.secondary,
                "verification"
            )
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Jail",
                "⛓️",
                discord.ButtonStyle.secondary,
                "jail"
            )
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Stats",
                "📊",
                discord.ButtonStyle.secondary,
                "stats"
            )
        )

        self.add_item(
            SimpleCategoryButton(
                config,
                "Announcements",
                "📢",
                discord.ButtonStyle.secondary,
                "announcements"
            )
        )


# =========================================================
# ROLES
# =========================================================

class RolesButton(discord.ui.Button):

    def __init__(self, config):

        self.config = config

        super().__init__(
            label="Roles",
            emoji="👥",
            style=discord.ButtonStyle.primary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="👥 Roles",
            description=(
                "Choose which role function "
                "you want to configure."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu(self.config)
        )


class RolesMenu(discord.ui.View):

    def __init__(self, config):

        super().__init__(
            timeout=600
        )

        for label, setting, emoji in ROLE_OPTIONS:

            self.add_item(
                RoleFunctionButton(
                    config,
                    label,
                    setting,
                    emoji
                )
            )

        self.add_item(
            BackButton(config)
        )


class RoleFunctionButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        setting,
        emoji
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        role_ids = self.config.get_roles(
            interaction.guild.id,
            self.setting
        )

        current = (
            "\n".join(
                f"<@&{role_id}>"
                for role_id in role_ids
            )
            if role_ids
            else "None"
        )

        embed = discord.Embed(
            title=f"👥 {self.label_name}",
            description=(
                f"**Current roles:**\n"
                f"{current}\n\n"
                "Select one or more roles."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RoleSelectionView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class RoleSelectionView(discord.ui.View):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            MultiRoleSelect(
                config,
                label,
                setting
            )
        )

        self.add_item(
            ManageRolesButton(
                config,
                label,
                setting
            )
        )

        self.add_item(
            ClearRolesButton(
                config,
                label,
                setting
            )
        )

        self.add_item(
            BackToRolesButton(config)
        )


class MultiRoleSelect(discord.ui.RoleSelect):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            placeholder="Select roles...",
            min_values=1,
            max_values=25
        )

    async def callback(
        self,
        interaction
    ):

        roles = self.values

        await self.config.add_roles(
            interaction.guild.id,
            interaction.user.id,
            self.setting,
            roles
        )

        embed = discord.Embed(
            title="✅ Roles Added",
            description=(
                "Added:\n\n"
                + "\n".join(
                    role.mention
                    for role in roles
                )
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu(self.config)
        )


# =========================================================
# MANAGE ROLES
# =========================================================

class ManageRolesButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label="Manage Roles",
            emoji="🛠️",
            style=discord.ButtonStyle.primary
        )

    async def callback(
        self,
        interaction
    ):

        role_ids = self.config.get_roles(
            interaction.guild.id,
            self.setting
        )

        if not role_ids:

            await interaction.response.send_message(
                "❌ No roles are configured.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title=f"🛠️ {self.label_name}",
            description=(
                "Select the role you want to remove."
            ),
            color=discord.Color.orange()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RemoveRoleView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class RemoveRoleView(discord.ui.View):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            RemoveRoleSelect(
                config,
                label,
                setting
            )
        )

        self.add_item(
            BackToRoleSelectionButton(
                config,
                label,
                setting
            )
        )


class RemoveRoleSelect(discord.ui.RoleSelect):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            placeholder="Select role to remove...",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        role = self.values[0]

        configured = self.config.get_roles(
            interaction.guild.id,
            self.setting
        )

        if role.id not in configured:

            await interaction.response.send_message(
                "❌ This role isn't configured.",
                ephemeral=True
            )

            return

        await self.config.remove_role(
            interaction.guild.id,
            interaction.user.id,
            self.setting,
            role.id
        )

        embed = discord.Embed(
            title="🗑️ Role Removed",
            description=(
                f"{role.mention} was removed from "
                f"**{self.label_name}**."
            ),
            color=discord.Color.red()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu(self.config)
        )


class ClearRolesButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label="Clear All",
            emoji="🗑️",
            style=discord.ButtonStyle.danger
        )

    async def callback(
        self,
        interaction
    ):

        await self.config.clear_roles(
            interaction.guild.id,
            interaction.user.id,
            self.setting
        )

        embed = discord.Embed(
            title="🗑️ Roles Cleared",
            description=(
                f"All roles were removed from "
                f"**{self.label_name}**."
            ),
            color=discord.Color.red()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu(self.config)
        )


# =========================================================
# CHANNELS
# =========================================================

class ChannelsButton(discord.ui.Button):

    def __init__(self, config):

        self.config = config

        super().__init__(
            label="Channels",
            emoji="📁",
            style=discord.ButtonStyle.primary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="📁 Channels",
            description=(
                "Choose which channel function "
                "you want to configure."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ChannelsMenu(self.config)
        )


class ChannelsMenu(discord.ui.View):

    def __init__(self, config):

        super().__init__(
            timeout=600
        )

        for label, setting, emoji in CHANNEL_OPTIONS:

            self.add_item(
                ChannelFunctionButton(
                    config,
                    label,
                    setting,
                    emoji
                )
            )

        self.add_item(
            BackButton(config)
        )


class ChannelFunctionButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        setting,
        emoji
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        current = self.config.get_channel_value(
            interaction.guild.id,
            self.setting
        )

        current_text = (
            f"<#{current}>"
            if current
            else "None"
        )

        embed = discord.Embed(
            title=f"{self.emoji} {self.label_name}",
            description=(
                f"**Current:** {current_text}\n\n"
                "Select the channel below."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ChannelSelectionView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class ChannelSelectionView(discord.ui.View):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            ChannelPicker(
                config,
                label,
                setting
            )
        )

        self.add_item(
            RemoveChannelButton(
                config,
                label,
                setting
            )
        )

        self.add_item(
            BackToChannelsButton(config)
        )


class ChannelPicker(discord.ui.ChannelSelect):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            placeholder="Select a channel...",
            channel_types=[
                discord.ChannelType.text
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        channel = self.values[0]

        await self.config.save_channel(
            interaction.guild.id,
            interaction.user.id,
            self.setting,
            channel.id
        )

        embed = discord.Embed(
            title="✅ Channel Saved",
            description=(
                f"**{self.label_name}** is now "
                f"{channel.mention}."
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ChannelsMenu(self.config)
        )


class RemoveChannelButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label="Remove",
            emoji="🗑️",
            style=discord.ButtonStyle.danger
        )

    async def callback(
        self,
        interaction
    ):

        current = self.config.get_channel_value(
            interaction.guild.id,
            self.setting
        )

        if not current:

            await interaction.response.send_message(
                "❌ No channel is configured.",
                ephemeral=True
            )

            return

        await self.config.remove_channel(
            interaction.guild.id,
            interaction.user.id,
            self.setting
        )

        embed = discord.Embed(
            title="🗑️ Channel Removed",
            description=(
                f"**{self.label_name}** has been "
                "removed."
            ),
            color=discord.Color.red()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ChannelsMenu(self.config)
        )


# =========================================================
# CATEGORY CONFIGURATION
# =========================================================

class SimpleCategoryButton(discord.ui.Button):

    def __init__(
        self,
        config,
        label,
        emoji,
        style,
        category
    ):

        self.config = config
        self.category = category

        super().__init__(
            label=label,
            emoji=emoji,
            style=style
        )

    async def callback(
        self,
        interaction
    ):

        # -------------------------------------------------
        # TICKETS
        # -------------------------------------------------

        if self.category == "tickets":

            embed = discord.Embed(
                title="🎫 Tickets",
                description=(
                    "Configure the ticket system.\n\n"
                    "• Ticket Category — category where "
                    "tickets will be created.\n"
                    "• Transcript Channel — channel where "
                    "ticket transcripts will be stored."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=TicketConfigView(
                    self.config
                )
            )

            return

        # -------------------------------------------------
        # MODERATION
        # -------------------------------------------------

        if self.category == "moderation":

            embed = discord.Embed(
                title="🛡️ Moderation",
                description=(
                    "Configure moderation settings."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=CategoryConfigView(
                    self.config,
                    [
                        (
                            "Moderation Logs",
                            "moderation_log_channel_id",
                            "🛡️"
                        ),
                    ],
                    [
                        (
                            "Moderator Role",
                            "moderator",
                            "🛡️"
                        ),
                    ]
                )
            )

            return

        # -------------------------------------------------
        # VERIFICATION
        # -------------------------------------------------

        if self.category == "verification":

            embed = discord.Embed(
                title="🔐 Verification",
                description=(
                    "Configure the verification system."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=CategoryConfigView(
                    self.config,
                    [
                        (
                            "Verification Channel",
                            "verification_channel_id",
                            "🔐"
                        ),
                        (
                            "Verified Logs",
                            "verified_log_channel_id",
                            "✅"
                        ),
                        (
                            "Unverified Logs",
                            "unverified_log_channel_id",
                            "❌"
                        ),
                    ],
                    [
                        (
                            "Verified Role",
                            "verified",
                            "✅"
                        ),
                    ]
                )
            )

            return

        # -------------------------------------------------
        # JAIL
        # -------------------------------------------------

        if self.category == "jail":

            embed = discord.Embed(
                title="⛓️ Jail",
                description=(
                    "Configure the jail system."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=CategoryConfigView(
                    self.config,
                    [
                        (
                            "Jail Logs",
                            "jail_log_channel_id",
                            "⛓️"
                        ),
                    ],
                    [
                        (
                            "Jailed Role",
                            "jailed",
                            "⛓️"
                        ),
                    ]
                )
            )

            return

        # -------------------------------------------------
        # STATS
        # -------------------------------------------------

        if self.category == "stats":

            embed = discord.Embed(
                title="📊 Stats",
                description=(
                    "The statistics module currently has "
                    "no configurable settings."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=BackOnlyView(
                    self.config
                )
            )

            return

        # -------------------------------------------------
        # ANNOUNCEMENTS
        # -------------------------------------------------

        if self.category == "announcements":

            embed = discord.Embed(
                title="📢 Announcements",
                description=(
                    "Configure the channel used for "
                    "announcements and welcome messages."
                ),
                color=discord.Color.blurple()
            )

            await interaction.response.edit_message(
                embed=embed,
                view=CategoryConfigView(
                    self.config,
                    [
                        (
                            "Welcome Channel",
                            "welcome_channel_id",
                            "👋"
                        ),
                    ],
                    []
                )
            )


# =========================================================
# TICKET CONFIGURATION
# =========================================================

class TicketConfigView(discord.ui.View):

    def __init__(
        self,
        config
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            TicketCategoryButton(
                config
            )
        )

        self.add_item(
            CategoryChannelButton(
                config,
                "Transcript Channel",
                "transcript_log_channel_id",
                "🧾"
            )
        )

        self.add_item(
            BackButton(config)
        )


class TicketCategoryButton(discord.ui.Button):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Ticket Category",
            emoji="📂",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        category_id = self.config.get_ticket_category(
            interaction.guild.id
        )

        current = (
            f"<#{category_id}>"
            if category_id
            else "None"
        )

        embed = discord.Embed(
            title="📂 Ticket Category",
            description=(
                f"**Current:** {current}\n\n"
                "Select the category where new "
                "tickets should be created."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=TicketCategorySelectionView(
                self.config
            )
        )


class TicketCategorySelectionView(
    discord.ui.View
):

    def __init__(
        self,
        config
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            CategoryPicker(
                config
            )
        )

        self.add_item(
            RemoveTicketCategoryButton(
                config
            )
        )

        self.add_item(
            BackToTicketConfigButton(
                config
            )
        )


class CategoryPicker(
    discord.ui.ChannelSelect
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            placeholder="Select ticket category...",
            channel_types=[
                discord.ChannelType.category
            ],
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        category = self.values[0]

        await self.config.save_ticket_category(
            interaction.guild.id,
            interaction.user.id,
            category.id
        )

        embed = discord.Embed(
            title="✅ Ticket Category Saved",
            description=(
                f"Tickets will now be created in "
                f"**{category.name}**."
            ),
            color=discord.Color.green()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=TicketConfigView(
                self.config
            )
        )


class RemoveTicketCategoryButton(
    discord.ui.Button
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Remove",
            emoji="🗑️",
            style=discord.ButtonStyle.danger
        )

    async def callback(
        self,
        interaction
    ):

        current = self.config.get_ticket_category(
            interaction.guild.id
        )

        if not current:

            await interaction.response.send_message(
                "❌ No ticket category is configured.",
                ephemeral=True
            )

            return

        await self.config.remove_ticket_category(
            interaction.guild.id,
            interaction.user.id
        )

        embed = discord.Embed(
            title="🗑️ Ticket Category Removed",
            description=(
                "The ticket category configuration "
                "has been removed."
            ),
            color=discord.Color.red()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=TicketConfigView(
                self.config
            )
        )


class BackToTicketConfigButton(
    discord.ui.Button
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Back",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="🎫 Tickets",
            description=(
                "Configure the ticket system."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=TicketConfigView(
                self.config
            )
        )


# =========================================================
# CATEGORY CONFIG VIEW
# =========================================================

class CategoryConfigView(
    discord.ui.View
):

    def __init__(
        self,
        config,
        channels,
        roles
    ):

        super().__init__(
            timeout=600
        )

        for label, setting, emoji in channels:

            self.add_item(
                CategoryChannelButton(
                    config,
                    label,
                    setting,
                    emoji
                )
            )

        for label, setting, emoji in roles:

            self.add_item(
                CategoryRoleButton(
                    config,
                    label,
                    setting,
                    emoji
                )
            )

        self.add_item(
            BackButton(config)
        )


# =========================================================
# CATEGORY CHANNEL
# =========================================================

class CategoryChannelButton(
    discord.ui.Button
):

    def __init__(
        self,
        config,
        label,
        setting,
        emoji
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        current = self.config.get_channel_value(
            interaction.guild.id,
            self.setting
        )

        current_text = (
            f"<#{current}>"
            if current
            else "None"
        )

        embed = discord.Embed(
            title=f"{self.emoji} {self.label_name}",
            description=(
                f"**Current:** {current_text}\n\n"
                "Select the channel below."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=CategoryChannelSelectionView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class CategoryChannelSelectionView(
    discord.ui.View
):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            ChannelPicker(
                config,
                label,
                setting
            )
        )

        self.add_item(
            RemoveChannelButton(
                config,
                label,
                setting
            )
        )

        self.add_item(
            BackButton(config)
        )


# =========================================================
# CATEGORY ROLE
# =========================================================

class CategoryRoleButton(
    discord.ui.Button
):

    def __init__(
        self,
        config,
        label,
        setting,
        emoji
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        role_ids = self.config.get_roles(
            interaction.guild.id,
            self.setting
        )

        current = (
            "\n".join(
                f"<@&{role_id}>"
                for role_id in role_ids
            )
            if role_ids
            else "None"
        )

        embed = discord.Embed(
            title=f"{self.emoji} {self.label_name}",
            description=(
                f"**Current:**\n{current}\n\n"
                "Select a role below."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=CategoryRoleSelectionView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class CategoryRoleSelectionView(
    discord.ui.View
):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            MultiRoleSelect(
                config,
                label,
                setting
            )
        )

        self.add_item(
            ClearRolesButton(
                config,
                label,
                setting
            )
        )

        self.add_item(
            BackButton(config)
        )


# =========================================================
# BACK BUTTONS
# =========================================================

class BackButton(
    discord.ui.Button
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Back",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="⚙️ Misuki Bot Setup",
            description=(
                "Configure Misuki for this server.\n\n"
                "Choose a category below."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=MainSetupView(
                self.config
            )
        )


class BackToRolesButton(
    discord.ui.Button
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Back",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="👥 Roles",
            description=(
                "Choose which role function "
                "you want to configure."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RolesMenu(
                self.config
            )
        )


class BackToRoleSelectionButton(
    discord.ui.Button
):

    def __init__(
        self,
        config,
        label,
        setting
    ):

        self.config = config
        self.label_name = label
        self.setting = setting

        super().__init__(
            label="Back",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        role_ids = self.config.get_roles(
            interaction.guild.id,
            self.setting
        )

        current = (
            "\n".join(
                f"<@&{role_id}>"
                for role_id in role_ids
            )
            if role_ids
            else "None"
        )

        embed = discord.Embed(
            title=f"👥 {self.label_name}",
            description=(
                f"**Current roles:**\n"
                f"{current}\n\n"
                "Select one or more roles."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=RoleSelectionView(
                self.config,
                self.label_name,
                self.setting
            )
        )


class BackToChannelsButton(
    discord.ui.Button
):

    def __init__(
        self,
        config
    ):

        self.config = config

        super().__init__(
            label="Back",
            emoji="↩️",
            style=discord.ButtonStyle.secondary
        )

    async def callback(
        self,
        interaction
    ):

        embed = discord.Embed(
            title="📁 Channels",
            description=(
                "Choose which channel function "
                "you want to configure."
            ),
            color=discord.Color.blurple()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=ChannelsMenu(
                self.config
            )
        )


class BackOnlyView(
    discord.ui.View
):

    def __init__(
        self,
        config
    ):

        super().__init__(
            timeout=600
        )

        self.add_item(
            BackButton(config)
        )


# =========================================================
# LOAD COG
# =========================================================

async def setup(
    bot
):

    await bot.add_cog(
        Config(bot)
    )