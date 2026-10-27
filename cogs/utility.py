
# =========================================================
# MISUKI - UTILITY
# =========================================================

import discord

from discord.ext import commands


import os
from zoneinfo import ZoneInfo

import psycopg2
from discord import app_commands
import discord
from discord.ext import commands


DATABASE_URL = os.getenv("DATABASE_URL")
SUPPORTED_LANGUAGES = {"en": "English", "pt": "Português", "de": "Deutsch", "es": "Español", "fr": "Français"}
DEFAULT_LANGUAGE = "en"
DEFAULT_TIMEZONE = "UTC"

TRANSLATIONS = {
    "en": {
        "title": "🤖 Misuki Bot — Commands",
        "setup_title": "Misuki Bot Setup",
        "setup_description": "Configure Misuki for this server.",
        "setup_choose": "Choose a category below.",
        "description": "/ping — Check if the bot is online.\n/help — Show this message.",
        "settings_title": "Personal settings",
        "settings_description": "Choose the language used in your DMs and set your timezone.",
        "language_button": "🌐 Language",
        "timezone_button": "🕐 Timezone",
        "language_title": "Choose your language",
        "timezone_title": "Set your timezone",
        "timezone_placeholder": "Example: Europe/Lisbon",
        "saved_language": "Language saved: **{value}**.",
        "saved_timezone": "Timezone saved: **{value}**.",
        "invalid_timezone": "That timezone is not valid. Use an IANA timezone such as Europe/Lisbon or America/New_York.",
        "settings_footer": "Language: {language} • Timezone: {timezone}",
        "ping": "🏓 **Pong!**\n📡 Latency: {latency}ms",
    }        "setup_language": "Language",
        "setup_timezone": "Timezone",
        "setup_settings": "Personal settings",
        "setup_settings_description": "Choose the language and timezone used by Misuki for your personal messages.",
,
    "pt": {
        "title": "🤖 Misuki Bot — Comandos",
        "setup_title": "Configuração do Misuki",
        "setup_description": "Configure o Misuki para este servidor.",
        "setup_choose": "Escolha uma categoria abaixo.",
        "description": "/ping — Verifica se o bot está online.\n/help — Mostra esta mensagem.",
        "settings_title": "Definições pessoais",
        "settings_description": "Escolha a língua usada nas suas DMs e defina o seu fuso horário.",
        "language_button": "🌐 Língua",
        "timezone_button": "🕐 Fuso horário",
        "language_title": "Escolha a sua língua",
        "timezone_title": "Defina o seu fuso horário",
        "timezone_placeholder": "Exemplo: Europe/Lisbon",
        "saved_language": "Língua guardada: **{value}**.",
        "saved_timezone": "Fuso horário guardado: **{value}**.",
        "invalid_timezone": "Esse fuso horário não é válido. Use um fuso IANA como Europe/Lisbon ou America/New_York.",
        "settings_footer": "Língua: {language} • Fuso horário: {timezone}",
        "ping": "🏓 **Pong!**\n📡 Latência: {latency}ms",
    }        "setup_language": "Língua",
        "setup_timezone": "Fuso horário",
        "setup_settings": "Definições pessoais",
        "setup_settings_description": "Escolha a língua e o fuso horário usados pelo Misuki nas suas mensagens pessoais.",
,
    "de": {
        "title": "🤖 Misuki Bot — Befehle",
        "setup_title": "Misuki Bot-Konfiguration",
        "setup_description": "Konfigurieren Sie Misuki für diesen Server.",
        "setup_choose": "Wählen Sie unten eine Kategorie.",
        "description": "/ping — Prüft, ob der Bot online ist.\n/help — Zeigt diese Nachricht.",
        "settings_title": "Persönliche Einstellungen",
        "settings_description": "Wählen Sie die Sprache für Ihre DMs und Ihre Zeitzone.",
        "language_button": "🌐 Sprache",
        "timezone_button": "🕐 Zeitzone",
        "language_title": "Sprache auswählen",
        "timezone_title": "Zeitzone festlegen",
        "timezone_placeholder": "Beispiel: Europe/Berlin",
        "saved_language": "Sprache gespeichert: **{value}**.",
        "saved_timezone": "Zeitzone gespeichert: **{value}**.",
        "invalid_timezone": "Diese Zeitzone ist ungültig. Verwenden Sie eine IANA-Zeitzone wie Europe/Berlin.",
        "settings_footer": "Sprache: {language} • Zeitzone: {timezone}",
        "ping": "🏓 **Pong!**\n📡 Latenz: {latency}ms",
    }        "setup_language": "Sprache",
        "setup_timezone": "Zeitzone",
        "setup_settings": "Persönliche Einstellungen",
        "setup_settings_description": "Wählen Sie die von Misuki für Ihre persönlichen Nachrichten verwendete Sprache und Zeitzone.",
,
    "es": {
        "title": "🤖 Misuki Bot — Comandos",
        "setup_title": "Configuración de Misuki",
        "setup_description": "Configura Misuki para este servidor.",
        "setup_choose": "Elige una categoría a continuación.",
        "description": "/ping — Comprueba si el bot está conectado.\n/help — Muestra este mensaje.",
        "settings_title": "Configuración personal",
        "settings_description": "Elige el idioma de tus DMs y configura tu zona horaria.",
        "language_button": "🌐 Idioma",
        "timezone_button": "🕐 Zona horaria",
        "language_title": "Elige tu idioma",
        "timezone_title": "Configura tu zona horaria",
        "timezone_placeholder": "Ejemplo: Europe/Madrid",
        "saved_language": "Idioma guardado: **{value}**.",
        "saved_timezone": "Zona horaria guardada: **{value}**.",
        "invalid_timezone": "Esa zona horaria no es válida. Usa una zona IANA como Europe/Madrid.",
        "settings_footer": "Idioma: {language} • Zona horaria: {timezone}",
        "ping": "🏓 **Pong!**\n📡 Latencia: {latency}ms",
    }        "setup_language": "Idioma",
        "setup_timezone": "Zona horaria",
        "setup_settings": "Configuración personal",
        "setup_settings_description": "Elige el idioma y la zona horaria que Misuki utilizará en tus mensajes personales.",
,
    "fr": {
        "title": "🤖 Misuki Bot — Commandes",
        "setup_title": "Configuration de Misuki",
        "setup_description": "Configurez Misuki pour ce serveur.",
        "setup_choose": "Choisissez une catégorie ci-dessous.",
        "description": "/ping — Vérifie si le bot est en ligne.\n/help — Affiche ce message.",
        "settings_title": "Paramètres personnels",
        "settings_description": "Choisissez la langue utilisée dans vos DMs et définissez votre fuseau horaire.",
        "language_button": "🌐 Langue",
        "timezone_button": "🕐 Fuseau horaire",
        "language_title": "Choisissez votre langue",
        "timezone_title": "Définissez votre fuseau horaire",
        "timezone_placeholder": "Exemple : Europe/Paris",
        "saved_language": "Langue enregistrée : **{value}**.",
        "saved_timezone": "Fuseau horaire enregistré : **{value}**.",
        "invalid_timezone": "Ce fuseau horaire n’est pas valide. Utilisez un fuseau IANA comme Europe/Paris.",
        "settings_footer": "Langue : {language} • Fuseau : {timezone}",
        "ping": "🏓 **Pong !**\n📡 Latence : {latency}ms",
    }        "setup_language": "Langue",
        "setup_timezone": "Fuseau horaire",
        "setup_settings": "Paramètres personnels",
        "setup_settings_description": "Choisissez la langue et le fuseau horaire utilisés par Misuki pour vos messages personnels.",
,
}


def get_db_connection():
    if not DATABASE_URL:
        return None
    return psycopg2.connect(DATABASE_URL, connect_timeout=10)


def initialize_preferences_database():
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    language TEXT NOT NULL DEFAULT 'en',
                    timezone TEXT NOT NULL DEFAULT 'UTC',
                    updated_at DOUBLE PRECISION NOT NULL
                )
            """)
        connection.commit()
        print("🌐 User preferences database initialized.")
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"⚠️ Could not initialize user preferences: {error}")
    finally:
        if connection:
            connection.close()


def get_user_preferences(user_id):
    language, timezone_name = DEFAULT_LANGUAGE, DEFAULT_TIMEZONE
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return language, timezone_name
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT language, timezone FROM user_preferences WHERE user_id = %s",
                (str(user_id),)
            )
            row = cursor.fetchone()
        if row:
            language = row[0] if row[0] in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
            timezone_name = row[1] or DEFAULT_TIMEZONE
    except Exception as error:
        print(f"⚠️ Could not read preferences for {user_id}: {error}")
    finally:
        if connection:
            connection.close()
    return language, timezone_name


def save_user_preferences(user_id, language=None, timezone_name=None):
    current_language, current_timezone = get_user_preferences(user_id)
    language = language if language in SUPPORTED_LANGUAGES else current_language
    timezone_name = timezone_name or current_timezone
    try:
        ZoneInfo(timezone_name)
    except Exception:
        timezone_name = current_timezone

    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            return False
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_preferences (user_id, language, timezone, updated_at)
                VALUES (%s, %s, %s, EXTRACT(EPOCH FROM NOW()))
                ON CONFLICT (user_id)
                DO UPDATE SET language = EXCLUDED.language,
                              timezone = EXCLUDED.timezone,
                              updated_at = EXCLUDED.updated_at
                """,
                (str(user_id), language, timezone_name)
            )
        connection.commit()
        return True
    except Exception as error:
        if connection:
            connection.rollback()
        print(f"⚠️ Could not save preferences for {user_id}: {error}")
        return False
    finally:
        if connection:
            connection.close()


def get_translation(user_id, key, **values):
    language, _ = get_user_preferences(user_id)
    text = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE]).get(
        key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    )
    return text.format(**values)


def format_user_datetime(value, timezone_name):
    if not value:
        return "Unknown"
    try:
        from datetime import timezone
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(ZoneInfo(timezone_name)).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return value.strftime("%d/%m/%Y %H:%M:%S")


class LanguageSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(
            placeholder="🌐 Select language",
            options=[
                discord.SelectOption(label="English", value="en", emoji="🇬🇧"),
                discord.SelectOption(label="Português", value="pt", emoji="🇵🇹"),
                discord.SelectOption(label="Deutsch", value="de", emoji="🇩🇪"),
                discord.SelectOption(label="Español", value="es", emoji="🇪🇸"),
                discord.SelectOption(label="Français", value="fr", emoji="🇫🇷"),
            ],
            custom_id=f"misuki_language_{user_id}"
        )

    async def callback(self, interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ These settings belong to another user.", ephemeral=True
            )
            return
        language = self.values[0]
        save_user_preferences(self.user_id, language=language)
        await interaction.response.send_message(
            get_translation(self.user_id, "saved_language", value=SUPPORTED_LANGUAGES[language]),
            ephemeral=True
        )


class TimezoneModal(discord.ui.Modal):
    def __init__(self, user_id):
        self.user_id = user_id
        _, current_timezone = get_user_preferences(user_id)
        super().__init__(title=get_translation(user_id, "timezone_title"))
        self.timezone_input = discord.ui.TextInput(
            label="Timezone",
            placeholder=get_translation(user_id, "timezone_placeholder"),
            default=current_timezone,
            required=True,
            max_length=100
        )
        self.add_item(self.timezone_input)

    async def on_submit(self, interaction):
        timezone_name = str(self.timezone_input.value).strip()
        try:
            ZoneInfo(timezone_name)
        except Exception:
            await interaction.response.send_message(
                get_translation(self.user_id, "invalid_timezone"), ephemeral=True
            )
            return
        save_user_preferences(self.user_id, timezone_name=timezone_name)
        await interaction.response.send_message(
            get_translation(self.user_id, "saved_timezone", value=timezone_name),
            ephemeral=True
        )


class SettingsView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id

    @discord.ui.button(label="🌐 Language", style=discord.ButtonStyle.secondary)
    async def language_button(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ These settings belong to another user.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            get_translation(self.user_id, "language_title"),
            view=LanguageView(self.user_id),
            ephemeral=True
        )

    @discord.ui.button(label="🕐 Timezone", style=discord.ButtonStyle.secondary)
    async def timezone_button(self, interaction, button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ These settings belong to another user.", ephemeral=True
            )
            return
        await interaction.response.send_modal(TimezoneModal(self.user_id))


class LanguageView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=180)
        self.add_item(LanguageSelect(user_id))


# =========================================================
# UTILITY COG
# =========================================================

class Utility(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot


    # =====================================================
    # /PING
    # =====================================================

    @discord.app_commands.command(
        name="ping",
        description="Check if the bot is online."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        try:

            latency = round(
                self.bot.latency * 1000
            )

            language, _ = get_user_preferences(
                interaction.user.id
            )

            text = TRANSLATIONS.get(
                language,
                TRANSLATIONS[DEFAULT_LANGUAGE]
            )["ping"].format(
                latency=latency
            )

            await interaction.response.send_message(
                text
            )

        except discord.HTTPException as error:

            print(
                f"❌ Error executing /ping: {error}"
            )


    # =====================================================
    # /HELP
    # =====================================================

    @discord.app_commands.command(
        name="help",
        description="Show available commands."
    )
    async def help_command(
        self,
        interaction: discord.Interaction
    ):

        language, timezone_name = get_user_preferences(interaction.user.id)
        translations = TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE])

        license_manager = self.bot.get_cog("LicenseManager")
        active_license = False
        if interaction.guild is not None and license_manager is not None:
            try:
                active_license = await license_manager.has_active_license(interaction.guild.id)
            except Exception as error:
                print(f"⚠️ Could not check license for /help: {error}")

        owner_id = int(os.getenv("OWNER_ID", "1146083816503529545"))
        free_commands = {"help", "ping", "setup", "license"}
        owner_commands = {"createlicense", "revokelicense", "extendlicense"}
        premium_commands = {"ticket", "verify", "warn", "warnings", "unwarn", "clearwarnings", "clear", "timeout", "untimeout", "kick", "ban", "unban", "softban", "jail", "unjail", "jailinfo", "announce", "trigger", "impersonate"}
        available_commands = []

        for command in self.bot.tree.get_commands():
            name = getattr(command, 'name', None)
            if not name:
                continue
            if name in owner_commands and interaction.user.id != owner_id:
                continue
            if name in premium_commands and not active_license:
                continue
            if name in free_commands or name in premium_commands or name in owner_commands:
                available_commands.append('/' + name)

        available_commands.sort()
        status_text = translations["license_active"] if active_license else translations["license_inactive"]

        embed = discord.Embed(
            title=translations["title"],
            description=translations["description"] + "\n\n" +
                "**" + translations["license_label"] + ":** " + status_text + "\n\n" +
                "**" + translations["available_commands"] + ":**\n" +
                "\n".join("• " + name for name in available_commands),
            color=discord.Color.green() if active_license else discord.Color.blurple()
        )

        embed.add_field(
            name=translations["settings_title"],
            value=translations["setup_help"],
            inline=False
        )

        embed.set_footer(
            text=translations["settings_footer"].format(
                language=SUPPORTED_LANGUAGES.get(language, DEFAULT_LANGUAGE),
                timezone=timezone_name
            )
        )

        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.HTTPException as error:
            print(f"❌ Error executing /help: {error}")


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    initialize_preferences_database()

    await bot.add_cog(
        Utility(bot)
    )

    print(
        "🛠️ Utility cog loaded."
    )

