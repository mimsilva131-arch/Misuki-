
# =========================================================
# MISUKI TRIGGERS
# Text Triggers + Automatic Responses
# Premium System
# =========================================================

import os
import sqlite3

import discord

from discord import app_commands
from discord.ext import commands


# =========================================================
# DATABASE
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
# TRIGGER MANAGER
# =========================================================

class TriggerManager(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.create_database()

    # =====================================================
    # DATABASE SETUP
    # =====================================================

    def create_database(self):

        with sqlite3.connect(
            DATABASE
        ) as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS triggers (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    guild_id INTEGER NOT NULL,

                    trigger TEXT NOT NULL,

                    response TEXT NOT NULL,

                    enabled INTEGER NOT NULL
                    DEFAULT 1,

                    created_by INTEGER NOT NULL,

                    created_at TEXT NOT NULL,

                    UNIQUE (
                        guild_id,
                        trigger
                    )

                )
                """
            )

            connection.commit()

    # =====================================================
    # PREMIUM
    # =====================================================

    def has_premium(
        self,
        guild_id
    ):

        """
        Verifica se o servidor possui uma licença
        Premium ativa.

        Usa a tabela 'licenses' criada pelo
        LicenseManager.
        """

        try:

            with sqlite3.connect(
                DATABASE
            ) as connection:

                cursor = connection.execute(
                    """
                    SELECT
                        status,
                        expires_at

                    FROM licenses

                    WHERE guild_id = ?
                    """,
                    (
                        guild_id,
                    )
                )

                license_data = cursor.fetchone()

        except sqlite3.Error as error:

            print(
                f"❌ Trigger premium check failed: {error}"
            )

            return False

        if license_data is None:

            return False

        status = license_data[0]

        expires_at = license_data[1]

        if status != "active":

            return False

        # -------------------------------------------------
        # CHECK EXPIRATION
        # -------------------------------------------------

        if expires_at:

            from datetime import datetime

            try:

                expiration = datetime.fromisoformat(
                    expires_at
                )

            except ValueError:

                return False

            if datetime.now() >= expiration:

                try:

                    with sqlite3.connect(
                        DATABASE
                    ) as connection:

                        connection.execute(
                            """
                            UPDATE licenses

                            SET status = 'expired'

                            WHERE guild_id = ?
                            """,
                            (
                                guild_id,
                            )
                        )

                        connection.commit()

                except sqlite3.Error as error:

                    print(
                        f"❌ Failed to expire license: {error}"
                    )

                return False

        return True

    # =====================================================
    # STAFF / ADMIN PERMISSION
    # =====================================================

    def member_is_staff(
        self,
        member: discord.Member
    ):

        # -------------------------------------------------
        # ADMINISTRATOR
        # -------------------------------------------------

        if member.guild_permissions.administrator:

            return True

        # -------------------------------------------------
        # GET STAFF ROLES FROM SETUP
        # -------------------------------------------------

        try:

            with sqlite3.connect(
                DATABASE
            ) as connection:

                cursor = connection.execute(
                    """
                    SELECT role_id

                    FROM role_permissions

                    WHERE guild_id = ?

                    AND setting = 'staff'
                    """,
                    (
                        member.guild.id,
                    )
                )

                staff_roles = {
                    row[0]
                    for row in cursor.fetchall()
                }

        except sqlite3.Error as error:

            print(
                f"❌ Staff permission check failed: {error}"
            )

            return False

        if not staff_roles:

            return False

        # -------------------------------------------------
        # CHECK MEMBER ROLES
        # -------------------------------------------------

        member_role_ids = {
            role.id
            for role in member.roles
        }

        return bool(
            staff_roles
            & member_role_ids
        )

    # =====================================================
    # ADD TRIGGER
    # =====================================================

    def add_trigger(
        self,
        guild_id,
        trigger,
        response,
        created_by
    ):

        from datetime import datetime

        trigger = trigger.strip().lower()

        with sqlite3.connect(
            DATABASE
        ) as connection:

            try:

                connection.execute(
                    """
                    INSERT INTO triggers
                    (
                        guild_id,
                        trigger,
                        response,
                        enabled,
                        created_by,
                        created_at
                    )

                    VALUES (?, ?, ?, 1, ?, ?)
                    """,
                    (
                        guild_id,
                        trigger,
                        response,
                        created_by,
                        datetime.utcnow().isoformat()
                    )
                )

                connection.commit()

                return True

            except sqlite3.IntegrityError:

                return False

    # =====================================================
    # REMOVE TRIGGER
    # =====================================================

    def remove_trigger(
        self,
        guild_id,
        trigger
    ):

        trigger = trigger.strip().lower()

        with sqlite3.connect(
            DATABASE
        ) as connection:

            cursor = connection.execute(
                """
                DELETE FROM triggers

                WHERE guild_id = ?

                AND trigger = ?
                """,
                (
                    guild_id,
                    trigger
                )
            )

            connection.commit()

            return cursor.rowcount > 0

    # =====================================================
    # EDIT TRIGGER
    # =====================================================

    def edit_trigger(
        self,
        guild_id,
        trigger,
        response
    ):

        trigger = trigger.strip().lower()

        with sqlite3.connect(
            DATABASE
        ) as connection:

            cursor = connection.execute(
                """
                UPDATE triggers

                SET response = ?

                WHERE guild_id = ?

                AND trigger = ?
                """,
                (
                    response,
                    guild_id,
                    trigger
                )
            )

            connection.commit()

            return cursor.rowcount > 0

    # =====================================================
    # ENABLE / DISABLE
    # =====================================================

    def set_enabled(
        self,
        guild_id,
        trigger,
        enabled
    ):

        trigger = trigger.strip().lower()

        with sqlite3.connect(
            DATABASE
        ) as connection:

            cursor = connection.execute(
                """
                UPDATE triggers

                SET enabled = ?

                WHERE guild_id = ?

                AND trigger = ?
                """,
                (
                    1 if enabled else 0,
                    guild_id,
                    trigger
                )
            )

            connection.commit()

            return cursor.rowcount > 0

    # =====================================================
    # GET TRIGGERS
    # =====================================================

    def get_triggers(
        self,
        guild_id
    ):

        with sqlite3.connect(
            DATABASE
        ) as connection:

            cursor = connection.execute(
                """
                SELECT
                    id,
                    trigger,
                    response,
                    enabled,
                    created_by,
                    created_at

                FROM triggers

                WHERE guild_id = ?

                ORDER BY id ASC
                """,
                (
                    guild_id,
                )
            )

            return cursor.fetchall()

    # =====================================================
    # GET ACTIVE TRIGGERS
    # =====================================================

    def get_active_triggers(
        self,
        guild_id
    ):

        with sqlite3.connect(
            DATABASE
        ) as connection:

            cursor = connection.execute(
                """
                SELECT
                    trigger,
                    response

                FROM triggers

                WHERE guild_id = ?

                AND enabled = 1

                ORDER BY LENGTH(trigger) DESC
                """,
                (
                    guild_id,
                )
            )

            return cursor.fetchall()

    # =====================================================
    # CHECK MANAGEMENT PERMISSION
    # =====================================================

    async def check_management_permission(
        self,
        interaction
    ):

        # -------------------------------------------------
        # SERVER
        # -------------------------------------------------

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return False

        # -------------------------------------------------
        # PREMIUM
        # -------------------------------------------------

        if not self.has_premium(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "💎 **Trigger System Premium**\n\n"
                    "This server does not have an "
                    "active Misuki Premium license."
                ),
                ephemeral=True
            )

            return False

        # -------------------------------------------------
        # MEMBER
        # -------------------------------------------------

        if not isinstance(
            interaction.user,
            discord.Member
        ):

            await interaction.response.send_message(
                "❌ Unable to verify your permissions.",
                ephemeral=True
            )

            return False

        # -------------------------------------------------
        # STAFF / ADMIN
        # -------------------------------------------------

        if not self.member_is_staff(
            interaction.user
        ):

            await interaction.response.send_message(
                (
                    "❌ You do not have permission "
                    "to manage triggers.\n\n"
                    "You must be an Administrator or "
                    "have a Staff role configured in "
                    "`/setup`."
                ),
                ephemeral=True
            )

            return False

        return True

    # =====================================================
    # /TRIGGER
    # =====================================================

    trigger_group = app_commands.Group(
        name="trigger",
        description="Manage automatic text triggers."
    )

    # =====================================================
    # /TRIGGER ADD
    # =====================================================

    @trigger_group.command(
        name="add",
        description="Create a new automatic trigger."
    )
    @app_commands.describe(
        trigger="Text that activates the response.",
        response="Text the bot will send."
    )
    async def trigger_add(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        trigger = trigger.strip()

        response = response.strip()

        if not trigger:

            await interaction.response.send_message(
                "❌ The trigger cannot be empty.",
                ephemeral=True
            )

            return

        if not response:

            await interaction.response.send_message(
                "❌ The response cannot be empty.",
                ephemeral=True
            )

            return

        success = self.add_trigger(
            interaction.guild.id,
            trigger,
            response,
            interaction.user.id
        )

        if not success:

            await interaction.response.send_message(
                (
                    "❌ This trigger already exists "
                    "in this server."
                ),
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="✅ Trigger Created",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Trigger",
            value=f"`{trigger}`",
            inline=False
        )

        embed.add_field(
            name="Response",
            value=response,
            inline=False
        )

        embed.add_field(
            name="Status",
            value="🟢 Enabled",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # /TRIGGER REMOVE
    # =====================================================

    @trigger_group.command(
        name="remove",
        description="Remove an automatic trigger."
    )
    @app_commands.describe(
        trigger="Trigger to remove."
    )
    async def trigger_remove(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        success = self.remove_trigger(
            interaction.guild.id,
            trigger
        )

        if not success:

            await interaction.response.send_message(
                (
                    "❌ No trigger with that name "
                    "was found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🗑️ Trigger `{trigger}` "
                "has been removed."
            ),
            ephemeral=True
        )

    # =====================================================
    # /TRIGGER EDIT
    # =====================================================

    @trigger_group.command(
        name="edit",
        description="Change the response of a trigger."
    )
    @app_commands.describe(
        trigger="Trigger to edit.",
        response="New response."
    )
    async def trigger_edit(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        response = response.strip()

        if not response:

            await interaction.response.send_message(
                "❌ The response cannot be empty.",
                ephemeral=True
            )

            return

        success = self.edit_trigger(
            interaction.guild.id,
            trigger,
            response
        )

        if not success:

            await interaction.response.send_message(
                (
                    "❌ No trigger with that name "
                    "was found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"✏️ Trigger `{trigger}` "
                "has been updated."
            ),
            ephemeral=True
        )

    # =====================================================
    # /TRIGGER LIST
    # =====================================================

    @trigger_group.command(
        name="list",
        description="List all triggers in this server."
    )
    async def trigger_list(
        self,
        interaction: discord.Interaction
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        triggers = self.get_triggers(
            interaction.guild.id
        )

        if not triggers:

            await interaction.response.send_message(
                (
                    "📭 This server does not have "
                    "any triggers."
                ),
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="📋 Server Triggers",
            color=discord.Color.blurple()
        )

        lines = []

        for (
            trigger_id,
            trigger,
            response,
            enabled,
            created_by,
            created_at
        ) in triggers:

            status = (
                "🟢"
                if enabled
                else "🔴"
            )

            preview = response.replace(
                "\n",
                " "
            )

            if len(preview) > 100:

                preview = (
                    preview[:97]
                    + "..."
                )

            lines.append(
                (
                    f"{status} "
                    f"`{trigger}` → "
                    f"{preview}"
                )
            )

        description = "\n".join(
            lines
        )

        if len(description) > 4000:

            description = (
                description[:3997]
                + "..."
            )

        embed.description = description

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # /TRIGGER ENABLE
    # =====================================================

    @trigger_group.command(
        name="enable",
        description="Enable an automatic trigger."
    )
    @app_commands.describe(
        trigger="Trigger to enable."
    )
    async def trigger_enable(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        success = self.set_enabled(
            interaction.guild.id,
            trigger,
            True
        )

        if not success:

            await interaction.response.send_message(
                (
                    "❌ No trigger with that name "
                    "was found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🟢 Trigger `{trigger}` "
                "has been enabled."
            ),
            ephemeral=True
        )

    # =====================================================
    # /TRIGGER DISABLE
    # =====================================================

    @trigger_group.command(
        name="disable",
        description="Disable an automatic trigger."
    )
    @app_commands.describe(
        trigger="Trigger to disable."
    )
    async def trigger_disable(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if not await self.check_management_permission(
            interaction
        ):

            return

        success = self.set_enabled(
            interaction.guild.id,
            trigger,
            False
        )

        if not success:

            await interaction.response.send_message(
                (
                    f"🔴 Trigger `{trigger}` "
                    "has been disabled."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🔴 Trigger `{trigger}` "
                "has been disabled."
            ),
            ephemeral=True
        )

    # =====================================================
    # MESSAGE LISTENER
    # =====================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        # -------------------------------------------------
        # IGNORE BOTS
        # -------------------------------------------------

        if message.author.bot:

            return

        # -------------------------------------------------
        # IGNORE DMs
        # -------------------------------------------------

        if message.guild is None:

            return

        # -------------------------------------------------
        # PREMIUM
        # -------------------------------------------------

        if not self.has_premium(
            message.guild.id
        ):

            return

        # -------------------------------------------------
        # MESSAGE CONTENT
        # -------------------------------------------------

        content = message.content.strip()

        if not content:

            return

        content_lower = content.lower()

        # -------------------------------------------------
        # GET ACTIVE TRIGGERS
        # -------------------------------------------------

        triggers = self.get_active_triggers(
            message.guild.id
        )

        if not triggers:

            return

        # -------------------------------------------------
        # CHECK TRIGGERS
        # -------------------------------------------------

        for trigger, response in triggers:

            if trigger in content_lower:

                try:

                    await message.channel.send(
                        response,
                        allowed_mentions=discord.AllowedMentions(
                            everyone=False,
                            users=False,
                            roles=False
                        )
                    )

                except discord.Forbidden:

                    print(
                        (
                            "❌ Missing permission "
                            f"to respond in "
                            f"#{message.channel.name} "
                            f"in {message.guild.name}"
                        )
                    )

                except discord.HTTPException as error:

                    print(
                        (
                            "❌ Trigger response "
                            f"failed: {error}"
                        )
                    )

                # -------------------------------------------------
                # ONLY ONE TRIGGER PER MESSAGE
                # -------------------------------------------------

                break


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    cog = TriggerManager(
        bot
    )

    await bot.add_cog(
        cog
    )

    print(
        "TriggerManager carregado."
    )

    commands_list = (
        cog.get_app_commands()
    )

    print(
        f"Comandos do TriggerManager: "
        f"{len(commands_list)}"
    )

    for command in commands_list:

        print(
            f"   /{command.name}"
        )

        if isinstance(
            command,
            discord.app_commands.Group
        ):

            for subcommand in command.commands:

                print(
                    f"      /{command.name} "
                    f"{subcommand.name}"
                )

