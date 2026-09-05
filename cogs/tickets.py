import asyncio
import io
import os
import sqlite3

from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from cogs.activity_statistics import increment_activity_stat


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
    "tickets.db"
)


# =========================================================
# DATABASE INIT
# =========================================================

def init_database():

    connection = sqlite3.connect(
        DATABASE
    )

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_counter (

                guild_id INTEGER PRIMARY KEY,

                number INTEGER NOT NULL
                    DEFAULT 0

            )
            """
        )

        connection.commit()

    finally:

        connection.close()


# =========================================================
# NEXT TICKET NUMBER
# =========================================================

def get_next_number(guild_id):

    connection = sqlite3.connect(
        DATABASE
    )

    try:

        cursor = connection.cursor()

        # -------------------------------------------------
        # Atomic counter update
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT number
            FROM ticket_counter
            WHERE guild_id = ?
            """,
            (
                guild_id,
            )
        )

        result = cursor.fetchone()

        if result is None:

            number = 1

            cursor.execute(
                """
                INSERT INTO ticket_counter
                (
                    guild_id,
                    number
                )

                VALUES (?, ?)
                """,
                (
                    guild_id,
                    number
                )
            )

        else:

            number = int(
                result[0]
            ) + 1

            cursor.execute(
                """
                UPDATE ticket_counter

                SET number = ?

                WHERE guild_id = ?
                """,
                (
                    number,
                    guild_id
                )
            )

        connection.commit()

        return number

    finally:

        connection.close()


# =========================================================
# CONFIG
# =========================================================

def get_config(bot):

    return bot.get_cog(
        "Config"
    )


# =========================================================
# LICENSE
# =========================================================

def get_license_manager(bot):

    return bot.get_cog(
        "LicenseManager"
    )


def check_license(
    bot,
    guild_id
):

    license_manager = get_license_manager(
        bot
    )

    if license_manager is None:

        print(
            "❌ LicenseManager não está carregado."
        )

        return False

    try:

        return bool(
            license_manager.has_active_license(
                guild_id
            )
        )

    except Exception as error:

        print(
            f"❌ License check error: {error}"
        )

        return False


# =========================================================
# STAFF
# =========================================================

def check_staff(
    member,
    config,
    guild_id
):

    if member is None:

        return False

    if not isinstance(
        member,
        discord.Member
    ):

        return False

    permissions = member.guild_permissions

    if permissions.administrator:

        return True

    if permissions.manage_guild:

        return True

    if config is None:

        return False

    try:

        staff_roles = config.get_roles(
            guild_id,
            "staff"
        )

        moderator_roles = config.get_roles(
            guild_id,
            "moderator"
        )

        staff_roles = (
            staff_roles
            if staff_roles
            else []
        )

        moderator_roles = (
            moderator_roles
            if moderator_roles
            else []
        )

        allowed_roles = (
            list(staff_roles)
            + list(moderator_roles)
        )

        member_roles = {
            role.id
            for role in member.roles
        }

        for role_id in allowed_roles:

            try:

                role_id = int(
                    role_id
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            if role_id in member_roles:

                return True

    except Exception as error:

        print(
            f"❌ Staff check error: {error}"
        )

    return False


# =========================================================
# SETUP AUTHORIZATION
# =========================================================

def authorized_setup(
    interaction,
    config
):

    guild = interaction.guild

    if guild is None:

        return False

    if not check_staff(
        interaction.user,
        config,
        guild.id
    ):

        print(
            f"🚫 Unauthorized ticket setup: "
            f"{interaction.user} "
            f"({interaction.user.id})"
        )

        return False

    if not check_license(
        interaction.client,
        guild.id
    ):

        print(
            f"🔒 Invalid license for "
            f"guild {guild.id}"
        )

        return False

    return True


# =========================================================
# TICKET GROUP
# =========================================================

class TicketGroup(
    app_commands.Group
):

    def __init__(self):

        super().__init__(
            name="ticket",
            description="Ticket system commands."
        )

    # =====================================================
    # /ticket setup
    # =====================================================

    @app_commands.command(
        name="setup",
        description="Create the ticket panel."
    )
    async def setup(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return

        config = get_config(
            interaction.client
        )

        if config is None:

            await interaction.response.send_message(
                "❌ Config cog is not loaded.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # SECURITY
        # -------------------------------------------------

        if not authorized_setup(
            interaction,
            config
        ):

            await interaction.response.send_message(
                (
                    "❌ **Staff only.**\n\n"
                    "You do not have permission "
                    "to use `/ticket setup`."
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        category_id = config.get_ticket_category(
            guild.id
        )

        if not category_id:

            await interaction.response.send_message(
                (
                    "❌ **Ticket Category not configured.**\n\n"
                    "Go to `/setup` → **Tickets** → "
                    "**Ticket Category** first."
                ),
                ephemeral=True
            )

            return

        try:

            category_id = int(
                category_id
            )

        except (
            TypeError,
            ValueError
        ):

            await interaction.response.send_message(
                "❌ The configured Ticket Category ID is invalid.",
                ephemeral=True
            )

            return

        category = guild.get_channel(
            category_id
        )

        if not isinstance(
            category,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                (
                    "❌ The configured Ticket Category "
                    "no longer exists."
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # PANEL
        # -------------------------------------------------

        embed = discord.Embed(
            title="🎫 Support Tickets",
            description=(
                "Need help from the staff team?\n\n"
                "Click **Create Ticket** below "
                "to open a private support ticket."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Misuki Ticket System"
        )

        # -------------------------------------------------
        # FINAL SECURITY CHECK
        # -------------------------------------------------

        if not check_staff(
            interaction.user,
            config,
            guild.id
        ):

            await interaction.response.send_message(
                "❌ Permission check failed.",
                ephemeral=True
            )

            return

        if not check_license(
            interaction.client,
            guild.id
        ):

            await interaction.response.send_message(
                "🔒 Your server does not have an active license.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CHANNEL CHECK
        # -------------------------------------------------

        if interaction.channel is None:

            await interaction.response.send_message(
                "❌ This command must be used in a channel.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # SEND PANEL
        # -------------------------------------------------

        try:

            await interaction.channel.send(
                embed=embed,
                view=TicketPanel()
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                (
                    "❌ I don't have permission "
                    "to send messages in this channel."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                (
                    "❌ Discord returned an error:\n"
                    f"`{error}`"
                ),
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            (
                "✅ **Ticket panel created.**\n"
                f"📍 Channel: {interaction.channel.mention}\n"
                f"📂 Category: {category.name}"
            ),
            ephemeral=True
        )


# =========================================================
# PANEL
# =========================================================

class TicketPanel(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            CreateTicket()
        )


# =========================================================
# CREATE TICKET
# =========================================================

class CreateTicket(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Create Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.primary,
            custom_id="ticket_create"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        if guild is None:

            await interaction.response.send_message(
                "❌ This can only be used in a server.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # LICENSE
        # -------------------------------------------------

        if not check_license(
            interaction.client,
            guild.id
        ):

            await interaction.response.send_message(
                (
                    "🔒 **License required.**\n\n"
                    "This server does not have "
                    "an active Misuki license."
                ),
                ephemeral=True
            )

            return

        config = get_config(
            interaction.client
        )

        if config is None:

            await interaction.response.send_message(
                "❌ Config cog is not loaded.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        category_id = config.get_ticket_category(
            guild.id
        )

        if not category_id:

            await interaction.response.send_message(
                (
                    "❌ Tickets are not configured.\n\n"
                    "An administrator must configure "
                    "the Ticket Category in `/setup`."
                ),
                ephemeral=True
            )

            return

        try:

            category_id = int(
                category_id
            )

        except (
            TypeError,
            ValueError
        ):

            await interaction.response.send_message(
                "❌ The configured Ticket Category ID is invalid.",
                ephemeral=True
            )

            return

        category = guild.get_channel(
            category_id
        )

        if not isinstance(
            category,
            discord.CategoryChannel
        ):

            await interaction.response.send_message(
                (
                    "❌ The configured Ticket Category "
                    "no longer exists."
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # EXISTING TICKET
        # -------------------------------------------------

        owner_topic = (
            f"Ticket owner: "
            f"{interaction.user.id}"
        )

        for channel in guild.text_channels:

            if not channel.name.startswith(
                "ticket-"
            ):

                continue

            if channel.topic == owner_topic:

                await interaction.response.send_message(
                    (
                        "❌ You already have an "
                        f"open ticket: {channel.mention}"
                    ),
                    ephemeral=True
                )

                return

        # -------------------------------------------------
        # NUMBER
        # -------------------------------------------------

        try:

            number = get_next_number(
                guild.id
            )

        except Exception as error:

            print(
                f"❌ Ticket counter error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to generate a ticket number.",
                ephemeral=True
            )

            return

        ticket_name = (
            f"ticket-{number:04d}"
        )

        # -------------------------------------------------
        # PERMISSIONS
        # -------------------------------------------------

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
        }

        # -------------------------------------------------
        # BOT
        # -------------------------------------------------

        bot_member = guild.me

        if bot_member:

            overwrites[bot_member] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True,
                    attach_files=True,
                    embed_links=True
                )
            )

        # -------------------------------------------------
        # STAFF ROLES
        # -------------------------------------------------

        try:

            staff_roles = config.get_roles(
                guild.id,
                "staff"
            )

            moderator_roles = config.get_roles(
                guild.id,
                "moderator"
            )

            staff_roles = (
                staff_roles
                if staff_roles
                else []
            )

            moderator_roles = (
                moderator_roles
                if moderator_roles
                else []
            )

            allowed_roles = (
                list(staff_roles)
                + list(moderator_roles)
            )

            added_role_ids = set()

            for role_id in allowed_roles:

                try:

                    role_id = int(
                        role_id
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    continue

                if role_id in added_role_ids:

                    continue

                added_role_ids.add(
                    role_id
                )

                role = guild.get_role(
                    role_id
                )

                if role is None:

                    continue

                overwrites[role] = (
                    discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        attach_files=True,
                        embed_links=True
                    )
                )

        except Exception as error:

            print(
                f"❌ Error loading ticket roles: {error}"
            )

        # -------------------------------------------------
        # CREATE CHANNEL
        # -------------------------------------------------

        try:

            ticket = await guild.create_text_channel(
                name=ticket_name,
                category=category,
                overwrites=overwrites,
                topic=owner_topic,
                reason=(
                    f"Misuki ticket created by "
                    f"{interaction.user}"
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                (
                    "❌ I don't have permission "
                    "to create ticket channels."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                (
                    "❌ Discord returned an error:\n"
                    f"`{error}`"
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # EMBED
        # -------------------------------------------------

        embed = discord.Embed(
            title=f"🎫 Ticket #{number:04d}",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                "Please explain your problem clearly "
                "and wait for a staff member.\n\n"
                "📄 **Transcript** — save the conversation\n"
                "🔒 **Close Ticket** — close this ticket"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="👤 Owner",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="🔢 Ticket",
            value=f"#{number:04d}",
            inline=True
        )

        embed.set_footer(
            text="Misuki Ticket System"
        )

        # -------------------------------------------------
        # SEND INITIAL MESSAGE
        # -------------------------------------------------

        try:

            await ticket.send(
                content=interaction.user.mention,
                embed=embed,
                view=TicketControls()
            )

        except discord.Forbidden:

            try:

                await ticket.delete(
                    reason="Failed to send ticket message"
                )

            except Exception:
                pass

            await interaction.response.send_message(
                (
                    "❌ I don't have permission "
                    "to send messages in the ticket."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            try:

                await ticket.delete(
                    reason="Failed to send ticket message"
                )

            except Exception:
                pass

            print(
                f"❌ Ticket message error: {error}"
            )

            await interaction.response.send_message(
                "❌ Failed to create the ticket message.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # ACTIVITY STATISTICS
        # -------------------------------------------------
        # Só conta depois de o ticket ter sido
        # completamente criado com sucesso.

        increment_activity_stat(
            "tickets"
        )

        await interaction.response.send_message(
            (
                "✅ Ticket created: "
                f"{ticket.mention}"
            ),
            ephemeral=True
        )


# =========================================================
# CONTROLS
# =========================================================

class TicketControls(
    discord.ui.View
):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            Transcript()
        )

        self.add_item(
            CloseTicket()
        )


# =========================================================
# ACCESS
# =========================================================

def can_access_ticket(
    interaction
):

    guild = interaction.guild

    channel = interaction.channel

    if guild is None:

        return False

    if channel is None:

        return False

    if not isinstance(
        channel,
        discord.TextChannel
    ):

        return False

    if not channel.name.startswith(
        "ticket-"
    ):

        return False

    config = get_config(
        interaction.client
    )

    if config is None:

        return False

    # -----------------------------------------------------
    # LICENSE
    # -----------------------------------------------------

    if not check_license(
        interaction.client,
        guild.id
    ):

        return False

    # -----------------------------------------------------
    # STAFF
    # -----------------------------------------------------

    if check_staff(
        interaction.user,
        config,
        guild.id
    ):

        return True

    # -----------------------------------------------------
    # OWNER
    # -----------------------------------------------------

    if channel.topic == (
        f"Ticket owner: "
        f"{interaction.user.id}"
    ):

        return True

    return False


# =========================================================
# TRANSCRIPT
# =========================================================

class Transcript(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Transcript",
            emoji="📄",
            style=discord.ButtonStyle.secondary,
            custom_id="ticket_transcript"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not can_access_ticket(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You do not have permission to use this ticket.",
                ephemeral=True
            )

            return

        guild = interaction.guild

        channel = interaction.channel

        if guild is None or channel is None:

            return

        await interaction.response.defer(
            ephemeral=True
        )

        config = get_config(
            interaction.client
        )

        if config is None:

            await interaction.followup.send(
                "❌ Config cog is not loaded.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # TRANSCRIPT CHANNEL
        # -------------------------------------------------

        channel_id = config.get_channel_value(
            guild.id,
            "transcript_log_channel_id"
        )

        if not channel_id:

            await interaction.followup.send(
                (
                    "❌ **Transcript Channel not configured.**\n\n"
                    "Go to `/setup` → **Tickets** → "
                    "**Transcript Channel**."
                ),
                ephemeral=True
            )

            return

        try:

            channel_id = int(
                channel_id
            )

        except (
            TypeError,
            ValueError
        ):

            await interaction.followup.send(
                "❌ The configured Transcript Channel ID is invalid.",
                ephemeral=True
            )

            return

        transcript_channel = guild.get_channel(
            channel_id
        )

        if not isinstance(
            transcript_channel,
            discord.TextChannel
        ):

            await interaction.followup.send(
                (
                    "❌ The configured Transcript Channel "
                    "no longer exists."
                ),
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        output = []

        try:

            async for message in channel.history(
                limit=None,
                oldest_first=True
            ):

                date = message.created_at.strftime(
                    "%d/%m/%Y %H:%M:%S"
                )

                author = (
                    f"{message.author.display_name} "
                    f"({message.author.id})"
                )

                content = message.content

                if not content:

                    content = "[sem texto]"

                output.append(
                    "================================================\n"
                    f"Data: {date}\n"
                    f"Autor: {author}\n"
                    "------------------------------------------------\n"
                    f"{content}\n"
                )

                if message.attachments:

                    output.append(
                        "\nAnexos:\n"
                        +
                        "\n".join(
                            attachment.url
                            for attachment
                            in message.attachments
                        )
                        +
                        "\n"
                    )

        except discord.Forbidden:

            await interaction.followup.send(
                (
                    "❌ I don't have permission "
                    "to read this ticket's history."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Transcript history error: {error}"
            )

            await interaction.followup.send(
                "❌ Failed to read the ticket history.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # FILE
        # -------------------------------------------------

        text = (
            "MISUKI TICKET TRANSCRIPT\n"
            "================================================\n\n"
            f"Servidor: {guild.name}\n"
            f"Servidor ID: {guild.id}\n"
            f"Ticket: {channel.name}\n"
            f"Gerado por: {interaction.user}\n"
            f"Gerado por ID: {interaction.user.id}\n"
            f"Data: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            "================================================\n\n"
        )

        text += "\n".join(
            output
        )

        file = discord.File(
            io.BytesIO(
                text.encode(
                    "utf-8"
                )
            ),
            filename=(
                f"{channel.name}-transcript.txt"
            )
        )

        embed = discord.Embed(
            title="📄 Ticket Transcript",
            description=(
                f"Transcript do **{channel.name}**"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.now(timezone.utc)
        )

        embed.add_field(
            name="👤 Gerado por",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="🎫 Ticket",
            value=channel.name,
            inline=True
        )

        embed.set_footer(
            text="Misuki Ticket System"
        )

        # -------------------------------------------------
        # SEND
        # -------------------------------------------------

        try:

            await transcript_channel.send(
                embed=embed,
                file=file
            )

        except discord.Forbidden:

            await interaction.followup.send(
                (
                    "❌ I don't have permission to "
                    "send transcripts to the configured channel."
                ),
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            print(
                f"❌ Transcript send error: {error}"
            )

            await interaction.followup.send(
                (
                    "❌ Discord returned an error:\n"
                    f"`{error}`"
                ),
                ephemeral=True
            )

            return

        await interaction.followup.send(
            (
                "✅ Transcript enviado para "
                f"{transcript_channel.mention}."
            ),
            ephemeral=True
        )


# =========================================================
# CLOSE
# =========================================================

class CloseTicket(
    discord.ui.Button
):

    def __init__(self):

        super().__init__(
            label="Close Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.danger,
            custom_id="ticket_close"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not can_access_ticket(
            interaction
        ):

            await interaction.response.send_message(
                "❌ You do not have permission to close this ticket.",
                ephemeral=True
            )

            return

        channel = interaction.channel

        if channel is None:

            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔒 Closing Ticket",
                description=(
                    "This ticket will be deleted "
                    "in **5 seconds**.\n\n"
                    "Use **📄 Transcript** first "
                    "if you need a copy."
                ),
                color=discord.Color.orange()
            )
        )

        await asyncio.sleep(
            5
        )

        try:

            await channel.delete(
                reason=(
                    f"Ticket closed by "
                    f"{interaction.user} "
                    f"({interaction.user.id})"
                )
            )

        except discord.NotFound:

            pass

        except discord.Forbidden:

            print(
                f"❌ Missing permission to delete "
                f"ticket {channel.id}"
            )

        except discord.HTTPException as error:

            print(
                f"❌ Ticket deletion error: {error}"
            )


# =========================================================
# COG
# =========================================================

class Tickets(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    init_database()

    await bot.add_cog(
        Tickets(bot)
    )

    # -----------------------------------------------------
    # REMOVE EXISTING TICKET COMMAND
    # -----------------------------------------------------

    old_ticket = bot.tree.get_command(
        "ticket"
    )

    if old_ticket is not None:

        bot.tree.remove_command(
            "ticket"
        )

        print(
            "🗑️ Removed existing /ticket command."
        )

    # -----------------------------------------------------
    # REGISTER GROUP
    # -----------------------------------------------------

    bot.tree.add_command(
        TicketGroup()
    )

    # -----------------------------------------------------
    # PERSISTENT VIEWS
    # -----------------------------------------------------
    # Isto permite que os botões continuem a funcionar
    # depois de o bot reiniciar.

    bot.add_view(
        TicketPanel()
    )

    bot.add_view(
        TicketControls()
    )

    print(
        "🎫 /ticket command registered."
    )

    print(
        "🎫 Persistent ticket views registered."
    )

    print(
        "🎫 Tickets cog loaded."
    )