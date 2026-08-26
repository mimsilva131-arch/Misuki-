
import discord
from discord import app_commands
from discord.ext import commands

from datetime import datetime
import asyncio
import io
import sqlite3
import os


# =========================================================
# DATABASE
# =========================================================

DATABASE = "data/tickets.db"


def init_database():

    os.makedirs(
        os.path.dirname(DATABASE),
        exist_ok=True
    )

    with sqlite3.connect(DATABASE) as db:

        db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_counter (
                guild_id INTEGER PRIMARY KEY,
                number INTEGER NOT NULL DEFAULT 0
            )
        """)

        db.commit()


def get_next_number(guild_id):

    with sqlite3.connect(DATABASE) as db:

        cursor = db.cursor()

        cursor.execute(
            """
            SELECT number
            FROM ticket_counter
            WHERE guild_id = ?
            """,
            (guild_id,)
        )

        result = cursor.fetchone()

        if result is None:

            number = 1

            cursor.execute(
                """
                INSERT INTO ticket_counter
                (guild_id, number)
                VALUES (?, ?)
                """,
                (
                    guild_id,
                    number
                )
            )

        else:

            number = result[0] + 1

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

        db.commit()

        return number


# =========================================================
# CONFIG HELPER
# =========================================================

def get_config(bot):

    return bot.get_cog("Config")


# =========================================================
# /TICKET GROUP
# =========================================================

class TicketGroup(app_commands.Group):

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
        description="Set up the ticket panel."
    )
    @app_commands.describe(
        channel="Channel where the ticket panel will be sent."
    )
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def setup(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

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

        await channel.send(
            embed=embed,
            view=TicketPanel()
        )

        await interaction.response.send_message(
            f"✅ Ticket panel created in "
            f"{channel.mention}.",
            ephemeral=True
        )


# =========================================================
# PANEL
# =========================================================

class TicketPanel(discord.ui.View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            CreateTicket()
        )


# =========================================================
# CREATE TICKET BUTTON
# =========================================================

class CreateTicket(discord.ui.Button):

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

            return

        # -------------------------------------------------
        # Prevent multiple tickets
        # -------------------------------------------------

        for channel in guild.text_channels:

            if not channel.name.startswith("ticket-"):

                continue

            if channel.topic == (
                f"Ticket owner: {interaction.user.id}"
            ):

                await interaction.response.send_message(
                    f"❌ You already have an open ticket: "
                    f"{channel.mention}",
                    ephemeral=True
                )

                return

        # -------------------------------------------------
        # Config
        # -------------------------------------------------

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
        # Category
        # -------------------------------------------------

        category_id = config.get_channel_value(
            guild.id,
            "ticket_category_id"
        )

        category = None

        if category_id:

            category = guild.get_channel(
                int(category_id)
            )

            if not isinstance(
                category,
                discord.CategoryChannel
            ):

                category = None

        # -------------------------------------------------
        # Number
        # -------------------------------------------------

        number = get_next_number(
            guild.id
        )

        ticket_name = (
            f"ticket-{number:04d}"
        )

        # -------------------------------------------------
        # Permissions
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

        # Bot

        if guild.me:

            overwrites[guild.me] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    manage_channels=True,
                    manage_messages=True
                )
            )

        # -------------------------------------------------
        # Staff
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

            for role_id in (
                staff_roles + moderator_roles
            ):

                role = guild.get_role(
                    int(role_id)
                )

                if role:

                    overwrites[role] = (
                        discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True,
                            attach_files=True,
                            embed_links=True
                        )
                    )

        except Exception:

            pass

        # -------------------------------------------------
        # Create channel
        # -------------------------------------------------

        try:

            ticket = await guild.create_text_channel(
                name=ticket_name,
                category=category,
                overwrites=overwrites,
                topic=(
                    f"Ticket owner: "
                    f"{interaction.user.id}"
                )
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ I don't have permission to "
                "create the ticket channel.",
                ephemeral=True
            )

            return

        except discord.HTTPException as error:

            await interaction.response.send_message(
                f"❌ Discord returned an error:\n"
                f"`{error}`",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # Ticket embed
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
            timestamp=datetime.now()
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

        await ticket.send(
            content=interaction.user.mention,
            embed=embed,
            view=TicketControls()
        )

        await interaction.response.send_message(
            f"✅ Ticket created: "
            f"{ticket.mention}",
            ephemeral=True
        )


# =========================================================
# TICKET CONTROLS
# =========================================================

class TicketControls(discord.ui.View):

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
# TRANSCRIPT
# =========================================================

class Transcript(discord.ui.Button):

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
        # Transcript channel
        # -------------------------------------------------

        channel_id = config.get_channel_value(
            guild.id,
            "transcript_log_channel_id"
        )

        if not channel_id:

            await interaction.followup.send(
                "❌ Transcript Logs has not been configured.",
                ephemeral=True
            )

            return

        transcript_channel = guild.get_channel(
            int(channel_id)
        )

        if not isinstance(
            transcript_channel,
            discord.TextChannel
        ):

            await interaction.followup.send(
                "❌ The Transcript Logs channel "
                "does not exist.",
                ephemeral=True
            )

            return

        # -------------------------------------------------
        # Get messages
        # -------------------------------------------------

        output = []

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
                        a.url
                        for a in message.attachments
                    )
                    +
                    "\n"
                )

        # -------------------------------------------------
        # Transcript
        # -------------------------------------------------

        text = (
            "MISUKI TICKET TRANSCRIPT\n"
            "================================================\n\n"
            f"Servidor: {guild.name}\n"
            f"Ticket: {channel.name}\n"
            f"Gerado por: {interaction.user}\n"
            f"Data: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            "================================================\n\n"
        )

        text += "\n".join(output)

        file = discord.File(
            io.BytesIO(
                text.encode("utf-8")
            ),
            filename=(
                f"{channel.name}-transcript.txt"
            )
        )

        # -------------------------------------------------
        # Log
        # -------------------------------------------------

        embed = discord.Embed(
            title="📄 Ticket Transcript",
            description=(
                f"Transcript do **{channel.name}**"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )

        embed.add_field(
            name="👤 Gerado por",
            value=interaction.user.mention,
            inline=True
        )

        embed.set_footer(
            text="Misuki Ticket System"
        )

        try:

            await transcript_channel.send(
                embed=embed,
                file=file
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ Não tenho permissão para enviar "
                "o transcript para esse canal.",
                ephemeral=True
            )

            return

        await interaction.followup.send(
            f"✅ Transcript enviado para "
            f"{transcript_channel.mention}.",
            ephemeral=True
        )


# =========================================================
# CLOSE
# =========================================================

class CloseTicket(discord.ui.Button):

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

        await asyncio.sleep(5)

        try:

            await channel.delete(
                reason=(
                    f"Ticket closed by "
                    f"{interaction.user}"
                )
            )

        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException
        ):

            pass


# =========================================================
# COG
# =========================================================

class Tickets(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


# =========================================================
# SETUP
# =========================================================

async def setup(bot):

    init_database()

    await bot.add_cog(
        Tickets(bot)
    )

    # Add /ticket only if it doesn't already exist
    if bot.tree.get_command("ticket") is None:

        bot.tree.add_command(
            TicketGroup()
        )

