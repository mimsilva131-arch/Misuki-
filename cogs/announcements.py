# =========================================================
# MISUKI - ANNOUNCEMENTS SYSTEM
# =========================================================

import os
import asyncio
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

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

# ---------------------------------------------------------
# Default timezone used when a user enters a custom date
# or scheduling time without a timezone.
# ---------------------------------------------------------

DEFAULT_TIMEZONE = ZoneInfo(
    "Europe/Lisbon"
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
# HELPERS
# =========================================================

def parse_hex_color(value):

    if not value:

        return discord.Color.blurple()

    value = value.strip()

    if value.startswith("#"):

        value = value[1:]

    if value.lower().startswith("0x"):

        value = value[2:]

    if len(value) != 6:

        raise ValueError(
            "A cor deve estar no formato #5865F2."
        )

    try:

        number = int(
            value,
            16
        )

    except ValueError:

        raise ValueError(
            "A cor fornecida não é válida."
        )

    return discord.Color(
        number
    )


def parse_datetime(
    value
):

    if not value:

        return None

    value = value.strip()

    formats = [
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
    ]

    parsed = None

    for date_format in formats:

        try:

            parsed = datetime.strptime(
                value,
                date_format
            )

            break

        except ValueError:

            continue

    if parsed is None:

        raise ValueError(
            "Data/hora inválida. Use DD/MM/AAAA HH:MM."
        )

    localized = parsed.replace(
        tzinfo=DEFAULT_TIMEZONE
    )

    return localized.astimezone(
        timezone.utc
    )


def format_datetime(
    value
):

    if value is None:

        return "—"

    if value.tzinfo is None:

        value = value.replace(
            tzinfo=timezone.utc
        )

    local_value = value.astimezone(
        DEFAULT_TIMEZONE
    )

    return local_value.strftime(
        "%d/%m/%Y %H:%M"
    )


def truncate(
    value,
    maximum
):

    if not value:

        return value

    if len(value) <= maximum:

        return value

    return value[:maximum - 3] + "..."


# =========================================================
# ANNOUNCEMENT DATA
# =========================================================

class AnnouncementData:

    def __init__(
        self,
        guild_id,
        channel_id
    ):

        self.guild_id = guild_id

        self.channel_id = channel_id

        self.title = ""

        self.description = ""

        self.color = "#5865F2"

        self.image_url = ""

        self.thumbnail_url = ""

        self.author_name = ""

        self.author_url = ""

        self.author_icon_url = ""

        self.use_server_name = False

        self.use_server_icon = False

        self.footer_text = ""

        self.footer_icon_url = ""

        self.timestamp_enabled = True

        self.custom_timestamp = None

        self.schedule_at = None

    def build_embed(
        self,
        guild
    ):

        embed = discord.Embed(
            title=truncate(
                self.title,
                256
            ) if self.title else None,
            description=truncate(
                self.description,
                4096
            ) if self.description else None,
            color=parse_hex_color(
                self.color
            )
        )

        # -------------------------------------------------
        # Title URL
        # -------------------------------------------------

        # URL support is handled by the main modal only
        # when a title URL is explicitly supplied.
        # The attribute is created dynamically below.
        # -------------------------------------------------

        title_url = getattr(
            self,
            "title_url",
            ""
        )

        if title_url and self.title:

            embed.url = title_url

        # -------------------------------------------------
        # Author
        # -------------------------------------------------

        author_name = self.author_name

        author_icon = self.author_icon_url

        author_url = self.author_url

        if self.use_server_name:

            author_name = guild.name

        if self.use_server_icon:

            if guild.icon:

                author_icon = guild.icon.url

        if author_name:

            try:

                embed.set_author(
                    name=truncate(
                        author_name,
                        256
                    ),
                    url=author_url or None,
                    icon_url=author_icon or None
                )

            except (ValueError, TypeError):

                embed.set_author(
                    name=truncate(
                        author_name,
                        256
                    )
                )

        # -------------------------------------------------
        # Images
        # -------------------------------------------------

        if self.image_url:

            embed.set_image(
                url=self.image_url
            )

        if self.thumbnail_url:

            embed.set_thumbnail(
                url=self.thumbnail_url
            )

        # -------------------------------------------------
        # Footer
        # -------------------------------------------------

        if self.footer_text:

            try:

                embed.set_footer(
                    text=truncate(
                        self.footer_text,
                        2048
                    ),
                    icon_url=(
                        self.footer_icon_url
                        or None
                    )
                )

            except (ValueError, TypeError):

                embed.set_footer(
                    text=truncate(
                        self.footer_text,
                        2048
                    )
                )

        # -------------------------------------------------
        # Timestamp
        # -------------------------------------------------

        if self.timestamp_enabled:

            if self.custom_timestamp:

                embed.timestamp = (
                    self.custom_timestamp
                )

            else:

                embed.timestamp = (
                    datetime.now(
                        timezone.utc
                    )
                )

        return embed


# =========================================================
# ANNOUNCEMENTS COG
# =========================================================

class Announcements(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.scheduler_task = None

        self.sessions = {}

        self.initialize_database()

    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    def initialize_database(
        self
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS announcements (

                        id BIGSERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        channel_id BIGINT NOT NULL,

                        creator_id BIGINT NOT NULL,

                        title TEXT,

                        description TEXT,

                        color TEXT,

                        title_url TEXT,

                        image_url TEXT,

                        thumbnail_url TEXT,

                        author_name TEXT,

                        author_url TEXT,

                        author_icon_url TEXT,

                        use_server_name BOOLEAN NOT NULL DEFAULT FALSE,

                        use_server_icon BOOLEAN NOT NULL DEFAULT FALSE,

                        footer_text TEXT,

                        footer_icon_url TEXT,

                        timestamp_enabled BOOLEAN NOT NULL DEFAULT TRUE,

                        custom_timestamp DOUBLE PRECISION,

                        scheduled_at DOUBLE PRECISION,

                        status TEXT NOT NULL DEFAULT 'draft',

                        created_at DOUBLE PRECISION NOT NULL,

                        sent_at DOUBLE PRECISION,

                        message_id BIGINT,

                        failure_reason TEXT
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_announcements_scheduled
                    ON announcements (
                        status,
                        scheduled_at
                    )
                    """
                )

            connection.commit()

            print(
                "📢 Announcements database initialized."
            )

        except Exception as error:

            if connection:

                connection.rollback()

            print(
                f"❌ Error initializing announcements database: {error}"
            )

        finally:

            if connection:

                connection.close()

    # =====================================================
    # CONFIG
    # =====================================================

    def get_config_cog(
        self
    ):

        return self.bot.get_cog(
            "Config"
        )

    # =====================================================
    # STAFF PERMISSION
    # =====================================================

    def has_staff_permission(
        self,
        member
    ):

        if member is None:

            return False

        if member.guild_permissions.administrator:

            return True

        config = self.get_config_cog()

        if config is None:

            return False

        role_ids = config.get_roles(
            member.guild.id,
            "staff"
        )

        if not role_ids:

            return False

        configured_ids = {
            int(role_id)
            for role_id in role_ids
        }

        return any(
            role.id in configured_ids
            for role in member.roles
        )

    # =====================================================
    # LOG CHANNEL
    # =====================================================

    def get_log_channel(
        self,
        guild
    ):

        config = self.get_config_cog()

        if config is None:

            return None

        # -------------------------------------------------
        # Prefer Moderation Logs.
        # Fall back to Configuration Logs.
        # -------------------------------------------------

        channel_id = config.get_channel_value(
            guild.id,
            "moderation_log_channel_id"
        )

        if channel_id:

            channel = guild.get_channel(
                int(channel_id)
            )

            if channel:

                return channel

        channel_id = config.get_channel_value(
            guild.id,
            "configuration_log_channel_id"
        )

        if channel_id:

            return guild.get_channel(
                int(channel_id)
            )

        return None

    # =====================================================
    # LOG ACTION
    # =====================================================

    async def send_log(
        self,
        guild,
        member,
        action,
        announcement_id=None,
        channel=None
    ):

        log_channel = self.get_log_channel(
            guild
        )

        if log_channel is None:

            return

        embed = discord.Embed(
            title="📢 Announcement",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Action",
            value=action,
            inline=True
        )

        embed.add_field(
            name="User",
            value=(
                f"{member.mention}\n"
                f"`{member.id}`"
            ),
            inline=True
        )

        if announcement_id:

            embed.add_field(
                name="Announcement ID",
                value=f"`{announcement_id}`",
                inline=True
            )

        if channel:

            embed.add_field(
                name="Channel",
                value=channel.mention,
                inline=True
            )

        embed.set_footer(
            text="Misuki Announcements"
        )

        try:

            await log_channel.send(
                embed=embed
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error sending announcement log: {error}"
            )

    # =====================================================
    # SAVE SCHEDULED ANNOUNCEMENT
    # =====================================================

    def save_announcement(
        self,
        data,
        creator_id
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO announcements (

                        guild_id,
                        channel_id,
                        creator_id,

                        title,
                        description,
                        color,
                        title_url,

                        image_url,
                        thumbnail_url,

                        author_name,
                        author_url,
                        author_icon_url,

                        use_server_name,
                        use_server_icon,

                        footer_text,
                        footer_icon_url,

                        timestamp_enabled,
                        custom_timestamp,

                        scheduled_at,
                        status,
                        created_at

                    )

                    VALUES (

                        %s,
                        %s,
                        %s,

                        %s,
                        %s,
                        %s,
                        %s,

                        %s,
                        %s,

                        %s,
                        %s,
                        %s,

                        %s,
                        %s,

                        %s,
                        %s,

                        %s,
                        %s,

                        %s,
                        'scheduled',
                        %s

                    )

                    RETURNING id
                    """,
                    (
                        data.guild_id,
                        data.channel_id,
                        creator_id,

                        data.title,
                        data.description,
                        data.color,
                        getattr(
                            data,
                            "title_url",
                            ""
                        ),

                        data.image_url,
                        data.thumbnail_url,

                        data.author_name,
                        data.author_url,
                        data.author_icon_url,

                        data.use_server_name,
                        data.use_server_icon,

                        data.footer_text,
                        data.footer_icon_url,

                        data.timestamp_enabled,

                        (
                            data.custom_timestamp.timestamp()
                            if data.custom_timestamp
                            else None
                        ),

                        data.schedule_at.timestamp(),

                        datetime.now(
                            timezone.utc
                        ).timestamp()
                    )
                )

                announcement_id = cursor.fetchone()[0]

            connection.commit()

            return announcement_id

        except Exception as error:

            if connection:

                connection.rollback()

            print(
                f"❌ Error saving scheduled announcement: {error}"
            )

            return None

        finally:

            if connection:

                connection.close()

    # =====================================================
    # GET SCHEDULED ANNOUNCEMENTS
    # =====================================================

    def get_due_announcements(
        self
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT

                        id,
                        guild_id,
                        channel_id,
                        creator_id,

                        title,
                        description,
                        color,
                        title_url,

                        image_url,
                        thumbnail_url,

                        author_name,
                        author_url,
                        author_icon_url,

                        use_server_name,
                        use_server_icon,

                        footer_text,
                        footer_icon_url,

                        timestamp_enabled,
                        custom_timestamp,
                        scheduled_at

                    FROM announcements

                    WHERE status = 'scheduled'

                    AND scheduled_at <= %s

                    ORDER BY scheduled_at ASC

                    LIMIT 25
                    """,
                    (
                        datetime.now(
                            timezone.utc
                        ).timestamp(),
                    )
                )

                return cursor.fetchall()

        except Exception as error:

            print(
                f"❌ Error reading scheduled announcements: {error}"
            )

            return []

        finally:

            if connection:

                connection.close()

    # =====================================================
    # MARK ANNOUNCEMENT
    # =====================================================

    def mark_announcement(
        self,
        announcement_id,
        status,
        message_id=None,
        failure_reason=None
    ):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE announcements

                    SET

                        status = %s,

                        sent_at = CASE
                            WHEN %s = 'sent'
                            THEN %s
                            ELSE sent_at
                        END,

                        message_id = COALESCE(
                            %s,
                            message_id
                        ),

                        failure_reason = %s

                    WHERE id = %s
                    """,
                    (
                        status,
                        status,
                        datetime.now(
                            timezone.utc
                        ).timestamp(),
                        message_id,
                        failure_reason,
                        announcement_id
                    )
                )

            connection.commit()

        except Exception as error:

            if connection:

                connection.rollback()

            print(
                f"❌ Error updating announcement {announcement_id}: {error}"
            )

        finally:

            if connection:

                connection.close()

    # =====================================================
    # BUILD DATA FROM DATABASE ROW
    # =====================================================

    def data_from_row(
        self,
        row
    ):

        data = AnnouncementData(
            row[1],
            row[2]
        )

        data.title = row[4] or ""

        data.description = row[5] or ""

        data.color = row[6] or "#5865F2"

        data.title_url = row[7] or ""

        data.image_url = row[8] or ""

        data.thumbnail_url = row[9] or ""

        data.author_name = row[10] or ""

        data.author_url = row[11] or ""

        data.author_icon_url = row[12] or ""

        data.use_server_name = bool(
            row[13]
        )

        data.use_server_icon = bool(
            row[14]
        )

        data.footer_text = row[15] or ""

        data.footer_icon_url = row[16] or ""

        data.timestamp_enabled = bool(
            row[17]
        )

        if row[18]:

            data.custom_timestamp = (
                datetime.fromtimestamp(
                    row[18],
                    timezone.utc
                )
            )

        if row[19]:

            data.schedule_at = (
                datetime.fromtimestamp(
                    row[19],
                    timezone.utc
                )
            )

        return data

    # =====================================================
    # SEND ANNOUNCEMENT
    # =====================================================

    async def publish_announcement(
        self,
        announcement_id,
        guild,
        data
    ):

        channel = guild.get_channel(
            int(data.channel_id)
        )

        if channel is None:

            self.mark_announcement(
                announcement_id,
                "failed",
                failure_reason=(
                    "The configured channel no longer exists."
                )
            )

            return False

        try:

            embed = data.build_embed(
                guild
            )

            message = await channel.send(
                embed=embed
            )

        except discord.Forbidden:

            self.mark_announcement(
                announcement_id,
                "failed",
                failure_reason=(
                    "The bot does not have permission "
                    "to send messages in this channel."
                )
            )

            return False

        except discord.HTTPException as error:

            self.mark_announcement(
                announcement_id,
                "failed",
                failure_reason=str(
                    error
                )
            )

            return False

        self.mark_announcement(
            announcement_id,
            "sent",
            message_id=message.id
        )

        return True

    # =====================================================
    # SCHEDULER
    # =====================================================

    async def scheduler_worker(
        self
    ):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            try:

                rows = (
                    self.get_due_announcements()
                )

                for row in rows:

                    (
                        announcement_id,
                        guild_id,
                        channel_id,
                        creator_id,

                        title,
                        description,
                        color,
                        title_url,

                        image_url,
                        thumbnail_url,

                        author_name,
                        author_url,
                        author_icon_url,

                        use_server_name,
                        use_server_icon,

                        footer_text,
                        footer_icon_url,

                        timestamp_enabled,
                        custom_timestamp,
                        scheduled_at
                    ) = row

                    guild = self.bot.get_guild(
                        int(guild_id)
                    )

                    if guild is None:

                        continue

                    data = self.data_from_row(
                        row
                    )

                    success = (
                        await self.publish_announcement(
                            announcement_id,
                            guild,
                            data
                        )
                    )

                    if success:

                        creator = guild.get_member(
                            int(creator_id)
                        )

                        if creator:

                            channel = guild.get_channel(
                                int(channel_id)
                            )

                            await self.send_log(
                                guild,
                                creator,
                                "Scheduled announcement sent.",
                                announcement_id,
                                channel
                            )

            except Exception as error:

                print(
                    f"❌ Announcement scheduler error: {error}"
                )

            await asyncio.sleep(
                10
            )

    # =====================================================
    # START SCHEDULER
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        if self.scheduler_task is None:

            self.scheduler_task = (
                asyncio.create_task(
                    self.scheduler_worker()
                )
            )

            print(
                "📢 Announcement scheduler started."
            )

    # =====================================================
    # /ANNOUNCE
    # =====================================================

    @app_commands.command(
        name="announce",
        description="Create a new announcement."
    )
    @app_commands.describe(
        channel="The channel where the announcement will be sent."
    )
    async def announce_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        if not self.has_staff_permission(
            interaction.user
        ):

            await interaction.response.send_message(
                (
                    "❌ You do not have permission to "
                    "create announcements."
                ),
                ephemeral=True
            )

            return

        data = AnnouncementData(
            interaction.guild.id,
            channel.id
        )

        session_id = (
            f"{interaction.guild.id}:"
            f"{interaction.user.id}:"
            f"{interaction.id}"
        )

        self.sessions[
            session_id
        ] = data

        await interaction.response.send_modal(
            AnnouncementContentModal(
                self,
                session_id
            )
        )


# =========================================================
# CONTENT MODAL
# =========================================================

class AnnouncementContentModal(
    discord.ui.Modal,
    title="📢 Announcement Content"
):

    title_input = discord.ui.TextInput(
        label="Title",
        placeholder="Announcement title",
        max_length=256,
        required=False
    )

    description_input = discord.ui.TextInput(
        label="Description",
        placeholder="Write the announcement...",
        style=discord.TextStyle.paragraph,
        max_length=4000,
        required=True
    )

    color_input = discord.ui.TextInput(
        label="Embed Color",
        placeholder="#5865F2",
        max_length=7,
        required=False,
        default="#5865F2"
    )

    title_url_input = discord.ui.TextInput(
        label="Title URL",
        placeholder="https://example.com",
        max_length=500,
        required=False
    )

    image_input = discord.ui.TextInput(
        label="Image URL",
        placeholder="https://example.com/image.png",
        max_length=500,
        required=False
    )

    def __init__(
        self,
        cog,
        session_id
    ):

        super().__init__()

        self.cog = cog

        self.session_id = session_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        try:

            parse_hex_color(
                self.color_input.value
                or "#5865F2"
            )

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

            return

        data.title = (
            self.title_input.value.strip()
        )

        data.description = (
            self.description_input.value.strip()
        )

        data.color = (
            self.color_input.value.strip()
            or "#5865F2"
        )

        data.title_url = (
            self.title_url_input.value.strip()
        )

        data.image_url = (
            self.image_input.value.strip()
        )

        await interaction.response.send_message(
            embed=data.build_embed(
                interaction.guild
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            ),
            ephemeral=True
        )


# =========================================================
# ADVANCED MODAL
# =========================================================

class AnnouncementAdvancedModal(
    discord.ui.Modal,
    title="👤 Author & Footer"
):

    author_name_input = discord.ui.TextInput(
        label="Author Name",
        placeholder="Leave empty for no author",
        max_length=256,
        required=False
    )

    author_url_input = discord.ui.TextInput(
        label="Author URL",
        placeholder="https://example.com",
        max_length=500,
        required=False
    )

    author_icon_input = discord.ui.TextInput(
        label="Author Profile Picture URL",
        placeholder="https://example.com/avatar.png",
        max_length=500,
        required=False
    )

    footer_input = discord.ui.TextInput(
        label="Footer Text",
        placeholder="Footer text",
        max_length=2048,
        required=False
    )

    footer_icon_input = discord.ui.TextInput(
        label="Footer Icon URL",
        placeholder="https://example.com/icon.png",
        max_length=500,
        required=False
    )

    def __init__(
        self,
        cog,
        session_id
    ):

        super().__init__()

        self.cog = cog

        self.session_id = session_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        data.author_name = (
            self.author_name_input.value.strip()
        )

        data.author_url = (
            self.author_url_input.value.strip()
        )

        data.author_icon_url = (
            self.author_icon_input.value.strip()
        )

        data.footer_text = (
            self.footer_input.value.strip()
        )

        data.footer_icon_url = (
            self.footer_icon_input.value.strip()
        )

        await interaction.response.edit_message(
            embed=data.build_embed(
                interaction.guild
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# TIMESTAMP / SCHEDULE MODAL
# =========================================================

class AnnouncementTimeModal(
    discord.ui.Modal,
    title="🕐 Timestamp & Schedule"
):

    custom_timestamp_input = discord.ui.TextInput(
        label="Custom Timestamp",
        placeholder="DD/MM/AAAA HH:MM — leave empty for current time",
        max_length=16,
        required=False
    )

    schedule_input = discord.ui.TextInput(
        label="Schedule Send Time",
        placeholder="DD/MM/AAAA HH:MM — leave empty to send now",
        max_length=16,
        required=False
    )

    def __init__(
        self,
        cog,
        session_id
    ):

        super().__init__()

        self.cog = cog

        self.session_id = session_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        try:

            if (
                self.custom_timestamp_input.value.strip()
            ):

                data.custom_timestamp = (
                    parse_datetime(
                        self.custom_timestamp_input.value
                    )
                )

                data.timestamp_enabled = True

            else:

                data.custom_timestamp = None

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

            return

        try:

            if self.schedule_input.value.strip():

                schedule_at = parse_datetime(
                    self.schedule_input.value
                )

                if schedule_at <= datetime.now(
                    timezone.utc
                ):

                    await interaction.response.send_message(
                        (
                            "❌ The scheduled time must "
                            "be in the future."
                        ),
                        ephemeral=True
                    )

                    return

                data.schedule_at = (
                    schedule_at
                )

            else:

                data.schedule_at = None

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

            return

        await interaction.response.edit_message(
            embed=data.build_embed(
                interaction.guild
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# BUILDER VIEW
# =========================================================

class AnnouncementBuilderView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        session_id
    ):

        super().__init__(
            timeout=900
        )

        self.cog = cog

        self.session_id = session_id

    # =====================================================
    # ADVANCED
    # =====================================================

    @discord.ui.button(
        label="Author / Footer",
        emoji="👤",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def advanced_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            AnnouncementAdvancedModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # SERVER
    # =====================================================

    @discord.ui.button(
        label="Server",
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def server_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        data.use_server_name = (
            not data.use_server_name
        )

        data.use_server_icon = (
            data.use_server_name
        )

        await interaction.response.edit_message(
            embed=data.build_embed(
                interaction.guild
            ),
            view=self
        )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    @discord.ui.button(
        label="Timestamp / Schedule",
        emoji="🕐",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def time_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            AnnouncementTimeModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # PREVIEW
    # =====================================================

    @discord.ui.button(
        label="Preview",
        emoji="👀",
        style=discord.ButtonStyle.primary,
        row=1
    )
    async def preview_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=data.build_embed(
                interaction.guild
            ),
            ephemeral=True
        )

    # =====================================================
    # SEND
    # =====================================================

    @discord.ui.button(
        label="Send",
        emoji="📢",
        style=discord.ButtonStyle.success,
        row=1
    )
    async def send_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ This announcement session expired.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # Scheduled
        # -------------------------------------------------

        if data.schedule_at:

            announcement_id = (
                self.cog.save_announcement(
                    data,
                    interaction.user.id
                )
            )

            if announcement_id is None:

                await interaction.response.send_message(
                    (
                        "❌ Could not save the "
                        "scheduled announcement."
                    ),
                    ephemeral=True
                )

                return

            channel = interaction.guild.get_channel(
                int(data.channel_id)
            )

            await self.cog.send_log(
                interaction.guild,
                interaction.user,
                "Announcement scheduled.",
                announcement_id,
                channel
            )

            self.cog.sessions.pop(
                self.session_id,
                None
            )

            await interaction.response.edit_message(
                content=(
                    "⏰ **Announcement scheduled successfully.**\n\n"
                    f"📅 {format_datetime(data.schedule_at)}\n"
                    f"📢 {channel.mention if channel else 'Unknown channel'}"
                ),
                embed=None,
                view=None
            )

            return

        # -------------------------------------------------
        # Send immediately
        # -------------------------------------------------

        channel = interaction.guild.get_channel(
            int(data.channel_id)
        )

        if channel is None:

            await interaction.response.send_message(
                "❌ The selected channel no longer exists.",
                ephemeral=True
            )

            return

        try:

            message = await channel.send(
                embed=data.build_embed(
                    interaction.guild
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                (
                    "❌ I don't have permission to "
                    "send messages in that channel."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error sending announcement: {error}"
            )

            await interaction.response.send_message(
                "❌ Discord rejected the announcement.",
                ephemeral=True
            )

            return

        await self.cog.send_log(
            interaction.guild,
            interaction.user,
            "Announcement published.",
            message.id,
            channel
        )

        self.cog.sessions.pop(
            self.session_id,
            None
        )

        await interaction.response.edit_message(
            content=(
                "✅ **Announcement published successfully.**\n\n"
                f"📢 {channel.mention}"
            ),
            embed=None,
            view=None
        )

    # =====================================================
    # CANCEL
    # =====================================================

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def cancel_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        self.cog.sessions.pop(
            self.session_id,
            None
        )

        await interaction.response.edit_message(
            content=(
                "❌ **Announcement cancelled.**"
            ),
            embed=None,
            view=None
        )


# =========================================================
# LOAD COG
# =========================================================

async def setup(
    bot
):

    cog = Announcements(
        bot
    )

    await bot.add_cog(
        cog
    )