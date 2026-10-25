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

        /* =====================================================
           ENGLISH
           ===================================================== */

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
                license_management: "License Management",
                my_advertisements: "My Advertisements",
                terms: "Terms",
                privacy: "Privacy",
                data: "Data",
                cookies: "Cookies",
                logout: "Logout",
                login: "Login with Discord"
            },

            licenses: {
                admin_eyebrow: "ADMINISTRATION",
                title: "License management",
                description: "Create, extend and revoke server licenses directly from the Misuki website.",
                back_statistics: "Back to statistics",
                create_title: "Create a license",
                create_description: "A new license becomes active immediately after creation.",
                server_id: "Server ID",
                days: "Duration (days)",
                create: "Create license",
                existing: "Existing licenses",
                created: "Created",
                expires: "Expires",
                extend: "Extend",
                revoke: "Revoke",
                status_active: "Active",
                status_expired: "Expired",
                status_revoked: "Revoked",
                status_none: "Unknown",
                none: "There are no license records."
            },

            advertisements: {
                status_page_title: "My Advertisements",
                status_id: "ID:",
                duration_days: "days",
                payment_completed: "Payment completed",
                status_unknown: "Status unavailable",
                advertisement_id: "ID :",
                      "section_kicker": "Advertisement",
                      "featured_servers": "Featured servers",
                      "subtitle": "Discover community servers on Misuki.",
                      "advertise_server": "Advertise your server",
                      "space_available": "Advertising space available",
                      "space_description": "Your server can appear here. Be one of the first to advertise on Misuki.",
                      "pending_review": "Pending review",
                      "approved_payment_pending": "Approved — payment pending",
                      "active": "Active",
                      "rejected": "Rejected",
                      "expired": "Expired",
                      "disabled": "Disabled",
                      "paid": "Paid",
                      "payment_pending": "Payment pending",
                      "payment_failed": "Payment not completed",
                      "reason": "Reason:",
                      "pay_paypal": "Pay with PayPal",
                      "open": "Open",
                      "no_advertisements": "You have no advertisements yet.",
                      "proposal_submitted": "Advertisement submitted",
                      "proposal_pending_review": "Your proposal is now pending review by the Misuki team. We will review it before any payment is requested.",
                      "proposal_review_before_payment": "Payment will only become available after the proposal has been approved.",
                      "back_to_dashboard": "Back to Dashboard",
                "status_intro": "Track each proposal, check whether it was approved, review the payment and confirm when the advertisement is active.",
                "approved_proposal": "Proposal approved",
                "rejection_reason": "Rejection reason",
                "period": "Period:",
                "pay_ad": "Make PayPal payment",
                "open_ad": "Open advertisement",
                "no_proposals": "You do not have any advertisement proposals yet.",
                "proposal_sent": "Proposal submitted",
                "send_another": "Submit another proposal",
                "panel": "Dashboard",
                "payment_completed": "Payment completed",
                "payment_status": "Advertisement status",
                "payment_status_desc": "You can check at any time whether the advertisement is active, the contracted period and the payment status in My Advertisements.",
                "payment_success_description": "Your advertisement payment was confirmed successfully. The approved proposal is now ready for the contracted period.",
                "return_dashboard": "Return to Dashboard",
                "payment_cancelled": "Payment cancelled",
                "payment_not_completed": "The payment was not completed.",
                "return": "Return",
                "advertisement_management": "Advertisement Management",
                "user_id": "User ID:",
                "duration": "Duration:",
                "start": "Start:",
                "end": "End:",
                "approve": "Approve",
                "reject": "Reject",
                "disable": "Disable",
                "approval_reason_placeholder": "Approval justification",
                "rejection_reason_placeholder": "Rejection justification",
                "no_ads_admin": "There are no advertisements yet."
            },

            menu_controls: {
                open: "Open menu",
                close: "Close menu"
            },

            notifications: {
                title: "Notifications",
                enable: "Enable notifications",
                enabled: "Notifications enabled",
                denied: "Notifications are blocked in your browser settings.",
                unsupported: "Notifications are not supported by this browser.",
                login_required: "Sign in with Discord to enable notifications.",
                error: "Could not enable notifications.",
                empty: "No notifications yet.",
                advertisement_approved_title: "Advertisement approved",
                advertisement_approved_body: "Your advertisement {advertisement} was approved. You can now complete the payment.",
                advertisement_rejected_title: "Advertisement rejected",
                advertisement_rejected_body: "Your advertisement {advertisement} was rejected. Reason: {reason}"
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
                information: "License information",
                description: "View the status and details of this server's license here.",
                inactive: "Inactive",
                created: "Created",
                no_license_title: "No license",
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
                license_active: "🟢 License Active",
                license_expired: "🔴 License Expired",
                license_revoked: "⛔ License Revoked",
                no_license: "🔒 No License",
                no_authorized: "🔒 No authorized servers found.",
                no_available: "No additional servers available.",
                add_permission: "Add permission ✓",
                no_authorization: "⚠️ No authorization",
                add_misuki: "➕ Add Misuki",
                cannot_add: "⚠️ Cannot Add",
                leave_review: "⭐ Leave a Review",
                license: "License"
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
                report_problem_text: "Found a bug or something that isn't working correctly? Contact the Misuki support team through Discord.",
                need_help: "Need help? Choose the option above that best matches what you need.",
                return_home: "← Return Home",
                try_login_again: "Try Login Again",
                continue_later: "If the problem continues, please try again later.",
                view_my_advertisements: "View My Advertisements",
                search_users: "Search name, @username or ID",
                added_misuki_server: "Added Misuki to a server",
                no_users_match: "No users match your search.",
                id_label: "ID:",
                account: "Account",
                servers: "Servers",
                return: "Return"
            ,

                advertisement_title: "Advertisement title",
                description: "Description",
                image_url: "Image URL",
                destination_url: "Destination URL",
                advertisement_duration: "Advertisement duration",
                server_name_placeholder: "Your server name",
                description_placeholder: "Tell people what makes your server special...",
                special_offer: "SPECIAL OFFER",
                promotional_prices: "Promotional prices",
                save_more: "SAVE MORE",
                popular: "POPULAR",
                save: "Save",
                secure_payment: "Payment after approval",
                payment_secure: "No payment is requested when you submit the proposal. If approved, you will receive access to PayPal payment.",
                continue_paypal: "Continue to PayPal",
                advertisement_note: "Your advertisement will be reviewed before any payment is requested. You can only pay after the Misuki team approves the proposal.",
                days: "days",
                option_7: "7 days — €0.99",
                option_14: "14 days — €1.50",
                option_30: "30 days — €2.50",
                days_7: "7 DAYS",
                days_14: "14 DAYS",
                days_30: "30 DAYS",
                save_001: "Save €0.01",
                save_050: "Save €0.50"
            },

            statistics: {
                overview_kicker: "Overview",
                status_kicker: "Status",
                performance_kicker: "Performance",
                hero_description: "Overview of the Misuki service and its current statistics.",
                service_description: "General statistics about the Misuki service.",
                servers: "Servers",
                users: "Users",
                channels: "Channels",
                commands_available: "Commands available",
                tickets_created: "Tickets created",
                verifications: "Verifications",
                system_status: "System status",
                system_description: "Current status of the Misuki service.",
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
                admin_description: "Detailed information available only to Misuki administrators.",
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
                privacy_description: "Public statistics are presented in an aggregated form. Specific server and user information is restricted to authorized Misuki administrators.",
                account: "Account",
                search_users: "Search name, @username or ID",
                added_misuki: "Added Misuki to a server",
                no_users_match: "No users match your search."
            },

            error: {
                title: "Something went wrong",
                subtitle: "We couldn't complete your request.",
                continue_later: "If the problem continues, please try again later."
            },

            cookies: {
                consent: "Cookie consent",
                title: "🍪 We use cookies",
                description: "Misuki uses cookies to improve your experience and keep the website working correctly.",
                accept: "Accept All",
                essential: "Essential Only",
                deny: "Deny",
                terms: "Terms",
                privacy: "Privacy",
                policy: "Cookie Policy"
            },

data: {
                title: "Your Data",
                subtitle: "Manage your Misuki data",
                intro: "Misuki stores certain information required to provide its features. This page explains the types of information that may be associated with your account or Discord server.",
                stored_title: "What Data May Be Stored?",
                stored_1: "Discord user ID",
                stored_2: "Discord server IDs",
                stored_3: "Server configuration",
                stored_4: "Misuki feature settings",
                stored_5: "Information required for licenses and subscriptions",
                stored_6: "Support or review information that you voluntarily provide",
                why_title: "Why Is It Stored?",
                why_text: "This information allows Misuki to provide its functionality, remember server settings, authenticate users and maintain the service.",
                request_title: "Requesting Your Data",
                request_text: "You may contact Misuki support if you would like to request information about the data associated with your account.",
                contact_support: "Contact Support",
                deletion_title: "Requesting Deletion",
                deletion_text: "If you would like your data to be deleted, contact Misuki support and provide enough information for us to identify the relevant account or server.",
                deletion_note: "Some information may need to be retained where required by law or where necessary for security, fraud prevention or legitimate technical purposes.",
                discord_title: "Discord Data",
                discord_text: "Misuki uses Discord authentication where applicable. Misuki does not store your Discord password.",
                discord_policy: "Information received through Discord is handled according to the Misuki Privacy Policy and the permissions requested during authentication.",
                privacy_button: "Read Privacy Policy"
            },

data: {
                title: "Os seus dados",
                subtitle: "Gerir os seus dados do Misuki",
                intro: "O Misuki armazena determinadas informações necessárias para disponibilizar as suas funcionalidades. Esta página explica os tipos de informação que podem estar associados à sua conta ou servidor Discord.",
                stored_title: "Que dados podem ser armazenados?",
                stored_1: "ID de utilizador do Discord",
                stored_2: "IDs dos servidores Discord",
                stored_3: "Configuração do servidor",
                stored_4: "Definições das funcionalidades do Misuki",
                stored_5: "Informações necessárias para licenças e subscrições",
                stored_6: "Informações de suporte ou avaliações que fornecer voluntariamente",
                why_title: "Porque são armazenados?",
                why_text: "Estas informações permitem ao Misuki disponibilizar as suas funcionalidades, guardar definições dos servidores, autenticar utilizadores e manter o serviço.",
                request_title: "Solicitar os seus dados",
                request_text: "Pode contactar o suporte do Misuki se pretender solicitar informações sobre os dados associados à sua conta.",
                contact_support: "Contactar o suporte",
                deletion_title: "Solicitar eliminação",
                deletion_text: "Se pretender que os seus dados sejam eliminados, contacte o suporte do Misuki e forneça informação suficiente para identificarmos a conta ou servidor relevante.",
                deletion_note: "Algumas informações poderão ter de ser conservadas quando exigido por lei ou quando necessário para segurança, prevenção de fraude ou fins técnicos legítimos.",
                discord_title: "Dados do Discord",
                discord_text: "O Misuki utiliza a autenticação do Discord quando aplicável. O Misuki não armazena a sua palavra-passe do Discord.",
                discord_policy: "As informações recebidas através do Discord são tratadas de acordo com a Política de Privacidade do Misuki e com as permissões solicitadas durante a autenticação.",
                privacy_button: "Ler a Política de Privacidade"
            },

data: {
                title: "Ihre Daten",
                subtitle: "Ihre Misuki-Daten verwalten",
                intro: "Misuki speichert bestimmte Informationen, die für die Bereitstellung seiner Funktionen erforderlich sind. Diese Seite erklärt, welche Arten von Informationen mit Ihrem Konto oder Discord-Server verknüpft sein können.",
                stored_title: "Welche Daten können gespeichert werden?",
                stored_1: "Discord-Benutzer-ID",
                stored_2: "Discord-Server-IDs",
                stored_3: "Serverkonfiguration",
                stored_4: "Misuki-Funktionseinstellungen",
                stored_5: "Für Lizenzen und Abonnements erforderliche Informationen",
                stored_6: "Freiwillig bereitgestellte Support- oder Bewertungsinformationen",
                why_title: "Warum werden sie gespeichert?",
                why_text: "Diese Informationen ermöglichen es Misuki, seine Funktionen bereitzustellen, Servereinstellungen zu speichern, Benutzer zu authentifizieren und den Dienst zu betreiben.",
                request_title: "Ihre Daten anfordern",
                request_text: "Sie können den Misuki-Support kontaktieren, wenn Sie Informationen zu den mit Ihrem Konto verbundenen Daten anfordern möchten.",
                contact_support: "Support kontaktieren",
                deletion_title: "Löschung anfordern",
                deletion_text: "Wenn Sie möchten, dass Ihre Daten gelöscht werden, kontaktieren Sie den Misuki-Support und geben Sie genügend Informationen an, damit wir das betreffende Konto oder den Server identifizieren können.",
                deletion_note: "Einige Informationen müssen möglicherweise aufbewahrt werden, wenn dies gesetzlich vorgeschrieben oder für Sicherheit, Betrugsprävention oder legitime technische Zwecke erforderlich ist.",
                discord_title: "Discord-Daten",
                discord_text: "Misuki verwendet gegebenenfalls die Discord-Authentifizierung. Misuki speichert Ihr Discord-Passwort nicht.",
                discord_policy: "Über Discord erhaltene Informationen werden gemäß der Misuki-Datenschutzerklärung und den während der Authentifizierung angeforderten Berechtigungen verarbeitet.",
                privacy_button: "Datenschutzerklärung lesen"
            },

data: {
                title: "Tus datos",
                subtitle: "Gestiona tus datos de Misuki",
                intro: "Misuki almacena cierta información necesaria para proporcionar sus funciones. Esta página explica los tipos de información que pueden estar asociados a tu cuenta o servidor de Discord.",
                stored_title: "¿Qué datos pueden almacenarse?",
                stored_1: "ID de usuario de Discord",
                stored_2: "IDs de servidores de Discord",
                stored_3: "Configuración del servidor",
                stored_4: "Configuración de funciones de Misuki",
                stored_5: "Información necesaria para licencias y suscripciones",
                stored_6: "Información de soporte o reseñas que proporciones voluntariamente",
                why_title: "¿Por qué se almacenan?",
                why_text: "Esta información permite a Misuki proporcionar sus funciones, recordar la configuración de los servidores, autenticar usuarios y mantener el servicio.",
                request_title: "Solicitar tus datos",
                request_text: "Puedes contactar con el soporte de Misuki si quieres solicitar información sobre los datos asociados a tu cuenta.",
                contact_support: "Contactar con soporte",
                deletion_title: "Solicitar eliminación",
                deletion_text: "Si quieres que se eliminen tus datos, contacta con el soporte de Misuki y proporciona información suficiente para identificar la cuenta o el servidor correspondiente.",
                deletion_note: "Es posible que algunos datos deban conservarse cuando lo exija la ley o cuando sea necesario por motivos de seguridad, prevención del fraude o fines técnicos legítimos.",
                discord_title: "Datos de Discord",
                discord_text: "Misuki utiliza la autenticación de Discord cuando corresponde. Misuki no almacena tu contraseña de Discord.",
                discord_policy: "La información recibida a través de Discord se trata de acuerdo con la Política de Privacidad de Misuki y los permisos solicitados durante la autenticación.",
                privacy_button: "Leer la Política de Privacidad"
            },

data: {
                title: "Vos données",
                subtitle: "Gérer vos données Misuki",
                intro: "Misuki stocke certaines informations nécessaires à la fourniture de ses fonctionnalités. Cette page explique les types d’informations pouvant être associés à votre compte ou serveur Discord.",
                stored_title: "Quelles données peuvent être stockées ?",
                stored_1: "Identifiant utilisateur Discord",
                stored_2: "Identifiants des serveurs Discord",
                stored_3: "Configuration du serveur",
                stored_4: "Paramètres des fonctionnalités de Misuki",
                stored_5: "Informations nécessaires aux licences et abonnements",
                stored_6: "Informations de support ou avis que vous fournissez volontairement",
                why_title: "Pourquoi sont-elles stockées ?",
                why_text: "Ces informations permettent à Misuki de fournir ses fonctionnalités, de mémoriser les paramètres des serveurs, d’authentifier les utilisateurs et de maintenir le service.",
                request_title: "Demander vos données",
                request_text: "Vous pouvez contacter le support Misuki si vous souhaitez demander des informations sur les données associées à votre compte.",
                contact_support: "Contacter le support",
                deletion_title: "Demander la suppression",
                deletion_text: "Si vous souhaitez supprimer vos données, contactez le support Misuki et fournissez suffisamment d’informations pour identifier le compte ou serveur concerné.",
                deletion_note: "Certaines informations peuvent devoir être conservées lorsque la loi l’exige ou lorsque cela est nécessaire à des fins de sécurité, de prévention de la fraude ou à des fins techniques légitimes.",
                discord_title: "Données Discord",
                discord_text: "Misuki utilise l’authentification Discord lorsque cela est applicable. Misuki ne stocke pas votre mot de passe Discord.",
                discord_policy: "Les informations reçues via Discord sont traitées conformément à la Politique de confidentialité de Misuki et aux autorisations demandées lors de l’authentification.",
                privacy_button: "Lire la Politique de confidentialité"
            },

            legal: {
          "policy_updated": "Last updated: August 2026",
          "privacy_title": "Privacy Policy",
          "privacy_intro": "This Privacy Policy explains how Misuki collects, uses, stores and protects information when you use our services.",
          "privacy_1_title": "1. Information We Collect",
          "privacy_1_p1": "Depending on the features you use, Misuki may process information provided by Discord or generated through your interaction with the service.",
          "privacy_1_p2": "This may include information such as your Discord user ID, username, server information and configuration data required for Misuki to operate.",
          "privacy_2_title": "2. Discord Authentication",
          "privacy_2_p1": "Misuki may use Discord OAuth2 to authenticate users.",
          "privacy_2_p2": "When you sign in with Discord, Discord may provide information permitted by the OAuth2 scopes requested by Misuki.",
          "privacy_2_p3": "Misuki does not receive or store your Discord password.",
          "privacy_3_title": "3. How We Use Information",
          "privacy_3_intro": "Information may be used to:",
          "privacy_3_li1": "Provide and operate Misuki features.",
          "privacy_3_li2": "Authenticate users.",
          "privacy_3_li3": "Maintain server configurations.",
          "privacy_3_li4": "Improve reliability and security.",
          "privacy_3_li5": "Respond to support requests.",
          "privacy_4_title": "4. Data Storage",
          "privacy_4_p1": "Some information may be stored in databases required for the operation of Misuki.",
          "privacy_4_p2": "We aim to retain only information that is necessary for providing the service.",
          "privacy_5_title": "5. Data Sharing",
          "privacy_5_p1": "Misuki does not sell personal information.",
          "privacy_5_p2": "Information may be processed by infrastructure or service providers when necessary to operate Misuki.",
          "privacy_6_title": "6. Security",
          "privacy_6_p1": "Reasonable technical measures are used to protect stored information against unauthorized access, alteration or disclosure.",
          "privacy_6_p2": "However, no online service can guarantee absolute security.",
          "privacy_7_title": "7. Data Retention",
          "privacy_7_p1": "Information is retained only for as long as reasonably necessary for the purposes described in this policy, unless a longer retention period is required by law.",
          "privacy_8_title": "8. Your Rights",
          "privacy_8_p1": "Depending on applicable law, you may have rights regarding your personal information, including rights to access, correct or request deletion of your data.",
          "privacy_8_p2": "For data-related requests, please contact Misuki support.",
          "privacy_9_title": "9. Children's Privacy",
          "privacy_9_p1": "Misuki is not intended to knowingly collect personal information from children in violation of applicable laws.",
          "privacy_10_title": "10. Third-Party Services",
          "privacy_10_p1": "Misuki may interact with third-party services, including Discord.",
          "privacy_10_p2": "Those services have their own privacy policies and terms that may apply to your use of them.",
          "privacy_11_title": "11. Changes to This Policy",
          "privacy_11_p1": "This Privacy Policy may be updated when necessary. Changes will be reflected on this page.",
          "privacy_12_title": "12. Contact",
          "privacy_12_p1": "If you have questions about this Privacy Policy or your data, please contact Misuki support.",
          "terms_title": "Terms of Service",
          "terms_1_title": "1. Acceptance of Terms",
          "terms_1_p1": "By using Misuki, you agree to comply with these Terms of Service. If you do not agree with these terms, you should not use the service.",
          "terms_2_title": "2. Use of the Service",
          "terms_2_p1": "Misuki provides Discord-related tools and services designed to help users manage and interact with their Discord servers.",
          "terms_2_p2": "You agree to use Misuki responsibly and in accordance with applicable laws and Discord's rules and policies.",
          "terms_3_title": "3. Discord",
          "terms_3_p1": "Misuki is an independent service and is not affiliated with, endorsed by, or sponsored by Discord Inc.",
          "terms_3_p2": "Your use of Discord remains subject to Discord's own Terms of Service and Community Guidelines.",
          "terms_4_title": "4. Accounts and Authentication",
          "terms_4_p1": "Some Misuki features may require authentication through Discord. You are responsible for maintaining the security of your account.",
          "terms_4_p2": "Misuki does not request or store your Discord password.",
          "terms_5_title": "5. Server Permissions",
          "terms_5_p1": "Misuki may require certain permissions in a Discord server to provide its features.",
          "terms_5_p2": "Server owners and administrators are responsible for deciding which permissions are granted to the bot.",
          "terms_6_title": "6. Prohibited Use",
          "terms_6_p1": "You must not use Misuki to abuse, disrupt, exploit, or interfere with Discord, other users, or the service.",
          "terms_6_p2": "You must also not attempt to gain unauthorized access to Misuki systems or data.",
          "terms_7_title": "7. Availability",
          "terms_7_p1": "We aim to keep Misuki available and functional, but we cannot guarantee uninterrupted access to the service.",
          "terms_7_p2": "Features may be changed, suspended, or discontinued when necessary.",
          "terms_8_title": "8. Third-Party Services",
          "terms_8_p1": "Misuki may rely on third-party services, including Discord and other infrastructure providers.",
          "terms_8_p2": "Their own terms and policies may apply when you use those services.",
          "terms_9_title": "9. Termination",
          "terms_9_p1": "Access to Misuki may be restricted or terminated if these Terms of Service are violated or if necessary to protect the service and its users.",
          "terms_10_title": "10. Changes to These Terms",
          "terms_10_p1": "These Terms of Service may be updated from time to time. Continued use of Misuki after changes are published constitutes acceptance of the updated terms.",
          "terms_11_title": "11. Contact",
          "terms_11_p1": "If you have questions regarding these terms, please contact Misuki support.",
          "cookies_title": "Cookie Policy",
          "cookies_intro": "Misuki may use cookies and similar technologies to provide and maintain the website and its features.",
          "cookies_1_title": "1. What Are Cookies?",
          "cookies_1_p1": "Cookies are small pieces of data stored by your browser when you visit a website. They can be used to remember information between requests and maintain sessions.",
          "cookies_2_title": "2. How Misuki Uses Cookies",
          "cookies_2_p1": "Misuki may use cookies for purposes such as keeping sessions active, remembering user preferences, and improving the overall service.",
          "cookies_3_title": "3. Your Choices",
          "cookies_3_p1": "You can choose to accept all cookies, allow only essential cookies, or deny cookies. Your choice is stored in your browser and may be reviewed again when you reload the site.",
          "cookies_4_title": "4. Contact",
          "cookies_4_p1": "If you have questions about this policy, please contact Misuki support."
},

            verification: {
                login_required: "Sign in to continue",
                login_description: "To start verification, you need to sign in with your Discord account.",
                login_note: "After signing in, you will automatically return to this page and can continue the verification.",
                title: "Verification",
                subtitle: "Confirm your Discord account to get access to the server.",
                authenticated_account: "Authenticated account",
                verified_account: "Verification account",
                server: "Server",
                confirm: "Confirm verification",
                confirmed: "Verification confirmed",
                request_sent: "Your verification request was sent successfully.",
                received: "Misuki received your request.",
                processing: "The bot will process your verification and assign the appropriate role on the server.",
                return_discord: "You can return to Discord. If the role takes a few seconds to be assigned, please wait while Misuki processes your request.",
                info: "By continuing, Misuki will confirm your Discord account and send a verification request to the bot to assign your verification role.",
                captcha_placeholder: "Answer",
                footer: "Protected by Misuki"
            }
        },

        /* =====================================================
           PORTUGUÊS
           ===================================================== */

        pt: {

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
                license_management: "Gestão de Licenças",
                my_advertisements: "As minhas publicidades",
                terms: "Termos",
                privacy: "Privacidade",
                data: "Dados",
                cookies: "Cookies",
                logout: "Terminar sessão",
                login: "Entrar com o Discord"
            },

            licenses: {
                admin_eyebrow: "ADMINISTRAÇÃO",
                title: "Gestão de licenças",
                description: "Crie, prolongue e revogue licenças de servidores diretamente no site do Misuki.",
                back_statistics: "Voltar às estatísticas",
                create_title: "Criar uma licença",
                create_description: "Uma nova licença fica ativa imediatamente após a criação.",
                server_id: "ID do servidor",
                days: "Duração (dias)",
                create: "Criar licença",
                existing: "Licenças existentes",
                created: "Criada",
                expires: "Expira",
                extend: "Prolongar",
                revoke: "Revogar",
                status_active: "Ativa",
                status_expired: "Expirada",
                status_revoked: "Revogada",
                status_none: "Desconhecida",
                none: "Não existem registos de licenças."
            },

            advertisements: {
                status_page_title: "As minhas publicidades",
                status_id: "ID:",
                duration_days: "dias",
                payment_completed: "Pagamento concluído",
                status_unknown: "Estado indisponível",
                advertisement_id: "ID:",
                      "section_kicker": "Publicidade",
                      "featured_servers": "Servidores em destaque",
                      "subtitle": "Descubra servidores da comunidade no Misuki.",
                      "advertise_server": "Publicitar o seu servidor",
                      "space_available": "Espaço publicitário disponível",
                      "space_description": "O seu servidor pode aparecer aqui. Seja um dos primeiros a publicitar no Misuki.",
                      "pending_review": "Pendente de análise",
                      "approved_payment_pending": "Aprovada — pagamento pendente",
                      "active": "Ativa",
                      "rejected": "Rejeitada",
                      "expired": "Expirada",
                      "disabled": "Desativada",
                      "paid": "Pago",
                      "payment_pending": "Pagamento pendente",
                      "payment_failed": "Pagamento não concluído",
                      "reason": "Motivo:",
                      "pay_paypal": "Pagar com PayPal",
                      "open": "Abrir",
                      "no_advertisements": "Ainda não existem publicidades.",
                      "proposal_submitted": "Publicidade enviada",
                      "proposal_pending_review": "A sua proposta está agora pendente de análise pela equipa do Misuki. Será analisada antes de qualquer pagamento ser solicitado.",
                      "proposal_review_before_payment": "O pagamento só ficará disponível depois de a proposta ser aprovada.",
                      "back_to_dashboard": "Voltar ao painel",
                "status_intro": "Aqui pode acompanhar cada proposta, verificar se foi aprovada, consultar o pagamento e confirmar quando a publicidade está ativa.",
                "approved_proposal": "Proposta aprovada",
                "rejection_reason": "Motivo da rejeição",
                "period": "Período:",
                "pay_ad": "Efetuar pagamento com PayPal",
                "open_ad": "Abrir publicidade",
                "no_proposals": "Ainda não tem propostas de publicidade.",
                "proposal_sent": "Proposta enviada",
                "send_another": "Enviar outra proposta",
                "panel": "Painel",
                "payment_completed": "Pagamento concluído",
                "payment_status": "Estado da publicidade",
                "payment_status_desc": "Pode consultar a qualquer momento se a publicidade está ativa, o período contratado e o estado do pagamento na área “As minhas publicidades”.",
                "payment_success_description": "O pagamento da sua publicidade foi confirmado com sucesso. A proposta aprovada está agora pronta para o período contratado.",
                "return_dashboard": "Voltar ao painel",
                "payment_cancelled": "Pagamento cancelado",
                "payment_not_completed": "O pagamento não foi concluído.",
                "return": "Voltar",
                "advertisement_management": "Gestão de publicidade",
                "user_id": "ID do utilizador:",
                "duration": "Duração:",
                "start": "Início:",
                "end": "Fim:",
                "approve": "Aprovar",
                "reject": "Rejeitar",
                "disable": "Desativar",
                "approval_reason_placeholder": "Justificação da aprovação",
                "rejection_reason_placeholder": "Justificação da rejeição",
                "no_ads_admin": "Ainda não existem publicidades."
            },

            menu_controls: {
                open: "Abrir menu",
                close: "Fechar menu"
            },

            notifications: {
                title: "Notificações",
                enable: "Ativar notificações",
                enabled: "Notificações ativadas",
                denied: "As notificações estão bloqueadas nas definições do navegador.",
                unsupported: "As notificações não são suportadas por este navegador.",
                login_required: "Entre com o Discord para ativar as notificações.",
                error: "Não foi possível ativar as notificações.",
                empty: "Ainda não existem notificações.",
                advertisement_approved_title: "Publicidade aprovada",
                advertisement_approved_body: "A sua publicidade {advertisement} foi aprovada. Já pode efetuar o pagamento.",
                advertisement_rejected_title: "Publicidade rejeitada",
                advertisement_rejected_body: "A sua publicidade {advertisement} foi rejeitada. Motivo: {reason}"
            },


            reviews: {
                intro: "Avaliações dos membros das comunidades do Misuki.",
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
                information: "Informação da licença",
                description: "Consulte aqui o estado e os detalhes da licença deste servidor.",
                inactive: "Inativa",
                created: "Criada",
                no_license_title: "Sem licença",
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
                license_active: "🟢 Licença Ativa",
                license_expired: "🔴 Licença Expirada",
                license_revoked: "⛔ Licença Revogada",
                no_license: "🔒 Sem Licença",
                no_authorized: "🔒 Não foram encontrados servidores autorizados.",
                no_available: "Não existem outros servidores disponíveis.",
                add_permission: "Adicionar permissão ✓",
                no_authorization: "⚠️ Sem autorização",
                add_misuki: "➕ Adicionar o Misuki",
                cannot_add: "⚠️ Não é possível adicionar",
                leave_review: "⭐ Deixar uma Avaliação",
                license: "Licença",
                no_authorized: "🔒 Não foram encontrados servidores autorizados.",
                no_available: "Não existem servidores adicionais disponíveis.",
                add_permission: "Permissão para adicionar ✓",
                no_authorization: "⚠️ Sem autorização",
                add_misuki: "➕ Adicionar o Misuki",
                cannot_add: "⚠️ Não é possível adicionar",
                leave_review: "⭐ Escrever uma avaliação"
            },

            footer: {
                copyright: "© 2026 Misuki. Todos os direitos reservados."
            },

            common: {
                product: "Produto",
                advertise_intro: "Promova o seu servidor Discord junto da comunidade do Misuki. Escolha a duração e crie o seu anúncio.",
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
                meet: "Conheça o",
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
                report_problem_text: "Encontrou um erro ou algo que não está a funcionar corretamente? Contacte a equipa de suporte do Misuki através do Discord.",
                advertisement_title: "Título da publicidade",
                description: "Descrição",
                image_url: "URL da imagem",
                destination_url: "URL de destino",
                advertisement_duration: "Duração da publicidade",
                server_name_placeholder: "Nome do seu servidor",
                description_placeholder: "Diga às pessoas o que torna o seu servidor especial...",
                special_offer: "OFERTA ESPECIAL",
                promotional_prices: "Preços promocionais",
                save_more: "POUPE MAIS",
                popular: "POPULAR",
                save: "Poupe",
                secure_payment: "Pagamento após aprovação",
                payment_secure: "Não é solicitado qualquer pagamento ao enviar a proposta. Se for aprovada, terá acesso ao pagamento através do PayPal.",
                continue_paypal: "Continuar para o PayPal",
                advertisement_note: "A sua publicidade será analisada antes de qualquer pagamento. Só poderá efetuar o pagamento depois de a equipa do Misuki aprovar a proposta.",
                days: "dias",
                option_7: "7 dias — €0,99",
                option_14: "14 dias — €1,50",
                option_30: "30 dias — €2,50",
                days_7: "7 DIAS",
                days_14: "14 DIAS",
                days_30: "30 DIAS",
                save_001: "Poupe €0,01",
                save_050: "Poupe €0,50",},

            statistics: {
                overview_kicker: "Visão geral",
                status_kicker: "Estado",
                performance_kicker: "Desempenho",
                hero_description: "Visão geral do serviço Misuki e das suas estatísticas atuais.",
                service_description: "Estatísticas gerais sobre o serviço Misuki.",
                servers: "Servidores",
                users: "Utilizadores",
                channels: "Canais",
                commands_available: "Comandos disponíveis",
                tickets_created: "Tickets criados",
                verifications: "Verificações",
                system_status: "Estado do sistema",
                system_description: "Estado atual do serviço Misuki.",
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
                admin_description: "Informação detalhada disponível apenas para administradores do Misuki.",
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
                privacy_description: "As estatísticas públicas são apresentadas de forma agregada. As informações específicas de servidores e utilizadores estão restritas aos administradores autorizados do Misuki."
            },

            cookies: {
                consent: "Consentimento de cookies",
                title: "🍪 Utilizamos cookies",
                description: "O Misuki utiliza cookies para melhorar a sua experiência e manter o website a funcionar corretamente.",
                accept: "Aceitar todos",
                essential: "Apenas essenciais",
                deny: "Recusar",
                terms: "Termos",
                privacy: "Privacidade",
                policy: "Política de Cookies"
            },

            legal: {
          "policy_updated": "Última atualização: agosto de 2026",
          "privacy_title": "Política de Privacidade",
          "privacy_intro": "Esta Política de Privacidade explica como o Misuki recolhe, utiliza, armazena e protege informações quando utiliza os nossos serviços.",
          "privacy_1_title": "1. Informações que Recolhemos",
          "privacy_1_p1": "Dependendo das funcionalidades que utiliza, o Misuki pode processar informações fornecidas pelo Discord ou geradas através da sua utilização do serviço.",
          "privacy_1_p2": "Estas informações podem incluir o seu ID de utilizador do Discord, nome de utilizador, informações do servidor e dados de configuração necessários para o funcionamento do Misuki.",
          "privacy_2_title": "2. Autenticação através do Discord",
          "privacy_2_p1": "O Misuki pode utilizar o Discord OAuth2 para autenticar utilizadores.",
          "privacy_2_p2": "Quando inicia sessão com o Discord, este pode fornecer informações permitidas pelos âmbitos OAuth2 solicitados pelo Misuki.",
          "privacy_2_p3": "O Misuki não recebe nem armazena a sua palavra-passe do Discord.",
          "privacy_3_title": "3. Como Utilizamos as Informações",
          "privacy_3_intro": "As informações podem ser utilizadas para:",
          "privacy_3_li1": "Disponibilizar e operar as funcionalidades do Misuki.",
          "privacy_3_li2": "Autenticar utilizadores.",
          "privacy_3_li3": "Manter as configurações dos servidores.",
          "privacy_3_li4": "Melhorar a fiabilidade e a segurança.",
          "privacy_3_li5": "Responder a pedidos de suporte.",
          "privacy_4_title": "4. Armazenamento de Dados",
          "privacy_4_p1": "Algumas informações podem ser armazenadas em bases de dados necessárias ao funcionamento do Misuki.",
          "privacy_4_p2": "Procuramos conservar apenas as informações necessárias para prestar o serviço.",
          "privacy_5_title": "5. Partilha de Dados",
          "privacy_5_p1": "O Misuki não vende informações pessoais.",
          "privacy_5_p2": "As informações podem ser processadas por fornecedores de infraestrutura ou de serviços quando tal for necessário para operar o Misuki.",
          "privacy_6_title": "6. Segurança",
          "privacy_6_p1": "São utilizadas medidas técnicas razoáveis para proteger as informações armazenadas contra acesso, alteração ou divulgação não autorizados.",
          "privacy_6_p2": "No entanto, nenhum serviço online pode garantir uma segurança absoluta.",
          "privacy_7_title": "7. Conservação de Dados",
          "privacy_7_p1": "As informações são conservadas apenas durante o período razoavelmente necessário para os fins descritos nesta política, salvo quando a lei exigir um período superior.",
          "privacy_8_title": "8. Os Seus Direitos",
          "privacy_8_p1": "Dependendo da legislação aplicável, poderá ter direitos relativamente às suas informações pessoais, incluindo o direito de aceder, corrigir ou solicitar a eliminação dos seus dados.",
          "privacy_8_p2": "Para pedidos relacionados com dados, contacte o suporte do Misuki.",
          "privacy_9_title": "9. Privacidade de Crianças",
          "privacy_9_p1": "O Misuki não se destina a recolher conscientemente informações pessoais de crianças em violação da legislação aplicável.",
          "privacy_10_title": "10. Serviços de Terceiros",
          "privacy_10_p1": "O Misuki pode interagir com serviços de terceiros, incluindo o Discord.",
          "privacy_10_p2": "Esses serviços têm as suas próprias políticas de privacidade e termos, que podem aplicar-se à sua utilização.",
          "privacy_11_title": "11. Alterações a Esta Política",
          "privacy_11_p1": "Esta Política de Privacidade pode ser atualizada quando necessário. As alterações serão refletidas nesta página.",
          "privacy_12_title": "12. Contacto",
          "privacy_12_p1": "Se tiver dúvidas sobre esta Política de Privacidade ou sobre os seus dados, contacte o suporte do Misuki.",
          "terms_title": "Termos de Serviço",
          "terms_1_title": "1. Aceitação dos Termos",
          "terms_1_p1": "Ao utilizar o Misuki, concorda em cumprir estes Termos de Serviço. Se não concordar com estes termos, não deverá utilizar o serviço.",
          "terms_2_title": "2. Utilização do Serviço",
          "terms_2_p1": "O Misuki disponibiliza ferramentas e serviços relacionados com o Discord, concebidos para ajudar os utilizadores a gerir e utilizar os seus servidores Discord.",
          "terms_2_p2": "Concorda em utilizar o Misuki de forma responsável e em conformidade com a legislação aplicável e com as regras e políticas do Discord.",
          "terms_3_title": "3. Discord",
          "terms_3_p1": "O Misuki é um serviço independente e não é afiliado, aprovado ou patrocinado pela Discord Inc.",
          "terms_3_p2": "A sua utilização do Discord continua sujeita aos próprios Termos de Serviço e às Diretrizes da Comunidade do Discord.",
          "terms_4_title": "4. Contas e Autenticação",
          "terms_4_p1": "Algumas funcionalidades do Misuki podem exigir autenticação através do Discord. É responsável por manter a segurança da sua conta.",
          "terms_4_p2": "O Misuki não solicita nem armazena a sua palavra-passe do Discord.",
          "terms_5_title": "5. Permissões do Servidor",
          "terms_5_p1": "O Misuki pode necessitar de determinadas permissões num servidor Discord para disponibilizar as suas funcionalidades.",
          "terms_5_p2": "Os proprietários e administradores dos servidores são responsáveis por decidir quais as permissões concedidas ao bot.",
          "terms_6_title": "6. Utilização Proibida",
          "terms_6_p1": "Não deve utilizar o Misuki para abusar, interromper, explorar ou interferir com o Discord, outros utilizadores ou o serviço.",
          "terms_6_p2": "Também não deve tentar obter acesso não autorizado aos sistemas ou dados do Misuki.",
          "terms_7_title": "7. Disponibilidade",
          "terms_7_p1": "Procuramos manter o Misuki disponível e funcional, mas não podemos garantir o acesso ininterrupto ao serviço.",
          "terms_7_p2": "As funcionalidades podem ser alteradas, suspensas ou descontinuadas quando necessário.",
          "terms_8_title": "8. Serviços de Terceiros",
          "terms_8_p1": "O Misuki pode depender de serviços de terceiros, incluindo o Discord e outros fornecedores de infraestrutura.",
          "terms_8_p2": "Os respetivos termos e políticas podem aplicar-se quando utiliza esses serviços.",
          "terms_9_title": "9. Terminação",
          "terms_9_p1": "O acesso ao Misuki pode ser restringido ou terminado se estes Termos de Serviço forem violados ou se tal for necessário para proteger o serviço e os seus utilizadores.",
          "terms_10_title": "10. Alterações a Estes Termos",
          "terms_10_p1": "Estes Termos de Serviço podem ser atualizados periodicamente. A utilização continuada do Misuki após a publicação de alterações constitui aceitação dos termos atualizados.",
          "terms_11_title": "11. Contacto",
          "terms_11_p1": "Se tiver dúvidas sobre estes termos, contacte o suporte do Misuki.",
          "cookies_title": "Política de Cookies",
          "cookies_intro": "O Misuki pode utilizar cookies e tecnologias semelhantes para disponibilizar e manter o website e as suas funcionalidades.",
          "cookies_1_title": "1. O que são Cookies?",
          "cookies_1_p1": "Os cookies são pequenos dados armazenados pelo seu navegador quando visita um website. Podem ser utilizados para memorizar informações entre pedidos e manter sessões.",
          "cookies_2_title": "2. Como o Misuki Utiliza Cookies",
          "cookies_2_p1": "O Misuki pode utilizar cookies para manter sessões ativas, memorizar preferências do utilizador e melhorar o serviço em geral.",
          "cookies_3_title": "3. As Suas Escolhas",
          "cookies_3_p1": "Pode optar por aceitar todos os cookies, permitir apenas os cookies essenciais ou recusar os cookies. A sua escolha é guardada no navegador e pode ser revista quando voltar a carregar o site.",
          "cookies_4_title": "4. Contacto",
          "cookies_4_p1": "Se tiver dúvidas sobre esta política, contacte o suporte do Misuki."
},

            verification: {
                login_required: "Inicie sessão para continuar",
                login_description: "Para iniciar a verificação, precisa de iniciar sessão com a sua conta Discord.",
                login_note: "Depois de iniciar sessão, voltará automaticamente para esta página e poderá continuar a verificação.",
                title: "Verificação",
                subtitle: "Confirme a sua conta Discord para obter acesso ao servidor.",
                authenticated_account: "Conta autenticada",
                verified_account: "Conta verificada",
                server: "Servidor",
                confirm: "Confirmar verificação",
                confirmed: "Verificação confirmada",
                request_sent: "O seu pedido de verificação foi enviado com sucesso.",
                received: "O Misuki recebeu o seu pedido.",
                processing: "O bot irá processar a sua verificação e atribuir o cargo correspondente no servidor.",
                return_discord: "Pode voltar ao Discord. Se a atribuição do cargo demorar alguns segundos, aguarde enquanto o Misuki processa o seu pedido.",
                info: "Ao continuar, o Misuki irá confirmar a sua conta Discord e enviar um pedido de verificação ao bot para atribuir o seu cargo de verificação.",
                captcha_placeholder: "Respuesta",
                footer: "Protegido por Misuki"
            }====================================
           DEUTSCH
           ===================================================== */

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
                license_management: "Lizenzverwaltung",
                my_advertisements: "Meine Werbungen",
                terms: "Bedingungen",
                privacy: "Datenschutz",
                data: "Daten",
                cookies: "Cookies",
                logout: "Abmelden",
                login: "Mit Discord anmelden"
            },

            licenses: {
                admin_eyebrow: "ADMINISTRATION",
                title: "Lizenzverwaltung",
                description: "Erstellen, verlängern und widerrufen Sie Serverlizenzen direkt auf der Misuki-Website.",
                back_statistics: "Zurück zu den Statistiken",
                create_title: "Lizenz erstellen",
                create_description: "Eine neue Lizenz wird sofort nach der Erstellung aktiv.",
                server_id: "Server-ID",
                days: "Dauer (Tage)",
                create: "Lizenz erstellen",
                existing: "Vorhandene Lizenzen",
                created: "Erstellt",
                expires: "Läuft ab",
                extend: "Verlängern",
                revoke: "Widerrufen",
                status_active: "Aktiv",
                status_expired: "Abgelaufen",
                status_revoked: "Widerrufen",
                status_none: "Unbekannt",
                none: "Keine Lizenzdatensätze vorhanden."
            },

            advertisements: {
                status_page_title: "Meine Werbungen",
                status_id: "ID:",
                duration_days: "Tage",
                payment_completed: "Zahlung abgeschlossen",
                status_unknown: "Status nicht verfügbar",
                advertisement_id: "ID:",
                      "section_kicker": "Werbung",
                      "featured_servers": "Ausgewählte Server",
                      "subtitle": "Entdecke Community-Server auf Misuki.",
                      "advertise_server": "Deinen Server bewerben",
                      "space_available": "Werbeplatz verfügbar",
                      "space_description": "Dein Server kann hier erscheinen. Sei einer der ersten, der auf Misuki wirbt.",
                      "pending_review": "Prüfung ausstehend",
                      "approved_payment_pending": "Genehmigt — Zahlung ausstehend",
                      "active": "Aktiv",
                      "rejected": "Abgelehnt",
                      "expired": "Abgelaufen",
                      "disabled": "Deaktiviert",
                      "paid": "Bezahlt",
                      "payment_pending": "Zahlung ausstehend",
                      "payment_failed": "Zahlung nicht abgeschlossen",
                      "reason": "Grund:",
                      "pay_paypal": "Mit PayPal bezahlen",
                      "open": "Öffnen",
                      "no_advertisements": "Du hast noch keine Werbungen.",
                      "proposal_submitted": "Werbung eingereicht",
                      "proposal_pending_review": "Dein Vorschlag wird jetzt vom Misuki-Team geprüft. Er wird vor jeder Zahlungsanforderung überprüft.",
                      "proposal_review_before_payment": "Die Zahlung wird erst nach Genehmigung des Vorschlags verfügbar.",
                      "back_to_dashboard": "Zurück zum Dashboard",
                "status_intro": "Verfolge jede Bewerbung, prüfe die Genehmigung, den Zahlungsstatus und wann die Werbung aktiv ist.",
                "approved_proposal": "Werbung genehmigt",
                "rejection_reason": "Ablehnungsgrund",
                "period": "Zeitraum:",
                "pay_ad": "Mit PayPal bezahlen",
                "open_ad": "Werbung öffnen",
                "no_proposals": "Du hast noch keine Werbevorschläge.",
                "proposal_sent": "Vorschlag eingereicht",
                "send_another": "Weiteren Vorschlag einreichen",
                "panel": "Dashboard",
                "payment_completed": "Zahlung abgeschlossen",
                "payment_status": "Werbestatus",
                "payment_status_desc": "Du kannst jederzeit prüfen, ob die Werbung aktiv ist, welchen Zeitraum du gebucht hast und wie der Zahlungsstatus ist.",
                "payment_success_description": "Die Zahlung für deine Werbung wurde erfolgreich bestätigt. Der genehmigte Vorschlag ist jetzt für den gebuchten Zeitraum bereit.",
                "return_dashboard": "Zurück zum Dashboard",
                "payment_cancelled": "Zahlung abgebrochen",
                "payment_not_completed": "Die Zahlung wurde nicht abgeschlossen.",
                "return": "Zurück",
                "advertisement_management": "Werbeverwaltung",
                "user_id": "Benutzer-ID:",
                "duration": "Dauer:",
                "start": "Beginn:",
                "end": "Ende:",
                "approve": "Genehmigen",
                "reject": "Ablehnen",
                "disable": "Deaktivieren",
                "approval_reason_placeholder": "Begründung der Genehmigung",
                "rejection_reason_placeholder": "Begründung der Ablehnung",
                "no_ads_admin": "Es gibt noch keine Werbungen."
            },

            menu_controls: {
                open: "Menü öffnen",
                close: "Menü schließen"
            },

            notifications: {
                title: "Benachrichtigungen",
                enable: "Benachrichtigungen aktivieren",
                enabled: "Benachrichtigungen aktiviert",
                denied: "Benachrichtigungen sind in den Browsereinstellungen blockiert.",
                unsupported: "Benachrichtigungen werden von diesem Browser nicht unterstützt.",
                login_required: "Melden Sie sich mit Discord an, um Benachrichtigungen zu aktivieren.",
                error: "Benachrichtigungen konnten nicht aktiviert werden.",
                empty: "Noch keine Benachrichtigungen.",
                advertisement_approved_title: "Werbung genehmigt",
                advertisement_approved_body: "Ihre Werbung {advertisement} wurde genehmigt. Sie können jetzt die Zahlung abschließen.",
                advertisement_rejected_title: "Werbung abgelehnt",
                advertisement_rejected_body: "Ihre Werbung {advertisement} wurde abgelehnt. Grund: {reason}"
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
                information: "Lizenzinformationen",
                description: "Sehen Sie hier den Status und die Details der Lizenz dieses Servers.",
                inactive: "Inaktiv",
                created: "Erstellt",
                no_license_title: "Keine Lizenz",
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
                license_active: "🟢 Lizenz aktiv",
                license_expired: "🔴 Lizenz abgelaufen",
                license_revoked: "⛔ Lizenz widerrufen",
                no_license: "🔒 Keine Lizenz",
                no_authorized: "🔒 Keine autorisierten Server gefunden.",
                no_available: "Keine weiteren Server verfügbar.",
                add_permission: "Berechtigung hinzufügen ✓",
                no_authorization: "⚠️ Keine Berechtigung",
                add_misuki: "➕ Misuki hinzufügen",
                cannot_add: "⚠️ Hinzufügen nicht möglich",
                leave_review: "⭐ Bewertung abgeben",
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
                copyright: "© 2026 Misuki. Alle Rechte vorbehalten."
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
                report_problem_text: "Hast du einen Fehler gefunden oder funktioniert etwas nicht korrekt? Kontaktiere das Misuki-Supportteam über Discord.",
                advertisement_title: "Werbeanzeigentitel",
                description: "Beschreibung",
                image_url: "Bild-URL",
                destination_url: "Ziel-URL",
                advertisement_duration: "Anzeigendauer",
                server_name_placeholder: "Name Ihres Servers",
                description_placeholder: "Sagen Sie anderen, was Ihren Server besonders macht...",
                special_offer: "SONDERANGEBOT",
                promotional_prices: "Aktionspreise",
                save_more: "MEHR SPAREN",
                popular: "BELIEBT",
                save: "Sparen",
                secure_payment: "Zahlung nach Genehmigung",
                payment_secure: "Beim Einreichen des Vorschlags ist keine Zahlung erforderlich. Nach der Genehmigung erhalten Sie Zugang zur PayPal-Zahlung.",
                continue_paypal: "Weiter zu PayPal",
                advertisement_note: "Ihre Werbung wird vor jeder Zahlungsanforderung geprüft. Sie können erst nach der Genehmigung durch das Misuki-Team bezahlen.",
                days: "Tage",
                option_7: "7 Tage — €0,99",
                option_14: "14 Tage — €1,50",
                option_30: "30 Tage — €2,50",
                days_7: "7 TAGE",
                days_14: "14 TAGE",
                days_30: "30 TAGE",
                save_001: "Sparen Sie €0,01",
                save_050: "Sparen Sie €0,50",},

            statistics: {
                overview_kicker: "Übersicht",
                status_kicker: "Status",
                performance_kicker: "Leistung",
                hero_description: "Übersicht über den Misuki-Dienst und seine aktuellen Statistiken.",
                service_description: "Allgemeine Statistiken über den Misuki-Dienst.",
                servers: "Server",
                users: "Benutzer",
                channels: "Kanäle",
                commands_available: "Verfügbare Befehle",
                tickets_created: "Erstellte Tickets",
                verifications: "Verifizierungen",
                system_status: "Systemstatus",
                system_description: "Aktueller Status des Misuki-Dienstes.",
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
                admin_description: "Detaillierte Informationen sind nur für Misuki-Administratoren verfügbar.",
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
                privacy_description: "Öffentliche Statistiken werden in aggregierter Form angezeigt. Spezifische Server- und Benutzerinformationen sind auf autorisierte Misuki-Administratoren beschränkt."
            },

            cookies: {
                consent: "Cookie-Einwilligung",
                title: "🍪 Wir verwenden Cookies",
                description: "Misuki verwendet Cookies, um Ihre Erfahrung zu verbessern und die Website ordnungsgemäß funktionsfähig zu halten.",
                accept: "Alle akzeptieren",
                essential: "Nur notwendige",
                deny: "Ablehnen",
                terms: "Bedingungen",
                privacy: "Datenschutz",
                policy: "Cookie-Richtlinie"
            },

            legal: {
          "policy_updated": "Zuletzt aktualisiert: August 2026",
          "privacy_title": "Datenschutzerklärung",
          "privacy_intro": "Diese Datenschutzerklärung erläutert, wie Misuki Informationen erhebt, verwendet, speichert und schützt, wenn Sie unsere Dienste nutzen.",
          "privacy_1_title": "1. Erhobene Informationen",
          "privacy_1_p1": "Je nach den von Ihnen verwendeten Funktionen kann Misuki von Discord bereitgestellte oder durch Ihre Nutzung des Dienstes erzeugte Informationen verarbeiten.",
          "privacy_1_p2": "Dazu können Ihre Discord-Benutzer-ID, Ihr Benutzername, Serverinformationen und für den Betrieb von Misuki erforderliche Konfigurationsdaten gehören.",
          "privacy_2_title": "2. Discord-Authentifizierung",
          "privacy_2_p1": "Misuki kann Discord OAuth2 zur Authentifizierung von Benutzern verwenden.",
          "privacy_2_p2": "Bei der Anmeldung mit Discord kann Discord Informationen bereitstellen, die durch die von Misuki angeforderten OAuth2-Bereiche erlaubt sind.",
          "privacy_2_p3": "Misuki erhält oder speichert Ihr Discord-Passwort nicht.",
          "privacy_3_title": "3. Verwendung von Informationen",
          "privacy_3_intro": "Informationen können verwendet werden, um:",
          "privacy_3_li1": "Misuki-Funktionen bereitzustellen und zu betreiben.",
          "privacy_3_li2": "Benutzer zu authentifizieren.",
          "privacy_3_li3": "Serverkonfigurationen zu verwalten.",
          "privacy_3_li4": "Zuverlässigkeit und Sicherheit zu verbessern.",
          "privacy_3_li5": "Supportanfragen zu beantworten.",
          "privacy_4_title": "4. Datenspeicherung",
          "privacy_4_p1": "Einige Informationen können in für den Betrieb von Misuki erforderlichen Datenbanken gespeichert werden.",
          "privacy_4_p2": "Wir bemühen uns, nur die für die Bereitstellung des Dienstes erforderlichen Informationen aufzubewahren.",
          "privacy_5_title": "5. Datenweitergabe",
          "privacy_5_p1": "Misuki verkauft keine personenbezogenen Informationen.",
          "privacy_5_p2": "Informationen können von Infrastruktur- oder Dienstleistern verarbeitet werden, wenn dies für den Betrieb von Misuki erforderlich ist.",
          "privacy_6_title": "6. Sicherheit",
          "privacy_6_p1": "Es werden angemessene technische Maßnahmen eingesetzt, um gespeicherte Informationen vor unbefugtem Zugriff, Änderung oder Offenlegung zu schützen.",
          "privacy_6_p2": "Kein Onlinedienst kann jedoch absolute Sicherheit garantieren.",
          "privacy_7_title": "7. Datenaufbewahrung",
          "privacy_7_p1": "Informationen werden nur so lange aufbewahrt, wie dies für die in dieser Richtlinie beschriebenen Zwecke angemessen erforderlich ist, sofern gesetzlich keine längere Aufbewahrung vorgeschrieben ist.",
          "privacy_8_title": "8. Ihre Rechte",
          "privacy_8_p1": "Je nach geltendem Recht können Sie Rechte in Bezug auf Ihre personenbezogenen Informationen haben, einschließlich des Rechts auf Auskunft, Berichtigung oder Löschung.",
          "privacy_8_p2": "Für datenschutzbezogene Anfragen wenden Sie sich bitte an den Misuki-Support.",
          "privacy_9_title": "9. Datenschutz von Kindern",
          "privacy_9_p1": "Misuki ist nicht dazu bestimmt, wissentlich personenbezogene Informationen von Kindern unter Verstoß gegen geltendes Recht zu erheben.",
          "privacy_10_title": "10. Dienste Dritter",
          "privacy_10_p1": "Misuki kann mit Diensten Dritter, einschließlich Discord, interagieren.",
          "privacy_10_p2": "Diese Dienste haben eigene Datenschutzrichtlinien und Nutzungsbedingungen, die für deren Nutzung gelten können.",
          "privacy_11_title": "11. Änderungen dieser Richtlinie",
          "privacy_11_p1": "Diese Datenschutzerklärung kann bei Bedarf aktualisiert werden. Änderungen werden auf dieser Seite veröffentlicht.",
          "privacy_12_title": "12. Kontakt",
          "privacy_12_p1": "Wenn Sie Fragen zu dieser Datenschutzerklärung oder Ihren Daten haben, wenden Sie sich bitte an den Misuki-Support.",
          "terms_title": "Nutzungsbedingungen",
          "terms_1_title": "1. Annahme der Bedingungen",
          "terms_1_p1": "Durch die Nutzung von Misuki stimmen Sie diesen Nutzungsbedingungen zu. Wenn Sie nicht zustimmen, sollten Sie den Dienst nicht nutzen.",
          "terms_2_title": "2. Nutzung des Dienstes",
          "terms_2_p1": "Misuki bietet Discord-bezogene Tools und Dienste, die Benutzern bei der Verwaltung und Nutzung ihrer Discord-Server helfen.",
          "terms_2_p2": "Sie verpflichten sich, Misuki verantwortungsvoll und gemäß den geltenden Gesetzen sowie den Regeln und Richtlinien von Discord zu nutzen.",
          "terms_3_title": "3. Discord",
          "terms_3_p1": "Misuki ist ein unabhängiger Dienst und nicht mit Discord Inc. verbunden, von diesem unterstützt oder gesponsert.",
          "terms_3_p2": "Ihre Nutzung von Discord unterliegt weiterhin den eigenen Nutzungsbedingungen und Community-Richtlinien von Discord.",
          "terms_4_title": "4. Konten und Authentifizierung",
          "terms_4_p1": "Einige Misuki-Funktionen können eine Authentifizierung über Discord erfordern. Sie sind für die Sicherheit Ihres Kontos verantwortlich.",
          "terms_4_p2": "Misuki fordert Ihr Discord-Passwort nicht an und speichert es nicht.",
          "terms_5_title": "5. Serverberechtigungen",
          "terms_5_p1": "Misuki kann bestimmte Berechtigungen auf einem Discord-Server benötigen, um seine Funktionen bereitzustellen.",
          "terms_5_p2": "Serverbesitzer und Administratoren entscheiden, welche Berechtigungen dem Bot erteilt werden.",
          "terms_6_title": "6. Verbotene Nutzung",
          "terms_6_p1": "Sie dürfen Misuki nicht missbrauchen, stören, ausnutzen oder Discord, andere Benutzer oder den Dienst beeinträchtigen.",
          "terms_6_p2": "Sie dürfen auch nicht versuchen, unbefugten Zugriff auf Misuki-Systeme oder -Daten zu erlangen.",
          "terms_7_title": "7. Verfügbarkeit",
          "terms_7_p1": "Wir bemühen uns, Misuki verfügbar und funktionsfähig zu halten, können jedoch keinen unterbrechungsfreien Zugriff garantieren.",
          "terms_7_p2": "Funktionen können bei Bedarf geändert, ausgesetzt oder eingestellt werden.",
          "terms_8_title": "8. Dienste Dritter",
          "terms_8_p1": "Misuki kann auf Dienste Dritter, einschließlich Discord und anderer Infrastrukturanbieter, angewiesen sein.",
          "terms_8_p2": "Deren eigene Bedingungen und Richtlinien können bei der Nutzung dieser Dienste gelten.",
          "terms_9_title": "9. Beendigung",
          "terms_9_p1": "Der Zugriff auf Misuki kann eingeschränkt oder beendet werden, wenn diese Nutzungsbedingungen verletzt werden oder dies zum Schutz des Dienstes und seiner Benutzer erforderlich ist.",
          "terms_10_title": "10. Änderungen dieser Bedingungen",
          "terms_10_p1": "Diese Nutzungsbedingungen können von Zeit zu Zeit aktualisiert werden. Die weitere Nutzung von Misuki nach der Veröffentlichung von Änderungen gilt als Zustimmung zu den aktualisierten Bedingungen.",
          "terms_11_title": "11. Kontakt",
          "terms_11_p1": "Bei Fragen zu diesen Bedingungen wenden Sie sich bitte an den Misuki-Support.",
          "cookies_title": "Cookie-Richtlinie",
          "cookies_intro": "Misuki kann Cookies und ähnliche Technologien verwenden, um die Website und ihre Funktionen bereitzustellen und zu erhalten.",
          "cookies_1_title": "1. Was sind Cookies?",
          "cookies_1_p1": "Cookies sind kleine Datenmengen, die Ihr Browser beim Besuch einer Website speichert. Sie können Informationen zwischen Anfragen speichern und Sitzungen aufrechterhalten.",
          "cookies_2_title": "2. Wie Misuki Cookies verwendet",
          "cookies_2_p1": "Misuki kann Cookies verwenden, um Sitzungen aktiv zu halten, Benutzereinstellungen zu speichern und den Dienst insgesamt zu verbessern.",
          "cookies_3_title": "3. Ihre Auswahl",
          "cookies_3_p1": "Sie können alle Cookies akzeptieren, nur notwendige Cookies zulassen oder Cookies ablehnen. Ihre Auswahl wird im Browser gespeichert und kann beim erneuten Laden der Website überprüft werden.",
          "cookies_4_title": "4. Kontakt",
          "cookies_4_p1": "Bei Fragen zu dieser Richtlinie wenden Sie sich bitte an den Misuki-Support."
},

            verification: {
                login_required: "Anmelden, um fortzufahren",
                login_description: "Um die Verifizierung zu starten, müssen Sie sich mit Ihrem Discord-Konto anmelden.",
                login_note: "Nach der Anmeldung kehren Sie automatisch zu dieser Seite zurück und können die Verifizierung fortsetzen.",
                title: "Verifizierung",
                subtitle: "Bestätigen Sie Ihr Discord-Konto, um Zugriff auf den Server zu erhalten.",
                authenticated_account: "Authentifiziertes Konto",
                verified_account: "Verifiziertes Konto",
                server: "Server",
                confirm: "Verifizierung bestätigen",
                confirmed: "Verifizierung bestätigt",
                request_sent: "Ihre Verifizierungsanfrage wurde erfolgreich gesendet.",
                received: "Misuki hat Ihre Anfrage erhalten.",
                processing: "Der Bot wird Ihre Verifizierung bearbeiten und die entsprechende Rolle auf dem Server vergeben.",
                return_discord: "Sie können zu Discord zurückkehren. Wenn die Vergabe der Rolle einige Sekunden dauert, warten Sie bitte, während Misuki Ihre Anfrage verarbeitet.",
                info: "Wenn Sie fortfahren, bestätigt Misuki Ihr Discord-Konto und sendet eine Verifizierungsanfrage an den Bot, damit Ihre Verifizierungsrolle vergeben werden kann.",
                captcha_placeholder: "Antwort",
                footer: "Geschützt durch Misuki"
            }
        },


        /* =====================================================
           ESPAÑOL
           ===================================================== */

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
                license_management: "Gestión de licencias",
                my_advertisements: "Mis publicidades",
                terms: "Términos",
                privacy: "Privacidad",
                data: "Datos",
                cookies: "Cookies",
                logout: "Cerrar sesión",
                login: "Iniciar sesión con Discord"
            },

            licenses: {
                admin_eyebrow: "ADMINISTRACIÓN",
                title: "Gestión de licencias",
                description: "Crea, amplía y revoca licencias de servidores directamente desde el sitio de Misuki.",
                back_statistics: "Volver a estadísticas",
                create_title: "Crear una licencia",
                create_description: "Una nueva licencia se activa inmediatamente después de crearla.",
                server_id: "ID del servidor",
                days: "Duración (días)",
                create: "Crear licencia",
                existing: "Licencias existentes",
                created: "Creada",
                expires: "Expira",
                extend: "Ampliar",
                revoke: "Revocar",
                status_active: "Activa",
                status_expired: "Expirada",
                status_revoked: "Revocada",
                status_none: "Desconocida",
                none: "No hay registros de licencias."
            },

            advertisements: {
                status_page_title: "Mis publicidades",
                status_id: "ID:",
                duration_days: "días",
                payment_completed: "Pago completado",
                status_unknown: "Estado no disponible",
                advertisement_id: "ID:",
                      "section_kicker": "Publicidad",
                      "featured_servers": "Servidores destacados",
                      "subtitle": "Descubre servidores de la comunidad en Misuki.",
                      "advertise_server": "Publicitar tu servidor",
                      "space_available": "Espacio publicitario disponible",
                      "space_description": "Tu servidor puede aparecer aquí. Sé de los primeros en publicitar en Misuki.",
                      "pending_review": "Pendiente de revisión",
                      "approved_payment_pending": "Aprobada — pago pendiente",
                      "active": "Activa",
                      "rejected": "Rechazada",
                      "expired": "Expirada",
                      "disabled": "Desactivada",
                      "paid": "Pagado",
                      "payment_pending": "Pago pendiente",
                      "payment_failed": "Pago no completado",
                      "reason": "Motivo:",
                      "pay_paypal": "Pagar con PayPal",
                      "open": "Abrir",
                      "no_advertisements": "Todavía no tienes publicidades.",
                      "proposal_submitted": "Publicidad enviada",
                      "proposal_pending_review": "Tu propuesta está pendiente de revisión por el equipo de Misuki. Se revisará antes de solicitar cualquier pago.",
                      "proposal_review_before_payment": "El pago solo estará disponible después de aprobar la propuesta.",
                      "back_to_dashboard": "Volver al panel",
                "status_intro": "Consulta cada propuesta, comprueba si fue aprobada, revisa el pago y confirma cuándo la publicidad está activa.",
                "approved_proposal": "Propuesta aprobada",
                "rejection_reason": "Motivo del rechazo",
                "period": "Periodo:",
                "pay_ad": "Realizar pago con PayPal",
                "open_ad": "Abrir publicidad",
                "no_proposals": "Todavía no tienes propuestas publicitarias.",
                "proposal_sent": "Propuesta enviada",
                "send_another": "Enviar otra propuesta",
                "panel": "Panel",
                "payment_completed": "Pago completado",
                "payment_status": "Estado de la publicidad",
                "payment_status_desc": "Puedes consultar en cualquier momento si la publicidad está activa, el periodo contratado y el estado del pago en Mis publicidades.",
                "payment_success_description": "El pago de tu publicidad se confirmó correctamente. La propuesta aprobada está lista para el periodo contratado.",
                "return_dashboard": "Volver al panel",
                "payment_cancelled": "Pago cancelado",
                "payment_not_completed": "El pago no se completó.",
                "return": "Volver",
                "advertisement_management": "Gestión de publicidad",
                "user_id": "ID de usuario:",
                "duration": "Duración:",
                "start": "Inicio:",
                "end": "Fin:",
                "approve": "Aprobar",
                "reject": "Rechazar",
                "disable": "Desactivar",
                "approval_reason_placeholder": "Justificación de la aprobación",
                "rejection_reason_placeholder": "Justificación del rechazo",
                "no_ads_admin": "Todavía no hay publicidades."
            },

            menu_controls: {
                open: "Abrir menú",
                close: "Cerrar menú"
            },

            notifications: {
                title: "Notificaciones",
                enable: "Activar notificaciones",
                enabled: "Notificaciones activadas",
                denied: "Las notificaciones están bloqueadas en la configuración del navegador.",
                unsupported: "Este navegador no admite notificaciones.",
                login_required: "Inicia sesión con Discord para activar las notificaciones.",
                error: "No se pudieron activar las notificaciones.",
                empty: "Aún no hay notificaciones.",
                advertisement_approved_title: "Publicidad aprobada",
                advertisement_approved_body: "Tu publicidad {advertisement} ha sido aprobada. Ya puedes completar el pago.",
                advertisement_rejected_title: "Publicidad rechazada",
                advertisement_rejected_body: "Tu publicidad {advertisement} ha sido rechazada. Motivo: {reason}"
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
                information: "Información de la licencia",
                description: "Consulta aquí el estado y los detalles de la licencia de este servidor.",
                inactive: "Inactiva",
                created: "Creada",
                no_license_title: "Sin licencia",
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
                license_active: "🟢 Licencia activa",
                license_expired: "🔴 Licencia caducada",
                license_revoked: "⛔ Licencia revocada",
                no_license: "🔒 Sin licencia",
                no_authorized: "🔒 No se encontraron servidores autorizados.",
                no_available: "No hay servidores adicionales disponibles.",
                add_permission: "Añadir permiso ✓",
                no_authorization: "⚠️ Sin autorización",
                add_misuki: "➕ Añadir Misuki",
                cannot_add: "⚠️ No se puede añadir",
                leave_review: "⭐ Dejar una reseña",
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
                copyright: "© 2026 Misuki. Todos los derechos reservados."
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
                report_problem_text: "¿Has encontrado un error o algo no funciona correctamente? Contacta con el equipo de soporte de Misuki a través de Discord.",
                advertisement_title: "Título del anuncio",
                description: "Descripción",
                image_url: "URL de la imagen",
                destination_url: "URL de destino",
                advertisement_duration: "Duración del anuncio",
                server_name_placeholder: "Nombre de tu servidor",
                description_placeholder: "Cuéntale a la gente qué hace especial a tu servidor...",
                special_offer: "OFERTA ESPECIAL",
                promotional_prices: "Precios promocionales",
                save_more: "AHORRA MÁS",
                popular: "POPULAR",
                save: "Ahorra",
                secure_payment: "Pago seguro con PayPal",
                payment_secure: "No se solicita ningún pago al enviar la propuesta. Si se aprueba, recibirás acceso al pago mediante PayPal.",
                continue_paypal: "Continuar a PayPal",
                advertisement_note: "Tu anuncio será revisado antes de solicitar cualquier pago. Solo podrás pagar después de que el equipo de Misuki apruebe la propuesta.",
                days: "días",
                option_7: "7 días — €0,99",
                option_14: "14 días — €1,50",
                option_30: "30 días — €2,50",
                days_7: "7 DÍAS",
                days_14: "14 DÍAS",
                days_30: "30 DÍAS",
                save_001: "Ahorra €0,01",
                save_050: "Ahorra €0,50",},

            statistics: {
                overview_kicker: "Resumen",
                status_kicker: "Estado",
                performance_kicker: "Rendimiento",
                hero_description: "Descripción general del servicio Misuki y sus estadísticas actuales.",
                service_description: "Estadísticas generales sobre el servicio Misuki.",
                servers: "Servidores",
                users: "Usuarios",
                channels: "Canales",
                commands_available: "Comandos disponibles",
                tickets_created: "Tickets creados",
                verifications: "Verificaciones",
                system_status: "Estado del sistema",
                system_description: "Estado actual del servicio Misuki.",
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
                admin_description: "La información detallada solo está disponible para los administradores de Misuki.",
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
                privacy_description: "Las estadísticas públicas se presentan de forma agregada. La información específica de servidores y usuarios está restringida a los administradores autorizados de Misuki."
            },

            cookies: {
                consent: "Consentimiento de cookies",
                title: "🍪 Utilizamos cookies",
                description: "Misuki utiliza cookies para mejorar su experiencia y mantener el sitio web funcionando correctamente.",
                accept: "Aceptar todos",
                essential: "Solo esenciales",
                deny: "Rechazar",
                terms: "Términos",
                privacy: "Privacidad",
                policy: "Política de Cookies"
            },

            legal: {
          "policy_updated": "Última actualización: agosto de 2026",
          "privacy_title": "Política de Privacidad",
          "privacy_intro": "Esta Política de Privacidad explica cómo Misuki recopila, utiliza, almacena y protege información cuando utiliza nuestros servicios.",
          "privacy_1_title": "1. Información que Recopilamos",
          "privacy_1_p1": "Dependiendo de las funciones que utilice, Misuki puede procesar información proporcionada por Discord o generada mediante su interacción con el servicio.",
          "privacy_1_p2": "Esto puede incluir su ID de usuario de Discord, nombre de usuario, información del servidor y datos de configuración necesarios para que Misuki funcione.",
          "privacy_2_title": "2. Autenticación de Discord",
          "privacy_2_p1": "Misuki puede utilizar Discord OAuth2 para autenticar a los usuarios.",
          "privacy_2_p2": "Cuando inicia sesión con Discord, Discord puede proporcionar información permitida por los ámbitos OAuth2 solicitados por Misuki.",
          "privacy_2_p3": "Misuki no recibe ni almacena su contraseña de Discord.",
          "privacy_3_title": "3. Cómo Utilizamos la Información",
          "privacy_3_intro": "La información puede utilizarse para:",
          "privacy_3_li1": "Proporcionar y operar las funciones de Misuki.",
          "privacy_3_li2": "Autenticar a los usuarios.",
          "privacy_3_li3": "Mantener las configuraciones de los servidores.",
          "privacy_3_li4": "Mejorar la fiabilidad y la seguridad.",
          "privacy_3_li5": "Responder a solicitudes de soporte.",
          "privacy_4_title": "4. Almacenamiento de Datos",
          "privacy_4_p1": "Parte de la información puede almacenarse en bases de datos necesarias para el funcionamiento de Misuki.",
          "privacy_4_p2": "Intentamos conservar únicamente la información necesaria para prestar el servicio.",
          "privacy_5_title": "5. Compartición de Datos",
          "privacy_5_p1": "Misuki no vende información personal.",
          "privacy_5_p2": "La información puede ser procesada por proveedores de infraestructura o servicios cuando sea necesario para operar Misuki.",
          "privacy_6_title": "6. Seguridad",
          "privacy_6_p1": "Se utilizan medidas técnicas razonables para proteger la información almacenada frente a accesos, modificaciones o divulgaciones no autorizadas.",
          "privacy_6_p2": "Sin embargo, ningún servicio en línea puede garantizar una seguridad absoluta.",
          "privacy_7_title": "7. Conservación de Datos",
          "privacy_7_p1": "La información se conserva solo durante el tiempo razonablemente necesario para los fines descritos en esta política, salvo que la ley exija un período mayor.",
          "privacy_8_title": "8. Sus Derechos",
          "privacy_8_p1": "Dependiendo de la legislación aplicable, puede tener derechos sobre su información personal, incluido el derecho de acceder, corregir o solicitar la eliminación de sus datos.",
          "privacy_8_p2": "Para solicitudes relacionadas con datos, contacte con el soporte de Misuki.",
          "privacy_9_title": "9. Privacidad de los Menores",
          "privacy_9_p1": "Misuki no está destinado a recopilar conscientemente información personal de menores infringiendo las leyes aplicables.",
          "privacy_10_title": "10. Servicios de Terceros",
          "privacy_10_p1": "Misuki puede interactuar con servicios de terceros, incluido Discord.",
          "privacy_10_p2": "Estos servicios tienen sus propias políticas de privacidad y condiciones que pueden aplicarse a su uso.",
          "privacy_11_title": "11. Cambios en esta Política",
          "privacy_11_p1": "Esta Política de Privacidad puede actualizarse cuando sea necesario. Los cambios se reflejarán en esta página.",
          "privacy_12_title": "12. Contacto",
          "privacy_12_p1": "Si tiene preguntas sobre esta Política de Privacidad o sus datos, contacte con el soporte de Misuki.",
          "terms_title": "Términos de Servicio",
          "terms_1_title": "1. Aceptación de los Términos",
          "terms_1_p1": "Al utilizar Misuki, acepta cumplir estos Términos de Servicio. Si no está de acuerdo, no debe utilizar el servicio.",
          "terms_2_title": "2. Uso del Servicio",
          "terms_2_p1": "Misuki proporciona herramientas y servicios relacionados con Discord diseñados para ayudar a los usuarios a gestionar e interactuar con sus servidores de Discord.",
          "terms_2_p2": "Acepta utilizar Misuki de forma responsable y de acuerdo con las leyes aplicables y las reglas y políticas de Discord.",
          "terms_3_title": "3. Discord",
          "terms_3_p1": "Misuki es un servicio independiente y no está afiliado, respaldado ni patrocinado por Discord Inc.",
          "terms_3_p2": "Su uso de Discord sigue estando sujeto a los propios Términos de Servicio y Directrices de la Comunidad de Discord.",
          "terms_4_title": "4. Cuentas y Autenticación",
          "terms_4_p1": "Algunas funciones de Misuki pueden requerir autenticación mediante Discord. Usted es responsable de mantener la seguridad de su cuenta.",
          "terms_4_p2": "Misuki no solicita ni almacena su contraseña de Discord.",
          "terms_5_title": "5. Permisos del Servidor",
          "terms_5_p1": "Misuki puede requerir determinados permisos en un servidor de Discord para proporcionar sus funciones.",
          "terms_5_p2": "Los propietarios y administradores del servidor deciden qué permisos se conceden al bot.",
          "terms_6_title": "6. Uso Prohibido",
          "terms_6_p1": "No debe utilizar Misuki para abusar, interrumpir, explotar o interferir con Discord, otros usuarios o el servicio.",
          "terms_6_p2": "Tampoco debe intentar obtener acceso no autorizado a los sistemas o datos de Misuki.",
          "terms_7_title": "7. Disponibilidad",
          "terms_7_p1": "Intentamos mantener Misuki disponible y funcional, pero no podemos garantizar un acceso ininterrumpido.",
          "terms_7_p2": "Las funciones pueden modificarse, suspenderse o discontinuarse cuando sea necesario.",
          "terms_8_title": "8. Servicios de Terceros",
          "terms_8_p1": "Misuki puede depender de servicios de terceros, incluidos Discord y otros proveedores de infraestructura.",
          "terms_8_p2": "Sus propias condiciones y políticas pueden aplicarse al utilizar esos servicios.",
          "terms_9_title": "9. Terminación",
          "terms_9_p1": "El acceso a Misuki puede restringirse o terminarse si se infringen estos Términos de Servicio o si es necesario para proteger el servicio y a sus usuarios.",
          "terms_10_title": "10. Cambios en estos Términos",
          "terms_10_p1": "Estos Términos de Servicio pueden actualizarse periódicamente. El uso continuado de Misuki después de publicar cambios constituye la aceptación de los términos actualizados.",
          "terms_11_title": "11. Contacto",
          "terms_11_p1": "Si tiene preguntas sobre estos términos, contacte con el soporte de Misuki.",
          "cookies_title": "Política de Cookies",
          "cookies_intro": "Misuki puede utilizar cookies y tecnologías similares para proporcionar y mantener el sitio web y sus funciones.",
          "cookies_1_title": "1. ¿Qué son las Cookies?",
          "cookies_1_p1": "Las cookies son pequeños datos almacenados por su navegador cuando visita un sitio web. Pueden utilizarse para recordar información entre solicitudes y mantener sesiones.",
          "cookies_2_title": "2. Cómo Utiliza Misuki las Cookies",
          "cookies_2_p1": "Misuki puede utilizar cookies para mantener las sesiones activas, recordar preferencias y mejorar el servicio en general.",
          "cookies_3_title": "3. Sus Opciones",
          "cookies_3_p1": "Puede aceptar todas las cookies, permitir solo las esenciales o rechazarlas. Su elección se guarda en el navegador y puede revisarse al volver a cargar el sitio.",
          "cookies_4_title": "4. Contacto",
          "cookies_4_p1": "Si tiene preguntas sobre esta política, contacte con el soporte de Misuki."
},

            verification: {
                login_required: "Inicia sesión para continuar",
                login_description: "Para iniciar la verificación, debes iniciar sesión con tu cuenta de Discord.",
                login_note: "Después de iniciar sesión, volverás automáticamente a esta página y podrás continuar con la verificación.",
                title: "Verificación",
                subtitle: "Confirma tu cuenta de Discord para obtener acceso al servidor.",
                authenticated_account: "Cuenta autenticada",
                verified_account: "Cuenta verificada",
                server: "Servidor",
                confirm: "Confirmar verificación",
                confirmed: "Verificación confirmada",
                request_sent: "Tu solicitud de verificación se ha enviado correctamente.",
                received: "Misuki ha recibido tu solicitud.",
                processing: "El bot procesará tu verificación y asignará el rol correspondiente en el servidor.",
                return_discord: "Puedes volver a Discord. Si el rol tarda unos segundos en asignarse, espera mientras Misuki procesa tu solicitud.",
                info: "Al continuar, Misuki confirmará tu cuenta de Discord y enviará una solicitud de verificación al bot para asignar tu rol de verificación.",
                footer: "Protegido por Misuki"
            }
        },


        /* =====================================================
           FRANÇAIS
           ===================================================== */

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
                license_management: "Gestion des licences",
                my_advertisements: "Mes publicités",
                terms: "Conditions",
                privacy: "Confidentialité",
                data: "Données",
                cookies: "Cookies",
                logout: "Se déconnecter",
                login: "Se connecter avec Discord"
            },

            licenses: {
                admin_eyebrow: "ADMINISTRATION",
                title: "Gestion des licences",
                description: "Créez, prolongez et révoquez les licences de serveurs directement depuis le site Misuki.",
                back_statistics: "Retour aux statistiques",
                create_title: "Créer une licence",
                create_description: "Une nouvelle licence devient active immédiatement après sa création.",
                server_id: "ID du serveur",
                days: "Durée (jours)",
                create: "Créer la licence",
                existing: "Licences existantes",
                created: "Créée",
                expires: "Expire",
                extend: "Prolonger",
                revoke: "Révoquer",
                status_active: "Active",
                status_expired: "Expirée",
                status_revoked: "Révoquée",
                status_none: "Inconnue",
                none: "Aucun enregistrement de licence."
            },

            advertisements: {
                status_page_title: "Mes publicités",
                status_id: "ID :",
                duration_days: "jours",
                payment_completed: "Paiement effectué",
                status_unknown: "État indisponible",
                advertisement_id: "ID:",
                      "section_kicker": "Publicité",
                      "featured_servers": "Serveurs en vedette",
                      "subtitle": "Découvrez les serveurs de la communauté sur Misuki.",
                      "advertise_server": "Publiciser votre serveur",
                      "space_available": "Espace publicitaire disponible",
                      "space_description": "Votre serveur peut apparaître ici. Soyez parmi les premiers à faire de la publicité sur Misuki.",
                      "pending_review": "En attente d'examen",
                      "approved_payment_pending": "Approuvée — paiement en attente",
                      "active": "Active",
                      "rejected": "Rejetée",
                      "expired": "Expirée",
                      "disabled": "Désactivée",
                      "paid": "Payée",
                      "payment_pending": "Paiement en attente",
                      "payment_failed": "Paiement non effectué",
                      "reason": "Motif :",
                      "pay_paypal": "Payer avec PayPal",
                      "open": "Ouvrir",
                      "no_advertisements": "Vous n'avez encore aucune publicité.",
                      "proposal_submitted": "Publicité envoyée",
                      "proposal_pending_review": "Votre proposition est maintenant en attente d'examen par l'équipe Misuki. Elle sera examinée avant toute demande de paiement.",
                      "proposal_review_before_payment": "Le paiement ne sera disponible qu'après l'approbation de la proposition.",
                      "back_to_dashboard": "Retour au tableau de bord",
                "status_intro": "Suivez chaque proposition, vérifiez son approbation, consultez le paiement et confirmez quand la publicité est active.",
                "approved_proposal": "Proposition approuvée",
                "rejection_reason": "Motif du rejet",
                "period": "Période :",
                "pay_ad": "Effectuer le paiement avec PayPal",
                "open_ad": "Ouvrir la publicité",
                "no_proposals": "Vous n'avez encore aucune proposition publicitaire.",
                "proposal_sent": "Proposition envoyée",
                "send_another": "Envoyer une autre proposition",
                "panel": "Tableau de bord",
                "payment_completed": "Paiement effectué",
                "payment_status": "État de la publicité",
                "payment_status_desc": "Vous pouvez vérifier à tout moment si la publicité est active, la période souscrite et l'état du paiement dans Mes publicités.",
                "payment_success_description": "Le paiement de votre publicité a été confirmé avec succès. La proposition approuvée est maintenant prête pour la période souscrite.",
                "return_dashboard": "Retour au tableau de bord",
                "payment_cancelled": "Paiement annulé",
                "payment_not_completed": "Le paiement n'a pas été effectué.",
                "return": "Retour",
                "advertisement_management": "Gestion de la publicité",
                "user_id": "ID utilisateur :",
                "duration": "Durée :",
                "start": "Début :",
                "end": "Fin :",
                "approve": "Approuver",
                "reject": "Rejeter",
                "disable": "Désactiver",
                "approval_reason_placeholder": "Justification de l'approbation",
                "rejection_reason_placeholder": "Justification du rejet",
                "no_ads_admin": "Aucune publicité pour le moment."
            },

            menu_controls: {
                open: "Ouvrir le menu",
                close: "Fermer le menu"
            },

            notifications: {
                title: "Notifications",
                enable: "Activer les notifications",
                enabled: "Notifications activées",
                denied: "Les notifications sont bloquées dans les paramètres du navigateur.",
                unsupported: "Les notifications ne sont pas prises en charge par ce navigateur.",
                login_required: "Connectez-vous avec Discord pour activer les notifications.",
                error: "Impossible d’activer les notifications.",
                empty: "Aucune notification pour le moment.",
                advertisement_approved_title: "Publicité approuvée",
                advertisement_approved_body: "Votre publicité {advertisement} a été approuvée. Vous pouvez maintenant effectuer le paiement.",
                advertisement_rejected_title: "Publicité refusée",
                advertisement_rejected_body: "Votre publicité {advertisement} a été refusée. Motif : {reason}"
            },


            reviews: {
                intro: "Avis des membres des communautés de Misuki.",
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
                information: "Informations sur la licence",
                description: "Consultez ici l’état et les détails de la licence de ce serveur.",
                inactive: "Inactive",
                created: "Créée",
                no_license_title: "Aucune licence",
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
                license_active: "🟢 Licence active",
                license_expired: "🔴 Licence expirée",
                license_revoked: "⛔ Licence révoquée",
                no_license: "🔒 Aucune licence",
                no_authorized: "🔒 Aucun serveur autorisé trouvé.",
                no_available: "Aucun autre serveur disponible.",
                add_permission: "Ajouter l’autorisation ✓",
                no_authorization: "⚠️ Aucune autorisation",
                add_misuki: "➕ Ajouter Misuki",
                cannot_add: "⚠️ Impossible d’ajouter",
                leave_review: "⭐ Laisser un avis",
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
                copyright: "© 2026 Misuki. Tous droits réservés."
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
                report_problem_text: "Vous avez trouvé un bug ou quelque chose ne fonctionne pas correctement ? Contactez l'équipe support de Misuki via Discord.",
                advertisement_title: "Titre de la publicité",
                description: "Description",
                image_url: "URL de l’image",
                destination_url: "URL de destination",
                advertisement_duration: "Durée de la publicité",
                server_name_placeholder: "Nom de votre serveur",
                description_placeholder: "Dites aux utilisateurs ce qui rend votre serveur spécial...",
                special_offer: "OFFRE SPÉCIALE",
                promotional_prices: "Prix promotionnels",
                save_more: "ÉCONOMISEZ PLUS",
                popular: "POPULAIRE",
                save: "Économisez",
                secure_payment: "Paiement après approbation",
                payment_secure: "Aucun paiement n'est demandé lors de l'envoi de la proposition. Si elle est approuvée, vous aurez accès au paiement via PayPal.",
                continue_paypal: "Continuer vers PayPal",
                advertisement_note: "Votre publicité sera examinée avant toute demande de paiement. Vous ne pourrez payer qu'après l'approbation de la proposition par l'équipe Misuki.",
                days: "jours",
                option_7: "7 jours — 0,99 €",
                option_14: "14 jours — 1,50 €",
                option_30: "30 jours — 2,50 €",
                days_7: "7 JOURS",
                days_14: "14 JOURS",
                days_30: "30 JOURS",
                save_001: "Économisez 0,01 €",
                save_050: "Économisez 0,50 €",},

            statistics: {
                overview_kicker: "Vue d’ensemble",
                status_kicker: "État",
                performance_kicker: "Performance",
                hero_description: "Vue d’ensemble du service Misuki et de ses statistiques actuelles.",
                service_description: "Statistiques générales du service Misuki.",
                servers: "Serveurs",
                users: "Utilisateurs",
                channels: "Salons",
                commands_available: "Commandes disponibles",
                tickets_created: "Tickets créés",
                verifications: "Vérifications",
                system_status: "État du système",
                system_description: "État actuel du service Misuki.",
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
                admin_description: "Les informations détaillées sont disponibles uniquement pour les administrateurs de Misuki.",
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
                privacy_description: "Les statistiques publiques sont présentées sous forme agrégée. Les informations spécifiques aux serveurs et aux utilisateurs sont réservées aux administrateurs Misuki autorisés."
            },

            cookies: {
                consent: "Consentement aux cookies",
                title: "🍪 Nous utilisons des cookies",
                description: "Misuki utilise des cookies pour améliorer votre expérience et assurer le bon fonctionnement du site.",
                accept: "Tout accepter",
                essential: "Essentiels uniquement",
                deny: "Refuser",
                terms: "Conditions",
                privacy: "Confidentialité",
                policy: "Politique relative aux cookies"
            },

            legal: {
          "policy_updated": "Dernière mise à jour : août 2026",
          "privacy_title": "Politique de confidentialité",
          "privacy_intro": "Cette Politique de confidentialité explique comment Misuki collecte, utilise, stocke et protège les informations lorsque vous utilisez nos services.",
          "privacy_1_title": "1. Informations collectées",
          "privacy_1_p1": "Selon les fonctionnalités que vous utilisez, Misuki peut traiter des informations fournies par Discord ou générées lors de votre utilisation du service.",
          "privacy_1_p2": "Cela peut inclure votre identifiant utilisateur Discord, votre nom d’utilisateur, des informations sur le serveur et les données de configuration nécessaires au fonctionnement de Misuki.",
          "privacy_2_title": "2. Authentification Discord",
          "privacy_2_p1": "Misuki peut utiliser Discord OAuth2 pour authentifier les utilisateurs.",
          "privacy_2_p2": "Lorsque vous vous connectez avec Discord, celui-ci peut fournir les informations autorisées par les scopes OAuth2 demandés par Misuki.",
          "privacy_2_p3": "Misuki ne reçoit ni ne stocke votre mot de passe Discord.",
          "privacy_3_title": "3. Utilisation des informations",
          "privacy_3_intro": "Les informations peuvent être utilisées pour :",
          "privacy_3_li1": "Fournir et exploiter les fonctionnalités de Misuki.",
          "privacy_3_li2": "Authentifier les utilisateurs.",
          "privacy_3_li3": "Gérer les configurations des serveurs.",
          "privacy_3_li4": "Améliorer la fiabilité et la sécurité.",
          "privacy_3_li5": "Répondre aux demandes d’assistance.",
          "privacy_4_title": "4. Stockage des données",
          "privacy_4_p1": "Certaines informations peuvent être stockées dans des bases de données nécessaires au fonctionnement de Misuki.",
          "privacy_4_p2": "Nous cherchons à conserver uniquement les informations nécessaires à la fourniture du service.",
          "privacy_5_title": "5. Partage des données",
          "privacy_5_p1": "Misuki ne vend pas d’informations personnelles.",
          "privacy_5_p2": "Les informations peuvent être traitées par des fournisseurs d’infrastructure ou de services lorsque cela est nécessaire au fonctionnement de Misuki.",
          "privacy_6_title": "6. Sécurité",
          "privacy_6_p1": "Des mesures techniques raisonnables sont utilisées pour protéger les informations stockées contre les accès, modifications ou divulgations non autorisés.",
          "privacy_6_p2": "Cependant, aucun service en ligne ne peut garantir une sécurité absolue.",
          "privacy_7_title": "7. Conservation des données",
          "privacy_7_p1": "Les informations sont conservées uniquement pendant la durée raisonnablement nécessaire aux fins décrites dans cette politique, sauf si la loi impose une durée plus longue.",
          "privacy_8_title": "8. Vos droits",
          "privacy_8_p1": "Selon la législation applicable, vous pouvez disposer de droits concernant vos informations personnelles, notamment le droit d’accès, de rectification ou de suppression de vos données.",
          "privacy_8_p2": "Pour toute demande concernant vos données, veuillez contacter le support Misuki.",
          "privacy_9_title": "9. Vie privée des enfants",
          "privacy_9_p1": "Misuki n’a pas pour objectif de collecter sciemment des informations personnelles d’enfants en violation des lois applicables.",
          "privacy_10_title": "10. Services tiers",
          "privacy_10_p1": "Misuki peut interagir avec des services tiers, notamment Discord.",
          "privacy_10_p2": "Ces services disposent de leurs propres politiques de confidentialité et conditions qui peuvent s’appliquer à leur utilisation.",
          "privacy_11_title": "11. Modifications de cette politique",
          "privacy_11_p1": "Cette Politique de confidentialité peut être mise à jour lorsque nécessaire. Les modifications seront indiquées sur cette page.",
          "privacy_12_title": "12. Contact",
          "privacy_12_p1": "Si vous avez des questions concernant cette Politique de confidentialité ou vos données, veuillez contacter le support Misuki.",
          "terms_title": "Conditions d’utilisation",
          "terms_1_title": "1. Acceptation des conditions",
          "terms_1_p1": "En utilisant Misuki, vous acceptez de respecter ces Conditions d’utilisation. Si vous n’êtes pas d’accord, vous ne devez pas utiliser le service.",
          "terms_2_title": "2. Utilisation du service",
          "terms_2_p1": "Misuki fournit des outils et services liés à Discord conçus pour aider les utilisateurs à gérer et utiliser leurs serveurs Discord.",
          "terms_2_p2": "Vous acceptez d’utiliser Misuki de manière responsable et conformément aux lois applicables ainsi qu’aux règles et politiques de Discord.",
          "terms_3_title": "3. Discord",
          "terms_3_p1": "Misuki est un service indépendant et n’est pas affilié à Discord Inc., ni approuvé ou sponsorisé par cette société.",
          "terms_3_p2": "Votre utilisation de Discord reste soumise aux propres Conditions d’utilisation et Règles communautaires de Discord.",
          "terms_4_title": "4. Comptes et authentification",
          "terms_4_p1": "Certaines fonctionnalités de Misuki peuvent nécessiter une authentification via Discord. Vous êtes responsable de la sécurité de votre compte.",
          "terms_4_p2": "Misuki ne demande ni ne stocke votre mot de passe Discord.",
          "terms_5_title": "5. Autorisations du serveur",
          "terms_5_p1": "Misuki peut nécessiter certaines autorisations sur un serveur Discord pour fournir ses fonctionnalités.",
          "terms_5_p2": "Les propriétaires et administrateurs des serveurs décident des autorisations accordées au bot.",
          "terms_6_title": "6. Utilisation interdite",
          "terms_6_p1": "Vous ne devez pas utiliser Misuki pour abuser, perturber, exploiter ou interférer avec Discord, d’autres utilisateurs ou le service.",
          "terms_6_p2": "Vous ne devez pas non plus tenter d’obtenir un accès non autorisé aux systèmes ou données de Misuki.",
          "terms_7_title": "7. Disponibilité",
          "terms_7_p1": "Nous cherchons à maintenir Misuki disponible et fonctionnel, mais nous ne pouvons pas garantir un accès ininterrompu.",
          "terms_7_p2": "Les fonctionnalités peuvent être modifiées, suspendues ou arrêtées lorsque cela est nécessaire.",
          "terms_8_title": "8. Services tiers",
          "terms_8_p1": "Misuki peut dépendre de services tiers, notamment Discord et d’autres fournisseurs d’infrastructure.",
          "terms_8_p2": "Leurs propres conditions et politiques peuvent s’appliquer lorsque vous utilisez ces services.",
          "terms_9_title": "9. Résiliation",
          "terms_9_p1": "L’accès à Misuki peut être restreint ou résilié si ces Conditions d’utilisation sont violées ou si cela est nécessaire pour protéger le service et ses utilisateurs.",
          "terms_10_title": "10. Modifications de ces conditions",
          "terms_10_p1": "Ces Conditions d’utilisation peuvent être mises à jour périodiquement. La poursuite de l’utilisation de Misuki après publication de modifications constitue une acceptation des conditions mises à jour.",
          "terms_11_title": "11. Contact",
          "terms_11_p1": "Si vous avez des questions concernant ces conditions, veuillez contacter le support Misuki.",
          "cookies_title": "Politique relative aux cookies",
          "cookies_intro": "Misuki peut utiliser des cookies et des technologies similaires pour fournir et maintenir le site web et ses fonctionnalités.",
          "cookies_1_title": "1. Que sont les cookies ?",
          "cookies_1_p1": "Les cookies sont de petites données stockées par votre navigateur lorsque vous visitez un site web. Ils peuvent servir à mémoriser des informations entre les requêtes et à maintenir les sessions.",
          "cookies_2_title": "2. Comment Misuki utilise les cookies",
          "cookies_2_p1": "Misuki peut utiliser des cookies pour maintenir les sessions actives, mémoriser les préférences et améliorer le service global.",
          "cookies_3_title": "3. Vos choix",
          "cookies_3_p1": "Vous pouvez accepter tous les cookies, autoriser uniquement les cookies essentiels ou les refuser. Votre choix est enregistré dans le navigateur et peut être revu lors du rechargement du site.",
          "cookies_4_title": "4. Contact",
          "cookies_4_p1": "Si vous avez des questions concernant cette politique, veuillez contacter le support Misuki."
},

            verification: {
                login_required: "Connectez-vous pour continuer",
                login_description: "Pour commencer la vérification, vous devez vous connecter avec votre compte Discord.",
                login_note: "Après vous être connecté, vous reviendrez automatiquement sur cette page et pourrez poursuivre la vérification.",
                title: "Vérification",
                subtitle: "Confirmez votre compte Discord pour obtenir l'accès au serveur.",
                authenticated_account: "Compte authentifié",
                verified_account: "Compte vérifié",
                server: "Serveur",
                confirm: "Confirmer la vérification",
                confirmed: "Vérification confirmée",
                request_sent: "Votre demande de vérification a été envoyée avec succès.",
                received: "Misuki a reçu votre demande.",
                processing: "Le bot traitera votre vérification et attribuera le rôle correspondant sur le serveur.",
                return_discord: "Vous pouvez retourner sur Discord. Si l'attribution du rôle prend quelques secondes, veuillez patienter pendant que Misuki traite votre demande.",
                info: "En continuant, Misuki confirmera votre compte Discord et enverra une demande de vérification au bot afin d'attribuer votre rôle de vérification.",
                captcha_placeholder: "Réponse",
                footer: "Protégé par Misuki"
            }
        }
    };


    /* =========================================================
       AUTOMATIC STATIC TEXT TRANSLATION
       ========================================================= */

    const staticPhraseKeys = {
        en: {},
        pt: {},
        de: {},
        es: {},
        fr: {}
    };

    function buildPhraseIndex(value, path, language) {
        if (!value || typeof value !== "object") return;

        Object.keys(value).forEach(function (key) {
            const current = value[key];
            const currentPath = path ? path + "." + key : key;

            if (typeof current === "string") {
                const normalized = normalizeStaticText(current);
                if (
                    normalized &&
                    !staticPhraseKeys[language][normalized]
                ) {
                    staticPhraseKeys[language][normalized] = currentPath;
                }
            } else if (current && typeof current === "object") {
                buildPhraseIndex(current, currentPath, language);
            }
        });
    }

    function findStaticTranslationKey(normalized) {
        if (!normalized) return null;

        for (const sourceLanguage of SUPPORTED_LANGUAGES) {
            const index = staticPhraseKeys[sourceLanguage];
            if (index && index[normalized]) {
                return index[normalized];
            }
        }

        return null;
    }

    function normalizeStaticText(value) {
        return String(value || "")
            .replace(/^\s+|\s+$/g, "")
            .replace(/^([\p{Extended_Pictographic}\uFE0F]\s*)+/u, "")
            .replace(/\s+/g, " ")
            .trim();
    }

    function isProtectedStaticElement(element) {
        if (!element || element.nodeType !== 1) return true;

        if (element.closest(
            "script, style, textarea, input, select, option, " +
            ".server-name, .server-id, .review-text, " +
            ".advertisement-card, .advertisement-content, " +
            "[data-dynamic-content]"
        )) {
            return true;
        }

        return element.hasAttribute("data-i18n");
    }

    function translateStaticText(language) {

        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT
        );

        const nodes = [];
        let node;

        while ((node = walker.nextNode())) {
            nodes.push(node);
        }

        nodes.forEach(function (textNode) {
            const parent = textNode.parentElement;

            if (isProtectedStaticElement(parent)) return;
            if (!textNode.nodeValue || !textNode.nodeValue.trim()) return;

            if (
                !textNode.__misukiOriginalText &&
                !textNode.nodeValue.includes("{{") &&
                !textNode.nodeValue.includes("{%")
            ) {
                textNode.__misukiOriginalText = textNode.nodeValue;
            }

            const original =
                textNode.__misukiOriginalText ||
                textNode.nodeValue;

            if (original.includes("{{") || original.includes("{%")) return;

            const normalized = normalizeStaticText(original);
            const key = findStaticTranslationKey(normalized);

            if (!key) {
                textNode.nodeValue = original;
                return;
            }

            const translated = getTranslation(language, key);

            if (translated === null || translated === normalized) {
                textNode.nodeValue = original;
                return;
            }

            const leading = original.match(/^\s*/)?.[0] || "";
            const trailing = original.match(/\s*$/)?.[0] || "";

            textNode.nodeValue = leading + translated + trailing;
        });
    }

    SUPPORTED_LANGUAGES.forEach(function (language) {
        buildPhraseIndex(
            translations[language],
            "",
            language
        );
    });

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
                    return getTranslation(
                        DEFAULT_LANGUAGE,
                        key
                    );
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
                document.getElementById(
                    "languageSelector"
                ),

            button:
                document.getElementById(
                    "languageButton"
                ),

            dropdown:
                document.getElementById(
                    "languageDropdown"
                )
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
            button.querySelector(
                ".language-flag"
            );

        if (flag) {
            flag.textContent =
                info.flag;
        }

        const short =
            button.querySelector(
                ".language-short"
            );

        if (short) {
            short.textContent =
                info.short;
        }

        const translatedLabel =
            getTranslation(
                language,
                "language.select"
            );

        button.setAttribute(
            "aria-label",
            translatedLabel ||
            "Select language"
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
                option.getAttribute(
                    "data-lang"
                ) === language;

            option.classList.toggle(
                "active",
                active
            );

            option.setAttribute(
                "aria-selected",
                active
                    ? "true"
                    : "false"
            );
        });
    }


    /* =========================================================
       TRANSLATE ATTRIBUTES
       ========================================================= */

    function translateAttributes(language) {

        document
            .querySelectorAll(
                "[data-i18n-attr]"
            )
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
                                .slice(
                                    0,
                                    separator
                                )
                                .trim();

                        const key =
                            definition
                                .slice(
                                    separator + 1
                                )
                                .trim();

                        const translated =
                            getTranslation(
                                language,
                                key
                            );

                        if (
                            translated !== null
                        ) {

                            element.setAttribute(
                                attribute,
                                translated
                            );
                        }
                    });
            });
    }


    /* =========================================================
       TRANSLATE DOCUMENT TITLE
       ========================================================= */

    function translateDocumentTitle(language) {

        const titleKeys = {

            "/": "common.home_title",

            "/dashboard": "nav.dashboard",

            "/reviews": "nav.reviews",

            "/statistics": "nav.statistics",

            "/documentation": "nav.documentation",

            "/support": "nav.support",

            "/advertise": "nav.advertisement",

            "/advertise/status": "nav.my_advertisements",

            "/advertise/success": "advertisements.proposal_submitted",

            "/payment/success": "advertisements.payment_completed",

            "/payment/cancel": "advertisements.payment_cancelled",

            "/admin/advertise": "advertisements.advertisement_management",

            "/terms": "nav.terms",

            "/privacy": "nav.privacy",

            "/data": "nav.data",

            "/cookies": "nav.cookies",

            "/verify": "verification.title"
        };

        const key =
            titleKeys[
                window.location.pathname
            ];

        const translated =
            key
                ? getTranslation(
                    language,
                    key
                )
                : null;

        if (
            translated !== null
        ) {

            document.title =
                translated +
                " — Misuki";
        }
    }


    /* =========================================================
       TRANSLATE PAGE
       ========================================================= */

    function translatePage(language) {

        if (
            !SUPPORTED_LANGUAGES.includes(
                language
            )
        ) {

            language =
                DEFAULT_LANGUAGE;
        }

        document
            .querySelectorAll(
                "[data-i18n]"
            )
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

                if (
                    translated !== null
                ) {

                    element.textContent =
                        translated;
                }
            });

        translateAttributes(
            language
        );

        translateStaticText(
            language
        );

        translateDocumentTitle(
            language
        );

        document.documentElement.lang =
            language;

        updateLanguageButton(
            language
        );

        updateActiveLanguage(
            language
        );

        saveLanguage(
            language
        );

        window.dispatchEvent(
            new CustomEvent(
                "misukiLanguageChanged",
                {
                    detail: {
                        language:
                            language
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

        if (
            !selector ||
            !button ||
            !dropdown
        ) {
            return;
        }

        selector.classList.remove(
            "open",
            "active"
        );

        dropdown.classList.remove(
            "show"
        );

        dropdown.style.display =
            "none";

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

        if (
            !selector ||
            !button ||
            !dropdown
        ) {

            console.warn(
                "Misuki: language selector elements missing."
            );

            return;
        }

        // The selector remains openable even when the main menu is open.
        // The main menu is layered above it by CSS.

        selector.classList.add(
            "open"
        );

        dropdown.classList.add(
            "show"
        );

        dropdown.style.display =
            "flex";

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
            selector.classList.contains(
                "open"
            ) ||
            selector.classList.contains(
                "active"
            )
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

                    translatePage(
                        language
                    );

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

        // Intentionally empty.
        // The language selector remains available independently of the
        // side menu, while CSS keeps the side menu above it.

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

        if (
            !selector ||
            !button ||
            !dropdown
        ) {

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

        setLanguage: function (
            language
        ) {

            if (
                !SUPPORTED_LANGUAGES.includes(
                    language
                )
            ) {
                return;
            }

            translatePage(
                language
            );
        },

        getLanguage: function () {

            return getSavedLanguage();
        },

        getTranslation: function (
            language,
            key
        ) {

            return getTranslation(
                language,
                key
            );
        },

        getTranslations: function () {

            return translations;
        },

        getSupportedLanguages: function () {

            return [
                ...SUPPORTED_LANGUAGES
            ];
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
        document.readyState ===
        "loading"
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