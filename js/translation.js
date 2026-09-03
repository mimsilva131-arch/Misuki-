/* =========================================================
   MISUKI — TRANSLATION.JS
   AUTOMATIC WEBSITE TRANSLATION
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       CONFIGURATION
    ===================================================== */

    const DEFAULT_LANGUAGE = "en";

    const STORAGE_KEY = "misuki_language";


    /* =====================================================
       LANGUAGES
    ===================================================== */

    const languages = {

        pt: {
            name: "Português",
            short: "PT",
            flag: "🇵🇹"
        },

        en: {
            name: "English",
            short: "EN",
            flag: "🇬🇧"
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


    /* =====================================================
       CURRENT LANGUAGE
    ===================================================== */

    let currentLanguage =
        localStorage.getItem(STORAGE_KEY) ||
        DEFAULT_LANGUAGE;


    if (!languages[currentLanguage]) {

        currentLanguage = DEFAULT_LANGUAGE;

    }


    /* =====================================================
       TRANSLATION DICTIONARY
    ===================================================== */

    const translations = {


        /* =================================================
           GENERAL / MENU
        ================================================= */

        "Menu": {
            pt: "Menu",
            en: "Menu",
            de: "Menü",
            es: "Menú",
            fr: "Menu"
        },

        "Navigation": {
            pt: "Navegação",
            en: "Navigation",
            de: "Navigation",
            es: "Navegación",
            fr: "Navigation"
        },

        "Resources": {
            pt: "Recursos",
            en: "Resources",
            de: "Ressourcen",
            es: "Recursos",
            fr: "Ressources"
        },

        "Legal": {
            pt: "Legal",
            en: "Legal",
            de: "Rechtliches",
            es: "Legal",
            fr: "Mentions légales"
        },

        "Account": {
            pt: "Conta",
            en: "Account",
            de: "Konto",
            es: "Cuenta",
            fr: "Compte"
        },

        "Administration": {
            pt: "Administração",
            en: "Administration",
            de: "Administration",
            es: "Administración",
            fr: "Administration"
        },


        /* =================================================
           NAVIGATION LINKS
        ================================================= */

        "Home": {
            pt: "Início",
            en: "Home",
            de: "Startseite",
            es: "Inicio",
            fr: "Accueil"
        },

        "Dashboard": {
            pt: "Painel",
            en: "Dashboard",
            de: "Dashboard",
            es: "Panel",
            fr: "Tableau de bord"
        },

        "Reviews": {
            pt: "Avaliações",
            en: "Reviews",
            de: "Bewertungen",
            es: "Reseñas",
            fr: "Avis"
        },

        "Statistics": {
            pt: "Estatísticas",
            en: "Statistics",
            de: "Statistiken",
            es: "Estadísticas",
            fr: "Statistiques"
        },

        "Documentation": {
            pt: "Documentação",
            en: "Documentation",
            de: "Dokumentation",
            es: "Documentación",
            fr: "Documentation"
        },

        "Support": {
            pt: "Suporte",
            en: "Support",
            de: "Support",
            es: "Soporte",
            fr: "Assistance"
        },

        "Advertisement": {
            pt: "Publicidade",
            en: "Advertisement",
            de: "Werbung",
            es: "Publicidad",
            fr: "Publicité"
        },

        "Advertise": {
            pt: "Publicitar",
            en: "Advertise",
            de: "Werben",
            es: "Publicitar",
            fr: "Faire de la publicité"
        },

        "Advertisement Admin": {
            pt: "Administração de Publicidade",
            en: "Advertisement Admin",
            de: "Werbeverwaltung",
            es: "Administración de Publicidad",
            fr: "Administration de la publicité"
        },

        "Admin Advertisement": {
            pt: "Administração de Publicidade",
            en: "Admin Advertisement",
            de: "Werbeverwaltung",
            es: "Administración de Publicidad",
            fr: "Administration de la publicité"
        },


        /* =================================================
           ACCOUNT
        ================================================= */

        "Logout": {
            pt: "Terminar sessão",
            en: "Logout",
            de: "Abmelden",
            es: "Cerrar sesión",
            fr: "Déconnexion"
        },

        "Login with Discord": {
            pt: "Iniciar sessão com Discord",
            en: "Login with Discord",
            de: "Mit Discord anmelden",
            es: "Iniciar sesión con Discord",
            fr: "Se connecter avec Discord"
        },

        "Account Dashboard": {
            pt: "Painel da Conta",
            en: "Account Dashboard",
            de: "Konto-Dashboard",
            es: "Panel de la cuenta",
            fr: "Tableau de bord du compte"
        },


        /* =================================================
           LEGAL
        ================================================= */

        "Terms": {
            pt: "Termos",
            en: "Terms",
            de: "Bedingungen",
            es: "Términos",
            fr: "Conditions"
        },

        "Privacy": {
            pt: "Privacidade",
            en: "Privacy",
            de: "Datenschutz",
            es: "Privacidad",
            fr: "Confidentialité"
        },

        "Data": {
            pt: "Dados",
            en: "Data",
            de: "Daten",
            es: "Datos",
            fr: "Données"
        },

        "Cookies": {
            pt: "Cookies",
            en: "Cookies",
            de: "Cookies",
            es: "Cookies",
            fr: "Cookies"
        },

        "Cookie Policy": {
            pt: "Política de Cookies",
            en: "Cookie Policy",
            de: "Cookie-Richtlinie",
            es: "Política de Cookies",
            fr: "Politique relative aux cookies"
        },


        /* =================================================
           FOOTER
        ================================================= */

        "Product": {
            pt: "Produto",
            en: "Product",
            de: "Produkt",
            es: "Producto",
            fr: "Produit"
        },

        "Community": {
            pt: "Comunidade",
            en: "Community",
            de: "Community",
            es: "Comunidad",
            fr: "Communauté"
        },


        /* =================================================
           COOKIE BANNER
        ================================================= */

        "Cookie consent": {
            pt: "Consentimento de Cookies",
            en: "Cookie consent",
            de: "Cookie-Einwilligung",
            es: "Consentimiento de cookies",
            fr: "Consentement aux cookies"
        },

        "🍪 We use cookies": {
            pt: "🍪 Utilizamos cookies",
            en: "🍪 We use cookies",
            de: "🍪 Wir verwenden Cookies",
            es: "🍪 Utilizamos cookies",
            fr: "🍪 Nous utilisons des cookies"
        },

        "Misuki uses cookies to improve your experience and keep the website working correctly.": {
            pt: "A Misuki utiliza cookies para melhorar a tua experiência e manter o website a funcionar corretamente.",
            en: "Misuki uses cookies to improve your experience and keep the website working correctly.",
            de: "Misuki verwendet Cookies, um deine Erfahrung zu verbessern und die Website ordnungsgemäß zu betreiben.",
            es: "Misuki utiliza cookies para mejorar tu experiencia y mantener el sitio web funcionando correctamente.",
            fr: "Misuki utilise des cookies pour améliorer votre expérience et assurer le bon fonctionnement du site."
        },

        "Accept All": {
            pt: "Aceitar Todos",
            en: "Accept All",
            de: "Alle akzeptieren",
            es: "Aceptar todos",
            fr: "Tout accepter"
        },

        "Essential Only": {
            pt: "Apenas Essenciais",
            en: "Essential Only",
            de: "Nur notwendige",
            es: "Solo esenciales",
            fr: "Essentiels uniquement"
        },

        "Deny": {
            pt: "Recusar",
            en: "Deny",
            de: "Ablehnen",
            es: "Rechazar",
            fr: "Refuser"
        },


        /* =================================================
           HOME
        ================================================= */

        "Meet Misuki.": {
            pt: "Conhece a Misuki.",
            en: "Meet Misuki.",
            de: "Lerne Misuki kennen.",
            es: "Conoce a Misuki.",
            fr: "Découvrez Misuki."
        },

        "A powerful Discord bot designed to make your server easier to manage, safer and more enjoyable.": {
            pt: "Um poderoso bot de Discord criado para tornar o teu servidor mais fácil de gerir, mais seguro e mais agradável.",
            en: "A powerful Discord bot designed to make your server easier to manage, safer and more enjoyable.",
            de: "Ein leistungsstarker Discord-Bot, der deinen Server einfacher zu verwalten, sicherer und angenehmer macht.",
            es: "Un potente bot de Discord diseñado para que tu servidor sea más fácil de gestionar, seguro y agradable.",
            fr: "Un puissant bot Discord conçu pour rendre votre serveur plus facile à gérer, plus sûr et plus agréable."
        },

        "🚀 Open Dashboard": {
            pt: "🚀 Abrir Painel",
            en: "🚀 Open Dashboard",
            de: "🚀 Dashboard öffnen",
            es: "🚀 Abrir panel",
            fr: "🚀 Ouvrir le tableau de bord"
        },

        "🔐 Login with Discord": {
            pt: "🔐 Iniciar sessão com Discord",
            en: "🔐 Login with Discord",
            de: "🔐 Mit Discord anmelden",
            es: "🔐 Iniciar sesión con Discord",
            fr: "🔐 Se connecter avec Discord"
        },

        "Why Misuki?": {
            pt: "Porquê a Misuki?",
            en: "Why Misuki?",
            de: "Warum Misuki?",
            es: "¿Por qué Misuki?",
            fr: "Pourquoi Misuki ?"
        },

        "Security": {
            pt: "Segurança",
            en: "Security",
            de: "Sicherheit",
            es: "Seguridad",
            fr: "Sécurité"
        },

        "Performance": {
            pt: "Desempenho",
            en: "Performance",
            de: "Leistung",
            es: "Rendimiento",
            fr: "Performance"
        },

        "Management": {
            pt: "Gestão",
            en: "Management",
            de: "Verwaltung",
            es: "Gestión",
            fr: "Gestion"
        },

        "No reviews yet.": {
            pt: "Ainda não existem avaliações.",
            en: "No reviews yet.",
            de: "Noch keine Bewertungen.",
            es: "Aún no hay reseñas.",
            fr: "Aucun avis pour le moment."
        },


        /* =================================================
           DASHBOARD
        ================================================= */

        "Logged in as": {
            pt: "Sessão iniciada como",
            en: "Logged in as",
            de: "Angemeldet als",
            es: "Sesión iniciada como",
            fr: "Connecté en tant que"
        },

        "🔐 Authorized Servers": {
            pt: "🔐 Servidores Autorizados",
            en: "🔐 Authorized Servers",
            de: "🔐 Autorisierte Server",
            es: "🔐 Servidores autorizados",
            fr: "🔐 Serveurs autorisés"
        },

        "License 🟢": {
            pt: "Licença 🟢",
            en: "License 🟢",
            de: "Lizenz 🟢",
            es: "Licencia 🟢",
            fr: "Licence 🟢"
        },

        "License 🔴": {
            pt: "Licença 🔴",
            en: "License 🔴",
            de: "Lizenz 🔴",
            es: "Licencia 🔴",
            fr: "Licence 🔴"
        },

        "License ⛔": {
            pt: "Licença ⛔",
            en: "License ⛔",
            de: "Lizenz ⛔",
            es: "Licencia ⛔",
            fr: "Licence ⛔"
        },

        "License ⚪": {
            pt: "Licença ⚪",
            en: "License ⚪",
            de: "Lizenz ⚪",
            es: "Licencia ⚪",
            fr: "Licence ⚪"
        },

        "⚙️ Manage": {
            pt: "⚙️ Gerir",
            en: "⚙️ Manage",
            de: "⚙️ Verwalten",
            es: "⚙️ Gestionar",
            fr: "⚙️ Gérer"
        },

        "➕ Available Servers": {
            pt: "➕ Servidores Disponíveis",
            en: "➕ Available Servers",
            de: "➕ Verfügbare Server",
            es: "➕ Servidores disponibles",
            fr: "➕ Serveurs disponibles"
        },

        "Add permission ✓": {
            pt: "Adicionar permissão ✓",
            en: "Add permission ✓",
            de: "Berechtigung hinzufügen ✓",
            es: "Añadir permiso ✓",
            fr: "Ajouter l'autorisation ✓"
        },

        "⚠️ No authorization": {
            pt: "⚠️ Sem autorização",
            en: "⚠️ No authorization",
            de: "⚠️ Keine Berechtigung",
            es: "⚠️ Sin autorización",
            fr: "⚠️ Aucune autorisation"
        },

        "➕ Add Misuki": {
            pt: "➕ Adicionar Misuki",
            en: "➕ Add Misuki",
            de: "➕ Misuki hinzufügen",
            es: "➕ Añadir Misuki",
            fr: "➕ Ajouter Misuki"
        },

        "⚠️ Cannot Add": {
            pt: "⚠️ Não é possível adicionar",
            en: "⚠️ Cannot Add",
            de: "⚠️ Hinzufügen nicht möglich",
            es: "⚠️ No se puede añadir",
            fr: "⚠️ Impossible d'ajouter"
        },

        "🔒 No authorized servers found.": {
            pt: "🔒 Não foram encontrados servidores autorizados.",
            en: "🔒 No authorized servers found.",
            de: "🔒 Keine autorisierten Server gefunden.",
            es: "🔒 No se encontraron servidores autorizados.",
            fr: "🔒 Aucun serveur autorisé trouvé."
        },

        "No additional servers available.": {
            pt: "Não existem servidores adicionais disponíveis.",
            en: "No additional servers available.",
            de: "Keine weiteren Server verfügbar.",
            es: "No hay servidores adicionales disponibles.",
            fr: "Aucun autre serveur disponible."
        },

        "⭐ Leave a Review": {
            pt: "⭐ Deixar uma Avaliação",
            en: "⭐ Leave a Review",
            de: "⭐ Bewertung abgeben",
            es: "⭐ Dejar una reseña",
            fr: "⭐ Laisser un avis"
        },


        /* =================================================
           REVIEWS
        ================================================= */

        "⭐ Misuki Reviews": {
            pt: "⭐ Avaliações da Misuki",
            en: "⭐ Misuki Reviews",
            de: "⭐ Misuki-Bewertungen",
            es: "⭐ Reseñas de Misuki",
            fr: "⭐ Avis sur Misuki"
        },

        "Reviews from members of Misuki communities.": {
            pt: "Avaliações de membros das comunidades Misuki.",
            en: "Reviews from members of Misuki communities.",
            de: "Bewertungen von Mitgliedern der Misuki-Community.",
            es: "Reseñas de miembros de las comunidades de Misuki.",
            fr: "Avis des membres des communautés Misuki."
        },

        "✍️ Write a review": {
            pt: "✍️ Escrever uma avaliação",
            en: "✍️ Write a review",
            de: "✍️ Bewertung schreiben",
            es: "✍️ Escribir una reseña",
            fr: "✍️ Écrire un avis"
        },

        "Rating": {
            pt: "Classificação",
            en: "Rating",
            de: "Bewertung",
            es: "Valoración",
            fr: "Évaluation"
        },

        "Review": {
            pt: "Avaliação",
            en: "Review",
            de: "Bewertung",
            es: "Reseña",
            fr: "Avis"
        },

        "⭐ Submit Review": {
            pt: "⭐ Enviar Avaliação",
            en: "⭐ Submit Review",
            de: "⭐ Bewertung senden",
            es: "⭐ Enviar reseña",
            fr: "⭐ Envoyer l'avis"
        },

        "💬 Community Reviews": {
            pt: "💬 Avaliações da Comunidade",
            en: "💬 Community Reviews",
            de: "💬 Community-Bewertungen",
            es: "💬 Reseñas de la comunidad",
            fr: "💬 Avis de la communauté"
        },

        "Tell us what you think about Misuki...": {
            pt: "Diz-nos o que achas da Misuki...",
            en: "Tell us what you think about Misuki...",
            de: "Sag uns, was du von Misuki hältst...",
            es: "Cuéntanos qué opinas de Misuki...",
            fr: "Dites-nous ce que vous pensez de Misuki..."
        },

        "🔒 You need an active Misuki license to write a review.": {
            pt: "🔒 Precisas de uma licença Misuki ativa para escrever uma avaliação.",
            en: "🔒 You need an active Misuki license to write a review.",
            de: "🔒 Du benötigst eine aktive Misuki-Lizenz, um eine Bewertung zu schreiben.",
            es: "🔒 Necesitas una licencia Misuki activa para escribir una reseña.",
            fr: "🔒 Vous avez besoin d'une licence Misuki active pour écrire un avis."
        },

        "🔐 Log in with Discord and have an active Misuki license to write a review.": {
            pt: "🔐 Inicia sessão com Discord e tem uma licença Misuki ativa para escrever uma avaliação.",
            en: "🔐 Log in with Discord and have an active Misuki license to write a review.",
            de: "🔐 Melde dich mit Discord an und besitze eine aktive Misuki-Lizenz, um eine Bewertung zu schreiben.",
            es: "🔐 Inicia sesión con Discord y ten una licencia Misuki activa para escribir una reseña.",
            fr: "🔐 Connectez-vous avec Discord et disposez d'une licence Misuki active pour écrire un avis."
        },


        /* =================================================
           SUPPORT
        ================================================= */

        "Get help with Misuki": {
            pt: "Obtém ajuda com a Misuki",
            en: "Get help with Misuki",
            de: "Hilfe mit Misuki erhalten",
            es: "Obtén ayuda con Misuki",
            fr: "Obtenez de l'aide avec Misuki"
        },

        "💬 Discord Support": {
            pt: "💬 Suporte no Discord",
            en: "💬 Discord Support",
            de: "💬 Discord-Support",
            es: "💬 Soporte de Discord",
            fr: "💬 Assistance Discord"
        },

        "Join the Misuki Discord server to get help, report problems, and talk with the community.": {
            pt: "Entra no servidor Discord da Misuki para obter ajuda, comunicar problemas e falar com a comunidade.",
            en: "Join the Misuki Discord server to get help, report problems, and talk with the community.",
            de: "Tritt dem Misuki-Discord-Server bei, um Hilfe zu erhalten, Probleme zu melden und mit der Community zu sprechen.",
            es: "Únete al servidor de Discord de Misuki para obtener ayuda, informar de problemas y hablar con la comunidad.",
            fr: "Rejoignez le serveur Discord de Misuki pour obtenir de l'aide, signaler des problèmes et échanger avec la communauté."
        },

        "Join Discord": {
            pt: "Entrar no Discord",
            en: "Join Discord",
            de: "Discord beitreten",
            es: "Unirse a Discord",
            fr: "Rejoindre Discord"
        },

        "📚 Documentation": {
            pt: "📚 Documentação",
            en: "📚 Documentation",
            de: "📚 Dokumentation",
            es: "📚 Documentación",
            fr: "📚 Documentation"
        },

        "Check the documentation for information about configuring and using Misuki.": {
            pt: "Consulta a documentação para obter informações sobre como configurar e utilizar a Misuki.",
            en: "Check the documentation for information about configuring and using Misuki.",
            de: "In der Dokumentation findest du Informationen zur Konfiguration und Verwendung von Misuki.",
            es: "Consulta la documentación para obtener información sobre cómo configurar y utilizar Misuki.",
            fr: "Consultez la documentation pour obtenir des informations sur la configuration et l'utilisation de Misuki."
        },

        "View Documentation": {
            pt: "Ver Documentação",
            en: "View Documentation",
            de: "Dokumentation ansehen",
            es: "Ver documentación",
            fr: "Voir la documentation"
        },

        "🐛 Report a Problem": {
            pt: "🐛 Comunicar um Problema",
            en: "🐛 Report a Problem",
            de: "🐛 Problem melden",
            es: "🐛 Informar de un problema",
            fr: "🐛 Signaler un problème"
        },

        "Found a bug or something that isn't working correctly? Contact the Misuki support team through Discord.": {
            pt: "Encontraste um erro ou algo que não está a funcionar corretamente? Contacta a equipa de suporte da Misuki através do Discord.",
            en: "Found a bug or something that isn't working correctly? Contact the Misuki support team through Discord.",
            de: "Hast du einen Fehler gefunden oder funktioniert etwas nicht richtig? Kontaktiere das Misuki-Supportteam über Discord.",
            es: "¿Has encontrado un error o algo que no funciona correctamente? Contacta con el equipo de soporte de Misuki a través de Discord.",
            fr: "Vous avez trouvé un bug ou quelque chose qui ne fonctionne pas correctement ? Contactez l'équipe d'assistance Misuki via Discord."
        },


        /* =================================================
           DOCUMENTATION
        ================================================= */

        "Learn how to configure and use Misuki in your Discord server.": {
            pt: "Aprende a configurar e utilizar a Misuki no teu servidor Discord.",
            en: "Learn how to configure and use Misuki in your Discord server.",
            de: "Erfahre, wie du Misuki auf deinem Discord-Server konfigurierst und verwendest.",
            es: "Aprende a configurar y utilizar Misuki en tu servidor de Discord.",
            fr: "Apprenez à configurer et utiliser Misuki sur votre serveur Discord."
        },

        "More documentation will be available here soon.": {
            pt: "Em breve estarão disponíveis aqui mais informações na documentação.",
            en: "More documentation will be available here soon.",
            de: "Weitere Dokumentation wird hier bald verfügbar sein.",
            es: "Próximamente habrá más documentación disponible aquí.",
            fr: "Davantage de documentation sera bientôt disponible ici."
        },


        /* =================================================
           DATA
        ================================================= */

        "Your Data": {
            pt: "Os Teus Dados",
            en: "Your Data",
            de: "Deine Daten",
            es: "Tus Datos",
            fr: "Vos données"
        },

        "Manage your Misuki data": {
            pt: "Gere os teus dados da Misuki",
            en: "Manage your Misuki data",
            de: "Verwalte deine Misuki-Daten",
            es: "Gestiona tus datos de Misuki",
            fr: "Gérez vos données Misuki"
        },

        "What Data May Be Stored?": {
            pt: "Que Dados Podem Ser Armazenados?",
            en: "What Data May Be Stored?",
            de: "Welche Daten können gespeichert werden?",
            es: "¿Qué datos pueden almacenarse?",
            fr: "Quelles données peuvent être stockées ?"
        },

        "Why Is It Stored?": {
            pt: "Porque É Armazenado?",
            en: "Why Is It Stored?",
            de: "Warum werden sie gespeichert?",
            es: "¿Por qué se almacenan?",
            fr: "Pourquoi sont-elles stockées ?"
        },

        "Requesting Your Data": {
            pt: "Solicitar os Teus Dados",
            en: "Requesting Your Data",
            de: "Deine Daten anfordern",
            es: "Solicitar tus datos",
            fr: "Demander vos données"
        },

        "Contact Support": {
            pt: "Contactar o Suporte",
            en: "Contact Support",
            de: "Support kontaktieren",
            es: "Contactar con soporte",
            fr: "Contacter l'assistance"
        },

        "Requesting Deletion": {
            pt: "Solicitar Eliminação",
            en: "Requesting Deletion",
            de: "Löschung anfordern",
            es: "Solicitar eliminación",
            fr: "Demander la suppression"
        },

        "Discord Data": {
            pt: "Dados do Discord",
            en: "Discord Data",
            de: "Discord-Daten",
            es: "Datos de Discord",
            fr: "Données Discord"
        },

        "Read Privacy Policy": {
            pt: "Ler a Política de Privacidade",
            en: "Read Privacy Policy",
            de: "Datenschutzerklärung lesen",
            es: "Leer la política de privacidad",
            fr: "Lire la politique de confidentialité"
        },


        /* =================================================
           MANAGE
        ================================================= */

        "← Back to Dashboard": {
            pt: "← Voltar ao Painel",
            en: "← Back to Dashboard",
            de: "← Zurück zum Dashboard",
            es: "← Volver al panel",
            fr: "← Retour au tableau de bord"
        },

        "🔐 License": {
            pt: "🔐 Licença",
            en: "🔐 License",
            de: "🔐 Lizenz",
            es: "🔐 Licencia",
            fr: "🔐 Licence"
        },

        "Status:": {
            pt: "Estado:",
            en: "Status:",
            de: "Status:",
            es: "Estado:",
            fr: "Statut :"
        },

        "🟢 Active": {
            pt: "🟢 Ativa",
            en: "🟢 Active",
            de: "🟢 Aktiv",
            es: "🟢 Activa",
            fr: "🟢 Active"
        },

        "🔴 Expired": {
            pt: "🔴 Expirada",
            en: "🔴 Expired",
            de: "🔴 Abgelaufen",
            es: "🔴 Expirada",
            fr: "🔴 Expirée"
        },

        "⛔ Revoked": {
            pt: "⛔ Revogada",
            en: "⛔ Revoked",
            de: "⛔ Widerrufen",
            es: "⛔ Revocada",
            fr: "⛔ Révoquée"
        },

        "License Key": {
            pt: "Chave da Licença",
            en: "License Key",
            de: "Lizenzschlüssel",
            es: "Clave de licencia",
            fr: "Clé de licence"
        },

        "Expires": {
            pt: "Expira",
            en: "Expires",
            de: "Läuft ab",
            es: "Caduca",
            fr: "Expire"
        },

        "Never": {
            pt: "Nunca",
            en: "Never",
            de: "Nie",
            es: "Nunca",
            fr: "Jamais"
        },

        "🔒 This server does not have a Misuki license.": {
            pt: "🔒 Este servidor não possui uma licença Misuki.",
            en: "🔒 This server does not have a Misuki license.",
            de: "🔒 Dieser Server besitzt keine Misuki-Lizenz.",
            es: "🔒 Este servidor no tiene una licencia Misuki.",
            fr: "🔒 Ce serveur ne possède pas de licence Misuki."
        },


        /* =================================================
           ADVERTISEMENT
        ================================================= */

        "MISUKI ADVERTISEMENT": {
            pt: "PUBLICIDADE MISUKI",
            en: "MISUKI ADVERTISEMENT",
            de: "MISUKI-WERBUNG",
            es: "PUBLICIDAD DE MISUKI",
            fr: "PUBLICITÉ MISUKI"
        },

        "Advertise your server": {
            pt: "Publicita o teu servidor",
            en: "Advertise your server",
            de: "Bewirb deinen Server",
            es: "Publicita tu servidor",
            fr: "Faites la promotion de votre serveur"
        },

        "Promote your Discord server to the Misuki community. Choose your duration and create your advertisement.": {
            pt: "Promove o teu servidor Discord junto da comunidade Misuki. Escolhe a duração e cria o teu anúncio.",
            en: "Promote your Discord server to the Misuki community. Choose your duration and create your advertisement.",
            de: "Bewirb deinen Discord-Server bei der Misuki-Community. Wähle die Dauer und erstelle deine Anzeige.",
            es: "Promociona tu servidor de Discord ante la comunidad de Misuki. Elige la duración y crea tu anuncio.",
            fr: "Faites la promotion de votre serveur Discord auprès de la communauté Misuki. Choisissez la durée et créez votre publicité."
        },

        "Advertisement title": {
            pt: "Título da publicidade",
            en: "Advertisement title",
            de: "Anzeigentitel",
            es: "Título del anuncio",
            fr: "Titre de la publicité"
        },

        "Your server name": {
            pt: "Nome do teu servidor",
            en: "Your server name",
            de: "Name deines Servers",
            es: "Nombre de tu servidor",
            fr: "Nom de votre serveur"
        },

        "Description": {
            pt: "Descrição",
            en: "Description",
            de: "Beschreibung",
            es: "Descripción",
            fr: "Description"
        },

        "Tell people what makes your server special...": {
            pt: "Diz às pessoas o que torna o teu servidor especial...",
            en: "Tell people what makes your server special...",
            de: "Erzähle den Leuten, was deinen Server besonders macht...",
            es: "Cuéntale a la gente qué hace especial a tu servidor...",
            fr: "Dites aux gens ce qui rend votre serveur spécial..."
        },

        "Image URL": {
            pt: "URL da imagem",
            en: "Image URL",
            de: "Bild-URL",
            es: "URL de imagen",
            fr: "URL de l'image"
        },

        "Destination URL": {
            pt: "URL de destino",
            en: "Destination URL",
            de: "Ziel-URL",
            es: "URL de destino",
            fr: "URL de destination"
        },

        "Advertisement duration": {
            pt: "Duração da publicidade",
            en: "Advertisement duration",
            de: "Anzeigendauer",
            es: "Duración del anuncio",
            fr: "Durée de la publicité"
        },

        "SPECIAL OFFER": {
            pt: "OFERTA ESPECIAL",
            en: "SPECIAL OFFER",
            de: "SONDERANGEBOT",
            es: "OFERTA ESPECIAL",
            fr: "OFFRE SPÉCIALE"
        },

        "Promotional prices": {
            pt: "Preços promocionais",
            en: "Promotional prices",
            de: "Aktionspreise",
            es: "Precios promocionales",
            fr: "Prix promotionnels"
        },

        "SAVE MORE": {
            pt: "POUPA MAIS",
            en: "SAVE MORE",
            de: "MEHR SPAREN",
            es: "AHORRA MÁS",
            fr: "ÉCONOMISEZ PLUS"
        },

        "7 DAYS": {
            pt: "7 DIAS",
            en: "7 DAYS",
            de: "7 TAGE",
            es: "7 DÍAS",
            fr: "7 JOURS"
        },

        "14 DAYS": {
            pt: "14 DIAS",
            en: "14 DAYS",
            de: "14 TAGE",
            es: "14 DÍAS",
            fr: "14 JOURS"
        },

        "30 DAYS": {
            pt: "30 DIAS",
            en: "30 DAYS",
            de: "30 TAGE",
            es: "30 DÍAS",
            fr: "30 JOURS"
        },

        "POPULAR": {
            pt: "POPULAR",
            en: "POPULAR",
            de: "BELIEBT",
            es: "POPULAR",
            fr: "POPULAIRE"
        },

        "Secure payment with PayPal": {
            pt: "Pagamento seguro com PayPal",
            en: "Secure payment with PayPal",
            de: "Sichere Zahlung mit PayPal",
            es: "Pago seguro con PayPal",
            fr: "Paiement sécurisé avec PayPal"
        },

        "Your payment will be securely processed through PayPal.": {
            pt: "O teu pagamento será processado de forma segura através do PayPal.",
            en: "Your payment will be securely processed through PayPal.",
            de: "Deine Zahlung wird sicher über PayPal verarbeitet.",
            es: "Tu pago se procesará de forma segura mediante PayPal.",
            fr: "Votre paiement sera traité en toute sécurité via PayPal."
        },

        "Continue to PayPal": {
            pt: "Continuar para o PayPal",
            en: "Continue to PayPal",
            de: "Weiter zu PayPal",
            es: "Continuar a PayPal",
            fr: "Continuer vers PayPal"
        },

        "Your advertisement will be reviewed and activated after successful payment.": {
            pt: "A tua publicidade será analisada e ativada após um pagamento bem-sucedido.",
            en: "Your advertisement will be reviewed and activated after successful payment.",
            de: "Deine Anzeige wird nach erfolgreicher Zahlung geprüft und aktiviert.",
            es: "Tu anuncio será revisado y activado después de un pago exitoso.",
            fr: "Votre publicité sera examinée et activée après un paiement réussi."
        },


        /* =================================================
           ADVERTISEMENT ADMIN
        ================================================= */

        "Advertisement Management": {
            pt: "Gestão de Publicidade",
            en: "Advertisement Management",
            de: "Werbeverwaltung",
            es: "Gestión de Publicidad",
            fr: "Gestion de la publicité"
        },

        "User ID:": {
            pt: "ID do utilizador:",
            en: "User ID:",
            de: "Benutzer-ID:",
            es: "ID de usuario:",
            fr: "ID utilisateur :"
        },

        "Duration:": {
            pt: "Duração:",
            en: "Duration:",
            de: "Dauer:",
            es: "Duración:",
            fr: "Durée :"
        },

        "days": {
            pt: "dias",
            en: "days",
            de: "Tage",
            es: "días",
            fr: "jours"
        },

        "Pending": {
            pt: "Pendente",
            en: "Pending",
            de: "Ausstehend",
            es: "Pendiente",
            fr: "En attente"
        },

        "Active": {
            pt: "Ativo",
            en: "Active",
            de: "Aktiv",
            es: "Activo",
            fr: "Actif"
        },

        "Rejected": {
            pt: "Rejeitado",
            en: "Rejected",
            de: "Abgelehnt",
            es: "Rechazado",
            fr: "Rejeté"
        },

        "Expired": {
            pt: "Expirado",
            en: "Expired",
            de: "Abgelaufen",
            es: "Expirado",
            fr: "Expiré"
        },

        "Disabled": {
            pt: "Desativado",
            en: "Disabled",
            de: "Deaktiviert",
            es: "Desactivado",
            fr: "Désactivé"
        },

        "Start:": {
            pt: "Início:",
            en: "Start:",
            de: "Start:",
            es: "Inicio:",
            fr: "Début :"
        },

        "End:": {
            pt: "Fim:",
            en: "End:",
            de: "Ende:",
            es: "Fin:",
            fr: "Fin :"
        },

        "Rejection reason:": {
            pt: "Motivo da rejeição:",
            en: "Rejection reason:",
            de: "Ablehnungsgrund:",
            es: "Motivo del rechazo:",
            fr: "Motif du rejet :"
        },

        "Open": {
            pt: "Abrir",
            en: "Open",
            de: "Öffnen",
            es: "Abrir",
            fr: "Ouvrir"
        },

        "Approve": {
            pt: "Aprovar",
            en: "Approve",
            de: "Genehmigen",
            es: "Aprobar",
            fr: "Approuver"
        },

        "Reason for rejection (optional)": {
            pt: "Motivo da rejeição (opcional)",
            en: "Reason for rejection (optional)",
            de: "Ablehnungsgrund (optional)",
            es: "Motivo del rechazo (opcional)",
            fr: "Motif du rejet (facultatif)"
        },

        "Reject": {
            pt: "Rejeitar",
            en: "Reject",
            de: "Ablehnen",
            es: "Rechazar",
            fr: "Rejeter"
        },

        "Disable": {
            pt: "Desativar",
            en: "Disable",
            de: "Deaktivieren",
            es: "Desactivar",
            fr: "Désactiver"
        },

        "No advertisements yet.": {
            pt: "Ainda não existem anúncios.",
            en: "No advertisements yet.",
            de: "Noch keine Anzeigen vorhanden.",
            es: "Aún no hay anuncios.",
            fr: "Aucune publicité pour le moment."
        },


        /* =================================================
           ADVERTISEMENT SUCCESS
        ================================================= */

        "✅ Advertisement Submitted": {
            pt: "✅ Publicidade Enviada",
            en: "✅ Advertisement Submitted",
            de: "✅ Anzeige eingereicht",
            es: "✅ Anuncio enviado",
            fr: "✅ Publicité envoyée"
        },

        "Your advertisement was sent successfully.": {
            pt: "A tua publicidade foi enviada com sucesso.",
            en: "Your advertisement was sent successfully.",
            de: "Deine Anzeige wurde erfolgreich gesendet.",
            es: "Tu anuncio se ha enviado correctamente.",
            fr: "Votre publicité a été envoyée avec succès."
        },

        "It is now pending review by the Misuki team. We will review it and decide whether it should be approved or rejected.": {
            pt: "Está agora pendente de análise pela equipa Misuki. Iremos analisá-la e decidir se deve ser aprovada ou rejeitada.",
            en: "It is now pending review by the Misuki team. We will review it and decide whether it should be approved or rejected.",
            de: "Sie wartet nun auf die Prüfung durch das Misuki-Team. Wir werden sie prüfen und entscheiden, ob sie genehmigt oder abgelehnt wird.",
            es: "Ahora está pendiente de revisión por el equipo de Misuki. La revisaremos y decidiremos si debe aprobarse o rechazarse.",
            fr: "Elle est maintenant en attente d'examen par l'équipe Misuki. Nous l'examinerons et déciderons si elle doit être approuvée ou rejetée."
        },

        "Submit another": {
            pt: "Enviar outra",
            en: "Submit another",
            de: "Eine weitere einreichen",
            es: "Enviar otra",
            fr: "En envoyer une autre"
        },


        /* =================================================
           PAYMENT
        ================================================= */

        "Payment Cancelled": {
            pt: "Pagamento Cancelado",
            en: "Payment Cancelled",
            de: "Zahlung abgebrochen",
            es: "Pago cancelado",
            fr: "Paiement annulé"
        },

        "The payment was not completed.": {
            pt: "O pagamento não foi concluído.",
            en: "The payment was not completed.",
            de: "Die Zahlung wurde nicht abgeschlossen.",
            es: "El pago no se completó.",
            fr: "Le paiement n'a pas été effectué."
        },

        "Return": {
            pt: "Voltar",
            en: "Return",
            de: "Zurück",
            es: "Volver",
            fr: "Retour"
        },

        "✅ Payment Successful": {
            pt: "✅ Pagamento Concluído",
            en: "✅ Payment Successful",
            de: "✅ Zahlung erfolgreich",
            es: "✅ Pago realizado",
            fr: "✅ Paiement réussi"
        },

        "Your payment was confirmed.": {
            pt: "O teu pagamento foi confirmado.",
            en: "Your payment was confirmed.",
            de: "Deine Zahlung wurde bestätigt.",
            es: "Tu pago ha sido confirmado.",
            fr: "Votre paiement a été confirmé."
        },

        "Your advertisement will be processed in accordance with Misuki rules.": {
            pt: "A tua publicidade será processada de acordo com as regras da Misuki.",
            en: "Your advertisement will be processed in accordance with Misuki rules.",
            de: "Deine Anzeige wird gemäß den Misuki-Regeln verarbeitet.",
            es: "Tu anuncio será procesado de acuerdo con las normas de Misuki.",
            fr: "Votre publicité sera traitée conformément aux règles de Misuki."
        },

        "Return to dashboard": {
            pt: "Voltar ao painel",
            en: "Return to dashboard",
            de: "Zum Dashboard zurückkehren",
            es: "Volver al panel",
            fr: "Retourner au tableau de bord"
        },


        /* =================================================
           STATISTICS
        ================================================= */

        "Overview of the Misuki service and its current statistics.": {
            pt: "Visão geral do serviço Misuki e das suas estatísticas atuais.",
            en: "Overview of the Misuki service and its current statistics.",
            de: "Übersicht über den Misuki-Dienst und seine aktuellen Statistiken.",
            es: "Resumen del servicio Misuki y sus estadísticas actuales.",
            fr: "Aperçu du service Misuki et de ses statistiques actuelles."
        },

        "Servers": {
            pt: "Servidores",
            en: "Servers",
            de: "Server",
            es: "Servidores",
            fr: "Serveurs"
        },

        "Servers currently using Misuki.": {
            pt: "Servidores que utilizam atualmente a Misuki.",
            en: "Servers currently using Misuki.",
            de: "Server, die Misuki derzeit verwenden.",
            es: "Servidores que utilizan actualmente Misuki.",
            fr: "Serveurs utilisant actuellement Misuki."
        },

        "Users": {
            pt: "Utilizadores",
            en: "Users",
            de: "Benutzer",
            es: "Usuarios",
            fr: "Utilisateurs"
        },

        "Users reached by Misuki.": {
            pt: "Utilizadores alcançados pela Misuki.",
            en: "Users reached by Misuki.",
            de: "Benutzer, die von Misuki erreicht werden.",
            es: "Usuarios alcanzados por Misuki.",
            fr: "Utilisateurs atteints par Misuki."
        },

        "Active Licenses": {
            pt: "Licenças Ativas",
            en: "Active Licenses",
            de: "Aktive Lizenzen",
            es: "Licencias Activas",
            fr: "Licences actives"
        },

        "Currently active Misuki licenses.": {
            pt: "Licenças Misuki atualmente ativas.",
            en: "Currently active Misuki licenses.",
            de: "Derzeit aktive Misuki-Lizenzen.",
            es: "Licencias Misuki actualmente activas.",
            fr: "Licences Misuki actuellement actives."
        },

        "Reviews submitted by the community.": {
            pt: "Avaliações enviadas pela comunidade.",
            en: "Reviews submitted by the community.",
            de: "Von der Community eingereichte Bewertungen.",
            es: "Reseñas enviadas por la comunidad.",
            fr: "Avis envoyés par la communauté."
        },

        "Active Advertisements": {
            pt: "Publicidade Ativa",
            en: "Active Advertisements",
            de: "Aktive Anzeigen",
            es: "Anuncios Activos",
            fr: "Publicités actives"
        },

        "Advertisements currently active.": {
            pt: "Publicidade atualmente ativa.",
            en: "Advertisements currently active.",
            de: "Derzeit aktive Anzeigen.",
            es: "Anuncios actualmente activos.",
            fr: "Publicités actuellement actives."
        },

        "Commands": {
            pt: "Comandos",
            en: "Commands",
            de: "Befehle",
            es: "Comandos",
            fr: "Commandes"
        },

        "Commands available through Misuki.": {
            pt: "Comandos disponíveis através da Misuki.",
            en: "Commands available through Misuki.",
            de: "Über Misuki verfügbare Befehle.",
            es: "Comandos disponibles a través de Misuki.",
            fr: "Commandes disponibles via Misuki."
        },

        "Uptime": {
            pt: "Tempo de atividade",
            en: "Uptime",
            de: "Betriebszeit",
            es: "Tiempo de actividad",
            fr: "Temps de fonctionnement"
        },

        "Current Misuki uptime.": {
            pt: "Tempo de atividade atual da Misuki.",
            en: "Current Misuki uptime.",
            de: "Aktuelle Betriebszeit von Misuki.",
            es: "Tiempo de actividad actual de Misuki.",
            fr: "Temps de fonctionnement actuel de Misuki."
        },

        "System Status": {
            pt: "Estado do Sistema",
            en: "System Status",
            de: "Systemstatus",
            es: "Estado del sistema",
            fr: "État du système"
        },

        "Current status of the Misuki service.": {
            pt: "Estado atual do serviço Misuki.",
            en: "Current status of the Misuki service.",
            de: "Aktueller Status des Misuki-Dienstes.",
            es: "Estado actual del servicio Misuki.",
            fr: "État actuel du service Misuki."
        },

        "Operational": {
            pt: "Operacional",
            en: "Operational",
            de: "Betriebsbereit",
            es: "Operativo",
            fr: "Opérationnel"
        },

        "📈 System Overview": {
            pt: "📈 Visão Geral do Sistema",
            en: "📈 System Overview",
            de: "📈 Systemübersicht",
            es: "📈 Resumen del sistema",
            fr: "📈 Vue d’ensemble du système"
        },

        "More detailed statistics and historical data will be available here in the future.": {
            pt: "Estatísticas mais detalhadas e dados históricos estarão disponíveis aqui no futuro.",
            en: "More detailed statistics and historical data will be available here in the future.",
            de: "Detailliertere Statistiken und historische Daten werden hier künftig verfügbar sein.",
            es: "En el futuro habrá estadísticas más detalladas y datos históricos disponibles aquí.",
            fr: "Des statistiques plus détaillées et des données historiques seront disponibles ici à l’avenir."
        },

        "Server Growth": {
            pt: "Crescimento de Servidores",
            en: "Server Growth",
            de: "Serverwachstum",
            es: "Crecimiento de servidores",
            fr: "Croissance des serveurs"
        },

        "User Growth": {
            pt: "Crescimento de Utilizadores",
            en: "User Growth",
            de: "Benutzerwachstum",
            es: "Crecimiento de usuarios",
            fr: "Croissance des utilisateurs"
        },

        "Commands Used": {
            pt: "Comandos Utilizados",
            en: "Commands Used",
            de: "Verwendete Befehle",
            es: "Comandos utilizados",
            fr: "Commandes utilisées"
        },

        "Service Health": {
            pt: "Estado do Serviço",
            en: "Service Health",
            de: "Dienststatus",
            es: "Estado del servicio",
            fr: "État du service"
        },

        "🔐 Admin Statistics": {
            pt: "🔐 Estatísticas de Administrador",
            en: "🔐 Admin Statistics",
            de: "🔐 Administrator-Statistiken",
            es: "🔐 Estadísticas de administrador",
            fr: "🔐 Statistiques administrateur"
        },

        "Detailed Misuki statistics available only to authorized administrators.": {
            pt: "Estatísticas detalhadas da Misuki disponíveis apenas para administradores autorizados.",
            en: "Detailed Misuki statistics available only to authorized administrators.",
            de: "Detaillierte Misuki-Statistiken sind nur für autorisierte Administratoren verfügbar.",
            es: "Estadísticas detalladas de Misuki disponibles solo para administradores autorizados.",
            fr: "Statistiques détaillées de Misuki disponibles uniquement pour les administrateurs autorisés."
        },

        "Total Servers": {
            pt: "Total de Servidores",
            en: "Total Servers",
            de: "Server insgesamt",
            es: "Total de servidores",
            fr: "Total des serveurs"
        },

        "Total Users": {
            pt: "Total de Utilizadores",
            en: "Total Users",
            de: "Benutzer insgesamt",
            es: "Total de usuarios",
            fr: "Total des utilisateurs"
        },

        "Total Reviews": {
            pt: "Total de Avaliações",
            en: "Total Reviews",
            de: "Bewertungen insgesamt",
            es: "Total de reseñas",
            fr: "Total des avis"
        },

        "Server Details": {
            pt: "Detalhes dos Servidores",
            en: "Server Details",
            de: "Serverdetails",
            es: "Detalles de los servidores",
            fr: "Détails des serveurs"
        },

        "Server": {
            pt: "Servidor",
            en: "Server",
            de: "Server",
            es: "Servidor",
            fr: "Serveur"
        },

        "Server ID": {
            pt: "ID do Servidor",
            en: "Server ID",
            de: "Server-ID",
            es: "ID del servidor",
            fr: "ID du serveur"
        },

        "Members": {
            pt: "Membros",
            en: "Members",
            de: "Mitglieder",
            es: "Miembros",
            fr: "Membres"
        },

        "License": {
            pt: "Licença",
            en: "License",
            de: "Lizenz",
            es: "Licencia",
            fr: "Licence"
        },

        "No server details available.": {
            pt: "Não existem detalhes de servidores disponíveis.",
            en: "No server details available.",
            de: "Keine Serverdetails verfügbar.",
            es: "No hay detalles de servidores disponibles.",
            fr: "Aucun détail de serveur disponible."
        },

        "Detailed Statistics": {
            pt: "Estatísticas Detalhadas",
            en: "Detailed Statistics",
            de: "Detaillierte Statistiken",
            es: "Estadísticas detalladas",
            fr: "Statistiques détaillées"
        },

        "Servers With License": {
            pt: "Servidores Com Licença",
            en: "Servers With License",
            de: "Server mit Lizenz",
            es: "Servidores con licencia",
            fr: "Serveurs avec licence"
        },

        "Servers Without License": {
            pt: "Servidores Sem Licença",
            en: "Servers Without License",
            de: "Server ohne Lizenz",
            es: "Servidores ohne Lizenz",
            fr: "Serveurs sans licence"
        },

        "Expired Licenses": {
            pt: "Licenças Expiradas",
            en: "Expired Licenses",
            de: "Abgelaufene Lizenzen",
            es: "Licencias expiradas",
            fr: "Licences expirées"
        },

        "Pending Advertisements": {
            pt: "Publicidade Pendente",
            en: "Pending Advertisements",
            de: "Ausstehende Anzeigen",
            es: "Anuncios pendientes",
            fr: "Publicités en attente"
        },


        /* =================================================
           ERROR
        ================================================= */

        "Error": {
            pt: "Erro",
            en: "Error",
            de: "Fehler",
            es: "Error",
            fr: "Erreur"
        },

        "Something went wrong": {
            pt: "Ocorreu um erro",
            en: "Something went wrong",
            de: "Etwas ist schiefgelaufen",
            es: "Algo salió mal",
            fr: "Une erreur s'est produite"
        },

        "Return Home": {
            pt: "Voltar ao Início",
            en: "Return Home",
            de: "Zur Startseite",
            es: "Volver al inicio",
            fr: "Retour à l'accueil"
        },

        "Try Login Again": {
            pt: "Tentar iniciar sessão novamente",
            en: "Try Login Again",
            de: "Erneut anmelden",
            es: "Intentar iniciar sesión de nuevo",
            fr: "Réessayer de se connecter"
        },


        /* =================================================
           ADMIN ADVERTISEMENT EXTRA
        ================================================= */

        "User ID": {
            pt: "ID do utilizador",
            en: "User ID",
            de: "Benutzer-ID",
            es: "ID de usuario",
            fr: "ID utilisateur"
        },


        /* =================================================
           PRIVACY / TERMS / COOKIES
        ================================================= */

        "Privacy Policy": {
            pt: "Política de Privacidade",
            en: "Privacy Policy",
            de: "Datenschutzerklärung",
            es: "Política de privacidad",
            fr: "Politique de confidentialité"
        },

        "Terms of Service": {
            pt: "Termos de Serviço",
            en: "Terms of Service",
            de: "Nutzungsbedingungen",
            es: "Términos de servicio",
            fr: "Conditions d'utilisation"
        },

        "Last updated: August 2026": {
            pt: "Última atualização: agosto de 2026",
            en: "Last updated: August 2026",
            de: "Zuletzt aktualisiert: August 2026",
            es: "Última actualización: agosto de 2026",
            fr: "Dernière mise à jour : août 2026"
        },

        "Cookie Policy": {
            pt: "Política de Cookies",
            en: "Cookie Policy",
            de: "Cookie-Richtlinie",
            es: "Política de Cookies",
            fr: "Politique relative aux cookies"
        },

        "1. What Are Cookies?": {
            pt: "1. O Que São Cookies?",
            en: "1. What Are Cookies?",
            de: "1. Was sind Cookies?",
            es: "1. ¿Qué son las cookies?",
            fr: "1. Que sont les cookies ?"
        },

        "2. How Misuki Uses Cookies": {
            pt: "2. Como a Misuki Utiliza Cookies",
            en: "2. How Misuki Uses Cookies",
            de: "2. Wie Misuki Cookies verwendet",
            es: "2. Cómo utiliza Misuki las cookies",
            fr: "2. Comment Misuki utilise les cookies"
        },

        "3. Your Choices": {
            pt: "3. As Tuas Escolhas",
            en: "3. Your Choices",
            de: "3. Deine Auswahl",
            es: "3. Tus opciones",
            fr: "3. Vos choix"
        },

        "4. Contact": {
            pt: "4. Contacto",
            en: "4. Contact",
            de: "4. Kontakt",
            es: "4. Contacto",
            fr: "4. Contact"
        }

    };


    /* =====================================================
       SPECIAL TEXT TRANSLATIONS
    ===================================================== */

    const pageTranslations = {


        /* =================================================
           PRIVACY POLICY
        ================================================= */

        "This Privacy Policy explains how Misuki collects, uses, stores and protects information when you use our services.": {
            pt: "Esta Política de Privacidade explica como a Misuki recolhe, utiliza, armazena e protege informações quando utilizas os nossos serviços.",
            en: "This Privacy Policy explains how Misuki collects, uses, stores and protects information when you use our services.",
            de: "Diese Datenschutzerklärung erklärt, wie Misuki Informationen sammelt, verwendet, speichert und schützt, wenn du unsere Dienste nutzt.",
            es: "Esta Política de Privacidad explica cómo Misuki recopila, utiliza, almacena y protege la información cuando utilizas nuestros servicios.",
            fr: "Cette Politique de confidentialité explique comment Misuki collecte, utilise, stocke et protège les informations lorsque vous utilisez nos services."
        },

        "Misuki does not sell personal information.": {
            pt: "A Misuki não vende informações pessoais.",
            en: "Misuki does not sell personal information.",
            de: "Misuki verkauft keine personenbezogenen Daten.",
            es: "Misuki no vende información personal.",
            fr: "Misuki ne vend pas d'informations personnelles."
        },

        "Misuki does not receive or store your Discord password.": {
            pt: "A Misuki não recebe nem armazena a tua palavra-passe do Discord.",
            en: "Misuki does not receive or store your Discord password.",
            de: "Misuki erhält oder speichert dein Discord-Passwort nicht.",
            es: "Misuki no recibe ni almacena tu contraseña de Discord.",
            fr: "Misuki ne reçoit ni ne stocke votre mot de passe Discord."
        },


        /* =================================================
           COMMON COOKIE TEXT
        ================================================= */

        "Cookies are small pieces of data stored by your browser when you visit a website. They can be used to remember information between requests and maintain sessions.": {
            pt: "Os cookies são pequenos dados armazenados pelo teu navegador quando visitas um website. Podem ser utilizados para guardar informações entre pedidos e manter sessões.",
            en: "Cookies are small pieces of data stored by your browser when you visit a website. They can be used to remember information between requests and maintain sessions.",
            de: "Cookies sind kleine Datenmengen, die dein Browser beim Besuch einer Website speichert. Sie können verwendet werden, um Informationen zwischen Anfragen zu speichern und Sitzungen aufrechtzuerhalten.",
            es: "Las cookies son pequeños datos almacenados por tu navegador cuando visitas un sitio web. Pueden utilizarse para recordar información entre solicitudes y mantener sesiones.",
            fr: "Les cookies sont de petites données stockées par votre navigateur lorsque vous visitez un site web. Ils peuvent être utilisés pour mémoriser des informations entre les requêtes et maintenir les sessions."
        }

    };


    /* =====================================================
       MERGE DICTIONARIES
    ===================================================== */

    Object.assign(
        translations,
        pageTranslations
    );


    /* =====================================================
       PROTECTED ELEMENTS
       
       These elements contain dynamic/server-generated
       information and should never be translated.
    ===================================================== */

    function isProtectedElement(element) {

        if (!element) {
            return true;
        }

        if (
            element.matches(
                "[data-no-translate], .no-translate"
            )
        ) {
            return true;
        }

        if (
            element.closest(
                "[data-no-translate], .no-translate"
            )
        ) {
            return true;
        }

        return false;
    }


    /* =====================================================
       FIND TRANSLATION
    ===================================================== */

    function getTranslation(text) {

        if (!text) {
            return null;
        }

        const cleanText = text.trim();

        if (!cleanText) {
            return null;
        }

        const entry =
            translations[cleanText];

        if (!entry) {
            return null;
        }

        return entry[currentLanguage] || cleanText;

    }


    /* =====================================================
       TRANSLATE TEXT NODES
    ===================================================== */

    function translateTextNodes(root) {

        const walker =
            document.createTreeWalker(
                root,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: function (node) {

                        const parent =
                            node.parentElement;

                        if (!parent) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        if (
                            isProtectedElement(parent)
                        ) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        const tag =
                            parent.tagName.toLowerCase();

                        if (
                            tag === "script" ||
                            tag === "style" ||
                            tag === "noscript" ||
                            tag === "template"
                        ) {
                            return NodeFilter.FILTER_REJECT;
                        }

                        return NodeFilter.FILTER_ACCEPT;

                    }
                }
            );


        const nodes = [];

        let node;

        while (
            (node = walker.nextNode())
        ) {

            nodes.push(node);

        }


        nodes.forEach(function (textNode) {

            const original =
                textNode.nodeValue;

            const translated =
                getTranslation(original);

            if (!translated) {
                return;
            }


            const leading =
                original.match(/^\s*/)?.[0] || "";

            const trailing =
                original.match(/\s*$/)?.[0] || "";


            textNode.nodeValue =
                leading +
                translated +
                trailing;

        });

    }


    /* =====================================================
       TRANSLATE ATTRIBUTES
    ===================================================== */

    function translateAttributes() {

        const elements =
            document.querySelectorAll(
                "input, textarea, button, img, [title], [aria-label], [placeholder]"
            );


        elements.forEach(function (element) {

            if (
                isProtectedElement(element)
            ) {
                return;
            }


            /* =============================================
               PLACEHOLDER
            ============================================= */

            if (
                element.hasAttribute(
                    "placeholder"
                )
            ) {

                const original =
                    element.getAttribute(
                        "placeholder"
                    );

                const translated =
                    getTranslation(original);

                if (translated) {

                    element.setAttribute(
                        "placeholder",
                        translated
                    );

                }

            }


            /* =============================================
               TITLE
            ============================================= */

            if (
                element.hasAttribute(
                    "title"
                )
            ) {

                const original =
                    element.getAttribute(
                        "title"
                    );

                const translated =
                    getTranslation(original);

                if (translated) {

                    element.setAttribute(
                        "title",
                        translated
                    );

                }

            }


            /* =============================================
               ARIA LABEL
            ============================================= */

            if (
                element.hasAttribute(
                    "aria-label"
                )
            ) {

                const original =
                    element.getAttribute(
                        "aria-label"
                    );

                const translated =
                    getTranslation(original);

                if (translated) {

                    element.setAttribute(
                        "aria-label",
                        translated
                    );

                }

            }

        });

    }


    /* =====================================================
       TRANSLATE PAGE TITLE
    ===================================================== */

    function translatePageTitle() {

        if (!document.title) {
            return;
        }


        const original =
            document.title;


        const parts =
            original.split(" — ");


        if (
            parts.length === 2
        ) {

            const translatedMain =
                getTranslation(
                    parts[0]
                );


            if (translatedMain) {

                document.title =
                    translatedMain +
                    " — " +
                    parts[1];

            }

        }

    }


    /* =====================================================
       TRANSLATE DOCUMENT
    ===================================================== */

    function translatePage() {

        translateTextNodes(
            document.body
        );

        translateAttributes();

        translatePageTitle();

    }


    /* =====================================================
       LANGUAGE SELECTOR
    ===================================================== */

    function createSelector() {

        const hamburger =
            document.querySelector(
                ".hamburger"
            );


        if (!hamburger) {
            return;
        }


        if (
            document.getElementById(
                "misukiLanguage"
            )
        ) {
            return;
        }


        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.className =
            "misuki-language";

        wrapper.id =
            "misukiLanguage";


        /* =============================================
           BUTTON
        ============================================= */

        const button =
            document.createElement(
                "button"
            );

        button.type =
            "button";

        button.className =
            "misuki-language-button";

        button.setAttribute(
            "aria-label",
            "Change language"
        );

        button.setAttribute(
            "aria-expanded",
            "false"
        );


        const flag =
            document.createElement(
                "span"
            );

        flag.className =
            "misuki-language-flag";


        const short =
            document.createElement(
                "span"
            );

        short.className =
            "misuki-language-short";


        const arrow =
            document.createElement(
                "span"
            );

        arrow.className =
            "misuki-language-arrow";

        arrow.textContent =
            "⌄";


        button.appendChild(flag);
        button.appendChild(short);
        button.appendChild(arrow);


        /* =============================================
           DROPDOWN
        ============================================= */

        const dropdown =
            document.createElement(
                "div"
            );

        dropdown.className =
            "misuki-language-dropdown";

        dropdown.setAttribute(
            "aria-hidden",
            "true"
        );


        Object.keys(
            languages
        ).forEach(function (code) {

            const language =
                languages[code];


            const option =
                document.createElement(
                    "button"
                );

            option.type =
                "button";

            option.className =
                "misuki-language-option";

            option.dataset.language =
                code;


            const optionFlag =
                document.createElement(
                    "span"
                );

            optionFlag.className =
                "misuki-language-option-flag";

            optionFlag.textContent =
                language.flag;


            const optionName =
                document.createElement(
                    "span"
                );

            optionName.className =
                "misuki-language-option-name";

            optionName.textContent =
                language.name;


            option.appendChild(
                optionFlag
            );

            option.appendChild(
                optionName
            );


            option.addEventListener(
                "click",
                function () {

                    setLanguage(
                        code
                    );

                }
            );


            dropdown.appendChild(
                option
            );

        });


        /* =============================================
           OPEN / CLOSE
        ============================================= */

        button.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                const open =
                    wrapper.classList.toggle(
                        "open"
                    );


                button.setAttribute(
                    "aria-expanded",
                    open
                        ? "true"
                        : "false"
                );


                dropdown.setAttribute(
                    "aria-hidden",
                    open
                        ? "false"
                        : "true"
                );

            }
        );


        document.addEventListener(
            "click",
            function (event) {

                if (
                    !wrapper.contains(
                        event.target
                    )
                ) {

                    wrapper.classList.remove(
                        "open"
                    );

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                    dropdown.setAttribute(
                        "aria-hidden",
                        "true"
                    );

                }

            }
        );


        /* =============================================
           BUILD
        ============================================= */

        wrapper.appendChild(
            button
        );

        wrapper.appendChild(
            dropdown
        );


        /*
         * Put language selector immediately
         * before the hamburger.
         *
         * Result:
         *
         * 🇬🇧 EN ▼   ☰
         */

        hamburger.parentNode.insertBefore(
            wrapper,
            hamburger
        );


        updateSelector();

    }


    /* =====================================================
       UPDATE SELECTOR
    ===================================================== */

    function updateSelector() {

        const wrapper =
            document.getElementById(
                "misukiLanguage"
            );


        if (!wrapper) {
            return;
        }


        const language =
            languages[currentLanguage];


        const flag =
            wrapper.querySelector(
                ".misuki-language-flag"
            );


        const short =
            wrapper.querySelector(
                ".misuki-language-short"
            );


        if (flag) {

            flag.textContent =
                language.flag;

        }


        if (short) {

            short.textContent =
                language.short;

        }


        wrapper
            .querySelectorAll(
                ".misuki-language-option"
            )
            .forEach(function (option) {

                option.classList.toggle(
                    "active",
                    option.dataset.language ===
                    currentLanguage
                );

            });

    }


    /* =====================================================
       SET LANGUAGE
    ===================================================== */

    function setLanguage(
        language
    ) {

        if (
            !languages[language]
        ) {
            return;
        }


        currentLanguage =
            language;


        localStorage.setItem(
            STORAGE_KEY,
            language
        );


        /*
         * Reloading ensures that the automatic
         * translation starts from the original
         * English text instead of translating
         * an already translated string.
         */

        window.location.reload();

    }


    /* =====================================================
       OBSERVER
       
       Useful for dynamically generated content.
    ===================================================== */

    function observeDynamicContent() {

        const observer =
            new MutationObserver(
                function (mutations) {

                    let shouldTranslate =
                        false;


                    mutations.forEach(
                        function (mutation) {

                            if (
                                mutation.type ===
                                "childList"
                            ) {

                                shouldTranslate =
                                    true;

                            }

                        }
                    );


                    if (
                        shouldTranslate
                    ) {

                        translateTextNodes(
                            document.body
                        );

                        translateAttributes();

                    }

                }
            );


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );

    }


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.MisukiTranslation = {

        setLanguage: setLanguage,

        getLanguage: function () {

            return currentLanguage;

        },

        getLanguages: function () {

            return languages;

        },

        translate: translatePage

    };


    /* =====================================================
       INITIALIZATION
    ===================================================== */

    function init() {

        createSelector();

        translatePage();

        updateSelector();

        observeDynamicContent();


        console.log(
            "🌐 Misuki translation initialized:",
            currentLanguage
        );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            init
        );

    } else {

        init();

    }


})();