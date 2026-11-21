import asyncio
import json
import os
import re
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
        self.duration_seconds = 0
        self._finishing = False
        self.bot_version = BOT_VERSION
        self.site_version = SITE_VERSION
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
                self.duration_seconds = int(state.get("duration_seconds") or self._parse_duration(self.estimated) or 0)
                self.bot_version = str(state.get("bot_version") or BOT_VERSION)
                self.site_version = str(state.get("site_version") or SITE_VERSION)
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
                "duration_seconds": self.duration_seconds,
                "bot_version": self.bot_version,
                "site_version": self.site_version,
            }
        else:
            state = {"active": False}

        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(state, file, ensure_ascii=False)
        os.replace(temporary, STATE_FILE)

    async def _sync_site(self):
        payload = {
            "active": self.active and self.scope in {"site", "both"},
            "estimated": self.estimated,
            "changes": self.changes,
            "scope": self.scope,
            "started_at": self.started_at,
            "bot_version": self.bot_version,
            "site_version": self.site_version,
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

    @staticmethod
    def _parse_duration(value):
        """Convert a friendly interval such as '15 minutes' or '1h 30m' to seconds."""
        text = str(value or "").strip().lower()
        if not text:
            return 0

        total = 0
        matched = False
        for amount, unit in re.findall(r"(\\d+(?:\\.\\d+)?)\\s*(seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d)", text):
            matched = True
            number = float(amount)
            if unit.startswith("s"):
                multiplier = 1
            elif unit.startswith("m"):
                multiplier = 60
            elif unit.startswith("h"):
                multiplier = 3600
            else:
                multiplier = 86400
            total += number * multiplier

        if not matched and re.fullmatch(r"\\d+(?:\\.\\d+)?", text):
            total = float(text) * 60
            matched = True

        seconds = int(total)
        if not matched or seconds <= 0 or seconds > 7 * 24 * 60 * 60:
            return 0
        return seconds

    async def _sync_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            if self.active:
                if self.duration_seconds > 0 and time.time() >= self.started_at + self.duration_seconds:
                    await self._finish_maintenance(self.changes, automatic=True)
                elif self.scope in {"site", "both"}:
                    await self._sync_site()
            await asyncio.sleep(10)

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
            if guild.me is None:
                continue

            permissions = channel.permissions_for(guild.me)
            if permissions.send_messages:
                return channel

        return None

    async def _finish_maintenance(self, changes, automatic=False):
        if not self.active or self._finishing:
            return False

        self._finishing = True
        try:
            final_changes = (changes or self.changes).strip()
            self.active = False
            self.changes = final_changes
            self.duration_seconds = 0
            self._save_state()

            site_synced = await self._sync_site()
            sent, failed = await self._announce_completion(final_changes)
            if automatic:
                print(
                    "🛠️ Maintenance ended automatically after the estimated interval. "
                    f"Announcements sent: {sent}, unavailable: {failed}."
                )
            return site_synced
        finally:
            self._finishing = False

    async def _announce_completion(self, changes):
        message = (
            "🛠️ **Misuki maintenance completed**\n\n"
            f"**What changed:** {changes}\n"
            f"**Bot version:** {self.bot_version}\n"
            f"**Site version:** {self.site_version}\n\n"
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
        bot_version="Bot version to publish.",
        site_version="Site version to publish.",
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
        estimated: str,
        scope: app_commands.Choice[str] | None = None,
        changes: str | None = None,
        bot_version: str | None = None,
        site_version: str | None = None,
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

            self.estimated = estimated.strip()
            self.duration_seconds = self._parse_duration(self.estimated)
            if self.duration_seconds <= 0:
                await interaction.response.send_message(
                    "❌ Invalid estimated interval. Use a value such as `15 minutes`, `1 hour`, `1h 30m`, or `90m` (maximum 7 days).",
                    ephemeral=True,
                )
                return

            self.active = True
            self.changes = (changes or "Maintenance work in progress.").strip()
            self.scope = scope.value if scope else "both"
            self.started_at = time.time()
            if bot_version and bot_version.strip():
                self.bot_version = bot_version.strip()
            if site_version and site_version.strip():
                self.site_version = site_version.strip()
            self._save_state()

            site_synced = await self._sync_site()

            await interaction.response.send_message(
                "🛠️ **Maintenance mode enabled.**\n\n"
                f"**Estimated time:** {self.estimated}\n"
                "**Automatic end:** enabled\n"
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
        if bot_version and bot_version.strip():
            self.bot_version = bot_version.strip()
        if site_version and site_version.strip():
            self.site_version = site_version.strip()
        site_synced = await self._finish_maintenance(final_changes)

        await interaction.response.send_message(
            "✅ **Maintenance completed.**\n\n"
            f"**Bot version:** {self.bot_version}\n"
            f"**Site version:** {self.site_version}\n"
            "**Server announcements:** sent to all available servers.\n"
            f"**Site sync:** {'✅ Restored' if site_synced else '⚠️ Site sync pending'}",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Maintenance(bot))
