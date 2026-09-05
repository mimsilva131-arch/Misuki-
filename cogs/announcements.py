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

DATABASE_URL = os.getenv("DATABASE_URL")

DEFAULT_TIMEZONE = ZoneInfo("Europe/Lisbon")


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

def parse_color(value):

    if not value:

        return 0x5865F2

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

        return int(
            value,
            16
        )

    except ValueError:

        raise ValueError(
            "A cor fornecida é inválida."
        )


def parse_datetime(value):

    value = value.strip()

    formats = (
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d %H:%M",
    )

    parsed = None

    for date_format in formats:

        try:

            parsed = datetime.strptime(
                value,
                date_format
            )

            break

        except ValueError:

            pass

    if parsed is None:

        raise ValueError(
            "Use o formato DD/MM/AAAA HH:MM."
        )

    parsed = parsed.replace(
        tzinfo=DEFAULT_TIMEZONE
    )

    return parsed.astimezone(
        timezone.utc
    )


def format_datetime(value):

    if value is None:

        return "—"

    return value.astimezone(
        DEFAULT_TIMEZONE
    ).strftime(
        "%d/%m/%Y %H:%M"
    )


def valid_url(value):

    if not value:

        return True

    return (
        value.startswith("http://")
        or value.startswith("https://")
    )


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

        self.color = 0x5865F2

        self.title_url = ""

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

        self.buttons = []

    # =====================================================
    # EMBED
    # =====================================================

    def build_embed(
        self,
        guild
    ):

        embed = discord.Embed(
            color=self.color
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        if self.title:

            embed.title = self.title

            if self.title_url:

                embed.url = self.title_url

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        if self.description:

            embed.description = self.description

        # -------------------------------------------------
        # AUTHOR
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
                    name=author_name[:256],
                    url=(
                        author_url
                        if author_url
                        else None
                    ),
                    icon_url=(
                        author_icon
                        if author_icon
                        else None
                    )
                )

            except (ValueError, TypeError):

                embed.set_author(
                    name=author_name[:256]
                )

        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        if self.image_url:

            embed.set_image(
                url=self.image_url
            )

        # -------------------------------------------------
        # THUMBNAIL
        # -------------------------------------------------

        if self.thumbnail_url:

            embed.set_thumbnail(
                url=self.thumbnail_url
            )

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        if self.footer_text:

            try:

                embed.set_footer(
                    text=self.footer_text[:2048],
                    icon_url=(
                        self.footer_icon_url
                        if self.footer_icon_url
                        else None
                    )
                )

            except (ValueError, TypeError):

                embed.set_footer(
                    text=self.footer_text[:2048]
                )

        # -------------------------------------------------
        # TIMESTAMP
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

    # =====================================================
    # BUTTON VIEW
    # =====================================================

    def build_button_view(self):

        if not self.buttons:

            return None

        view = discord.ui.View(
            timeout=None
        )

        for button in self.buttons:

            view.add_item(
                discord.ui.Button(
                    label=button["label"][:80],
                    emoji=(
                        button["emoji"]
                        if button["emoji"]
                        else None
                    ),
                    style=discord.ButtonStyle.link,
                    url=button["url"]
                )
            )

        return view


# =========================================================
# ANNOUNCEMENTS COG
# =========================================================

class Announcements(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.sessions = {}

        self.scheduler_task = None

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
                    CREATE TABLE IF NOT EXISTS announcements (

                        id BIGSERIAL PRIMARY KEY,

                        guild_id BIGINT NOT NULL,

                        channel_id BIGINT NOT NULL,

                        creator_id BIGINT NOT NULL,

                        title TEXT,

                        description TEXT,

                        color INTEGER,

                        title_url TEXT,

                        image_url TEXT,

                        thumbnail_url TEXT,

                        author_name TEXT,

                        author_url TEXT,

                        author_icon_url TEXT,

                        use_server_name BOOLEAN NOT NULL
                            DEFAULT FALSE,

                        use_server_icon BOOLEAN NOT NULL
                            DEFAULT FALSE,

                        footer_text TEXT,

                        footer_icon_url TEXT,

                        timestamp_enabled BOOLEAN NOT NULL
                            DEFAULT TRUE,

                        custom_timestamp DOUBLE PRECISION,

                        schedule_at DOUBLE PRECISION,

                        buttons JSONB,

                        status TEXT NOT NULL
                            DEFAULT 'scheduled',

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
                    idx_announcements_scheduler
                    ON announcements (
                        status,
                        schedule_at
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

    def get_config_cog(self):

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
    # LOG
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
                name="ID",
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
                f"❌ Announcement log error: {error}"
            )

    # =====================================================
    # SAVE
    # =====================================================

    def save_scheduled(
        self,
        data,
        creator_id
    ):

        connection = None

        try:

            import json

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

                        schedule_at,
                        buttons,

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
                        data.title_url,

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

                        json.dumps(
                            data.buttons
                        ),

                        datetime.now(
                            timezone.utc
                        ).timestamp()
                    )
                )

                announcement_id = (
                    cursor.fetchone()[0]
                )

            connection.commit()

            return announcement_id

        except Exception as error:

            if connection:

                connection.rollback()

            print(
                f"❌ Error saving announcement: {error}"
            )

            return None

        finally:

            if connection:

                connection.close()

    # =====================================================
    # GET DUE
    # =====================================================

    def get_due_announcements(self):

        connection = None

        try:

            connection = get_database_connection()

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT *

                    FROM announcements

                    WHERE status = 'scheduled'

                    AND schedule_at <= %s

                    ORDER BY schedule_at ASC

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
                f"❌ Error loading scheduled announcements: {error}"
            )

            return []

        finally:

            if connection:

                connection.close()

    # =====================================================
    # MARK STATUS
    # =====================================================

    def mark_status(
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
                f"❌ Error updating announcement: {error}"
            )

        finally:

            if connection:

                connection.close()

    # =====================================================
    # PUBLISH
    # =====================================================

    async def publish_scheduled(
        self,
        row
    ):

        import json

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

            schedule_at,
            buttons,

            status,
            created_at,
            sent_at,
            message_id,
            failure_reason

        ) = row

        guild = self.bot.get_guild(
            int(guild_id)
        )

        if guild is None:

            return

        channel = guild.get_channel(
            int(channel_id)
        )

        if channel is None:

            self.mark_status(
                announcement_id,
                "failed",
                failure_reason=(
                    "The configured channel no longer exists."
                )
            )

            return

        data = AnnouncementData(
            guild.id,
            channel.id
        )

        data.title = title or ""

        data.description = description or ""

        data.color = (
            color
            if color is not None
            else 0x5865F2
        )

        data.title_url = title_url or ""

        data.image_url = image_url or ""

        data.thumbnail_url = (
            thumbnail_url or ""
        )

        data.author_name = (
            author_name or ""
        )

        data.author_url = (
            author_url or ""
        )

        data.author_icon_url = (
            author_icon_url or ""
        )

        data.use_server_name = bool(
            use_server_name
        )

        data.use_server_icon = bool(
            use_server_icon
        )

        data.footer_text = (
            footer_text or ""
        )

        data.footer_icon_url = (
            footer_icon_url or ""
        )

        data.timestamp_enabled = bool(
            timestamp_enabled
        )

        if custom_timestamp:

            data.custom_timestamp = (
                datetime.fromtimestamp(
                    custom_timestamp,
                    timezone.utc
                )
            )

        if buttons:

            if isinstance(
                buttons,
                str
            ):

                data.buttons = json.loads(
                    buttons
                )

            else:

                data.buttons = buttons

        try:

            embed = data.build_embed(
                guild
            )

            view = (
                data.build_button_view()
            )

            message = await channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            self.mark_status(
                announcement_id,
                "failed",
                failure_reason=(
                    "The bot does not have permission "
                    "to send messages in this channel."
                )
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Error sending scheduled announcement: {error}"
            )

            return

        self.mark_status(
            announcement_id,
            "sent",
            message_id=message.id
        )

        creator = guild.get_member(
            int(creator_id)
        )

        if creator:

            await self.send_log(
                guild,
                creator,
                "Scheduled announcement sent.",
                announcement_id,
                channel
            )

    # =====================================================
    # SCHEDULER
    # =====================================================

    async def scheduler_worker(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            try:

                rows = (
                    self.get_due_announcements()
                )

                for row in rows:

                    await self.publish_scheduled(
                        row
                    )

            except Exception as error:

                print(
                    f"❌ Announcement scheduler error: {error}"
                )

            await asyncio.sleep(
                10
            )

    # =====================================================
    # READY
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(self):

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
        description="Create an interactive announcement."
    )
    @app_commands.describe(
        channel="Channel where the announcement will be published."
    )
    async def announce(
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
                    "❌ You do not have permission "
                    "to create announcements."
                ),
                ephemeral=True
            )

            return

        data = AnnouncementData(
            interaction.guild.id,
            channel.id
        )

        session_id = str(
            interaction.id
        )

        self.sessions[
            session_id
        ] = data

        await interaction.response.send_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                channel
            ),
            view=AnnouncementBuilderView(
                self,
                session_id
            ),
            ephemeral=True
        )


# =========================================================
# BUILDER EMBED
# =========================================================

def build_builder_embed(
    guild,
    data,
    channel
):

    embed = discord.Embed(
        title="📢 Announcement Builder",
        description=(
            "Configure o seu anúncio através das "
            "opções abaixo.\n\n"
            "A pré-visualização será atualizada "
            "à medida que fizer alterações."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="📍 Canal",
        value=channel.mention,
        inline=False
    )

    embed.add_field(
        name="📝 Conteúdo",
        value=(
            f"**Título:** "
            f"{data.title or 'Não definido'}\n"
            f"**Descrição:** "
            f"{'Configurada' if data.description else 'Não definida'}"
        ),
        inline=True
    )

    embed.add_field(
        name="🎨 Aparência",
        value=(
            f"**Cor:** `#{data.color:06X}`\n"
            f"**Imagem:** "
            f"{'✅' if data.image_url else '❌'}\n"
            f"**Thumbnail:** "
            f"{'✅' if data.thumbnail_url else '❌'}"
        ),
        inline=True
    )

    embed.add_field(
        name="👤 Autor",
        value=(
            f"{data.author_name or 'Não definido'}\n"
            f"Servidor: "
            f"{'✅' if data.use_server_name else '❌'}"
        ),
        inline=True
    )

    embed.add_field(
        name="🕐 Timestamp",
        value=(
            "Desativado"
            if not data.timestamp_enabled
            else (
                format_datetime(
                    data.custom_timestamp
                )
                if data.custom_timestamp
                else "Hora de envio"
            )
        ),
        inline=True
    )

    embed.add_field(
        name="🔻 Footer",
        value=(
            data.footer_text
            if data.footer_text
            else "Não definido"
        ),
        inline=True
    )

    embed.add_field(
        name="🔗 Links / Botões",
        value=(
            f"{len(data.buttons)} botão"
            f"{'ões' if len(data.buttons) != 1 else ''}"
        ),
        inline=True
    )

    embed.add_field(
        name="⏰ Envio",
        value=(
            format_datetime(
                data.schedule_at
            )
            if data.schedule_at
            else "Enviar agora"
        ),
        inline=False
    )

    embed.set_footer(
        text="Misuki • Announcement Builder"
    )

    return embed


# =========================================================
# CONTENT MODAL
# =========================================================

class ContentModal(
    discord.ui.Modal,
    title="📝 Conteúdo"
):

    title_input = discord.ui.TextInput(
        label="Título",
        placeholder="Título do anúncio",
        max_length=256,
        required=False
    )

    description_input = discord.ui.TextInput(
        label="Descrição",
        placeholder="Escreva o conteúdo do anúncio...",
        style=discord.TextStyle.paragraph,
        max_length=4000,
        required=True
    )

    color_input = discord.ui.TextInput(
        label="Cor",
        placeholder="#5865F2",
        max_length=7,
        required=False
    )

    title_url_input = discord.ui.TextInput(
        label="URL do título",
        placeholder="https://example.com",
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        try:

            color = parse_color(
                self.color_input.value
                or "#5865F2"
            )

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

            return

        title_url = (
            self.title_url_input.value.strip()
        )

        if not valid_url(title_url):

            await interaction.response.send_message(
                "❌ A URL do título é inválida.",
                ephemeral=True
            )

            return

        data.title = (
            self.title_input.value.strip()
        )

        data.description = (
            self.description_input.value.strip()
        )

        data.color = color

        data.title_url = title_url

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# AUTHOR MODAL
# =========================================================

class AuthorModal(
    discord.ui.Modal,
    title="👤 Autor"
):

    name_input = discord.ui.TextInput(
        label="Author Name",
        placeholder="Nome do autor",
        max_length=256,
        required=False
    )

    url_input = discord.ui.TextInput(
        label="Author URL",
        placeholder="https://example.com",
        max_length=500,
        required=False
    )

    icon_input = discord.ui.TextInput(
        label="Author Profile Picture",
        placeholder="https://example.com/avatar.png",
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        for value in (
            self.url_input.value,
            self.icon_input.value
        ):

            if value and not valid_url(
                value.strip()
            ):

                await interaction.response.send_message(
                    "❌ Uma das URLs fornecidas é inválida.",
                    ephemeral=True
                )

                return

        data.author_name = (
            self.name_input.value.strip()
        )

        data.author_url = (
            self.url_input.value.strip()
        )

        data.author_icon_url = (
            self.icon_input.value.strip()
        )

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# IMAGE MODAL
# =========================================================

class ImageModal(
    discord.ui.Modal,
    title="🖼️ Imagens"
):

    image_input = discord.ui.TextInput(
        label="Image URL",
        placeholder="https://example.com/image.png",
        max_length=500,
        required=False
    )

    thumbnail_input = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="https://example.com/thumb.png",
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        for value in (
            self.image_input.value,
            self.thumbnail_input.value
        ):

            if value and not valid_url(
                value.strip()
            ):

                await interaction.response.send_message(
                    "❌ Uma das URLs fornecidas é inválida.",
                    ephemeral=True
                )

                return

        data.image_url = (
            self.image_input.value.strip()
        )

        data.thumbnail_url = (
            self.thumbnail_input.value.strip()
        )

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# FOOTER MODAL
# =========================================================

class FooterModal(
    discord.ui.Modal,
    title="🔻 Footer"
):

    text_input = discord.ui.TextInput(
        label="Footer Text",
        placeholder="Texto do footer",
        max_length=2048,
        required=False
    )

    icon_input = discord.ui.TextInput(
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        icon_url = (
            self.icon_input.value.strip()
        )

        if icon_url and not valid_url(
            icon_url
        ):

            await interaction.response.send_message(
                "❌ O Footer Icon URL é inválido.",
                ephemeral=True
            )

            return

        data.footer_text = (
            self.text_input.value.strip()
        )

        data.footer_icon_url = icon_url

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# TIME MODAL
# =========================================================

class TimeModal(
    discord.ui.Modal,
    title="🕐 Timestamp"
):

    custom_timestamp = discord.ui.TextInput(
        label="Timestamp personalizado",
        placeholder="DD/MM/AAAA HH:MM",
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        value = (
            self.custom_timestamp.value.strip()
        )

        if not value:

            data.custom_timestamp = None

            data.timestamp_enabled = True

        else:

            try:

                parsed = parse_datetime(
                    value
                )

            except ValueError as error:

                await interaction.response.send_message(
                    f"❌ {error}",
                    ephemeral=True
                )

                return

            data.custom_timestamp = parsed

            data.timestamp_enabled = True

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# SCHEDULE MODAL
# =========================================================

class ScheduleModal(
    discord.ui.Modal,
    title="⏰ Agendar anúncio"
):

    schedule_input = discord.ui.TextInput(
        label="Data e hora",
        placeholder="DD/MM/AAAA HH:MM",
        max_length=16,
        required=True
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        try:

            schedule_at = parse_datetime(
                self.schedule_input.value
            )

        except ValueError as error:

            await interaction.response.send_message(
                f"❌ {error}",
                ephemeral=True
            )

            return

        if schedule_at <= datetime.now(
            timezone.utc
        ):

            await interaction.response.send_message(
                (
                    "❌ A data/hora tem de estar "
                    "no futuro."
                ),
                ephemeral=True
            )

            return

        data.schedule_at = schedule_at

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=AnnouncementBuilderView(
                self.cog,
                self.session_id
            )
        )


# =========================================================
# BUTTON MODAL
# =========================================================

class AddButtonModal(
    discord.ui.Modal,
    title="🔗 Adicionar botão"
):

    label_input = discord.ui.TextInput(
        label="Nome do botão",
        placeholder="Website",
        max_length=80,
        required=True
    )

    url_input = discord.ui.TextInput(
        label="URL",
        placeholder="https://example.com",
        max_length=500,
        required=True
    )

    emoji_input = discord.ui.TextInput(
        label="Emoji",
        placeholder="🌐",
        max_length=10,
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
        interaction
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        url = (
            self.url_input.value.strip()
        )

        if not valid_url(url):

            await interaction.response.send_message(
                "❌ A URL tem de começar por http:// ou https://.",
                ephemeral=True
            )

            return

        if len(data.buttons) >= 5:

            await interaction.response.send_message(
                (
                    "❌ Um anúncio pode ter no máximo "
                    "5 botões."
                ),
                ephemeral=True
            )

            return

        data.buttons.append(
            {
                "label": (
                    self.label_input.value.strip()
                ),
                "url": url,
                "emoji": (
                    self.emoji_input.value.strip()
                )
            }
        )

        await interaction.response.edit_message(
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
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
    # CONTENT
    # =====================================================

    @discord.ui.button(
        label="Conteúdo",
        emoji="📝",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def content_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            ContentModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # AUTHOR
    # =====================================================

    @discord.ui.button(
        label="Autor",
        emoji="👤",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def author_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            AuthorModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # IMAGES
    # =====================================================

    @discord.ui.button(
        label="Imagens",
        emoji="🖼️",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def images_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            ImageModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # FOOTER
    # =====================================================

    @discord.ui.button(
        label="Footer",
        emoji="🔻",
        style=discord.ButtonStyle.secondary,
        row=0
    )
    async def footer_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            FooterModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # SERVER
    # =====================================================

    @discord.ui.button(
        label="Servidor",
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def server_button(
        self,
        interaction,
        button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
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
            embed=build_builder_embed(
                interaction.guild,
                data,
                interaction.guild.get_channel(
                    data.channel_id
                )
            ),
            view=self
        )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    @discord.ui.button(
        label="Timestamp",
        emoji="🕐",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def timestamp_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            TimeModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # ADD BUTTON
    # =====================================================

    @discord.ui.button(
        label="Adicionar link",
        emoji="🔗",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def link_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            AddButtonModal(
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
        row=2
    )
    async def preview_button(
        self,
        interaction,
        button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            embed=data.build_embed(
                interaction.guild
            ),
            view=data.build_button_view(),
            ephemeral=True
        )

    # =====================================================
    # SEND NOW
    # =====================================================

    @discord.ui.button(
        label="Enviar agora",
        emoji="📢",
        style=discord.ButtonStyle.success,
        row=2
    )
    async def send_button(
        self,
        interaction,
        button
    ):

        data = self.cog.sessions.get(
            self.session_id
        )

        if data is None:

            await interaction.response.send_message(
                "❌ Esta sessão expirou.",
                ephemeral=True
            )

            return

        channel = interaction.guild.get_channel(
            data.channel_id
        )

        if channel is None:

            await interaction.response.send_message(
                "❌ O canal selecionado já não existe.",
                ephemeral=True
            )

            return

        try:

            message = await channel.send(
                embed=data.build_embed(
                    interaction.guild
                ),
                view=data.build_button_view()
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                (
                    "❌ Não tenho permissão para "
                    "enviar mensagens nesse canal."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Announcement send error: {error}"
            )

            await interaction.response.send_message(
                "❌ O Discord rejeitou o anúncio.",
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
                "✅ **Anúncio publicado com sucesso!**\n\n"
                f"📢 {channel.mention}"
            ),
            embed=None,
            view=None
        )

    # =====================================================
    # SCHEDULE
    # =====================================================

    @discord.ui.button(
        label="Agendar",
        emoji="⏰",
        style=discord.ButtonStyle.primary,
        row=3
    )
    async def schedule_button(
        self,
        interaction,
        button
    ):

        await interaction.response.send_modal(
            ScheduleModal(
                self.cog,
                self.session_id
            )
        )

    # =====================================================
    # CANCEL
    # =====================================================

    @discord.ui.button(
        label="Cancelar",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        row=3
    )
    async def cancel_button(
        self,
        interaction,
        button
    ):

        self.cog.sessions.pop(
            self.session_id,
            None
        )

        await interaction.response.edit_message(
            content=(
                "❌ **Criação do anúncio cancelada.**"
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