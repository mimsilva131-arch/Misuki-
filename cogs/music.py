# =========================================================
# MISUKI - MUSIC
# =========================================================

import asyncio
import requests
from dataclasses import dataclass, field
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
import imageio_ffmpeg
import yt_dlp


YTDL_OPTIONS = {
    "format": "bestaudio[acodec!=none]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "source_address": "0.0.0.0",
    "socket_timeout": 12,
    "retries": 2,
    "fragment_retries": 2,
    "extractor_retries": 2,
    "skip_unavailable_fragments": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


@dataclass
class Track:
    title: str
    webpage_url: str
    stream_url: str
    duration: Optional[int] = None
    requester_id: Optional[int] = None


@dataclass
class GuildPlayer:
    queue: list[Track] = field(default_factory=list)
    current: Optional[Track] = None
    voice: Optional[discord.VoiceClient] = None
    loop: bool = False


class Music(commands.Cog):
    """In-memory music player. It does not use PostgreSQL."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, GuildPlayer] = {}
        self._extract_lock = asyncio.Lock()
        self.ffmpeg_executable = imageio_ffmpeg.get_ffmpeg_exe()

    def player_for(self, guild_id: int) -> GuildPlayer:
        return self.players.setdefault(guild_id, GuildPlayer())

    async def _extract_soundcloud(self, query: str) -> Track:
        loop = asyncio.get_running_loop()

        def extract():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
                info = ytdl.extract_info(f"scsearch3:{query}", download=False)
                entries = [entry for entry in (info.get("entries") or []) if entry]
                if not entries:
                    raise RuntimeError("No SoundCloud results")

                last_error = None
                for candidate in entries:
                    try:
                        if candidate.get("url"):
                            stream_url = candidate["url"]
                        else:
                            resolved = ytdl.extract_info(candidate.get("webpage_url"), download=False)
                            stream_url = resolved.get("url")

                        if not stream_url:
                            raise RuntimeError("No playable SoundCloud stream")

                        return Track(
                            title=str(candidate.get("title") or "Unknown track"),
                            webpage_url=str(candidate.get("webpage_url") or ""),
                            stream_url=stream_url,
                            duration=candidate.get("duration"),
                        )
                    except Exception as error:
                        last_error = error

                raise RuntimeError(f"No playable SoundCloud result: {last_error}")

        return await loop.run_in_executor(None, extract)

    async def _extract_archive(self, query: str) -> Track:
        loop = asyncio.get_running_loop()

        def extract():
            params = {
                "q": f"title:({query}) OR description:({query})",
                "fl[]": ["identifier", "title", "description"],
                "rows": 5,
                "page": 1,
                "output": "json",
            }
            response = requests.get(
                "https://archive.org/advancedsearch.php",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            docs = response.json().get("response", {}).get("docs", [])

            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
                last_error = None
                for doc in docs:
                    identifier = doc.get("identifier")
                    if not identifier:
                        continue
                    try:
                        info = ytdl.extract_info(
                            f"https://archive.org/details/{identifier}",
                            download=False,
                        )
                        stream_url = info.get("url")
                        if not stream_url:
                            formats = info.get("formats") or []
                            audio_formats = [
                                item for item in formats
                                if item.get("url") and item.get("acodec") != "none"
                            ]
                            if audio_formats:
                                stream_url = audio_formats[-1]["url"]
                        if not stream_url:
                            raise RuntimeError("No playable audio stream")

                        return Track(
                            title=str(info.get("title") or doc.get("title") or "Unknown track"),
                            webpage_url=str(info.get("webpage_url") or f"https://archive.org/details/{identifier}"),
                            stream_url=stream_url,
                            duration=info.get("duration"),
                        )
                    except Exception as error:
                        last_error = error

            raise RuntimeError(f"No playable Internet Archive result: {last_error or 'no results'}")

        return await loop.run_in_executor(None, extract)

    async def _extract(self, query: str) -> Track:
        search_query = query.strip()
        if not search_query:
            raise RuntimeError("Empty music query")

        async with self._extract_lock:
            is_url = search_query.startswith(("http://", "https://"))

            if is_url:
                lower_url = search_query.lower()
                if "youtube.com" in lower_url or "youtu.be" in lower_url:
                    raise RuntimeError("YouTube is not supported by Misuki's music player")

                loop = asyncio.get_running_loop()

                def extract_url():
                    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
                        info = ytdl.extract_info(search_query, download=False)
                        stream_url = info.get("url")
                        if not stream_url:
                            formats = info.get("formats") or []
                            audio_formats = [
                                item for item in formats
                                if item.get("url") and item.get("acodec") != "none"
                            ]
                            if audio_formats:
                                stream_url = audio_formats[-1]["url"]
                        if not stream_url:
                            raise RuntimeError("The URL does not contain a playable audio stream")
                        return Track(
                            title=str(info.get("title") or "Unknown track"),
                            webpage_url=str(info.get("webpage_url") or search_query),
                            stream_url=stream_url,
                            duration=info.get("duration"),
                        )

                return await loop.run_in_executor(None, extract_url)

            errors = []
            try:
                return await self._extract_soundcloud(search_query)
            except Exception as error:
                errors.append(f"SoundCloud: {error}")

            try:
                return await self._extract_archive(search_query)
            except Exception as error:
                errors.append(f"Internet Archive: {error}")

            raise RuntimeError(" | ".join(errors))

    async def _play_next(self, guild_id: int):
        player = self.players.get(guild_id)
        if player is None or player.voice is None or not player.voice.is_connected():
            return

        if player.current is not None and player.loop:
            track = player.current
        elif player.queue:
            track = player.queue.pop(0)
            player.current = track
        else:
            player.current = None
            return

        voice = player.voice

        def after(error):
            if error:
                print(f"⚠️ Music playback error in guild {guild_id}: {error}")
            if not player.loop:
                player.current = None
            future = asyncio.run_coroutine_threadsafe(
                self._play_next(guild_id),
                self.bot.loop,
            )
            try:
                future.result(timeout=30)
            except Exception as callback_error:
                print(f"⚠️ Could not continue music queue in guild {guild_id}: {callback_error}")

        try:
            source = discord.FFmpegPCMAudio(
                track.stream_url,
                executable=self.ffmpeg_executable,
                **FFMPEG_OPTIONS,
            )
            voice.play(source, after=after)
        except Exception as error:
            print(f"⚠️ Could not start music in guild {guild_id}: {type(error).__name__}: {error}")
            player.current = None
            if player.queue:
                await self._play_next(guild_id)

    async def _ensure_voice(self, interaction: discord.Interaction) -> Optional[GuildPlayer]:
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ This command can only be used inside a server.",
                ephemeral=True,
            )
            return None

        member = interaction.user
        if not isinstance(member, discord.Member) or member.voice is None or member.voice.channel is None:
            await interaction.followup.send(
                "🎧 Join a voice channel first.",
                ephemeral=True,
            )
            return None

        channel = member.voice.channel
        player = self.player_for(interaction.guild.id)

        if interaction.guild.voice_client is not None:
            voice = interaction.guild.voice_client
            player.voice = voice
            if voice.channel != channel:
                await interaction.followup.send(
                    "❌ I am already playing in another voice channel.",
                    ephemeral=True,
                )
                return None
        else:
            try:
                player.voice = await channel.connect()
            except Exception as error:
                print(f"⚠️ Could not join voice channel: {error}")
                await interaction.followup.send(
                    "❌ I could not join your voice channel.",
                    ephemeral=True,
                )
                return None

        return player

    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        if seconds is None:
            return "Live"
        seconds = max(0, int(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @app_commands.command(name="play", description="Play a song or add it to the music queue.")
    @app_commands.describe(query="A song name, SoundCloud/Internet Archive URL, or direct audio URL.")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()

        player = await self._ensure_voice(interaction)
        if player is None:
            return

        try:
            track = await self._extract(query)
        except Exception as error:
            print(f"⚠️ Music search failed: {type(error).__name__}: {error}")
            await interaction.followup.send(
                "❌ I could not find or load that track. Try a different song name or URL.",
                ephemeral=True,
            )
            return

        track.requester_id = interaction.user.id
        was_playing = player.voice is not None and player.voice.is_playing()

        if player.current is None and not was_playing:
            player.current = track
            await self._play_next(interaction.guild.id)

            if player.voice is None or not player.voice.is_playing():
                player.current = None
                raise RuntimeError("The audio stream could not be started")

            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"[{track.title}]({track.webpage_url})",
                color=discord.Color.blurple(),
            )
            embed.add_field(name="Duration", value=self._format_duration(track.duration))
            await interaction.followup.send(embed=embed)
            return

        player.queue.append(track)
        position = len(player.queue)
        embed = discord.Embed(
            title="➕ Added to Queue",
            description=f"[{track.title}]({track.webpage_url})",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Position", value=str(position))
        embed.add_field(name="Duration", value=self._format_duration(track.duration))
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="Pause the current track.")
    async def pause(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.voice or not player.voice.is_playing():
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return
        player.voice.pause()
        await interaction.response.send_message("⏸️ Playback paused.")

    @app_commands.command(name="resume", description="Resume the current track.")
    async def resume(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.voice or not player.voice.is_paused():
            await interaction.response.send_message("❌ Playback is not paused.", ephemeral=True)
            return
        player.voice.resume()
        await interaction.response.send_message("▶️ Playback resumed.")

    @app_commands.command(name="skip", description="Skip the current track.")
    async def skip(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.voice or not (player.voice.is_playing() or player.voice.is_paused()):
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return
        player.loop = False
        player.current = None
        player.voice.stop()
        await interaction.response.send_message("⏭️ Track skipped.")

    @app_commands.command(name="stop", description="Stop playback and clear the queue.")
    async def stop(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.voice:
            await interaction.response.send_message("❌ The music player is not active.", ephemeral=True)
            return
        player.queue.clear()
        player.current = None
        player.loop = False
        if player.voice.is_playing() or player.voice.is_paused():
            player.voice.stop()
        await interaction.response.send_message("⏹️ Playback stopped and the queue was cleared.")

    @app_commands.command(name="queue", description="Show the current music queue.")
    async def queue(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or (player.current is None and not player.queue):
            await interaction.response.send_message("🎵 The music queue is empty.", ephemeral=True)
            return

        lines = []
        if player.current:
            lines.append(f"**Now:** [{player.current.title}]({player.current.webpage_url})")
        for index, track in enumerate(player.queue[:10], 1):
            lines.append(f"{index}. [{track.title}]({track.webpage_url})")
        if len(player.queue) > 10:
            lines.append(f"… and {len(player.queue) - 10} more.")

        embed = discord.Embed(
            title="🎵 Music Queue",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Show the current track.")
    async def nowplaying(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.current:
            await interaction.response.send_message("🎵 Nothing is currently playing.", ephemeral=True)
            return

        track = player.current
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"[{track.title}]({track.webpage_url})",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Duration", value=self._format_duration(track.duration))
        embed.add_field(name="Loop", value="On" if player.loop else "Off")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Toggle looping for the current track.")
    async def loop(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing is currently playing.", ephemeral=True)
            return
        player.loop = not player.loop
        await interaction.response.send_message(
            "🔁 Loop enabled." if player.loop else "➡️ Loop disabled."
        )

    @app_commands.command(name="leave", description="Disconnect Misuki from the voice channel.")
    async def leave(self, interaction: discord.Interaction):
        player = self.players.get(interaction.guild.id) if interaction.guild else None
        if not player or not player.voice:
            await interaction.response.send_message("❌ I am not in a voice channel.", ephemeral=True)
            return

        player.queue.clear()
        player.current = None
        player.loop = False
        await player.voice.disconnect()
        player.voice = None
        await interaction.response.send_message("👋 Left the voice channel.")

    async def cog_unload(self):
        for player in self.players.values():
            if player.voice:
                try:
                    await player.voice.disconnect(force=True)
                except Exception:
                    pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
    print("🎵 Music cog loaded.")
