
# =========================================================
# MISUKI
# TRIGGER MANAGER
# PostgreSQL / NEON
# =========================================================

import os
import psycopg2

import discord

from discord import app_commands
from discord.ext import commands


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv("DATABASE_URL")


# =========================================================
# TRIGGER MANAGER
# =========================================================

class TriggerManager(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.create_database()

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
    # DATABASE SETUP
    # =====================================================

    def create_database(self):

        with self.get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS triggers (

                        id SERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        trigger TEXT NOT NULL,

                        response TEXT NOT NULL,

                        enabled BOOLEAN NOT NULL
                        DEFAULT TRUE,

                        UNIQUE (
                            guild_id,
                            trigger
                        )
                    )
                """)

            connection.commit()

        print(
            "⚡ Tabela de triggers verificada."
        )

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

                cursor.execute("""
                    SELECT
                        id,
                        guild_id,
                        trigger,
                        response,
                        enabled
                    FROM triggers
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                """, (
                    guild_id,
                    trigger
                ))

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

                cursor.execute("""
                    SELECT
                        id,
                        trigger,
                        response,
                        enabled
                    FROM triggers
                    WHERE guild_id = %s
                    ORDER BY id ASC
                """, (
                    guild_id,
                ))

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

        try:

            with self.get_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute("""
                        INSERT INTO triggers
                        (
                            guild_id,
                            trigger,
                            response,
                            enabled
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            TRUE
                        )
                        RETURNING id
                    """, (
                        guild_id,
                        trigger,
                        response
                    ))

                    trigger_id = cursor.fetchone()[0]

                connection.commit()

            return trigger_id

        except psycopg2.errors.UniqueViolation:

            return None

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

                cursor.execute("""
                    DELETE FROM triggers
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    RETURNING id
                """, (
                    guild_id,
                    trigger
                ))

                result = cursor.fetchone()

            connection.commit()

        return result is not None

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

                cursor.execute("""
                    UPDATE triggers
                    SET response = %s
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    RETURNING id
                """, (
                    response,
                    guild_id,
                    trigger
                ))

                result = cursor.fetchone()

            connection.commit()

        return result is not None

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

                cursor.execute("""
                    UPDATE triggers
                    SET enabled = TRUE
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    RETURNING id
                """, (
                    guild_id,
                    trigger
                ))

                result = cursor.fetchone()

            connection.commit()

        return result is not None

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

                cursor.execute("""
                    UPDATE triggers
                    SET enabled = FALSE
                    WHERE guild_id = %s
                    AND LOWER(trigger) = LOWER(%s)
                    RETURNING id
                """, (
                    guild_id,
                    trigger
                ))

                result = cursor.fetchone()

            connection.commit()

        return result is not None

    # =====================================================
    # /TRIGGER
    # =====================================================

    trigger_group = app_commands.Group(
        name="trigger",
        description="Manage server triggers."
    )

    # =====================================================
    # /TRIGGER ADD
    # =====================================================

    @trigger_group.command(
        name="add",
        description="Add a new trigger."
    )
    @app_commands.describe(
        trigger="The word or phrase that activates the trigger.",
        response="The message the bot will send."
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

        trigger = trigger.strip()

        if not trigger:

            await interaction.response.send_message(
                "❌ The trigger cannot be empty.",
                ephemeral=True
            )

            return

        try:

            trigger_id = self.add_trigger(
                interaction.guild.id,
                trigger,
                response
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to save the trigger.",
                ephemeral=True
            )

            return

        if trigger_id is None:

            await interaction.response.send_message(
                (
                    "❌ This trigger already exists "
                    "in this server."
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "✅ **Trigger added.**\n\n"
                f"Trigger: `{trigger}`\n"
                f"Response: {response}"
            ),
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

        try:

            success = self.remove_trigger(
                interaction.guild.id,
                trigger.strip()
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to remove the trigger.",
                ephemeral=True
            )

            return

        if not success:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "🗑️ **Trigger removed.**\n\n"
                f"Trigger: `{trigger}`"
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

        try:

            success = self.edit_trigger(
                interaction.guild.id,
                trigger.strip(),
                response
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to edit the trigger.",
                ephemeral=True
            )

            return

        if not success:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "✏️ **Trigger updated.**\n\n"
                f"Trigger: `{trigger}`\n"
                f"New response: {response}"
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

        try:

            triggers = self.get_triggers(
                interaction.guild.id
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to load triggers.",
                ephemeral=True
            )

            return

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

        embed = discord.Embed(
            title="⚡ Misuki Triggers",
            description=description,
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Misuki • Trigger System"
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

        try:

            success = self.enable_trigger(
                interaction.guild.id,
                trigger.strip()
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to enable the trigger.",
                ephemeral=True
            )

            return

        if not success:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "🟢 **Trigger enabled.**\n\n"
                f"Trigger: `{trigger}`"
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

        try:

            success = self.disable_trigger(
                interaction.guild.id,
                trigger.strip()
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to disable the trigger.",
                ephemeral=True
            )

            return

        if not success:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "🔴 **Trigger disabled.**\n\n"
                f"Trigger: `{trigger}`"
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
        # EMPTY MESSAGE
        # -------------------------------------------------

        if not message.content:

            return

        content = (
            message.content
            .strip()
            .lower()
        )

        print(
            f"📩 Mensagem recebida: "
            f"{message.content!r}"
        )

        print(
            f"👤 Autor: {message.author}"
        )

        print(
            f"🏠 Guild: {message.guild}"
        )

        # -------------------------------------------------
        # GET TRIGGERS
        # -------------------------------------------------

        try:

            triggers = self.get_triggers(
                message.guild.id
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )

            return

        # -------------------------------------------------
        # CHECK TRIGGERS
        # -------------------------------------------------

        for (
            trigger_id,
            trigger,
            response,
            enabled
        ) in triggers:

            if not enabled:

                continue

            trigger_text = (
                trigger
                .strip()
                .lower()
            )

            # Exact message match
            if content == trigger_text:

                try:

                    # -------------------------------------------------
                    # PUBLIC CHANNEL MESSAGE
                    # -------------------------------------------------

                    await message.channel.send(
                        response
                    )

                    print(
                        f"⚡ Trigger ativado: "
                        f"{trigger}"
                    )

                except discord.Forbidden:

                    print(
                        "❌ Não tenho permissão "
                        "para enviar mensagens neste canal."
                    )

                except discord.HTTPException as error:

                    print(
                        f"❌ Discord API error: {error}"
                    )

                break

        # -------------------------------------------------
        # COMMAND PROCESSING
        # -------------------------------------------------

        await self.bot.process_commands(
            message
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot):

    cog = TriggerManager(
        bot
    )

    await bot.add_cog(
        cog
    )

    print(
        "⚡ TriggerManager carregado."
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
            f"/trigger {command.name}"
        )

