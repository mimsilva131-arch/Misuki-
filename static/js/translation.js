(function () {
    "use strict";

    /* =========================================================
       MISUKI — TRANSLATION SYSTEM
       ========================================================= */

    const DEFAULT_LANGUAGE = "en";
    const STORAGE_KEY = "misuki_language";

    const SUPPORTED_LANGUAGES = [
        "en",
        "pt",
        "de",
        "es",
        "fr"
    ];

    const LANGUAGE_INFO = {
        en: {
            name: "English",
            short: "EN",
            flag: "🇬🇧"
        },

        pt: {
            name: "Português",
            short: "PT",
            flag: "🇵🇹"
        },

        de: {
            name: "Deutsch",
            short: "DE",
            flag: "🇩🇪"
        },

        es: {
            name: "Español",
            short: "ES",
            flag: "🇪🇸"
        },

        fr: {
            name: "Français",
            short: "FR",
            flag: "🇫🇷"
        }
    };


    /* =========================================================
       TRANSLATIONS
       ========================================================= */

    const translations = {

        en: {
            language: {
                select: "Select language",
                en: "English",
                pt: "Portuguese",
                de: "German",
                es: "Spanish",
                fr: "French"
            },

            menu: {
                title: "Menu",
                navigation: "Navigation",
                resources: "Resources",
                legal: "Legal",
                account: "Account"
            },

            nav: {
                home: "Home",
                dashboard: "Dashboard",
                reviews: "Reviews",
                statistics: "Statistics",
                documentation: "Documentation",
                support: "Support",
                advertisement: "Advertisement",
                advertisement_admin: "Advertisement Admin",
                terms: "Terms",
                privacy: "Privacy",
                data: "Data",
                cookies: "Cookies",
                logout: "Logout",
                login: "Login with Discord"
            },

            menu_controls: {
                open: "Open menu",
                close: "Close menu"
            },

            reviews: {
                intro: "Reviews from members of Misuki communities.",
                title: "Community Reviews",
                no_reviews: "No reviews yet.",
                write_review: "Write a review",
                rating: "Rating",
                review: "Review",
                submit: "Submit Review",
                need_license: "You need an active Misuki license to write a review.",
                login_required: "Log in with Discord and have an active Misuki license to write a review.",
                section_title: "💬 Community Reviews"
            },

            license: {
                title: "License",
                back_to_dashboard: "Back to Dashboard",
                status: "Status",
                active: "Active",
                expired: "Expired",
                revoked: "Revoked",
                key: "License Key",
                expires: "Expires",
                never: "Never",
                missing: "This server does not have a Misuki license."
            },

            dashboard: {
                license: "License",
                no_authorized: "🔒 No authorized servers found.",
                no_available: "No additional servers available.",
                add_permission: "Add permission ✓",
                no_authorization: "⚠️ No authorization",
                add_misuki: "➕ Add Misuki",
                cannot_add: "⚠️ Cannot Add",
                leave_review: "⭐ Leave a Review"
            },

            footer: {
                copyright: "© 2026 Misuki. All rights reserved."
            },

            common: {
                product: "Product",
                advertise_intro: "Promote your Discord server to the Misuki community. Choose your duration and create your advertisement.",
                documentation_intro: "Learn how to configure and use Misuki in your Discord server.",
                logged_in_as: "Logged in as",
                authorized_servers: "🔐 Authorized Servers",
                available_servers: "➕ Available Servers",
                manage: "⚙️ Manage",
                write_review: "✍️ Write a review",
                rating: "Rating",
                review: "Review",
                review_placeholder: "Tell us what you think about Misuki...",
                advertisement_title: "Advertisement title",
                description: "Description",
                image_url: "Image URL",
                destination_url: "Destination URL",
                advertisement_duration: "Advertisement duration",
                server_name_placeholder: "Your server name",
                description_placeholder: "Tell people what makes your server special...",
                home_title: "Discord Bot",
                community: "Community",
                advertise: "Advertise",
                meet: "Meet",
                hero_description: "A powerful Discord bot designed to make your server easier to manage, safer and more enjoyable.",
                open_dashboard: "🚀 Open Dashboard",
                why_misuki: "Why Misuki?",
                security: "Security",
                security_description: "Keep your Discord server protected with reliable moderation and management tools.",
                performance: "Performance",
                performance_description: "Fast and responsive commands designed to work smoothly on your server.",
                management: "Management",
                management_description: "Manage your Misuki configuration directly through the dashboard.",
                service_overview: "Service overview",
                statistics_preparing: "Statistics are being prepared.",
                get_help: "Get help with Misuki",
                discord_support: "💬 Discord Support",
                join_discord: "Join Discord",
                support_description: "Join the Misuki Discord server to get help, report problems, and talk with the community.",
                documentation: "📚 Documentation",
                view_documentation: "View Documentation",
                advertisement: "Advertisement",
                what_users_say: "⭐ What users say",
                report_problem: "🐛 Report a Problem",
                documentation_help: "Check the documentation for information about configuring and using Misuki.",
                report_problem_text: "Found a bug or something that isn't working correctly? Contact the Misuki support team through Discord."
            },

            /* =====================================================
               STATISTICS
               ===================================================== */

            statistics: {
                hero_description: "Overview of the Miskui service and its current statistics.",
                service_description: "General statistics about the Miskui service.",
                servers: "Servers",
                users: "Users",
                channels: "Channels",
                commands_available: "Commands available",
                tickets_created: "Tickets created",
                verifications: "Verifications",
                system_status: "System status",
                system_description: "Current status of the Miskui service.",
                discord_bot: "Discord Bot",
                website: "Website",
                database: "Database",
                api: "API",
                operational: "Operational",
                unavailable: "Unavailable",
                online: "Online",
                offline: "Offline",
                error: "Error",
                bot_latency: "Bot latency",
                uptime: "Uptime",
                version: "Version",
                milliseconds: "ms",
                administrator_statistics: "🔐 Administrator statistics",
                admin_description: "Detailed information available only to Miskui administrators.",
                admin: "ADMIN",
                members: "Members",
                no_server_information: "No server information available.",
                no_user_information: "No user information available.",
                activity: "Activity",
                commands: "Commands",
                tickets: "Tickets",
                moderation_actions: "Moderation actions",
                announcements: "Announcements",
                privacy: "Privacy",
                privacy_description: "Public statistics are presented in an aggregated form. Specific server and user information is restricted to authorized Miskui administrators."
            },

            cookies: {
                consent: "Cookie consent",
                title: "🍪 We use cookies",
                description:
                    "Misuki uses cookies to improve your experience and keep the website working correctly.",
                accept: "Accept All",
                essential: "Essential Only",
                deny: "Deny",
                terms: "Terms",
                privacy: "Privacy",
                policy: "Cookie Policy"
            }
        },


        pt: {
            language: {
                select: "Selecionar idioma",
                en: "Inglês",
                pt: "Português",
                de: "Alemão",
                es: "Espanhol",
                fr: "Francês"
            },

            menu: {
                title: "Menu",
                navigation: "Navegação",
                resources: "Recursos",
                legal: "Legal",
                account: "Conta"
            },

            nav: {
                home: "Início",
                dashboard: "Painel",
                reviews: "Avaliações",
                statistics: "Estatísticas",
                documentation: "Documentação",
                support: "Suporte",
                advertisement: "Publicidade",
                advertisement_admin: "Administração de Publicidade",
                terms: "Termos",
                privacy: "Privacidade",
                data: "Dados",
                cookies: "Cookies",
                logout: "Terminar sessão",
                login: "Entrar com o Discord"
            },

            menu_controls: {
                open: "Abrir menu",
                close: "Fechar menu"
            },

            reviews: {
                intro: "Avaliações dos membros das comunidades Misuki.",
                title: "Avaliações da comunidade",
                no_reviews: "Ainda não há avaliações.",
                write_review: "Escrever uma avaliação",
                rating: "Classificação",
                review: "Avaliação",
                submit: "Enviar avaliação",
                need_license: "Precisa de uma licença ativa do Misuki para escrever uma avaliação.",
                login_required: "Inicie sessão no Discord e tenha uma licença ativa do Misuki para escrever uma avaliação.",
                section_title: "💬 Avaliações da comunidade"
            },

            license: {
                title: "Licença",
                back_to_dashboard: "Voltar ao painel",
                status: "Estado",
                active: "Ativa",
                expired: "Expirada",
                revoked: "Revogada",
                key: "Chave da licença",
                expires: "Expira",
                never: "Nunca",
                missing: "Este servidor não tem uma licença do Misuki."
            },

            dashboard: {
                license: "Licença",
                no_authorized: "🔒 Não foram encontrados servidores autorizados.",
                no_available: "Não existem servidores adicionais disponíveis.",
                add_permission: "Permissão para adicionar ✓",
                no_authorization: "⚠️ Sem autorização",
                add_misuki: "➕ Adicionar Misuki",
                cannot_add: "⚠️ Não é possível adicionar",
                leave_review: "⭐ Escrever uma avaliação"
            },

            footer: {
                copyright:
                    "© 2026 Misuki. Todos os direitos reservados."
            },

            common: {
                product: "Produto",
                advertise_intro: "Promova o seu servidor Discord junto da comunidade Misuki. Escolha a duração e crie o seu anúncio.",
                documentation_intro: "Aprenda a configurar e utilizar o Misuki no seu servidor Discord.",
                logged_in_as: "Sessão iniciada como",
                authorized_servers: "🔐 Servidores autorizados",
                available_servers: "➕ Servidores disponíveis",
                manage: "⚙️ Gerir",
                write_review: "✍️ Escrever uma avaliação",
                rating: "Classificação",
                review: "Avaliação",
                review_placeholder: "Diga-nos o que pensa sobre o Misuki...",
                advertisement_title: "Título da publicidade",
                description: "Descrição",
                image_url: "URL da imagem",
                destination_url: "URL de destino",
                advertisement_duration: "Duração da publicidade",
                server_name_placeholder: "Nome do seu servidor",
                description_placeholder: "Diga às pessoas o que torna o seu servidor especial...",
                home_title: "Bot do Discord",
                community: "Comunidade",
                advertise: "Publicidade",
                meet: "Conheça a",
                hero_description: "Um poderoso bot do Discord criado para tornar o seu servidor mais fácil de gerir, seguro e divertido.",
                open_dashboard: "🚀 Abrir painel",
                why_misuki: "Porquê o Misuki?",
                security: "Segurança",
                security_description: "Mantenha o seu servidor Discord protegido com ferramentas fiáveis de moderação e gestão.",
                performance: "Desempenho",
                performance_description: "Comandos rápidos e responsivos, concebidos para funcionar sem problemas no seu servidor.",
                management: "Gestão",
                management_description: "Gira a configuração do Misuki diretamente através do painel.",
                service_overview: "Visão geral do serviço",
                statistics_preparing: "As estatísticas estão a ser preparadas.",
                get_help: "Obtenha ajuda com o Misuki",
                discord_support: "💬 Suporte do Discord",
                join_discord: "Entrar no Discord",
                support_description: "Entre no servidor Discord do Misuki para obter ajuda, reportar problemas e falar com a comunidade.",
                documentation: "📚 Documentação",
                view_documentation: "Ver documentação",
                advertisement: "Publicidade",
                what_users_say: "⭐ O que dizem os utilizadores",
                report_problem: "🐛 Reportar um problema",
                documentation_help: "Consulte a documentação para obter informações sobre como configurar e utilizar o Misuki.",
                report_problem_text: "Encontrou um erro ou algo que não está a funcionar corretamente? Contacte a equipa de suporte do Misuki através do Discord."
            },

            /* =====================================================
               ESTATÍSTICAS
               ===================================================== */

            statistics: {
                hero_description: "Visão geral do serviço Miskui e das suas estatísticas atuais.",
                service_description: "Estatísticas gerais sobre o serviço Miskui.",
                servers: "Servidores",
                users: "Utilizadores",
                channels: "Canais",
                commands_available: "Comandos disponíveis",
                tickets_created: "Tickets criados",
                verifications: "Verificações",
                system_status: "Estado do sistema",
                system_description: "Estado atual do serviço Miskui.",
                discord_bot: "Bot do Discord",
                website: "Website",
                database: "Base de dados",
                api: "API",
                operational: "Operacional",
                unavailable: "Indisponível",
                online: "Online",
                offline: "Offline",
                error: "Erro",
                bot_latency: "Latência do bot",
                uptime: "Tempo de atividade",
                version: "Versão",
                milliseconds: "ms",
                administrator_statistics: "🔐 Estatísticas do administrador",
                admin_description: "Informação detalhada disponível apenas para administradores do Miskui.",
                admin: "ADMIN",
                members: "Membros",
                no_server_information: "Não existem informações de servidores disponíveis.",
                no_user_information: "Não existem informações de utilizadores disponíveis.",
                activity: "Atividade",
                commands: "Comandos",
                tickets: "Tickets",
                moderation_actions: "Ações de moderação",
                announcements: "Anúncios",
                privacy: "Privacidade",
                privacy_description: "As estatísticas públicas são apresentadas de forma agregada. As informações específicas de servidores e utilizadores estão restritas aos administradores autorizados do Miskui."
            },

            cookies: {
                consent: "Consentimento de cookies",
                title: "🍪 Utilizamos cookies",
                description:
                    "O Misuki utiliza cookies para melhorar a sua experiência e manter o website a funcionar corretamente.",
                accept: "Aceitar todos",
                essential: "Apenas essenciais",
                deny: "Recusar",
                terms: "Termos",
                privacy: "Privacidade",
                policy: "Política de Cookies"
            }
        },


        de: {
            language: {
                select: "Sprache auswählen",
                en: "Englisch",
                pt: "Portugiesisch",
                de: "Deutsch",
                es: "Spanisch",
                fr: "Französisch"
            },

            menu: {
                title: "Menü",
                navigation: "Navigation",
                resources: "Ressourcen",
                legal: "Rechtliches",
                account: "Konto"
            },

            nav: {
                home: "Startseite",
                dashboard: "Dashboard",
                reviews: "Bewertungen",
                statistics: "Statistiken",
                documentation: "Dokumentation",
                support: "Support",
                advertisement: "Werbung",
                advertisement_admin: "Werbeverwaltung",
                terms: "Bedingungen",
                privacy: "Datenschutz",
                data: "Daten",
                cookies: "Cookies",
                logout: "Abmelden",
                login: "Mit Discord anmelden"
            },

            menu_controls: {
                open: "Menü öffnen",
                close: "Menü schließen"
            },

            reviews: {
                intro: "Bewertungen von Mitgliedern der Misuki-Community.",
                title: "Community-Bewertungen",
                no_reviews: "Noch keine Bewertungen.",
                write_review: "Bewertung schreiben",
                rating: "Bewertung",
                review: "Bewertung",
                submit: "Bewertung senden",
                need_license: "Du brauchst eine aktive Misuki-Lizenz, um eine Bewertung zu schreiben.",
                login_required: "Melde dich mit Discord an und habe eine aktive Misuki-Lizenz, um eine Bewertung zu schreiben.",
                section_title: "💬 Community-Bewertungen"
            },

            license: {
                title: "Lizenz",
                back_to_dashboard: "Zurück zum Dashboard",
                status: "Status",
                active: "Aktiv",
                expired: "Abgelaufen",
                revoked: "Widerrufen",
                key: "Lizenzschlüssel",
                expires: "Läuft ab",
                never: "Niemals",
                missing: "Dieser Server hat keine Misuki-Lizenz."
            },

            dashboard: {
                license: "Lizenz",
                no_authorized: "🔒 Keine autorisierten Server gefunden.",
                no_available: "Keine zusätzlichen Server verfügbar.",
                add_permission: "Erlaubnis zum Hinzufügen ✓",
                no_authorization: "⚠️ Keine Berechtigung",
                add_misuki: "➕ Misuki hinzufügen",
                cannot_add: "⚠️ Kann nicht hinzugefügt werden",
                leave_review: "⭐ Bewertung schreiben"
            },

            footer: {
                copyright:
                    "© 2026 Misuki. Alle Rechte vorbehalten."
            },

            common: {
                product: "Produkt",
                advertise_intro: "Bewirb deinen Discord-Server in der Misuki-Community. Wähle die Dauer und erstelle deine Werbung.",
                documentation_intro: "Erfahre, wie du Misuki auf deinem Discord-Server konfigurierst und nutzt.",
                logged_in_as: "Angemeldet als",
                authorized_servers: "🔐 Autorisierte Server",
                available_servers: "➕ Verfügbare Server",
                manage: "⚙️ Verwalten",
                write_review: "✍️ Bewertung schreiben",
                rating: "Bewertung",
                review: "Rezension",
                review_placeholder: "Teile uns deine Meinung über Misuki mit ...",
                advertisement_title: "Werbetitel",
                description: "Beschreibung",
                image_url: "Bild-URL",
                destination_url: "Ziel-URL",
                advertisement_duration: "Werbedauer",
                server_name_placeholder: "Name deines Servers",
                description_placeholder: "Erzähle anderen, was deinen Server besonders macht ...",
                home_title: "Discord-Bot",
                community: "Community",
                advertise: "Werben",
                meet: "Lerne kennen:",
                hero_description: "Ein leistungsstarker Discord-Bot, der deinen Server einfacher, sicherer und angenehmer macht.",
                open_dashboard: "🚀 Dashboard öffnen",
                why_misuki: "Warum Misuki?",
                security: "Sicherheit",
                security_description: "Schütze deinen Discord-Server mit zuverlässigen Moderations- und Verwaltungstools.",
                performance: "Leistung",
                performance_description: "Schnelle und reaktionsfähige Befehle für einen reibungslosen Serverbetrieb.",
                management: "Verwaltung",
                management_description: "Verwalte deine Misuki-Konfiguration direkt über das Dashboard.",
                service_overview: "Serviceübersicht",
                statistics_preparing: "Statistiken werden vorbereitet.",
                get_help: "Hilfe mit Misuki erhalten",
                discord_support: "💬 Discord-Support",
                join_discord: "Discord beitreten",
                support_description: "Tritt dem Misuki-Discord-Server bei, um Hilfe zu erhalten, Probleme zu melden und mit der Community zu sprechen.",
                documentation: "📚 Dokumentation",
                view_documentation: "Dokumentation anzeigen",
                advertisement: "Werbung",
                what_users_say: "⭐ Was Benutzer sagen",
                report_problem: "🐛 Problem melden",
                documentation_help: "Prüfe die Dokumentation für Informationen zur Konfiguration und Nutzung von Misuki.",
                report_problem_text: "Hast du einen Fehler gefunden oder funktioniert etwas nicht korrekt? Kontaktiere das Misuki-Supportteam über Discord."
            },

            /* =====================================================
               STATISTIKEN
               ===================================================== */

            statistics: {
                hero_description: "Übersicht über den Miskui-Dienst und seine aktuellen Statistiken.",
                service_description: "Allgemeine Statistiken über den Miskui-Dienst.",
                servers: "Server",
                users: "Benutzer",
                channels: "Kanäle",
                commands_available: "Verfügbare Befehle",
                tickets_created: "Erstellte Tickets",
                verifications: "Verifizierungen",
                system_status: "Systemstatus",
                system_description: "Aktueller Status des Miskui-Dienstes.",
                discord_bot: "Discord-Bot",
                website: "Website",
                database: "Datenbank",
                api: "API",
                operational: "Betriebsbereit",
                unavailable: "Nicht verfügbar",
                online: "Online",
                offline: "Offline",
                error: "Fehler",
                bot_latency: "Bot-Latenz",
                uptime: "Betriebszeit",
                version: "Version",
                milliseconds: "ms",
                administrator_statistics: "🔐 Administratorstatistiken",
                admin_description: "Detaillierte Informationen sind nur für Miskui-Administratoren verfügbar.",
                admin: "ADMIN",
                members: "Mitglieder",
                no_server_information: "Keine Serverinformationen verfügbar.",
                no_user_information: "Keine Benutzerinformationen verfügbar.",
                activity: "Aktivität",
                commands: "Befehle",
                tickets: "Tickets",
                moderation_actions: "Moderationsaktionen",
                announcements: "Ankündigungen",
                privacy: "Datenschutz",
                privacy_description: "Öffentliche Statistiken werden in aggregierter Form angezeigt. Spezifische Server- und Benutzerinformationen sind auf autorisierte Miskui-Administratoren beschränkt."
            },

            cookies: {
                consent: "Cookie-Einwilligung",
                title: "🍪 Wir verwenden Cookies",
                description:
                    "Misuki verwendet Cookies, um Ihre Erfahrung zu verbessern und die Website ordnungsgemäß funktionsfähig zu halten.",
                accept: "Alle akzeptieren",
                essential: "Nur notwendige",
                deny: "Ablehnen",
                terms: "Bedingungen",
                privacy: "Datenschutz",
                policy: "Cookie-Richtlinie"
            }
        },


        es: {
            language: {
                select: "Seleccionar idioma",
                en: "Inglés",
                pt: "Portugués",
                de: "Alemán",
                es: "Español",
                fr: "Francés"
            },

            menu: {
                title: "Menú",
                navigation: "Navegación",
                resources: "Recursos",
                legal: "Legal",
                account: "Cuenta"
            },

            nav: {
                home: "Inicio",
                dashboard: "Panel",
                reviews: "Reseñas",
                statistics: "Estadísticas",
                documentation: "Documentación",
                support: "Soporte",
                advertisement: "Publicidad",
                advertisement_admin: "Administración de Publicidad",
                terms: "Términos",
                privacy: "Privacidad",
                data: "Datos",
                cookies: "Cookies",
                logout: "Cerrar sesión",
                login: "Iniciar sesión con Discord"
            },

            menu_controls: {
                open: "Abrir menú",
                close: "Cerrar menú"
            },

            reviews: {
                intro: "Reseñas de miembros de las comunidades de Misuki.",
                title: "Reseñas de la comunidad",
                no_reviews: "Todavía no hay reseñas.",
                write_review: "Escribir una reseña",
                rating: "Valoración",
                review: "Reseña",
                submit: "Enviar reseña",
                need_license: "Necesitas una licencia activa de Misuki para escribir una reseña.",
                login_required: "Inicia sesión con Discord y ten una licencia activa de Misuki para escribir una reseña.",
                section_title: "💬 Reseñas de la comunidad"
            },

            license: {
                title: "Licencia",
                back_to_dashboard: "Volver al panel",
                status: "Estado",
                active: "Activa",
                expired: "Caducada",
                revoked: "Revocada",
                key: "Clave de licencia",
                expires: "Caduca",
                never: "Nunca",
                missing: "Este servidor no tiene una licencia de Misuki."
            },

            dashboard: {
                license: "Licencia",
                no_authorized: "🔒 No se encontraron servidores autorizados.",
                no_available: "No hay servidores adicionales disponibles.",
                add_permission: "Permiso para añadir ✓",
                no_authorization: "⚠️ Sin autorización",
                add_misuki: "➕ Añadir Misuki",
                cannot_add: "⚠️ No se puede añadir",
                leave_review: "⭐ Escribir una reseña"
            },

            footer: {
                copyright:
                    "© 2026 Misuki. Todos los derechos reservados."
            },

            common: {
                product: "Producto",
                advertise_intro: "Promociona tu servidor de Discord en la comunidad de Misuki. Elige la duración y crea tu anuncio.",
                documentation_intro: "Aprende a configurar y usar Misuki en tu servidor de Discord.",
                logged_in_as: "Has iniciado sesión como",
                authorized_servers: "🔐 Servidores autorizados",
                available_servers: "➕ Servidores disponibles",
                manage: "⚙️ Gestionar",
                write_review: "✍️ Escribir una reseña",
                rating: "Valoración",
                review: "Reseña",
                review_placeholder: "Cuéntanos qué opinas de Misuki...",
                advertisement_title: "Título del anuncio",
                description: "Descripción",
                image_url: "URL de imagen",
                destination_url: "URL de destino",
                advertisement_duration: "Duración del anuncio",
                server_name_placeholder: "Nombre de tu servidor",
                description_placeholder: "Cuéntale a la gente qué hace especial a tu servidor...",
                home_title: "Bot de Discord",
                community: "Comunidad",
                advertise: "Publicidad",
                meet: "Conoce",
                hero_description: "Un potente bot de Discord diseñado para hacer tu servidor más fácil de gestionar, seguro y agradable.",
                open_dashboard: "🚀 Abrir panel",
                why_misuki: "¿Por qué Misuki?",
                security: "Seguridad",
                security_description: "Mantén tu servidor de Discord protegido con herramientas fiables de moderación y gestión.",
                performance: "Rendimiento",
                performance_description: "Comandos rápidos y receptivos diseñados para funcionar sin problemas en tu servidor.",
                management: "Gestión",
                management_description: "Gestiona la configuración de Misuki directamente desde el panel.",
                service_overview: "Resumen del servicio",
                statistics_preparing: "Las estadísticas se están preparando.",
                get_help: "Obtén ayuda con Misuki",
                discord_support: "💬 Soporte de Discord",
                join_discord: "Unirse a Discord",
                support_description: "Únete al servidor de Discord de Misuki para obtener ayuda, informar de problemas y hablar con la comunidad.",
                documentation: "📚 Documentación",
                view_documentation: "Ver documentación",
                advertisement: "Publicidad",
                what_users_say: "⭐ Lo que dicen los usuarios",
                report_problem: "🐛 Informar de un problema",
                documentation_help: "Consulta la documentación para obtener información sobre cómo configurar y utilizar Misuki.",
                report_problem_text: "¿Has encontrado un error o algo no funciona correctamente? Contacta con el equipo de soporte de Misuki a través de Discord."
            },

            /* =====================================================
               ESTADÍSTICAS
               ===================================================== */

            statistics: {
                hero_description: "Descripción general del servicio Miskui y sus estadísticas actuales.",
                service_description: "Estadísticas generales sobre el servicio Miskui.",
                servers: "Servidores",
                users: "Usuarios",
                channels: "Canales",
                commands_available: "Comandos disponibles",
                tickets_created: "Tickets creados",
                verifications: "Verificaciones",
                system_status: "Estado del sistema",
                system_description: "Estado actual del servicio Miskui.",
                discord_bot: "Bot de Discord",
                website: "Sitio web",
                database: "Base de datos",
                api: "API",
                operational: "Operativa",
                unavailable: "No disponible",
                online: "En línea",
                offline: "Fuera de línea",
                error: "Error",
                bot_latency: "Latencia del bot",
                uptime: "Tiempo de actividad",
                version: "Versión",
                milliseconds: "ms",
                administrator_statistics: "🔐 Estadísticas del administrador",
                admin_description: "La información detallada solo está disponible para los administradores de Miskui.",
                admin: "ADMIN",
                members: "Miembros",
                no_server_information: "No hay información de servidores disponible.",
                no_user_information: "No hay información de usuarios disponible.",
                activity: "Actividad",
                commands: "Comandos",
                tickets: "Tickets",
                moderation_actions: "Acciones de moderación",
                announcements: "Anuncios",
                privacy: "Privacidad",
                privacy_description: "Las estadísticas públicas se presentan de forma agregada. La información específica de servidores y usuarios está restringida a los administradores autorizados de Miskui."
            },

            cookies: {
                consent: "Consentimiento de cookies",
                title: "🍪 Utilizamos cookies",
                description:
                    "Misuki utiliza cookies para mejorar su experiencia y mantener el sitio web funcionando correctamente.",
                accept: "Aceptar todos",
                essential: "Solo esenciales",
                deny: "Rechazar",
                terms: "Términos",
                privacy: "Privacidad",
                policy: "Política de Cookies"
            }
        },


        fr: {
            language: {
                select: "Sélectionner la langue",
                en: "Anglais",
                pt: "Portugais",
                de: "Allemand",
                es: "Espagnol",
                fr: "Français"
            },

            menu: {
                title: "Menu",
                navigation: "Navigation",
                resources: "Ressources",
                legal: "Mentions légales",
                account: "Compte"
            },

            nav: {
                home: "Accueil",
                dashboard: "Tableau de bord",
                reviews: "Avis",
                statistics: "Statistiques",
                documentation: "Documentation",
                support: "Support",
                advertisement: "Publicité",
                advertisement_admin: "Administration de la publicité",
                terms: "Conditions",
                privacy: "Confidentialité",
                data: "Données",
                cookies: "Cookies",
                logout: "Se déconnecter",
                login: "Se connecter avec Discord"
            },

            menu_controls: {
                open: "Ouvrir le menu",
                close: "Fermer le menu"
            },

            reviews: {
                intro: "Avis des membres des communautés Misuki.",
                title: "Avis de la communauté",
                no_reviews: "Aucun avis pour le moment.",
                write_review: "Écrire un avis",
                rating: "Note",
                review: "Avis",
                submit: "Envoyer l'avis",
                need_license: "Vous devez avoir une licence Misuki active pour écrire un avis.",
                login_required: "Connectez-vous avec Discord et disposez d'une licence Misuki active pour écrire un avis.",
                section_title: "💬 Avis de la communauté"
            },

            license: {
                title: "Licence",
                back_to_dashboard: "Retour au tableau de bord",
                status: "Statut",
                active: "Active",
                expired: "Expirée",
                revoked: "Révoquée",
                key: "Clé de licence",
                expires: "Expire",
                never: "Jamais",
                missing: "Ce serveur n'a pas de licence Misuki."
            },

            dashboard: {
                license: "Licence",
                no_authorized: "🔒 Aucun serveur autorisé trouvé.",
                no_available: "Aucun serveur supplémentaire disponible.",
                add_permission: "Permission d'ajout ✓",
                no_authorization: "⚠️ Aucune autorisation",
                add_misuki: "➕ Ajouter Misuki",
                cannot_add: "⚠️ Impossible à ajouter",
                leave_review: "⭐ Écrire un avis"
            },

            footer: {
                copyright:
                    "© 2026 Misuki. Tous droits réservés."
            },

            common: {
                product: "Produit",
                advertise_intro: "Promouvez votre serveur Discord auprès de la communauté Misuki. Choisissez la durée et créez votre publicité.",
                documentation_intro: "Apprenez à configurer et utiliser Misuki sur votre serveur Discord.",
                logged_in_as: "Connecté en tant que",
                authorized_servers: "🔐 Serveurs autorisés",
                available_servers: "➕ Serveurs disponibles",
                manage: "⚙️ Gérer",
                write_review: "✍️ Écrire un avis",
                rating: "Note",
                review: "Avis",
                review_placeholder: "Dites-nous ce que vous pensez de Misuki...",
                advertisement_title: "Titre de la publicité",
                description: "Description",
                image_url: "URL de l'image",
                destination_url: "URL de destination",
                advertisement_duration: "Durée de la publicité",
                server_name_placeholder: "Nom de votre serveur",
                description_placeholder: "Dites ce qui rend votre serveur spécial...",
                home_title: "Bot Discord",
                community: "Communauté",
                advertise: "Publicité",
                meet: "Découvrez",
                hero_description: "Un puissant bot Discord conçu pour rendre votre serveur plus facile à gérer, plus sûr et plus agréable.",
                open_dashboard: "🚀 Ouvrir le tableau de bord",
                why_misuki: "Pourquoi Misuki ?",
                security: "Sécurité",
                security_description: "Protégez votre serveur Discord avec des outils fiables de modération et de gestion.",
                performance: "Performance",
                performance_description: "Des commandes rapides et réactives conçues pour fonctionner parfaitement sur votre serveur.",
                management: "Gestion",
                management_description: "Gérez la configuration de Misuki directement depuis le tableau de bord.",
                service_overview: "Vue d'ensemble du service",
                statistics_preparing: "Les statistiques sont en préparation.",
                get_help: "Obtenir de l'aide avec Misuki",
                discord_support: "💬 Support Discord",
                join_discord: "Rejoindre Discord",
                support_description: "Rejoignez le serveur Discord de Misuki pour obtenir de l'aide, signaler des problèmes et échanger avec la communauté.",
                documentation: "📚 Documentation",
                view_documentation: "Voir la documentation",
                advertisement: "Publicité",
                what_users_say: "⭐ Ce qu'en disent les utilisateurs",
                report_problem: "🐛 Signaler un problème",
                documentation_help: "Consultez la documentation pour savoir comment configurer et utiliser Misuki.",
                report_problem_text: "Vous avez trouvé un bug ou quelque chose ne fonctionne pas correctement ? Contactez l'équipe support de Misuki via Discord."
            },

            /* =====================================================
               STATISTIQUES
               ===================================================== */

            statistics: {
                hero_description: "Vue d’ensemble du service Miskui et de ses statistiques actuelles.",
                service_description: "Statistiques générales du service Miskui.",
                servers: "Serveurs",
                users: "Utilisateurs",
                channels: "Salons",
                commands_available: "Commandes disponibles",
                tickets_created: "Tickets créés",
                verifications: "Vérifications",
                system_status: "État du système",
                system_description: "État actuel du service Miskui.",
                discord_bot: "Bot Discord",
                website: "Site web",
                database: "Base de données",
                api: "API",
                operational: "Opérationnelle",
                unavailable: "Indisponible",
                online: "En ligne",
                offline: "Hors ligne",
                error: "Erreur",
                bot_latency: "Latence du bot",
                uptime: "Temps de fonctionnement",
                version: "Version",
                milliseconds: "ms",
                administrator_statistics: "🔐 Statistiques administrateur",
                admin_description: "Les informations détaillées sont disponibles uniquement pour les administrateurs de Miskui.",
                admin: "ADMIN",
                members: "Membres",
                no_server_information: "Aucune information sur les serveurs n’est disponible.",
                no_user_information: "Aucune information sur les utilisateurs n’est disponible.",
                activity: "Activité",
                commands: "Commandes",
                tickets: "Tickets",
                moderation_actions: "Actions de modération",
                announcements: "Annonces",
                privacy: "Confidentialité",
                privacy_description: "Les statistiques publiques sont présentées sous forme agrégée. Les informations spécifiques aux serveurs et aux utilisateurs sont réservées aux administrateurs Miskui autorisés."
            },

            cookies: {
                consent: "Consentement aux cookies",
                title: "🍪 Nous utilisons des cookies",
                description:
                    "Misuki utilise des cookies pour améliorer votre expérience et assurer le bon fonctionnement du site.",
                accept: "Tout accepter",
                essential: "Essentiels uniquement",
                deny: "Refuser",
                terms: "Conditions",
                privacy: "Confidentialité",
                policy: "Politique relative aux cookies"
            }
        }
    };


    /* =========================================================
       GET TRANSLATION
       ========================================================= */

    function getTranslation(language, key) {

        let value = translations[language];

        if (!value) {
            value = translations[DEFAULT_LANGUAGE];
        }

        for (const part of key.split(".")) {

            if (
                value === null ||
                value === undefined ||
                typeof value !== "object" ||
                !(part in value)
            ) {
                if (language !== DEFAULT_LANGUAGE) {
                    return getTranslation(DEFAULT_LANGUAGE, key);
                }

                return null;
            }

            value = value[part];
        }

        return typeof value === "string"
            ? value
            : null;
    }


    /* =========================================================
       LANGUAGE STORAGE
       ========================================================= */

    function getSavedLanguage() {

        try {

            const saved =
                localStorage.getItem(STORAGE_KEY);

            if (
                SUPPORTED_LANGUAGES.includes(saved)
            ) {
                return saved;
            }

        } catch (error) {

            console.warn(
                "Misuki: could not read saved language.",
                error
            );
        }

        return DEFAULT_LANGUAGE;
    }


    function saveLanguage(language) {

        try {

            localStorage.setItem(
                STORAGE_KEY,
                language
            );

        } catch (error) {

            console.warn(
                "Misuki: could not save language.",
                error
            );
        }
    }


    /* =========================================================
       ELEMENTS
       ========================================================= */

    function getLanguageElements() {

        return {
            selector:
                document.getElementById("languageSelector"),

            button:
                document.getElementById("languageButton"),

            dropdown:
                document.getElementById("languageDropdown")
        };
    }


    /* =========================================================
       UPDATE LANGUAGE BUTTON
       ========================================================= */

    function updateLanguageButton(language) {

        const {
            button
        } = getLanguageElements();

        if (!button) {
            return;
        }

        const info =
            LANGUAGE_INFO[language] ||
            LANGUAGE_INFO[DEFAULT_LANGUAGE];


        const flag =
            button.querySelector(".language-flag");

        if (flag) {
            flag.textContent = info.flag;
        }


        const short =
            button.querySelector(".language-short");

        if (short) {
            short.textContent = info.short;
        }


        const translatedLabel =
            getTranslation(
                language,
                "language.select"
            );


        button.setAttribute(
            "aria-label",
            translatedLabel || "Select language"
        );
    }


    /* =========================================================
       UPDATE ACTIVE LANGUAGE
       ========================================================= */

    function updateActiveLanguage(language) {

        const options =
            document.querySelectorAll(
                "#languageDropdown [data-lang]"
            );

        options.forEach(function (option) {

            const active =
                option.getAttribute("data-lang") ===
                language;

            option.classList.toggle(
                "active",
                active
            );

            option.setAttribute(
                "aria-selected",
                active ? "true" : "false"
            );
        });
    }


    /* =========================================================
       TRANSLATE ATTRIBUTES
       ========================================================= */

    function translateAttributes(language) {

        document
            .querySelectorAll("[data-i18n-attr]")
            .forEach(function (element) {

                const definitions =
                    element.getAttribute(
                        "data-i18n-attr"
                    );

                if (!definitions) {
                    return;
                }

                definitions
                    .split(";")
                    .forEach(function (definition) {

                        const separator =
                            definition.indexOf(":");

                        if (separator === -1) {
                            return;
                        }

                        const attribute =
                            definition
                                .slice(0, separator)
                                .trim();

                        const key =
                            definition
                                .slice(separator + 1)
                                .trim();

                        const translated =
                            getTranslation(
                                language,
                                key
                            );

                        if (translated !== null) {

                            element.setAttribute(
                                attribute,
                                translated
                            );
                        }
                    });
            });
    }


    function translateDocumentTitle(language) {

        const titleKeys = {
            "/": "common.home_title",
            "/dashboard": "nav.dashboard",
            "/reviews": "nav.reviews",
            "/statistics": "nav.statistics",
            "/documentation": "nav.documentation",
            "/support": "nav.support",
            "/advertise": "nav.advertisement",
            "/terms": "nav.terms",
            "/privacy": "nav.privacy",
            "/data": "nav.data",
            "/cookies": "nav.cookies"
        };

        const key = titleKeys[window.location.pathname];
        const translated = key ? getTranslation(language, key) : null;

        if (translated !== null) {
            document.title = translated + " — Misuki";
        }
    }


    /* =========================================================
       TRANSLATE PAGE
       ========================================================= */

    function translatePage(language) {

        if (
            !SUPPORTED_LANGUAGES.includes(language)
        ) {
            language = DEFAULT_LANGUAGE;
        }


        document
            .querySelectorAll("[data-i18n]")
            .forEach(function (element) {

                const key =
                    element.getAttribute(
                        "data-i18n"
                    );

                if (!key) {
                    return;
                }

                const translated =
                    getTranslation(
                        language,
                        key
                    );

                if (translated !== null) {

                    element.textContent =
                        translated;
                }
            });


        translateAttributes(language);

        translateDocumentTitle(language);


        document.documentElement.lang =
            language;


        updateLanguageButton(language);
        updateActiveLanguage(language);
        saveLanguage(language);


        window.dispatchEvent(
            new CustomEvent(
                "misukiLanguageChanged",
                {
                    detail: {
                        language: language
                    }
                }
            )
        );
    }


    /* =========================================================
       CLOSE DROPDOWN
       ========================================================= */

    function closeLanguageDropdown() {

        const {
            selector,
            button,
            dropdown
        } = getLanguageElements();

        if (!selector || !button || !dropdown) {
            return;
        }

        selector.classList.remove(
            "open",
            "active"
        );

        dropdown.classList.remove("show");

        dropdown.style.display = "none";

        dropdown.setAttribute(
            "aria-hidden",
            "true"
        );

        button.setAttribute(
            "aria-expanded",
            "false"
        );
    }


    /* =========================================================
       OPEN DROPDOWN
       ========================================================= */

    function openLanguageDropdown() {

        const {
            selector,
            button,
            dropdown
        } = getLanguageElements();

        if (!selector || !button || !dropdown) {
            console.warn(
                "Misuki: language selector elements missing."
            );
            return;
        }


        const menu =
            document.getElementById("menu");


        if (
            document.body.classList.contains("menu-open") ||
            (
                menu &&
                (
                    menu.classList.contains("open") ||
                    menu.classList.contains("active")
                )
            )
        ) {
            return;
        }


        selector.classList.add("open");
        dropdown.classList.add("show");

        dropdown.style.display = "flex";

        dropdown.setAttribute(
            "aria-hidden",
            "false"
        );

        button.setAttribute(
            "aria-expanded",
            "true"
        );
    }


    /* =========================================================
       TOGGLE DROPDOWN
       ========================================================= */

    function toggleLanguageDropdown() {

        const {
            selector
        } = getLanguageElements();

        if (!selector) {
            return;
        }

        if (
            selector.classList.contains("open") ||
            selector.classList.contains("active")
        ) {

            closeLanguageDropdown();

        } else {

            openLanguageDropdown();
        }
    }


    /* =========================================================
       LANGUAGE BUTTON
       ========================================================= */

    function setupLanguageButton() {

        const {
            button
        } = getLanguageElements();

        if (!button) {
            return;
        }


        button.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                toggleLanguageDropdown();

            }
        );
    }


    /* =========================================================
       LANGUAGE OPTIONS
       ========================================================= */

    function setupLanguageOptions() {

        const options =
            document.querySelectorAll(
                "#languageDropdown [data-lang]"
            );


        options.forEach(function (option) {

            option.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();
                    event.stopPropagation();


                    const language =
                        option.getAttribute(
                            "data-lang"
                        );


                    if (
                        !SUPPORTED_LANGUAGES.includes(
                            language
                        )
                    ) {
                        return;
                    }


                    translatePage(language);

                    closeLanguageDropdown();

                }
            );

        });
    }


    /* =========================================================
       CLICK OUTSIDE
       ========================================================= */

    function setupOutsideClick() {

        document.addEventListener(
            "click",
            function (event) {

                const {
                    selector
                } = getLanguageElements();

                if (!selector) {
                    return;
                }


                if (
                    !selector.contains(
                        event.target
                    )
                ) {

                    closeLanguageDropdown();
                }

            }
        );
    }


    /* =========================================================
       KEYBOARD
       ========================================================= */

    function setupKeyboard() {

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                ) {

                    closeLanguageDropdown();
                }

            }
        );
    }


    /* =========================================================
       MENU INTEGRATION
       ========================================================= */

    function setupMenuIntegration() {

        const hamburger =
            document.getElementById("hamburger");


        if (hamburger) {

            hamburger.addEventListener(
                "click",
                function () {

                    closeLanguageDropdown();

                }
            );
        }


        const menu =
            document.getElementById("menu");


        if (!menu) {
            return;
        }


        const observer =
            new MutationObserver(
                function () {

                    if (
                        menu.classList.contains("open") ||
                        menu.classList.contains("active") ||
                        document.body.classList.contains("menu-open")
                    ) {

                        closeLanguageDropdown();
                    }

                }
            );


        observer.observe(
            menu,
            {
                attributes: true,
                attributeFilter: ["class"]
            }
        );


        const bodyObserver =
            new MutationObserver(
                function () {

                    if (
                        document.body.classList.contains(
                            "menu-open"
                        )
                    ) {

                        closeLanguageDropdown();
                    }

                }
            );


        bodyObserver.observe(
            document.body,
            {
                attributes: true,
                attributeFilter: ["class"]
            }
        );
    }


    /* =========================================================
       INITIALIZATION
       ========================================================= */

    function initialize() {

        const {
            selector,
            button,
            dropdown
        } = getLanguageElements();

        translatePage(
            getSavedLanguage()
        );


        if (!selector || !button || !dropdown) {
            console.warn(
                "⚠️ Misuki language selector elements not found; page translation was applied."
            );
            return;
        }


        closeLanguageDropdown();


        setupLanguageButton();
        setupLanguageOptions();
        setupOutsideClick();
        setupKeyboard();
        setupMenuIntegration();


        console.log(
            "✅ Misuki translation system initialized."
        );
    }


    /* =========================================================
       PUBLIC API
       ========================================================= */

    window.MisukiTranslation = {

        setLanguage: function (language) {

            if (
                !SUPPORTED_LANGUAGES.includes(
                    language
                )
            ) {
                return;
            }

            translatePage(language);
        },

        getLanguage: function () {
            return getSavedLanguage();
        },

        getTranslation: function (language, key) {
            return getTranslation(language, key);
        },

        getTranslations: function () {
            return translations;
        },

        getSupportedLanguages: function () {
            return [...SUPPORTED_LANGUAGES];
        },

        openLanguageSelector: function () {
            openLanguageDropdown();
        },

        closeLanguageSelector: function () {
            closeLanguageDropdown();
        },

        toggleLanguageSelector: function () {
            toggleLanguageDropdown();
        }
    };


    /* =========================================================
       START
       ========================================================= */

    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initialize,
            {
                once: true
            }
        );

    } else {

        initialize();
    }

})();