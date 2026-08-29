# =========================================================
# MISUKI MODERATION SYSTEM
# Discord.py
# =========================================================

import os
import sqlite3

from datetime import datetime, timedelta, timezone

import discord

from discord import app_commands
from discord.ext import commands


# =========================================================
# DATABASE
# =========================================================

DATABASE = "data/moderation.db"


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():

    os.makedirs("data", exist_ok=True)

    with sqlite3.connect(DATABASE) as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        db.commit()


# =========================================================
# CONFIG
# =========================================================

def get_config(bot):

    return bot.get_cog("Config")


async def get_log_channel(bot, guild):

    if guild is None:
        return None

    config = get_config(bot)

    if config is None:
        return None

    try:

        channel_id = config.get_channel_value(
            guild.id,
            "moderation_log_channel_id"
        )

        if not channel_id:
            return None

        channel = guild.get_channel(
            int(channel_id)
        )

        if isinstance(
            channel,
            discord.TextChannel
        ):
            return channel

    except Exception as error:

        print(
            f"[Moderation] Error getting log channel: {error}"
        )

    return None


# =========================================================
# MODERATION LOG
# =========================================================

async def send_mod_log(
    bot,
    guild,
    action,
    target,
    moderator,
    reason,
    color=discord.Color.blurple()
):

    try:

        if guild is None:
            return

        channel = await get_log_channel(
            bot,
            guild
        )

        if channel is None:
            return

        embed = discord.Embed(
            title=f"🛡️ {action}",
            color=color,
            timestamp=datetime.now(
                timezone.utc
            )
        )

        # -------------------------------------------------
        # TARGET
        # -------------------------------------------------

        if isinstance(
            target,
            discord.Member
        ):

            target_text = (
                f"{target.mention}\n"
                f"`{target.id}`"
            )

        elif isinstance(
            target,
            discord.User
        ):

            target_text = (
                f"**{target}**\n"
                f"`{target.id}`"
            )

        else:

            target_text = (
                f"**{target}**"
            )

        embed.add_field(
            name="👤 User",
            value=target_text,
            inline=True
        )

        # -------------------------------------------------
        # MODERATOR
        # -------------------------------------------------

        if isinstance(
            moderator,
            discord.Member
        ):

            moderator_text = (
                f"{moderator.mention}\n"
                f"`{moderator.id}`"
            )

        elif isinstance(
            moderator,
            discord.User
        ):

            moderator_text = (
                f"**{moderator}**\n"
                f"`{moderator.id}`"
            )

        else:

            moderator_text = str(
                moderator
            )

        embed.add_field(
            name="🛡️ Moderator",
            value=moderator_text,
            inline=True
        )

        # -------------------------------------------------
        # REASON
        # -------------------------------------------------

        if not reason:
            reason = "No reason provided."

        if len(reason) > 1024:
            reason = reason[:1021] + "..."

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        # -------------------------------------------------
        # AVATAR
        # -------------------------------------------------

        if hasattr(
            target,
            "display_avatar"
        ):

            embed.set_thumbnail(
                url=target.display_avatar.url
            )

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        embed.set_footer(
            text="Misuki • Moderation"
        )

        await channel.send(
            embed=embed
        )

    except Exception as error:

        print(
            f"[Moderation] Error sending log: {error}"
        )


# =========================================================
# DM
# =========================================================

async def send_dm(
    user,
    title,
    description,
    color=discord.Color.blurple()
):

    try:

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(
                timezone.utc
            )
        )

        embed.set_footer(
            text="Misuki • Moderation"
        )

        await user.send(
            embed=embed
        )

    except (
        discord.Forbidden,
        discord.HTTPException
    ):

        pass


# =========================================================
# MODERATION COG
# =========================================================

class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot


    # =====================================================
    # HIERARCHY
    # =====================================================

    def can_moderate(
        self,
        moderator,
        target
    ):

        if not isinstance(
            moderator,
            discord.Member
        ):

            return False

        if not isinstance(
            target,
            discord.Member
        ):

            return False

        # -------------------------------------------------
        # SELF
        # -------------------------------------------------

        if target.id == moderator.id:
            return False

        # -------------------------------------------------
        # BOT
        # -------------------------------------------------

        if self.bot.user:

            if target.id == self.bot.user.id:
                return False

        # -------------------------------------------------
        # SERVER OWNER
        # -------------------------------------------------

        if target.id == moderator.guild.owner_id:
            return False

        # -------------------------------------------------
        # MODERATOR HIERARCHY
        # -------------------------------------------------

        if target.top_role >= moderator.top_role:

            return False

        # -------------------------------------------------
        # BOT HIERARCHY
        # -------------------------------------------------

        bot_member = moderator.guild.me

        if bot_member is None:
            return False

        if target.top_role >= bot_member.top_role:

            return False

        return True


    # =====================================================
    # WARN
    # =====================================================

    @app_commands.command(
        name="warn",
        description="Warns a member."
    )
    @app_commands.describe(
        member="Member to warn.",
        reason="Reason for the warning."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        try:

            with sqlite3.connect(
                DATABASE
            ) as db:

                cursor = db.cursor()

                cursor.execute(
                    """
                    INSERT INTO warnings
                    (
                        guild_id,
                        user_id,
                        moderator_id,
                        reason,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        guild.id,
                        member.id,
                        interaction.user.id,
                        reason,
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )
                )

                warning_id = cursor.lastrowid

                db.commit()

        except Exception as error:

            print(
                f"[Moderation] Database error: {error}"
            )

            await interaction.followup.send(
                "❌ An error occurred while saving the warning."
            )

            return

        # -------------------------------------------------
        # DM
        # -------------------------------------------------

        await send_dm(
            member,
            "⚠️ You received a warning",
            (
                f"**Server:** {guild.name}\n"
                f"**Reason:** {reason}\n"
                f"**Warning ID:** #{warning_id}"
            ),
            discord.Color.orange()
        )

        # -------------------------------------------------
        # LOG
        # -------------------------------------------------

        await send_mod_log(
            self.bot,
            guild,
            "Warning Issued",
            member,
            interaction.user,
            (
                f"{reason}\n"
                f"Warning ID: #{warning_id}"
            ),
            discord.Color.orange()
        )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=(
                f"{member.mention} has received a warning."
            ),
            color=discord.Color.orange()
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="🔢 ID",
            value=f"#{warning_id}",
            inline=True
        )

        await interaction.followup.send(
            embed=embed
        )


    # =====================================================
    # WARNINGS
    # =====================================================

    @app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    @app_commands.describe(
        member="Member."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def warnings(
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
                "❌ This command can only be used in a server."
            )

            return

        try:

            with sqlite3.connect(
                DATABASE
            ) as db:

                cursor = db.cursor()

                cursor.execute(
                    """
                    SELECT
                        id,
                        moderator_id,
                        reason,
                        created_at
                    FROM warnings
                    WHERE guild_id = ?
                    AND user_id = ?
                    ORDER BY id DESC
                    """,
                    (
                        guild.id,
                        member.id
                    )
                )

                rows = cursor.fetchall()

        except Exception as error:

            print(
                f"[Moderation] Error getting warnings: {error}"
            )

            await interaction.followup.send(
                "❌ An error occurred while retrieving the warnings."
            )

            return

        embed = discord.Embed(
            title=f"📋 Warnings — {member.display_name}",
            color=discord.Color.orange()
        )

        if not rows:

            embed.description = (
                "✅ This member has no warnings."
            )

            await interaction.followup.send(
                embed=embed
            )

            return

        text = ""

        for (
            warning_id,
            moderator_id,
            warning_reason,
            created_at
        ) in rows[:10]:

            try:

                date = datetime.fromisoformat(
                    created_at
                ).strftime(
                    "%d/%m/%Y %H:%M"
                )

            except Exception:

                date = created_at

            text += (
                f"**#{warning_id}** — "
                f"{warning_reason}\n"
                f"🛡️ <@{moderator_id}> • "
                f"🕐 {date}\n\n"
            )

        # Discord embed description limit
        if len(text) > 4096:

            text = text[:4093] + "..."

        embed.description = text

        if len(rows) > 10:

            embed.set_footer(
                text=(
                    f"Showing 10 of "
                    f"{len(rows)} warnings."
                )
            )

        await interaction.followup.send(
            embed=embed
        )


    # =====================================================
    # UNWARN
    # =====================================================

    @app_commands.command(
        name="unwarn",
        description="Remove a specific warning."
    )
    @app_commands.describe(
        member="Member.",
        warning_id="Warning ID.",
        reason="Reason for removing the warning."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def unwarn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        warning_id: int,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        try:

            with sqlite3.connect(
                DATABASE
            ) as db:

                cursor = db.cursor()

                cursor.execute(
                    """
                    SELECT reason
                    FROM warnings
                    WHERE id = ?
                    AND guild_id = ?
                    AND user_id = ?
                    """,
                    (
                        warning_id,
                        guild.id,
                        member.id
                    )
                )

                warning = cursor.fetchone()

                if warning is None:

                    await interaction.followup.send(
                        f"❌ Warning **#{warning_id}** "
                        f"does not exist for this member."
                    )

                    return

                original_reason = warning[0]

                cursor.execute(
                    """
                    DELETE FROM warnings
                    WHERE id = ?
                    AND guild_id = ?
                    AND user_id = ?
                    """,
                    (
                        warning_id,
                        guild.id,
                        member.id
                    )
                )

                db.commit()

        except Exception as error:

            print(
                f"[Moderation] Error in unwarn: {error}"
            )

            await interaction.followup.send(
                "❌ An error occurred while removing the warning."
            )

            return

        await send_dm(
            member,
            "✅ Warning Removed",
            (
                f"**Server:** {guild.name}\n"
                f"**Warning:** #{warning_id}\n"
                f"**Removal reason:** {reason}"
            ),
            discord.Color.green()
        )

        await send_mod_log(
            self.bot,
            guild,
            "Warning Removed",
            member,
            interaction.user,
            (
                f"ID: #{warning_id}\n"
                f"Original reason: {original_reason}\n"
                f"Removal reason: {reason}"
            ),
            discord.Color.green()
        )

        await interaction.followup.send(
            f"✅ Warning **#{warning_id}** has been "
            f"removed from {member.mention}."
        )


    # =====================================================
    # CLEAR WARNINGS
    # =====================================================

    @app_commands.command(
        name="clearwarnings",
        description="Remove all warnings from a member."
    )
    @app_commands.describe(
        member="Member.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def clearwarnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        try:

            with sqlite3.connect(
                DATABASE
            ) as db:

                cursor = db.cursor()

                cursor.execute(
                    """
                    DELETE FROM warnings
                    WHERE guild_id = ?
                    AND user_id = ?
                    """,
                    (
                        guild.id,
                        member.id
                    )
                )

                removed = cursor.rowcount

                db.commit()

        except Exception as error:

            print(
                f"[Moderation] Error clearing warnings: {error}"
            )

            await interaction.followup.send(
                "❌ An error occurred while clearing the warnings."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Warnings Cleared",
            member,
            interaction.user,
            (
                f"{reason}\n"
                f"Warnings removed: {removed}"
            ),
            discord.Color.green()
        )

        await interaction.followup.send(
            f"✅ Removed **{removed}** warning(s) "
            f"from {member.mention}."
        )


    # =====================================================
    # CLEAR
    # =====================================================

    @app_commands.command(
        name="clear",
        description="Delete messages from a channel."
    )
    @app_commands.describe(
        amount="Number of messages to delete."
    )
    @app_commands.default_permissions(
        manage_messages=True
    )
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        guild = interaction.guild
        channel = interaction.channel

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not isinstance(
            channel,
            discord.TextChannel
        ):

            await interaction.followup.send(
                "❌ This command cannot be used in this channel."
            )

            return

        try:

            deleted = await channel.purge(
                limit=amount
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to delete messages."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Clear error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while deleting messages."
            )

            return

        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)}** messages."
        )

        await send_mod_log(
            self.bot,
            guild,
            "Messages Cleared",
            interaction.user,
            interaction.user,
            f"{len(deleted)} messages deleted.",
            discord.Color.blurple()
        )


    # =====================================================
    # TIMEOUT
    # =====================================================

    @app_commands.command(
        name="timeout",
        description="Timeout a member."
    )
    @app_commands.describe(
        member="Member.",
        duration="Duration in minutes.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: app_commands.Range[int, 1, 40320],
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        until = (
            discord.utils.utcnow()
            + timedelta(minutes=duration)
        )

        try:

            await member.timeout(
                until,
                reason=reason
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to timeout this member."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Timeout error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while applying the timeout."
            )

            return

        await send_dm(
            member,
            "🔇 You received a timeout",
            (
                f"**Server:** {guild.name}\n"
                f"**Duration:** {duration} minute(s)\n"
                f"**Reason:** {reason}"
            ),
            discord.Color.red()
        )

        await send_mod_log(
            self.bot,
            guild,
            "Timeout Applied",
            member,
            interaction.user,
            (
                f"{reason}\n"
                f"Duration: {duration} minute(s)"
            ),
            discord.Color.red()
        )

        await interaction.followup.send(
            f"🔇 {member.mention} has been timed out "
            f"for **{duration} minute(s)**."
        )


    # =====================================================
    # UNTIMEOUT
    # =====================================================

    @app_commands.command(
        name="untimeout",
        description="Remove a member's timeout."
    )
    @app_commands.describe(
        member="Member.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        try:

            await member.timeout(
                None,
                reason=reason
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to remove the timeout."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Untimeout error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while removing the timeout."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Timeout Removed",
            member,
            interaction.user,
            reason,
            discord.Color.green()
        )

        await interaction.followup.send(
            f"🔊 The timeout has been removed from "
            f"{member.mention}."
        )


    # =====================================================
    # KICK
    # =====================================================

    @app_commands.command(
        name="kick",
        description="Kick a member."
    )
    @app_commands.describe(
        member="Member.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        kick_members=True
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        # -------------------------------------------------
        # DM BEFORE KICK
        # -------------------------------------------------

        await send_dm(
            member,
            "👢 You were kicked",
            (
                f"**Server:** {guild.name}\n"
                f"**Reason:** {reason}"
            ),
            discord.Color.red()
        )

        try:

            await member.kick(
                reason=reason
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to kick this member."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Kick error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while kicking this member."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Member Kicked",
            member,
            interaction.user,
            reason,
            discord.Color.red()
        )

        await interaction.followup.send(
            f"👢 **{member}** has been kicked from the server."
        )


    # =====================================================
    # BAN
    # =====================================================

    @app_commands.command(
        name="ban",
        description="Ban a member."
    )
    @app_commands.describe(
        member="Member.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        ban_members=True
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        await send_dm(
            member,
            "🔨 You were banned",
            (
                f"**Server:** {guild.name}\n"
                f"**Reason:** {reason}"
            ),
            discord.Color.dark_red()
        )

        try:

            await member.ban(
                reason=reason,
                delete_message_seconds=0
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to ban this member."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Ban error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while banning this member."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Member Banned",
            member,
            interaction.user,
            reason,
            discord.Color.dark_red()
        )

        await interaction.followup.send(
            f"🔨 **{member}** has been banned from the server."
        )


    # =====================================================
    # UNBAN
    # =====================================================

    @app_commands.command(
        name="unban",
        description="Unban a user."
    )
    @app_commands.describe(
        user_id="User ID.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        ban_members=True
    )
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        try:

            parsed_id = int(
                user_id
            )

        except ValueError:

            await interaction.followup.send(
                "❌ The user ID is invalid."
            )

            return

        try:

            user = await self.bot.fetch_user(
                parsed_id
            )

        except (
            discord.NotFound,
            discord.HTTPException
        ):

            await interaction.followup.send(
                "❌ The user could not be found."
            )

            return

        try:

            await guild.unban(
                user,
                reason=reason
            )

        except discord.NotFound:

            await interaction.followup.send(
                "❌ This user is not banned."
            )

            return

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to unban this user."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Unban error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while unbanning this user."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Member Unbanned",
            user,
            interaction.user,
            reason,
            discord.Color.green()
        )

        await interaction.followup.send(
            f"🔓 **{user}** has been unbanned."
        )


    # =====================================================
    # SOFTBAN
    # =====================================================

    @app_commands.command(
        name="softban",
        description="Ban and immediately unban a member."
    )
    @app_commands.describe(
        member="Member.",
        reason="Reason."
    )
    @app_commands.default_permissions(
        ban_members=True
    )
    async def softban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        await interaction.response.defer()

        guild = interaction.guild

        if guild is None:

            await interaction.followup.send(
                "❌ This command can only be used in a server."
            )

            return

        if not self.can_moderate(
            interaction.user,
            member
        ):

            await interaction.followup.send(
                "❌ You cannot moderate this member."
            )

            return

        # -------------------------------------------------
        # SAVE USER BEFORE BAN
        # -------------------------------------------------

        user = member

        try:

            await member.ban(
                reason=reason,
                delete_message_seconds=86400
            )

            await guild.unban(
                user,
                reason="Softban"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ I do not have permission to softban this member."
            )

            return

        except discord.HTTPException as error:

            print(
                f"[Moderation] Softban error: {error}"
            )

            await interaction.followup.send(
                "❌ A Discord error occurred while softbanning this member."
            )

            return

        await send_mod_log(
            self.bot,
            guild,
            "Softban",
            user,
            interaction.user,
            reason,
            discord.Color.orange()
        )

        await interaction.followup.send(
            f"🧹 **{user}** has received a softban."
        )


# =========================================================
# SETUP
# =========================================================

async def setup(bot):

    init_database()

    await bot.add_cog(
        Moderation(bot)
    )

    print(
        "🛡️ Moderation carregado."
    )

    print(
        "🛡️ Comandos de moderação carregados."
    )