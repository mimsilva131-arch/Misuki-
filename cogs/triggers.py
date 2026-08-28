
# =========================================================
# MISUKI - TRIGGERS
# =========================================================

import os

import psycopg2

import discord
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


# =========================================================
# TRIGGER MANAGER
# =========================================================

class TriggerManager(
    commands.GroupCog,
    group_name="trigger"
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        if not DATABASE_URL:

            print(
                "❌ DATABASE_URL não está configurado."
            )

            return

        self.create_database()


    # =====================================================
    # DATABASE CONNECTION
    # =====================================================

    def get_connection(
        self
    ):

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

    def create_database(
        self
    ):

        try:

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

                            UNIQUE(
                                guild_id,
                                trigger
                            )

                        )
                        """
                    )

                connection.commit()

            print(
                "⚡ Trigger database ready."
            )

        except Exception as error:

            print(
                f"❌ Trigger database error: {error}"
            )


    # =====================================================
    # GET TRIGGERS
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

                    ORDER BY id ASC
                    """,
                    (
                        guild_id,
                    )
                )

                return cursor.fetchall()


    # =====================================================
    # GET SINGLE TRIGGER
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
                        trigger,
                        response,
                        enabled

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
    # ON MESSAGE
    #
    # IMPORTANT:
    #
    # This listener receives messages sent by Discord.
    #
    # Bots are ignored BEFORE checking triggers.
    #
    # =====================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        print(
            "📩 EVENTO on_message RECEBIDO"
        )

        print(
            f"👤 Autor: {message.author} "
            f"(ID: {message.author.id})"
        )

        print(
            f"🤖 É bot: {message.author.bot}"
        )

        print(
            f"🏠 Guild: {message.guild}"
        )

        print(
            f"📝 Conteúdo: {message.content!r}"
        )


        # -------------------------------------------------
        # IGNORE BOT MESSAGES
        # -------------------------------------------------

        if message.author.bot:

            print(
                "🤖 Mensagem ignorada: autor é um bot."
            )

            return


        # -------------------------------------------------
        # IGNORE DMs
        # -------------------------------------------------

        if message.guild is None:

            print(
                "📨 Mensagem ignorada: DM."
            )

            return


        # -------------------------------------------------
        # CHECK MESSAGE CONTENT
        # -------------------------------------------------

        content = (
            message.content
            .strip()
            .lower()
        )


        if not content:

            print(
                "⚠️ A mensagem chegou sem conteúdo."
            )

            print(
                "⚠️ Confirma o Message Content Intent "
                "no Discord Developer Portal."
            )

            return


        print(
            f"🔤 Conteúdo processado: {content!r}"
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


        print(
            f"📋 Triggers encontrados: "
            f"{len(triggers)}"
        )


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


            print(
                f"🔎 A verificar: "
                f"{content!r} == {trigger_text!r}"
            )


            # -------------------------------------------------
            # EXACT MATCH
            # -------------------------------------------------

            if content != trigger_text:

                continue


            print(
                f"⚡ Trigger encontrado: {trigger}"
            )


            # -------------------------------------------------
            # SEND RESPONSE
            # -------------------------------------------------

            try:

                await message.channel.send(
                    response
                )

                print(
                    f"✅ Resposta enviada para "
                    f"'{trigger}'."
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


    # =====================================================
    # /TRIGGER ADD
    # =====================================================

    @app_commands.command(
        name="add",
        description="Add a new trigger."
    )
    @app_commands.describe(
        trigger="The word or phrase that activates the response.",
        response="The message the bot should send."
    )
    async def add(
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

                        VALUES (
                            %s,
                            %s,
                            %s,
                            TRUE
                        )
                        """,
                        (
                            interaction.guild.id,
                            trigger,
                            response
                        )
                    )

                connection.commit()


        except psycopg2.errors.UniqueViolation:

            await interaction.response.send_message(
                "❌ This trigger already exists.",
                ephemeral=True
            )

            return


        except Exception as error:

            print(
                f"❌ Error adding trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to add the trigger.",
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

    @app_commands.command(
        name="remove",
        description="Remove a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to remove."
    )
    async def remove(
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


        trigger = trigger.strip()


        try:

            with self.get_connection() as connection:

                with connection.cursor() as cursor:

                    cursor.execute(
                        """
                        DELETE FROM triggers

                        WHERE guild_id = %s

                        AND LOWER(trigger) = LOWER(%s)
                        """,
                        (
                            interaction.guild.id,
                            trigger
                        )
                    )

                    deleted = cursor.rowcount

                connection.commit()


        except Exception as error:

            print(
                f"❌ Error removing trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to remove the trigger.",
                ephemeral=True
            )

            return


        if deleted == 0:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return


        await interaction.response.send_message(
            f"🗑️ Trigger `{trigger}` removed.",
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER EDIT
    # =====================================================

    @app_commands.command(
        name="edit",
        description="Edit an existing trigger."
    )
    @app_commands.describe(
        trigger="The trigger to edit.",
        response="The new response."
    )
    async def edit(
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


        try:

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
                            interaction.guild.id,
                            trigger
                        )
                    )

                    updated = cursor.rowcount

                connection.commit()


        except Exception as error:

            print(
                f"❌ Error editing trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to edit the trigger.",
                ephemeral=True
            )

            return


        if updated == 0:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return


        await interaction.response.send_message(
            f"✅ Trigger `{trigger}` updated.",
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER LIST
    # =====================================================

    @app_commands.command(
        name="list",
        description="List all triggers."
    )
    async def list(
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
                f"❌ Error listing triggers: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to load triggers.",
                ephemeral=True
            )

            return


        if not triggers:

            await interaction.response.send_message(
                "📭 No triggers have been configured.",
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
                "🟢 Enabled"
                if enabled
                else "🔴 Disabled"
            )


            lines.append(
                f"**{trigger}** — {status}\n"
                f"└ {response}"
            )


        embed = discord.Embed(
            title="⚡ Misuki Triggers",
            description="\n\n".join(lines),
            color=discord.Color.blurple()
        )


        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER ENABLE
    # =====================================================

    @app_commands.command(
        name="enable",
        description="Enable a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to enable."
    )
    async def enable(
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


        trigger = trigger.strip()


        try:

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
                            interaction.guild.id,
                            trigger
                        )
                    )

                    updated = cursor.rowcount

                connection.commit()


        except Exception as error:

            print(
                f"❌ Error enabling trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to enable the trigger.",
                ephemeral=True
            )

            return


        if updated == 0:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return


        await interaction.response.send_message(
            f"🟢 Trigger `{trigger}` enabled.",
            ephemeral=True
        )


    # =====================================================
    # /TRIGGER DISABLE
    # =====================================================

    @app_commands.command(
        name="disable",
        description="Disable a trigger."
    )
    @app_commands.describe(
        trigger="The trigger to disable."
    )
    async def disable(
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


        trigger = trigger.strip()


        try:

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
                            interaction.guild.id,
                            trigger
                        )
                    )

                    updated = cursor.rowcount

                connection.commit()


        except Exception as error:

            print(
                f"❌ Error disabling trigger: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to disable the trigger.",
                ephemeral=True
            )

            return


        if updated == 0:

            await interaction.response.send_message(
                "❌ Trigger not found.",
                ephemeral=True
            )

            return


        await interaction.response.send_message(
            f"🔴 Trigger `{trigger}` disabled.",
            ephemeral=True
        )


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
        "⚡ TriggerManager carregado."
    )


    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

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

