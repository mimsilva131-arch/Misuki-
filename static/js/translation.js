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

            statistics: {
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
                privacy_description: "Public statistics are presented in an aggregated form. Specific server and user information is restricted to authorized Misuki administrators."
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
                title: "Verification",
                subtitle: "Confirm your Discord account to get access to the server.",
                authenticated_account: "Authenticated account",
                verified_account: "Verification account",
                server: "Server",
                confirm: "Confirm verification",
                confirmed: "Verification confirmed",
                request_sent: "Your verification request was sent successfully.",
                received: "Miskui received your request.",
                processing: "The bot will process your verification and assign the appropriate role on the server.",
                return_discord: "You can return to Discord. If the role takes a few seconds to be assigned, please wait while Miskui processes your request.",
                info: "By continuing, Miskui will confirm your Discord account and send a verification request to the bot to assign your verification role.",
                footer: "Protected by Miskui"
            }
        },


        /* =====================================================
           PORTUGUÊS
           ===================================================== */

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
                copyright: "© 2026 Misuki. Todos os direitos reservados."
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

            statistics: {
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
                title: "Verificação",
                subtitle: "Confirme a sua conta Discord para obter acesso ao servidor.",
                authenticated_account: "Conta autenticada",
                verified_account: "Conta verificada",
                server: "Servidor",
                confirm: "Confirmar verificação",
                confirmed: "Verificação confirmada",
                request_sent: "O seu pedido de verificação foi enviado com sucesso.",
                received: "O Miskui recebeu o seu pedido.",
                processing: "O bot irá processar a sua verificação e atribuir o cargo correspondente no servidor.",
                return_discord: "Pode voltar ao Discord. Se a atribuição do cargo demorar alguns segundos, aguarde enquanto o Miskui processa o seu pedido.",
                info: "Ao continuar, o Miskui irá confirmar a sua conta Discord e enviar um pedido de verificação ao bot para atribuir o seu cargo de verificação.",
                footer: "Protegido por Miskui"
            }
        },


        /* =====================================================
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
                report_problem_text: "Hast du einen Fehler gefunden oder funktioniert etwas nicht korrekt? Kontaktiere das Misuki-Supportteam über Discord."
            },

            statistics: {
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
                title: "Verifizierung",
                subtitle: "Bestätigen Sie Ihr Discord-Konto, um Zugriff auf den Server zu erhalten.",
                authenticated_account: "Authentifiziertes Konto",
                verified_account: "Verifiziertes Konto",
                server: "Server",
                confirm: "Verifizierung bestätigen",
                confirmed: "Verifizierung bestätigt",
                request_sent: "Ihre Verifizierungsanfrage wurde erfolgreich gesendet.",
                received: "Miskui hat Ihre Anfrage erhalten.",
                processing: "Der Bot wird Ihre Verifizierung bearbeiten und die entsprechende Rolle auf dem Server vergeben.",
                return_discord: "Sie können zu Discord zurückkehren. Wenn die Vergabe der Rolle einige Sekunden dauert, warten Sie bitte, während Miskui Ihre Anfrage verarbeitet.",
                info: "Wenn Sie fortfahren, bestätigt Miskui Ihr Discord-Konto und sendet eine Verifizierungsanfrage an den Bot, damit Ihre Verifizierungsrolle vergeben werden kann.",
                footer: "Geschützt durch Miskui"
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
                report_problem_text: "¿Has encontrado un error o algo no funciona correctamente? Contacta con el equipo de soporte de Misuki a través de Discord."
            },

            statistics: {
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
                title: "Verificación",
                subtitle: "Confirma tu cuenta de Discord para obtener acceso al servidor.",
                authenticated_account: "Cuenta autenticada",
                verified_account: "Cuenta verificada",
                server: "Servidor",
                confirm: "Confirmar verificación",
                confirmed: "Verificación confirmada",
                request_sent: "Tu solicitud de verificación se ha enviado correctamente.",
                received: "Miskui ha recibido tu solicitud.",
                processing: "El bot procesará tu verificación y asignará el rol correspondiente en el servidor.",
                return_discord: "Puedes volver a Discord. Si el rol tarda unos segundos en asignarse, espera mientras Miskui procesa tu solicitud.",
                info: "Al continuar, Miskui confirmará tu cuenta de Discord y enviará una solicitud de verificación al bot para asignar tu rol de verificación.",
                footer: "Protegido por Miskui"
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
                report_problem_text: "Vous avez trouvé un bug ou quelque chose ne fonctionne pas correctement ? Contactez l'équipe support de Misuki via Discord."
            },

            statistics: {
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
                title: "Vérification",
                subtitle: "Confirmez votre compte Discord pour obtenir l'accès au serveur.",
                authenticated_account: "Compte authentifié",
                verified_account: "Compte vérifié",
                server: "Serveur",
                confirm: "Confirmer la vérification",
                confirmed: "Vérification confirmée",
                request_sent: "Votre demande de vérification a été envoyée avec succès.",
                received: "Miskui a reçu votre demande.",
                processing: "Le bot traitera votre vérification et attribuera le rôle correspondant sur le serveur.",
                return_discord: "Vous pouvez retourner sur Discord. Si l'attribution du rôle prend quelques secondes, veuillez patienter pendant que Miskui traite votre demande.",
                info: "En continuant, Miskui confirmera votre compte Discord et enverra une demande de vérification au bot afin d'attribuer votre rôle de vérification.",
                footer: "Protégé par Miskui"
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

        const menu =
            document.getElementById(
                "menu"
            );

        if (
            document.body.classList.contains(
                "menu-open"
            ) ||
            (
                menu &&
                (
                    menu.classList.contains(
                        "open"
                    ) ||
                    menu.classList.contains(
                        "active"
                    )
                )
            )
        ) {
            return;
        }

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

        const hamburger =
            document.getElementById(
                "hamburger"
            );

        if (hamburger) {

            hamburger.addEventListener(
                "click",
                function () {

                    closeLanguageDropdown();

                }
            );
        }

        const menu =
            document.getElementById(
                "menu"
            );

        if (!menu) {
            return;
        }

        const observer =
            new MutationObserver(
                function () {

                    if (
                        menu.classList.contains(
                            "open"
                        ) ||
                        menu.classList.contains(
                            "active"
                        ) ||
                        document.body.classList.contains(
                            "menu-open"
                        )
                    ) {

                        closeLanguageDropdown();
                    }
                }
            );

        observer.observe(
            menu,
            {
                attributes: true,
                attributeFilter: [
                    "class"
                ]
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
                attributeFilter: [
                    "class"
                ]
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