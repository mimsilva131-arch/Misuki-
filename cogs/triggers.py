
# =========================================================
# MISUKI
# Trigger Manager
# =========================================================

import os

from datetime import datetime

import discord
import psycopg2

from discord import app_commands
from discord.ext import commands


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
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

        print(
            "TriggerManager carregado."
        )


    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    def get_connection(self):

        if not DATABASE_URL:

            raise RuntimeError(
                "DATABASE_URL não está configurado."
            )

        return psycopg2.connect(
            DATABASE_URL
        )


    # =====================================================
    # CREATE DATABASE
    # =====================================================

    def create_database(self):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS triggers (

                        id SERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        trigger TEXT NOT NULL,

                        response TEXT NOT NULL,

                        enabled BOOLEAN NOT NULL
                        DEFAULT TRUE,

                        created_at TIMESTAMP NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,

                        UNIQUE (
                            guild_id,
                            trigger
                        )

                    )
                    """
                )

            connection.commit()


    # =====================================================
    # CHECK LICENSE
    # =====================================================

    def has_active_license(
        self,
        guild_id
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        status,
                        expires_at
                    FROM licenses
                    WHERE guild_id = %s
                    """,
                    (
                        guild_id,
                    )
                )

                license_data = cursor.fetchone()

        if license_data is None:

            return False

        status = license_data[0]
        expires_at = license_data[1]

        if status != "active":

            return False

        if expires_at is None:

            return True

        # PostgreSQL pode devolver diretamente
        # um datetime.

        if isinstance(
            expires_at,
            datetime
        ):

            expiration = expires_at

        else:

            try:

                expiration = datetime.fromisoformat(
                    str(expires_at)
                )

            except ValueError:

                return False

        if datetime.now() >= expiration:

            with self.get_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        UPDATE licenses
                        SET status = 'expired'
                        WHERE guild_id = %s
                        """,
                        (
                            guild_id,
                        )
                    )

                connection.commit()

            return False

        return True


    # =====================================================
    # GET TRIGGER
    # =====================================================

    def get_trigger(
        self,
        guild_id,
        trigger
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        guild_id,
                        trigger,
                        response,
                        enabled,
                        created_at
                    FROM triggers
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    """,
                    (
                        guild_id,
                        trigger
                    )
                )

                return cursor.fetchone()


    # =====================================================
    # GET ALL TRIGGERS
    # =====================================================

    def get_triggers(
        self,
        guild_id
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        trigger,
                        response,
                        enabled
                    FROM triggers
                    WHERE guild_id = %s
                    ORDER BY trigger ASC
                    """,
                    (
                        guild_id,
                    )
                )

                return cursor.fetchall()


    # =====================================================
    # ADD TRIGGER
    # =====================================================

    def add_trigger(
        self,
        guild_id,
        trigger,
        response
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO triggers
                    (
                        guild_id,
                        trigger,
                        response,
                        enabled
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        TRUE
                    )
                    """,
                    (
                        guild_id,
                        trigger,
                        response
                    )
                )

            connection.commit()


    # =====================================================
    # REMOVE TRIGGER
    # =====================================================

    def remove_trigger(
        self,
        guild_id,
        trigger
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    DELETE FROM triggers
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    """,
                    (
                        guild_id,
                        trigger
                    )
                )

                deleted = (
                    cursor.rowcount > 0
                )

            connection.commit()

        return deleted


    # =====================================================
    # EDIT TRIGGER
    # =====================================================

    def edit_trigger(
        self,
        guild_id,
        trigger,
        response
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE triggers
                    SET response = %s
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    """,
                    (
                        response,
                        guild_id,
                        trigger
                    )
                )

                updated = (
                    cursor.rowcount > 0
                )

            connection.commit()

        return updated


    # =====================================================
    # ENABLE
    # =====================================================

    def enable_trigger(
        self,
        guild_id,
        trigger
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE triggers
                    SET enabled = TRUE
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    """,
                    (
                        guild_id,
                        trigger
                    )
                )

                updated = (
                    cursor.rowcount > 0
                )

            connection.commit()

        return updated


    # =====================================================
    # DISABLE
    # =====================================================

    def disable_trigger(
        self,
        guild_id,
        trigger
    ):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE triggers
                    SET enabled = FALSE
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    """,
                    (
                        guild_id,
                        trigger
                    )
                )

                updated = (
                    cursor.rowcount > 0
                )

            connection.commit()

        return updated


    # =====================================================
    # TRIGGER GROUP
    # =====================================================

    trigger_group = app_commands.Group(
        name="trigger",
        description="Manage Misuki triggers."
    )


    # =====================================================
    # /TRIGGER ADD
    # =====================================================

    @trigger_group.command(
        name="add",
        description="Create a new trigger."
    )
    @app_commands.describe(
        trigger="The word or phrase that activates the trigger.",
        response="The response sent by Misuki."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_add(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        trigger = trigger.strip()

        if not trigger:

            await interaction.response.send_message(
                "❌ The trigger cannot be empty.",
                ephemeral=True
            )

            return

        if not response.strip():

            await interaction.response.send_message(
                "❌ The response cannot be empty.",
                ephemeral=True
            )

            return

        existing = self.get_trigger(
            interaction.guild.id,
            trigger
        )

        if existing:

            await interaction.response.send_message(
                (
                    f"❌ The trigger "
                    f"`{trigger}` already exists."
                ),
                ephemeral=True
            )

            return

        try:

            self.add_trigger(
                interaction.guild.id,
                trigger,
                response
            )

        except Exception as error:

            print(
                f"❌ Error adding trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Could not create the trigger.",
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
        description="Remove a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to remove."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_remove(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        success = self.remove_trigger(
            interaction.guild.id,
            trigger.strip()
        )

        if not success:

            await interaction.response.send_message(
                (
                    f"❌ Trigger `{trigger}` "
                    "was not found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🗑️ Trigger `{trigger}` "
                "**removed successfully.**"
            ),
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER EDIT
    # =====================================================

    @trigger_group.command(
        name="edit",
        description="Edit a trigger response."
    )
    @app_commands.describe(
        trigger="The trigger to edit.",
        response="The new response."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_edit(
        self,
        interaction: discord.Interaction,
        trigger: str,
        response: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        if not response.strip():

            await interaction.response.send_message(
                "❌ The response cannot be empty.",
                ephemeral=True
            )

            return

        success = self.edit_trigger(
            interaction.guild.id,
            trigger.strip(),
            response
        )

        if not success:

            await interaction.response.send_message(
                (
                    f"❌ Trigger `{trigger}` "
                    "was not found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"✏️ Trigger `{trigger}` "
                "**updated successfully.**"
            ),
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER LIST
    # =====================================================

    @trigger_group.command(
        name="list",
        description="List all triggers."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_list(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        triggers = self.get_triggers(
            interaction.guild.id
        )

        if not triggers:

            await interaction.response.send_message(
                "📭 This server has no triggers.",
                ephemeral=True
            )

            return

        lines = []

        for (
            trigger_id,
            trigger,
            response,
            enabled
        ) in triggers:

            status = (
                "🟢"
                if enabled
                else "🔴"
            )

            lines.append(
                f"{status} `{trigger}` → {response}"
            )

        description = "\n".join(
            lines
        )

        # Discord embed descriptions have a
        # 4096-character limit.

        if len(description) > 4000:

            description = (
                description[:3990]
                + "\n..."
            )

        embed = discord.Embed(
            title="📋 Misuki Triggers",
            description=description,
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text=f"{len(triggers)} trigger(s)"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER ENABLE
    # =====================================================

    @trigger_group.command(
        name="enable",
        description="Enable a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to enable."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_enable(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        success = self.enable_trigger(
            interaction.guild.id,
            trigger.strip()
        )

        if not success:

            await interaction.response.send_message(
                (
                    f"❌ Trigger `{trigger}` "
                    "was not found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🟢 Trigger `{trigger}` "
                "**enabled.**"
            ),
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER DISABLE
    # =====================================================

    @trigger_group.command(
        name="disable",
        description="Disable a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to disable."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def trigger_disable(
        self,
        interaction: discord.Interaction,
        trigger: str
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_active_license(
            interaction.guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **Premium feature**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        success = self.disable_trigger(
            interaction.guild.id,
            trigger.strip()
        )

        if not success:

            await interaction.response.send_message(
                (
                    f"❌ Trigger `{trigger}` "
                    "was not found."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                f"🔴 Trigger `{trigger}` "
                "**disabled.**"
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
        # IGNORE DMS
        # -------------------------------------------------

        if message.guild is None:
            return

        # -------------------------------------------------
        # MESSAGE CONTENT
        # -------------------------------------------------

        content = message.content

        if not content:

            print(
                "⚠️ Mensagem sem conteúdo recebida "
                f"no servidor {message.guild.id}."
            )

            return

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        try:

            with self.get_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        SELECT
                            trigger,
                            response
                        FROM triggers
                        WHERE guild_id = %s
                        AND enabled = TRUE
                        """,
                        (
                            message.guild.id,
                        )
                    )

                    triggers = cursor.fetchall()

        except Exception as error:

            print(
                f"❌ Error reading triggers: {error}"
            )

            return

        # -------------------------------------------------
        # CHECK LICENSE
        # -------------------------------------------------

        if not self.has_active_license(
            message.guild.id
        ):

            return

        # -------------------------------------------------
        # CHECK TRIGGERS
        # -------------------------------------------------

        content_lower = content.lower()

        for (
            trigger,
            response
        ) in triggers:

            trigger_lower = (
                trigger.lower()
            )

            # -------------------------------------------------
            # EXACT WORD / PHRASE
            # -------------------------------------------------

            if trigger_lower in content_lower:

                try:

                    await message.channel.send(
                        response
                    )

                    print(
                        "⚡ Trigger activated: "
                        f"'{trigger}' "
                        f"in guild "
                        f"{message.guild.id}"
                    )

                except discord.Forbidden:

                    print(
                        "❌ No permission to send "
                        f"messages in channel "
                        f"{message.channel.id}"
                    )

                except discord.HTTPException as error:

                    print(
                        f"❌ Discord error sending "
                        f"trigger response: {error}"
                    )

                # -------------------------------------------------
                # ONLY FIRST MATCH
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
            f"/{command.name}"
        )

        if isinstance(
            command,
            discord.app_commands.Group
        ):

            for subcommand in command.commands:

                print(
                    f"/{command.name} "
                    f"{subcommand.name}"
                )
