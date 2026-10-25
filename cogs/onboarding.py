# =========================================================
# MISUKI ONBOARDING
# Automatic welcome DM + one-time 30-day free license
# =========================================================

import asyncio

import discord
from discord.ext import commands

from cogs.utility import get_user_preferences, format_user_datetime


class Onboarding(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def find_installer(self, guild):
        try:
            async for entry in guild.audit_logs(
                limit=20,
                action=discord.AuditLogAction.bot_add
            ):
                target = getattr(entry, "target", None)

                if target and getattr(target, "id", None) == self.bot.user.id:
                    user = getattr(entry, "user", None)
                    if user is not None:
                        return user
        except Exception as error:
            print(
                f"Could not read installer audit log for "
                f"{guild.name} ({guild.id}): {error}"
            )

        return guild.owner

    async def send_welcome_dm(
        self,
        guild,
        user,
        license_key,
        expires_at
    ):

        language, timezone_name = get_user_preferences(
            user.id
        )

        texts = {
            "en": {
                "title": "Welcome to Misuki",
                "description": f"Thank you for adding Misuki to **{guild.name}**.\n\nYour server has received **30 days of Misuki Premium completely free**.",
                "guide": "Quick Start Guide",
                "steps": "1. Configure your server settings.\n2. Set up the verification system.\n3. Configure tickets and support channels.\n4. Configure moderation features.\n5. Check your license and Premium features.",
                "license": "Your Free 30-Day License",
                "license_text": "License key: {key}\nExpires: {date}\n\nNo funds will be charged when your free license expires. There are no automatic charges, renewals, or payments after the free period. When the license expires, your Premium benefits will simply end.",
                "help": "Need Help?",
                "help_text": "You can use the Misuki dashboard to manage your server and license. Make sure Misuki has the permissions required by the features you enable.",
                "footer": "Misuki • Premium License"
            },
            "pt": {
                "title": "Bem-vindo ao Misuki",
                "description": f"Obrigado por adicionar o Misuki a **{guild.name}**.\n\nO seu servidor recebeu **30 dias de Misuki Premium totalmente grátis**.",
                "guide": "Guia rápido",
                "steps": "1. Configure as definições do servidor.\n2. Configure o sistema de verificação.\n3. Configure os tickets e canais de suporte.\n4. Configure as funcionalidades de moderação.\n5. Consulte a sua licença e as funcionalidades Premium.",
                "license": "A sua licença gratuita de 30 dias",
                "license_text": "Chave da licença: {key}\nExpira em: {date}\n\nNão será cobrado qualquer valor quando a sua licença gratuita expirar. Não existem cobranças, renovações ou pagamentos automáticos após o período gratuito. Quando a licença expirar, os benefícios Premium simplesmente terminam.",
                "help": "Precisa de ajuda?",
                "help_text": "Pode utilizar o painel do Misuki para gerir o seu servidor e a licença. Certifique-se de que o Misuki tem as permissões necessárias para as funcionalidades que ativar.",
                "footer": "Misuki • Licença Premium"
            },
            "de": {
                "title": "Willkommen bei Misuki",
                "description": f"Danke, dass Sie Misuki zu **{guild.name}** hinzugefügt haben.\n\nIhr Server hat **30 Tage Misuki Premium kostenlos** erhalten.",
                "guide": "Schnellstart",
                "steps": "1. Servereinstellungen konfigurieren.\n2. Verifizierung einrichten.\n3. Tickets und Support-Kanäle konfigurieren.\n4. Moderationsfunktionen konfigurieren.\n5. Lizenz und Premium-Funktionen prüfen.",
                "license": "Ihre kostenlose 30-Tage-Lizenz",
                "license_text": "Lizenzschlüssel: {key}\nLäuft ab: {date}\n\nNach Ablauf der kostenlosen Lizenz werden keine Kosten berechnet. Es gibt keine automatischen Gebühren, Verlängerungen oder Zahlungen. Nach Ablauf endet einfach der Premium-Zugriff.",
                "help": "Brauchen Sie Hilfe?",
                "help_text": "Sie können das Misuki-Dashboard verwenden, um Ihren Server und Ihre Lizenz zu verwalten. Stellen Sie sicher, dass Misuki die erforderlichen Berechtigungen besitzt.",
                "footer": "Misuki • Premium-Lizenz"
            },
            "es": {
                "title": "Bienvenido a Misuki",
                "description": f"Gracias por añadir Misuki a **{guild.name}**.\n\nTu servidor ha recibido **30 días de Misuki Premium completamente gratis**.",
                "guide": "Guía rápida",
                "steps": "1. Configura los ajustes del servidor.\n2. Configura el sistema de verificación.\n3. Configura los tickets y canales de soporte.\n4. Configura las funciones de moderación.\n5. Consulta tu licencia y funciones Premium.",
                "license": "Tu licencia gratuita de 30 días",
                "license_text": "Clave de licencia: {key}\nCaduca: {date}\n\nNo se cobrará ningún importe cuando expire tu licencia gratuita. No hay cargos, renovaciones ni pagos automáticos. Cuando expire la licencia, simplemente terminarán los beneficios Premium.",
                "help": "¿Necesitas ayuda?",
                "help_text": "Puedes usar el panel de Misuki para gestionar tu servidor y tu licencia. Asegúrate de que Misuki tenga los permisos necesarios.",
                "footer": "Misuki • Licencia Premium"
            },
            "fr": {
                "title": "Bienvenue sur Misuki",
                "description": f"Merci d’avoir ajouté Misuki à **{guild.name}**.\n\nVotre serveur a reçu **30 jours de Misuki Premium entièrement gratuits**.",
                "guide": "Guide de démarrage",
                "steps": "1. Configurez les paramètres du serveur.\n2. Configurez le système de vérification.\n3. Configurez les tickets et les canaux d’assistance.\n4. Configurez les fonctions de modération.\n5. Consultez votre licence et les fonctions Premium.",
                "license": "Votre licence gratuite de 30 jours",
                "license_text": "Clé de licence : {key}\nExpire le : {date}\n\nAucun montant ne sera facturé à l’expiration de votre licence gratuite. Il n’y a aucun prélèvement, renouvellement ou paiement automatique. À l’expiration, les avantages Premium prennent simplement fin.",
                "help": "Besoin d’aide ?",
                "help_text": "Vous pouvez utiliser le tableau de bord Misuki pour gérer votre serveur et votre licence. Vérifiez que Misuki dispose des permissions nécessaires.",
                "footer": "Misuki • Licence Premium"
            }
        }

        text = texts.get(
            language,
            texts["en"]
        )

        expiration = (
            format_user_datetime(
                expires_at,
                timezone_name
            )
            if expires_at
            else "30 days after activation"
        )

        embed = discord.Embed(
            title=text["title"],
            description=text["description"],
            color=discord.Color.blurple()
        )

        embed.add_field(
            name=text["guide"],
            value=text["steps"],
            inline=False
        )

        embed.add_field(
            name=text["license"],
            value=text["license_text"].format(
                key=license_key,
                date=expiration
            ),
            inline=False
        )

        embed.add_field(
            name=text["help"],
            value=text["help_text"],
            inline=False
        )

        embed.set_footer(
            text=text["footer"]
        )

        try:
            await user.send(
                embed=embed
            )
            print(
                f"Sent onboarding DM to {user} for "
                f"{guild.name} ({guild.id})."
            )
        except Exception as error:
            print(
                f"Could not send onboarding DM to {user} "
                f"for {guild.name} ({guild.id}): {error}"
            )


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await asyncio.sleep(3)

        license_manager = self.bot.get_cog("LicenseManager")

        if license_manager is None:
            print(
                f"LicenseManager is unavailable; onboarding skipped for "
                f"{guild.name} ({guild.id})."
            )
            return

        if not license_manager.database_ready():
            print(
                f"License database is unavailable; onboarding skipped for "
                f"{guild.name} ({guild.id})."
            )
            return

        installer = await self.find_installer(guild)

        if installer is None:
            print(
                f"Could not determine installer for "
                f"{guild.name} ({guild.id})."
            )
            return

        license_key = await license_manager.create_license(
            guild.id,
            30
        )

        if license_key is None:
            print(
                f"No new free license created for {guild.name} ({guild.id}); "
                "the server already has a license."
            )
            return

        license_data = await license_manager.get_license(guild.id)

        if license_data is None:
            print(
                f"Free license was created but could not be read for "
                f"{guild.name} ({guild.id})."
            )
            return

        await self.send_welcome_dm(
            guild,
            installer,
            license_key,
            license_data["expires_at"]
        )


async def setup(bot):
    await bot.add_cog(Onboarding(bot))
    print("Onboarding loaded.")
