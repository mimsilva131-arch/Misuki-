# =========================================================
# MISUKI - TRIGGERS
# =========================================================

import os
import time

import psycopg2

import discord
from discord import app_commands
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class TriggerManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.trigger_group = app_commands.Group(
            name="trigger",
            description="Manage server triggers."
        )

        # Trigger definitions are cached per guild. Message events therefore
        # do not open a PostgreSQL connection on every message.
        self._trigger_cache = {}
        self._trigger_cache_ttl = max(
            30,
            min(int(os.getenv("TRIGGER_CACHE_TTL", "300")), 900)
        )

        if not DATABASE_URL:
            print("❌ DATABASE_URL não está configurado.")
            return

        self.create_database()

    def cog_unload(self):
        self._trigger_cache.clear()

    def get_connection(self):
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL não está configurado.")
        return psycopg2.connect(DATABASE_URL, connect_timeout=10)

    def create_database(self):
        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS triggers (
                            id SERIAL PRIMARY KEY,
                            guild_id BIGINT NOT NULL,
                            trigger TEXT NOT NULL,
                            response TEXT NOT NULL,
                            enabled BOOLEAN NOT NULL DEFAULT TRUE,
                            UNIQUE (guild_id, trigger)
                        )
                    """)
                connection.commit()
            print("⚡ Trigger database ready.")
        except Exception as error:
            print(f"❌ Trigger database error: {error}")

    def invalidate_trigger_cache(self, guild_id):
        self._trigger_cache.pop(int(guild_id), None)

    def get_triggers(self, guild_id):
        guild_id = int(guild_id)
        now = time.monotonic()

        cached = self._trigger_cache.get(guild_id)
        if cached is not None:
            expires_at, triggers = cached
            if now < expires_at:
                return triggers

        with self.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, trigger, response, enabled
                    FROM triggers
                    WHERE guild_id = %s
                    ORDER BY id ASC
                """, (guild_id,))
                triggers = cursor.fetchall()

        self._trigger_cache[guild_id] = (
            now + self._trigger_cache_ttl,
            triggers
        )
        return triggers

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        content = message.content.strip().lower()
        if not content:
            return

        try:
            triggers = self.get_triggers(message.guild.id)
        except Exception as error:
            print(f"❌ Trigger database error: {error}")
            return

        for _, trigger, response, enabled in triggers:
            if enabled and content == str(trigger).strip().lower():
                try:
                    await message.channel.send(response)
                except discord.Forbidden:
                    pass
                except discord.HTTPException as error:
                    print(f"❌ Discord API error: {error}")
                break

    @app_commands.command(name="add", description="Add a new trigger.")
    @app_commands.describe(
        trigger="The word or phrase that activates the response.",
        response="The message the bot should send."
    )
    async def add(self, interaction: discord.Interaction, trigger: str, response: str):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        trigger = trigger.strip()
        response = response.strip()

        if not trigger or not response:
            await interaction.response.send_message(
                "❌ The trigger and response cannot be empty.",
                ephemeral=True
            )
            return

        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO triggers (guild_id, trigger, response, enabled)
                        VALUES (%s, %s, %s, TRUE)
                    """, (interaction.guild.id, trigger, response))
                connection.commit()
        except psycopg2.errors.UniqueViolation:
            await interaction.response.send_message(
                "❌ This trigger already exists.",
                ephemeral=True
            )
            return
        except Exception as error:
            print(f"❌ Error adding trigger: {error}")
            await interaction.response.send_message(
                "❌ Failed to add the trigger.",
                ephemeral=True
            )
            return

        self.invalidate_trigger_cache(interaction.guild.id)
        await interaction.response.send_message(
            f"✅ **Trigger added.**\n\nTrigger: `{trigger}`\nResponse: {response}",
            ephemeral=True
        )

    @app_commands.command(name="remove", description="Remove a trigger.")
    @app_commands.describe(trigger="The trigger to remove.")
    async def remove(self, interaction: discord.Interaction, trigger: str):
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
                    cursor.execute("""
                        DELETE FROM triggers
                        WHERE guild_id = %s
                        AND LOWER(trigger) = LOWER(%s)
                    """, (interaction.guild.id, trigger))
                    deleted = cursor.rowcount
                connection.commit()
        except Exception as error:
            print(f"❌ Error removing trigger: {error}")
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

        self.invalidate_trigger_cache(interaction.guild.id)
        await interaction.response.send_message(
            f"🗑️ Trigger `{trigger}` removed.",
            ephemeral=True
        )

    @app_commands.command(name="edit", description="Edit an existing trigger.")
    @app_commands.describe(
        trigger="The trigger to edit.",
        response="The new response."
    )
    async def edit(self, interaction: discord.Interaction, trigger: str, response: str):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        trigger = trigger.strip()
        response = response.strip()

        if not trigger or not response:
            await interaction.response.send_message(
                "❌ The trigger and response cannot be empty.",
                ephemeral=True
            )
            return

        try:
            with self.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE triggers
                        SET response = %s
                        WHERE guild_id = %s
                        AND LOWER(trigger) = LOWER(%s)
                    """, (response, interaction.guild.id, trigger))
                    updated = cursor.rowcount
                connection.commit()
        except Exception as error:
            print(f"❌ Error editing trigger: {error}")
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

        self.invalidate_trigger_cache(interaction.guild.id)
        await interaction.response.send_message(
            f"✅ Trigger `{trigger}` updated.",
            ephemeral=True
        )

    @app_commands.command(name="list", description="List all triggers.")
    async def list(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        try:
            triggers = self.get_triggers(interaction.guild.id)
        except Exception as error:
            print(f"❌ Error listing triggers: {error}")
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
        for _, trigger, response, enabled in triggers:
            status = "🟢 Enabled" if enabled else "🔴 Disabled"
            lines.append(f"**{trigger}** — {status}\n└ {response}")

        description = "\n\n".join(lines)
        if len(description) > 4096:
            description = description[:4080] + "\n\n..."

        embed = discord.Embed(
            title="⚡ Misuki Triggers",
            description=description,
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(name="enable", description="Enable a trigger.")
    @app_commands.describe(trigger="The trigger to enable.")
    async def enable(self, interaction: discord.Interaction, trigger: str):
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
                    cursor.execute("""
                        UPDATE triggers
                        SET enabled = TRUE
                        WHERE guild_id = %s
                        AND LOWER(trigger) = LOWER(%s)
                    """, (interaction.guild.id, trigger))
                    updated = cursor.rowcount
                connection.commit()
        except Exception as error:
            print(f"❌ Error enabling trigger: {error}")
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

        self.invalidate_trigger_cache(interaction.guild.id)
        await interaction.response.send_message(
            f"🟢 Trigger `{trigger}` enabled.",
            ephemeral=True
        )

    @app_commands.command(name="disable", description="Disable a trigger.")
    @app_commands.describe(trigger="The trigger to disable.")
    async def disable(self, interaction: discord.Interaction, trigger: str):
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
                    cursor.execute("""
                        UPDATE triggers
                        SET enabled = FALSE
                        WHERE guild_id = %s
                        AND LOWER(trigger) = LOWER(%s)
                    """, (interaction.guild.id, trigger))
                    updated = cursor.rowcount
                connection.commit()
        except Exception as error:
            print(f"❌ Error disabling trigger: {error}")
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

        self.invalidate_trigger_cache(interaction.guild.id)
        await interaction.response.send_message(
            f"🔴 Trigger `{trigger}` disabled.",
            ephemeral=True
        )

    async def cog_load(self):
        return


async def setup(bot):
    cog = TriggerManager(bot)
    await bot.add_cog(cog)

    commands_list = list(cog.get_app_commands())
    for command in commands_list:
        bot.tree.remove_command(command.name)
        cog.trigger_group.add_command(command)

    bot.tree.add_command(cog.trigger_group)

    print(f"⚡ TriggerManager commands registered: {len(cog.trigger_group.commands)}")
    for command in cog.trigger_group.commands:
        print(f"/trigger {command.name}")
