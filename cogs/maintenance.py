import asyncio
import json
import os
import time

import discord
import requests
from discord import app_commands
from discord.ext import commands


OWNER_ID = int(os.getenv("OWNER_ID", "0") or 0)
SITE_URL = os.getenv("MISUKI_SITE_URL", "https://misuki.onrender.com").rstrip("/")
BOT_VERSION = os.getenv("MISUKI_VERSION", "").strip() or "Unspecified"
SITE_VERSION = os.getenv("SITE_VERSION", "").strip() or "Unspecified"

STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "maintenance.json",
)

ESSENTIAL_COMMANDS = {
    "maintenance",
    "help",
    "ping",
    "status",
}


class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = False
        self.estimated = ""
        self.changes = ""
        self.scope = "both"
        self.started_at = 0.0
        self._sync_task = None
        self._load_state()

    def _load_state(self):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                state = json.load(file)

            if isinstance(state, dict) and state.get("active"):
                self.active = True
                self.estimated = str(state.get("estimated") or "Not specified")
                self.changes = str(state.get("changes") or "Maintenance work in progress.")
                self.scope = str(state.get("scope") or "both")
                self.started_at = float(state.get("started_at") or time.time())
        except Exception:
            pass

    def _save_state(self):
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        temporary = STATE_FILE + ".tmp"

        if self.active:
            state = {
                "active": True,
                "estimated": self.estimated,
                "changes": self.changes,
                "scope": self.scope,
                "started_at": self.started_at,
            }
        else:
            state = {"active": False}

        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False)
        os.replace(temporary, STATE_FILE)

    async def _sync_site(self):
        payload = {
            "active": self.active,
            "estimated": self.estimated,
            "changes": self.changes,
            "scope": self.scope,
            "started_at": self.started_at,
            "bot_version": BOT_VERSION,
            "site_version": SITE_VERSION,
        }

        def send():
            try:
                return requests.post(
                    f"{SITE_URL}/api/maintenance",
                    json=payload,
                    headers={
                        "X-Misuki-Bot-Token": os.getenv("DISCORD_BOT_TOKEN", "")
                    },
                    timeout=4,
                )
            except Exception as error:
                print(f"⚠️ Could not sync maintenance state with site: {error}")
                return None

        response = await asyncio.to_thread(send)
        if response is None:
            return False

        if response.status_code >= 400:
            print(
                f"⚠️ Site maintenance endpoint returned "
                f"{response.status_code}: {response.text[:200]}"
            )
            return False

        return True

    async def _sync_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            if self.active:
                await self._sync_site()
            await asyncio.sleep(30)

    async def cog_load(self):
        if self._sync_task is None or self._sync_task.done():
            self._sync_task = asyncio.create_task(self._sync_loop())

    def cog_unload(self):
        if self._sync_task:
            self._sync_task.cancel()

    def is_active(self):
        return self.active

    def is_command_allowed(self, command_name):
        return command_name in ESSENTIAL_COMMANDS

    def _find_announcement_channel(self, guild):
        candidates = []

        if guild.system_channel is not None:
            candidates.append(guild.system_channel)

        candidates.extend(
            channel
            for channel in guild.text_channels
            if channel not in candidates
        )

        for channel in candidates:
            permissions = channel.permissions_for(guild.me)
            if permissions.send_messages:
                return channel

        return None

    async def _announce_completion(self, changes):
        message = (
            "🛠️ **Misuki maintenance completed**\n\n"
            f"**What changed:** {changes}\n"
            f"**Bot version:** {BOT_VERSION}\n"
            f"**Site version:** {SITE_VERSION}\n\n"
            "The maintenance has finished and normal activity has been restored. "
            "Thank you for your patience."
        )

        sent = 0
        failed = 0

        for guild in list(self.bot.guilds):
            channel = self._find_announcement_channel(guild)
            if channel is None:
                failed += 1
                continue

            try:
                await channel.send(message)
                sent += 1
            except (discord.Forbidden, discord.HTTPException):
                failed += 1

        return sent, failed

    @app_commands.command(
        name="maintenance",
        description="Start or finish Misuki maintenance mode."
    )
    @app_commands.describe(
        action="Start or finish maintenance.",
        estimated="Estimated maintenance interval, for example 15 minutes.",
        scope="What is being maintained.",
        changes="What the update/maintenance will change.",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Start", value="start"),
            app_commands.Choice(name="Finish", value="finish"),
        ],
        scope=[
            app_commands.Choice(name="Bot + Site", value="both"),
            app_commands.Choice(name="Bot only", value="bot"),
            app_commands.Choice(name="Site only", value="site"),
        ],
    )
    async def maintenance(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        estimated: str | None = None,
        scope: app_commands.Choice[str] | None = None,
        changes: str | None = None,
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ You do not have permission to use maintenance mode.",
                ephemeral=True,
            )
            return

        if action.value == "start":
            if self.active:
                await interaction.response.send_message(
                    "⚠️ Maintenance mode is already active.",
                    ephemeral=True,
                )
                return

            self.active = True
            self.estimated = (estimated or "Not specified").strip()
            self.changes = (changes or "Maintenance work in progress.").strip()
            self.scope = scope.value if scope else "both"
            self.started_at = time.time()
            self._save_state()

            site_synced = await self._sync_site()

            await interaction.response.send_message(
                "🛠️ **Maintenance mode enabled.**\n\n"
                f"**Estimated time:** {self.estimated}\n"
                f"**Scope:** {self.scope}\n"
                f"**Changes:** {self.changes}\n\n"
                f"**Site page:** {SITE_URL}/maintenance\n"
                f"**Site sync:** {'✅ Active' if site_synced else '⚠️ Waiting for site connection'}\n\n"
                "The bot is now restricted to essential activity.",
                ephemeral=True,
            )
            return

        if not self.active:
            await interaction.response.send_message(
                "ℹ️ Maintenance mode is not active.",
                ephemeral=True,
            )
            return

        final_changes = (changes or self.changes).strip()
        self.active = False
        self.changes = final_changes
        self._save_state()

        site_synced = await self._sync_site()
        sent, failed = await self._announce_completion(final_changes)

        await interaction.response.send_message(
            "✅ **Maintenance completed.**\n\n"
            f"**Bot version:** {BOT_VERSION}\n"
            f"**Site version:** {SITE_VERSION}\n"
            f"**Server announcements:** {sent} sent"
            + (f", {failed} unavailable" if failed else "")
            + f"\n**Site sync:** {'✅ Restored' if site_synced else '⚠️ Site sync pending'}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Maintenance(bot))
