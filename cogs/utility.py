
# =========================================================
# MISUKI - UTILITY
# =========================================================

import discord

from discord.ext import commands


import os
import time
import json
from zoneinfo import ZoneInfo

import psycopg2
from discord import app_commands
import discord
from discord.ext import commands


DATABASE_URL = os.getenv("DATABASE_URL")
SUPPORTED_LANGUAGES = {"en": "English", "pt": "Português", "de": "Deutsch", "es": "Español", "fr": "Français"}
DEFAULT_LANGUAGE = "en"
DEFAULT_TIMEZONE = "UTC"

# Discord server locales are used for public bot messages. Personal language
# preferences remain reserved for DMs/personal responses.
DISCORD_LOCALE_LANGUAGES = {
    "en-US": "en",
    "en-GB": "en",
    "pt-BR": "pt",
    "pt-PT": "pt",
    "de": "de",
    "es-ES": "es",
    "fr": "fr",
}

SERVER_TRANSLATIONS = {
    "en": {
        "command_check_failure": "⚠️ This command cannot be executed right now. Please check the required conditions and try again.",
        "command_error": "⚠️ An error occurred while executing this command. Misuki may be temporarily experiencing problems. Please try again shortly.",
        "maintenance": "🛠️ Misuki is currently under maintenance. The bot is limited to essential activity while the update is being completed. Our staff is already working on it. Please try again later.",
        "premium_unavailable": "❌ Premium functionality is temporarily unavailable. Please try again later.",
        "license_verify_error": "❌ The license could not be verified. Please try again later.",
        "license_required": "🔒 This command requires an active Misuki license for this server.",
        "impersonate_permission": "❌ Misuki does not have permission to manage webhooks in this channel.",
        "impersonate_http": "❌ Discord rejected the operation.",
        "impersonate_error": "❌ An unexpected error occurred.",
        "database_url_missing": "❌ DATABASE_URL is not configured.",
        "license_manager_missing": "❌ The LicenseManager is not loaded.",
        "transcript_sent": "✅ Transcript sent to ",
        "license_database_unavailable": "License database is not available.",
        "license_min": "The license duration must be at least 1 day.",
        "license_max": "The maximum license duration is 3650 days.",
    },
    "pt": {
        "command_check_failure": "⚠️ Este comando não pode ser executado neste momento. Verifique as condições necessárias e tente novamente.",
        "command_error": "⚠️ Ocorreu um erro ao executar este comando. O Misuki pode estar temporariamente com problemas. Tente novamente daqui a pouco.",
        "maintenance": "🛠️ O Misuki está atualmente em manutenção. O bot está limitado à atividade essencial enquanto a atualização é concluída. A nossa equipa já está a tratar do problema. Tente novamente mais tarde.",
        "premium_unavailable": "❌ As funcionalidades Premium estão temporariamente indisponíveis. Tente novamente mais tarde.",
        "license_verify_error": "❌ Não foi possível verificar a licença. Tente novamente mais tarde.",
        "license_required": "🔒 Este comando requer uma licença Misuki ativa para este servidor.",
        "impersonate_permission": "❌ O Misuki não tem permissão para gerir webhooks neste canal.",
        "impersonate_http": "❌ O Discord rejeitou a operação.",
        "impersonate_error": "❌ Ocorreu um erro inesperado.",
        "database_url_missing": "❌ A DATABASE_URL não está configurada.",
        "license_manager_missing": "❌ O LicenseManager não está carregado.",
        "transcript_sent": "✅ Transcrição enviada para ",
        "license_database_unavailable": "A base de dados das licenças não está disponível.",
        "license_min": "A duração da licença deve ser de pelo menos 1 dia.",
        "license_max": "A duração máxima da licença é de 3650 dias.",
    },
    "de": {
        "command_check_failure": "⚠️ Dieser Befehl kann derzeit nicht ausgeführt werden. Prüfen Sie die erforderlichen Bedingungen und versuchen Sie es erneut.",
        "command_error": "⚠️ Beim Ausführen dieses Befehls ist ein Fehler aufgetreten. Misuki hat möglicherweise vorübergehend Probleme. Versuchen Sie es gleich erneut.",
        "maintenance": "🛠️ Misuki befindet sich derzeit in Wartung. Der Bot ist während der Aktualisierung auf wesentliche Aktivitäten beschränkt. Unser Team arbeitet bereits daran. Bitte versuchen Sie es später erneut.",
        "premium_unavailable": "❌ Premium-Funktionen sind vorübergehend nicht verfügbar. Bitte versuchen Sie es später erneut.",
        "license_verify_error": "❌ Die Lizenz konnte nicht überprüft werden. Bitte versuchen Sie es später erneut.",
        "license_required": "🔒 Dieser Befehl erfordert eine aktive Misuki-Lizenz für diesen Server.",
        "impersonate_permission": "❌ Misuki hat keine Berechtigung, Webhooks in diesem Kanal zu verwalten.",
        "impersonate_http": "❌ Discord hat den Vorgang abgelehnt.",
        "impersonate_error": "❌ Ein unerwarteter Fehler ist aufgetreten.",
        "database_url_missing": "❌ DATABASE_URL ist nicht konfiguriert.",
        "license_manager_missing": "❌ Der LicenseManager ist nicht geladen.",
        "transcript_sent": "✅ Transkript gesendet an ",
        "license_database_unavailable": "Die Lizenzdatenbank ist nicht verfügbar.",
        "license_min": "Die Lizenzdauer muss mindestens 1 Tag betragen.",
        "license_max": "Die maximale Lizenzdauer beträgt 3650 Tage.",
    },
    "es": {
        "command_check_failure": "⚠️ Este comando no se puede ejecutar en este momento. Comprueba las condiciones necesarias e inténtalo de nuevo.",
        "command_error": "⚠️ Se produjo un error al ejecutar este comando. Es posible que Misuki tenga problemas temporalmente. Inténtalo de nuevo en unos instantes.",
        "maintenance": "🛠️ Misuki está actualmente en mantenimiento. El bot está limitado a la actividad esencial mientras se completa la actualización. Nuestro equipo ya está trabajando en ello. Inténtalo de nuevo más tarde.",
        "premium_unavailable": "❌ Las funciones Premium no están disponibles temporalmente. Inténtalo de nuevo más tarde.",
        "license_verify_error": "❌ No se ha podido verificar la licencia. Inténtalo de nuevo más tarde.",
        "license_required": "🔒 Este comando requiere una licencia activa de Misuki para este servidor.",
        "impersonate_permission": "❌ Misuki no tiene permiso para gestionar webhooks en este canal.",
        "impersonate_http": "❌ Discord rechazó la operación.",
        "impersonate_error": "❌ Se produjo un error inesperado.",
        "database_url_missing": "❌ DATABASE_URL no está configurada.",
        "license_manager_missing": "❌ El LicenseManager no está cargado.",
        "transcript_sent": "✅ Transcripción enviada a ",
        "license_database_unavailable": "La base de datos de licencias no está disponible.",
        "license_min": "La duración de la licencia debe ser de al menos 1 día.",
        "license_max": "La duración máxima de la licencia es de 3650 días.",
    },
    "fr": {
        "command_check_failure": "⚠️ Cette commande ne peut pas être exécutée pour le moment. Vérifiez les conditions requises et réessayez.",
        "command_error": "⚠️ Une erreur s'est produite lors de l'exécution de cette commande. Misuki rencontre peut-être des problèmes temporaires. Réessayez dans quelques instants.",
        "maintenance": "🛠️ Misuki est actuellement en maintenance. Le bot est limité aux activités essentielles pendant la mise à jour. Notre équipe travaille déjà dessus. Veuillez réessayer plus tard.",
        "premium_unavailable": "❌ Les fonctionnalités Premium sont temporairement indisponibles. Veuillez réessayer plus tard.",
        "license_verify_error": "❌ La licence n'a pas pu être vérifiée. Veuillez réessayer plus tard.",
        "license_required": "🔒 Cette commande nécessite une licence Misuki active pour ce serveur.",
        "impersonate_permission": "❌ Misuki n'a pas la permission de gérer les webhooks dans ce salon.",
        "impersonate_http": "❌ Discord a refusé l'opération.",
        "impersonate_error": "❌ Une erreur inattendue s'est produite.",
        "database_url_missing": "❌ DATABASE_URL n'est pas configurée.",
        "license_manager_missing": "❌ Le LicenseManager n'est pas chargé.",
        "transcript_sent": "✅ Transcription envoyée à ",
        "license_database_unavailable": "La base de données des licences n'est pas disponible.",
        "license_min": "La durée de la licence doit être d'au moins 1 jour.",
        "license_max": "La durée maximale de la licence est de 3650 jours.",
    },
}


def get_server_language(guild):
    """Return the bot language for public server messages, defaulting to English."""
    locale = str(getattr(guild, "preferred_locale", "") or "").strip()
    return DISCORD_LOCALE_LANGUAGES.get(locale, "en")


def get_server_translation(guild, key, **kwargs):
    """Return a translated public message, with English as the final fallback."""
    language = get_server_language(guild)
    text = SERVER_TRANSLATIONS.get(language, SERVER_TRANSLATIONS["en"]).get(
        key,
        SERVER_TRANSLATIONS["en"].get(key, key),
    )
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return text

TRANSLATIONS = {
    "en": {
        "license_active": "Active",
        "license_inactive": "Inactive",
        "license_label": "License",
        "available_commands": "Available commands",
        "setup_help": "Use Personal Settings to choose your language and timezone.",
        "title": "🤖 Misuki Bot — Commands",
        "setup_roles": "Roles",
        "setup_channels": "Channels",
        "setup_tickets": "Tickets",
        "setup_moderation": "Moderation",
        "setup_verification": "Verification",
        "setup_jail": "Jail",
        "setup_stats": "Stats",
        "setup_announcements": "Announcements",
        "setup_title": "Misuki Bot Setup",
        "setup_description": "Configure Misuki for this server.",
        "setup_choose": "Choose a category below.",
        "tutorial_title": "Misuki setup tutorial",
        "tutorial_description": "Configure Misuki from the setup panel. This guide explains the required steps and provides direct access to the panel.",
        "tutorial_permissions_title": "Required permissions",
        "tutorial_permissions": "For initial setup, allow Misuki to view channels, send messages, embed links, read message history, manage channels and manage roles. Specific features may require additional permissions.",
        "tutorial_steps_title": "Steps",
        "tutorial_steps": "1. Invite Misuki with the required permissions.\n2. Open {setup} to enter the setup panel.\n3. In Personal Settings, choose your language and timezone.\n4. In Roles, configure the roles used by each system.\n5. In Channels, select the channels for logs, verification, announcements and tickets.\n6. Open Tickets, Moderation, Verification and Jail and confirm the required settings.\n7. Publish the panels for the features you want to use.\n8. Reopen this guide with {tutorial}.",
        "tutorial_setup_title": "Setup panel",
        "tutorial_setup": "Open {setup} to configure the server. The panel lets you select roles, channels and ticket categories directly, without copying IDs.",
        "tutorial_configuration_title": "Recommended order",
        "tutorial_configuration": "Start with Personal Settings, then Roles and Channels. Next configure Tickets, Moderation, Verification and Jail. Stats does not require manual configuration.",
        "tutorial_open_setup": "Open Setup",
        "tutorial_wrong_user": "These setup controls belong to another user.",
        "tutorial_footer": "Misuki • Setup guide",

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
        "setup_language": "Language",
        "setup_timezone": "Timezone",
        "setup_settings": "Personal settings",
        "setup_settings_description": "Choose the language and timezone used by Misuki for your personal messages.",
    },
    "pt": {
        "license_active": "Ativa",
        "license_inactive": "Inativa",
        "license_label": "Licença",
        "available_commands": "Comandos disponíveis",
        "setup_help": "Use as Definições pessoais para escolher a sua língua e o fuso horário.",

        "tutorial_title": "Tutorial de configuração do Misuki",
        "tutorial_description": "Configure o Misuki através do painel de configuração. Este guia explica os passos necessários e dá acesso direto ao painel.",
        "tutorial_permissions_title": "Permissões necessárias",
        "tutorial_permissions": "Para a configuração inicial, permita ao Misuki ver canais, enviar mensagens, incorporar links, ler o histórico de mensagens, gerir canais e gerir cargos. Algumas funcionalidades podem exigir permissões adicionais.",
        "tutorial_steps_title": "Passos",
        "tutorial_steps": "1. Convide o Misuki com as permissões necessárias.\n2. Abra {setup} para entrar no painel de configuração.\n3. Em Definições pessoais, escolha a sua língua e o fuso horário.\n4. Em Cargos, defina os cargos usados por cada sistema.\n5. Em Canais, escolha os canais de logs, verificação, anúncios e tickets.\n6. Abra Tickets, Moderação, Verificação e Prisão e confirme as definições necessárias.\n7. Publique os painéis das funcionalidades que pretende utilizar.\n8. Volte a abrir este guia com {tutorial}.",
        "tutorial_setup_title": "Painel de configuração",
        "tutorial_setup": "Abra {setup} para configurar o servidor. O painel permite selecionar diretamente cargos, canais e a categoria dos tickets, sem ter de copiar IDs.",
        "tutorial_configuration_title": "Ordem recomendada",
        "tutorial_configuration": "Comece por Definições pessoais, depois Cargos e Canais. Em seguida configure Tickets, Moderação, Verificação e Prisão. As Estatísticas não precisam de configuração manual.",
        "tutorial_open_setup": "Abrir configuração",
        "tutorial_wrong_user": "Estes controlos de configuração pertencem a outro utilizador.",
        "tutorial_footer": "Misuki • Guia de configuração",

        "title": "🤖 Misuki Bot — Comandos",
        "setup_roles": "Cargos",
        "setup_channels": "Canais",
        "setup_tickets": "Tickets",
        "setup_moderation": "Moderação",
        "setup_verification": "Verificação",
        "setup_jail": "Prisão",
        "setup_stats": "Estatísticas",
        "setup_announcements": "Anúncios",
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
        "setup_language": "Língua",
        "setup_timezone": "Fuso horário",
        "setup_settings": "Definições pessoais",
        "setup_settings_description": "Escolha a língua e o fuso horário usados pelo Misuki nas suas mensagens pessoais.",
    },
    "de": {
        "license_active": "Aktiv",
        "license_inactive": "Inaktiv",
        "license_label": "Lizenz",
        "available_commands": "Verfügbare Befehle",
        "setup_help": "Verwenden Sie die persönlichen Einstellungen, um Sprache und Zeitzone auszuwählen.",

        "tutorial_title": "Misuki-Einrichtungsanleitung",
        "tutorial_description": "Folgen Sie diesen Schritten, um Misuki korrekt auf Ihrem Server zu konfigurieren.",
        "tutorial_permissions_title": "Erforderliche Berechtigungen",
        "tutorial_permissions": "Server verwalten, Kanäle verwalten, Rollen verwalten, Kanäle ansehen, Nachrichten senden, Links einbetten, Nachrichtenverlauf lesen, Nachrichten verwalten, Webhooks verwalten, Mitglieder moderieren und Audit-Log ansehen. Einige Funktionen können zusätzliche Berechtigungen erfordern.",
        "tutorial_steps_title": "Schritte",
        "tutorial_steps": "1. Laden Sie Misuki mit den erforderlichen Berechtigungen ein.\n2. Führen Sie /setup aus.\n3. Öffnen Sie die persönlichen Einstellungen und wählen Sie Ihre Sprache.\n4. Konfigurieren Sie Rollen und Kanäle für die gewünschten Funktionen.\n5. Testen Sie die konfigurierten Panels und Befehle.",
        "tutorial_setup_title": "Setup-Befehl",
        "tutorial_setup": "Verwenden Sie /setup, um das Konfigurationsmenü zu öffnen. Verwenden Sie jederzeit /tutorial, um diese Anleitung erneut anzuzeigen.",
        "tutorial_open_setup": "Setup öffnen",
        "tutorial_wrong_user": "Diese Einrichtungselemente gehören einem anderen Benutzer.",
        "tutorial_footer": "Misuki • Einrichtungsanleitung",
        "title": "🤖 Misuki Bot — Befehle",
        "setup_roles": "Rollen",
        "setup_channels": "Kanäle",
        "setup_tickets": "Tickets",
        "setup_moderation": "Moderation",
        "setup_verification": "Verifizierung",
        "setup_jail": "Gefängnis",
        "setup_stats": "Statistiken",
        "setup_announcements": "Ankündigungen",
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
        "setup_language": "Sprache",
        "setup_timezone": "Zeitzone",
        "setup_settings": "Persönliche Einstellungen",
        "setup_settings_description": "Wählen Sie die von Misuki für Ihre persönlichen Nachrichten verwendete Sprache und Zeitzone.",
    },
    "es": {
        "license_active": "Activa",
        "license_inactive": "Inactiva",
        "license_label": "Licencia",
        "available_commands": "Comandos disponibles",
        "setup_help": "Usa la configuración personal para elegir tu idioma y zona horaria.",

        "tutorial_title": "Tutorial de configuración de Misuki",
        "tutorial_description": "Sigue estos pasos para configurar correctamente Misuki en tu servidor.",
        "tutorial_permissions_title": "Permisos necesarios",
        "tutorial_permissions": "Gestionar servidor, Gestionar canales, Gestionar roles, Ver canales, Enviar mensajes, Insertar enlaces, Leer historial de mensajes, Gestionar mensajes, Gestionar webhooks, Moderar miembros y Ver registro de auditoría. Algunas funciones pueden requerir permisos adicionales.",
        "tutorial_steps_title": "Pasos",
        "tutorial_steps": "1. Invita o Misuki con los permisos necesarios.\n2. Ejecuta /setup.\n3. Abre Configuración personal y elige tu idioma.\n4. Configura los roles y canales de las funciones que utilices.\n5. Prueba los paneles y comandos configurados.",
        "tutorial_setup_title": "Comando de configuración",
        "tutorial_setup": "Usa /setup para abrir el menú de configuración. Usa /tutorial en cualquier momento para volver a consultar esta guía.",
        "tutorial_open_setup": "Abrir configuración",
        "tutorial_wrong_user": "Estos controles de configuración pertenecen a otro usuario.",
        "tutorial_footer": "Misuki • Guía de configuración",
        "title": "🤖 Misuki Bot — Comandos",
        "setup_roles": "Roles",
        "setup_channels": "Canales",
        "setup_tickets": "Tickets",
        "setup_moderation": "Moderación",
        "setup_verification": "Verificación",
        "setup_jail": "Prisión",
        "setup_stats": "Estadísticas",
        "setup_announcements": "Anuncios",
        "setup_title": "Configuración de Misuki",
        "setup_description": "Configuro Misuki para este servidor.",
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
        "setup_language": "Idioma",
        "setup_timezone": "Zona horaria",
        "setup_settings": "Configuración personal",
        "setup_settings_description": "Elige el idioma y la zona horaria que Misuki utilizará en tus mensajes personales.",
    },
    "fr": {
        "license_active": "Active",
        "license_inactive": "Inactive",
        "license_label": "Licence",
        "available_commands": "Commandes disponibles",
        "setup_help": "Utilisez les paramètres personnels pour choisir votre langue et votre fuseau horaire.",

        "tutorial_title": "Guide de configuration de Misuki",
        "tutorial_description": "Suivez ces étapes pour configurer correctement Misuki sur votre serveur.",
        "tutorial_permissions_title": "Permissions requises",
        "tutorial_permissions": "Gérer le serveur, Gérer les salons, Gérer les rôles, Voir les salons, Envoyer des messages, Intégrer des liens, Lire l’historique des messages, Gérer les messages, Gérer les webhooks, Modérer les membres et Voir le journal d’audit. Certaines fonctions peuvent nécessiter des permissions supplémentaires.",
        "tutorial_steps_title": "Étapes",
        "tutorial_steps": "1. Invitez Misuki avec les permissions requises.\n2. Exécutez /setup.\n3. Ouvrez les paramètres personnels et choisissez votre langue.\n4. Configurez les rôles et salons des fonctions utilisées.\n5. Testez les panneaux et commandes configurés.",
        "tutorial_setup_title": "Commande de configuration",
        "tutorial_setup": "Utilisez /setup pour ouvrir le menu de configuration. Utilisez /tutorial à tout moment pour revoir ce guide.",
        "tutorial_open_setup": "Ouvrir la configuration",
        "tutorial_wrong_user": "Ces contrôles de configuration appartiennent à un autre utilisateur.",
        "tutorial_footer": "Misuki • Guide de configuration",
        "title": "🤖 Misuki Bot — Commandes",
        "setup_roles": "Rôles",
        "setup_channels": "Salons",
        "setup_tickets": "Tickets",
        "setup_moderation": "Modération",
        "setup_verification": "Vérification",
        "setup_jail": "Prison",
        "setup_stats": "Statistiques",
        "setup_announcements": "Annonces",
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
        "setup_language": "Langue",
        "setup_timezone": "Fuseau horaire",
        "setup_settings": "Paramètres personnels",
        "setup_settings_description": "Choisissez la langue et le fuseau horaire utilisés par Misuki pour vos messages personnels.",
    },
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

            if interaction.response.is_done():
                await interaction.followup.send(
                    text,
                    ephemeral=True
                )
            else:
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
        free_commands = {
            "help", "ping", "setup", "tutorial", "license"
        }

        owner_commands = {
            "createlicense", "revokelicense", "extendlicense"
        }

        premium_commands = {
            "ticket", "verify", "warn", "warnings", "unwarn",
            "clearwarnings", "clear", "timeout", "untimeout",
            "kick", "ban", "unban", "softban", "jail", "unjail",
            "jailinfo", "announce", "trigger", "impersonate"
        }

        available_commands = []

        def collect_commands(command, prefix=""):
            command_name = getattr(command, "name", None)
            if not command_name:
                return

            full_name = f"{prefix} {command_name}".strip()
            root_name = full_name.split(" ", 1)[0]

            if root_name in owner_commands and interaction.user.id != owner_id:
                return

            if root_name in premium_commands and not active_license:
                return

            if (
                root_name not in free_commands
                and root_name not in premium_commands
                and root_name not in owner_commands
            ):
                return

            children = getattr(command, "commands", None)

            if children:
                for child in children:
                    collect_commands(child, full_name)
                return

            available_commands.append("/" + full_name)

        for command in self.bot.tree.get_commands():
            collect_commands(command)

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
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
        except discord.HTTPException as error:
            print(f"❌ Error executing /help: {error}")


# =========================================================
# /DIAGNOSE (SECRET)
# =========================================================

    @discord.app_commands.command(
        name="diagnose",
        description="Run a private Misuki system diagnostic."
    )
    @discord.app_commands.describe(
        advanced="Run the extended diagnostic checks."
    )
    @discord.app_commands.default_permissions(
        administrator=True
    )
    async def diagnose(
        self,
        interaction: discord.Interaction,
        advanced: bool = False
    ):
        """Private operational diagnostic for server administrators."""
        owner_id = int(os.getenv("OWNER_ID", "0") or "0")
        is_owner = interaction.user.id == owner_id
        is_admin = (
            interaction.guild is not None
            and isinstance(interaction.user, discord.Member)
            and interaction.user.guild_permissions.administrator
        )

        if not is_owner and not is_admin:
            await interaction.response.send_message(
                "❌ You do not have permission to use this diagnostic.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)
        results = []

        try:
            latency = round(self.bot.latency * 1000)
            results.append((
                "Bot",
                "🟢 Operational" if self.bot.is_ready() else "🔴 Down",
                f"{latency} ms"
            ))
        except Exception as error:
            results.append(("Bot", "🔴 Error", str(error)[:120]))

        database_ok = False
        database_detail = "DATABASE_URL unavailable"
        connection = None
        try:
            if DATABASE_URL:
                started = time.perf_counter()
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                database_detail = f"{round((time.perf_counter() - started) * 1000)} ms"
                database_ok = True
        except Exception as error:
            database_detail = str(error)[:120]
        finally:
            if connection:
                connection.close()

        results.append((
            "Database",
            "🟢 Operational" if database_ok else "🔴 Down",
            database_detail
        ))

        website_ok = False
        website_detail = "No response"
        try:
            from urllib.request import Request, urlopen
            site_url = os.getenv(
                "MISUKI_SITE_URL",
                "https://misuki.onrender.com"
            ).rstrip("/")
            started = time.perf_counter()
            request = Request(
                f"{site_url}/api/health",
                headers={"User-Agent": "Misuki-Diagnostic/1.0"}
            )
            with urlopen(request, timeout=5) as response:
                status_code = response.status
                body = response.read(4096).decode("utf-8", errors="replace")
            elapsed = round((time.perf_counter() - started) * 1000)
            if 200 <= status_code < 300:
                website_ok = True
                website_detail = f"{status_code} • {elapsed} ms"
                try:
                    current = json.loads(body).get("current", {})
                    website_detail = (
                        f"{status_code} • {elapsed} ms • "
                        f"API {current.get('api', 'unknown')} • "
                        f"DB {current.get('database', 'unknown')} • "
                        f"Bot {current.get('bot', 'unknown')}"
                    )
                except Exception:
                    pass
            else:
                website_detail = f"HTTP {status_code}"
        except Exception as error:
            website_detail = str(error)[:120]

        results.append((
            "Website / API",
            "🟢 Operational" if website_ok else "🔴 Down",
            website_detail
        ))

        if interaction.guild is not None:
            me = interaction.guild.me
            if me is not None:
                required = {
                    "View Channels": me.guild_permissions.view_channel,
                    "Send Messages": me.guild_permissions.send_messages,
                    "Embed Links": me.guild_permissions.embed_links,
                    "Read History": me.guild_permissions.read_message_history,
                    "Manage Channels": me.guild_permissions.manage_channels,
                    "Manage Roles": me.guild_permissions.manage_roles,
                }
                missing = [
                    name for name, allowed in required.items()
                    if not allowed
                ]
                results.append((
                    "Permissions",
                    "🟡 Warning" if missing else "🟢 Operational",
                    "Missing: " + ", ".join(missing) if missing else "Core permissions OK"
                ))
            else:
                results.append(("Permissions", "🟡 Warning", "Bot member cache unavailable"))

        try:
            from bot import MISUKI_VERSION, get_uptime
            results.append((
                "Version / Uptime",
                "🟢 Operational",
                f"v{MISUKI_VERSION} • {get_uptime()}"
            ))
        except Exception as error:
            results.append(("Version / Uptime", "🟡 Warning", str(error)[:120]))

        warnings = sum(1 for _, state, _ in results if state.startswith("🟡"))
        failures = sum(1 for _, state, _ in results if state.startswith("🔴"))

        if failures:
            overall, color = "🔴 Critical issues detected", discord.Color.red()
        elif warnings:
            overall, color = "🟡 Operational with warnings", discord.Color.orange()
        else:
            overall, color = "🟢 Fully operational", discord.Color.green()

        embed = discord.Embed(
            title="🕵️ Misuki Diagnostic Report",
            description=(
                f"**Overall:** {overall}\n"
                f"**Checks:** {len(results) - failures - warnings} passed • "
                f"{warnings} warnings • {failures} critical"
            ),
            color=color
        )

        for name, state, detail in results:
            embed.add_field(
                name=f"{state}  {name}",
                value=detail[:1024],
                inline=False
            )

        if advanced:
            embed.add_field(
                name="🔧 Advanced",
                value=(
                    f"**Guild:** {interaction.guild.name if interaction.guild else 'DM'}\n"
                    f"**Guild ID:** {interaction.guild.id if interaction.guild else 'N/A'}\n"
                    f"**Bot:** {self.bot.user} ({self.bot.user.id if self.bot.user else 'N/A'})\n"
                    f"**Latency:** {round(self.bot.latency * 1000)} ms"
                ),
                inline=False
            )

        embed.set_footer(text="Misuki • Private diagnostic")
        await interaction.followup.send(embed=embed, ephemeral=True)


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

