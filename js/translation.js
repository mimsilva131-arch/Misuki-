/* =========================================================
   MISUKI — TRANSLATION.JS
   LANGUAGE SYSTEM
========================================================= */

(function () {

    "use strict";


    /* =====================================================
       AVAILABLE LANGUAGES
    ===================================================== */

    const languages = {

        pt: {
            name: "Português",
            flag: "🇵🇹"
        },

        en: {
            name: "English",
            flag: "🇬🇧"
        },

        de: {
            name: "Deutsch",
            flag: "🇩🇪"
        },

        es: {
            name: "Español",
            flag: "🇪🇸"
        },

        fr: {
            name: "Français",
            flag: "🇫🇷"
        }

    };


    /* =====================================================
       TRANSLATIONS
    ===================================================== */

    const translations = {

        pt: {

            menu: "Menu",

            navigation: "Navegação",
            resources: "Recursos",
            legal: "Legal",
            account: "Conta",

            home: "Início",
            dashboard: "Painel",
            reviews: "Avaliações",

            documentation: "Documentação",
            support: "Suporte",
            advertisement: "Publicidade",
            advertisementAdmin: "Administração de publicidade",

            terms: "Termos",
            privacy: "Privacidade",
            data: "Dados",
            cookies: "Cookies",

            login: "Entrar com Discord",
            logout: "Sair",

            language: "Idioma",

            close: "Fechar",
            open: "Abrir menu",

            cookieTitle: "🍪 Usamos cookies",
            cookieText:
                "A Misuki utiliza cookies para melhorar a tua experiência e manter o website a funcionar corretamente.",

            acceptAll: "Aceitar todos",
            essentialOnly: "Apenas essenciais",
            deny: "Recusar",

            cookiePolicy: "Política de Cookies"

        },


        en: {

            menu: "Menu",

            navigation: "Navigation",
            resources: "Resources",
            legal: "Legal",
            account: "Account",

            home: "Home",
            dashboard: "Dashboard",
            reviews: "Reviews",

            documentation: "Documentation",
            support: "Support",
            advertisement: "Advertisement",
            advertisementAdmin: "Advertisement Admin",

            terms: "Terms",
            privacy: "Privacy",
            data: "Data",
            cookies: "Cookies",

            login: "Login with Discord",
            logout: "Logout",

            language: "Language",

            close: "Close",
            open: "Open menu",

            cookieTitle: "🍪 We use cookies",
            cookieText:
                "Misuki uses cookies to improve your experience and keep the website working correctly.",

            acceptAll: "Accept All",
            essentialOnly: "Essential Only",
            deny: "Deny",

            cookiePolicy: "Cookie Policy"

        },


        de: {

            menu: "Menü",

            navigation: "Navigation",
            resources: "Ressourcen",
            legal: "Rechtliches",
            account: "Konto",

            home: "Startseite",
            dashboard: "Dashboard",
            reviews: "Bewertungen",

            documentation: "Dokumentation",
            support: "Support",
            advertisement: "Werbung",
            advertisementAdmin: "Werbungsverwaltung",

            terms: "Bedingungen",
            privacy: "Datenschutz",
            data: "Daten",
            cookies: "Cookies",

            login: "Mit Discord anmelden",
            logout: "Abmelden",

            language: "Sprache",

            close: "Schließen",
            open: "Menü öffnen",

            cookieTitle: "🍪 Wir verwenden Cookies",
            cookieText:
                "Misuki verwendet Cookies, um deine Erfahrung zu verbessern und die Website korrekt funktionieren zu lassen.",

            acceptAll: "Alle akzeptieren",
            essentialOnly: "Nur notwendige",
            deny: "Ablehnen",

            cookiePolicy: "Cookie-Richtlinie"

        },


        es: {

            menu: "Menú",

            navigation: "Navegación",
            resources: "Recursos",
            legal: "Legal",
            account: "Cuenta",

            home: "Inicio",
            dashboard: "Panel",
            reviews: "Reseñas",

            documentation: "Documentación",
            support: "Soporte",
            advertisement: "Publicidad",
            advertisementAdmin: "Administración de publicidad",

            terms: "Términos",
            privacy: "Privacidad",
            data: "Datos",
            cookies: "Cookies",

            login: "Iniciar sesión con Discord",
            logout: "Cerrar sesión",

            language: "Idioma",

            close: "Cerrar",
            open: "Abrir menú",

            cookieTitle: "🍪 Usamos cookies",
            cookieText:
                "Misuki utiliza cookies para mejorar tu experiencia y mantener el sitio web funcionando correctamente.",

            acceptAll: "Aceptar todas",
            essentialOnly: "Solo esenciales",
            deny: "Rechazar",

            cookiePolicy: "Política de Cookies"

        },


        fr: {

            menu: "Menu",

            navigation: "Navigation",
            resources: "Ressources",
            legal: "Mentions légales",
            account: "Compte",

            home: "Accueil",
            dashboard: "Tableau de bord",
            reviews: "Avis",

            documentation: "Documentation",
            support: "Support",
            advertisement: "Publicité",
            advertisementAdmin: "Administration de la publicité",

            terms: "Conditions",
            privacy: "Confidentialité",
            data: "Données",
            cookies: "Cookies",

            login: "Se connecter avec Discord",
            logout: "Déconnexion",

            language: "Langue",

            close: "Fermer",
            open: "Ouvrir le menu",

            cookieTitle: "🍪 Nous utilisons des cookies",
            cookieText:
                "Misuki utilise des cookies pour améliorer votre expérience et assurer le bon fonctionnement du site.",

            acceptAll: "Tout accepter",
            essentialOnly: "Essentiels uniquement",
            deny: "Refuser",

            cookiePolicy: "Politique des cookies"

        }

    };


    /* =====================================================
       CURRENT LANGUAGE
    ===================================================== */

    const savedLanguage =
        localStorage.getItem("misuki_language");

    let currentLanguage =
        languages[savedLanguage]
            ? savedLanguage
            : "en";


    /* =====================================================
       GET TRANSLATION
    ===================================================== */

    function translate(key) {

        if (
            translations[currentLanguage] &&
            translations[currentLanguage][key]
        ) {

            return translations[currentLanguage][key];

        }

        if (translations.en[key]) {
            return translations.en[key];
        }

        return key;

    }


    /* =====================================================
       APPLY TRANSLATIONS
    ===================================================== */

    function applyTranslations() {

        document.documentElement.lang =
            currentLanguage;


        const elements =
            document.querySelectorAll("[data-i18n]");


        elements.forEach(function (element) {

            const key =
                element.getAttribute("data-i18n");

            const value =
                translate(key);


            if (value) {

                element.textContent = value;

            }

        });


        const placeholders =
            document.querySelectorAll(
                "[data-i18n-placeholder]"
            );


        placeholders.forEach(function (element) {

            const key =
                element.getAttribute(
                    "data-i18n-placeholder"
                );


            element.setAttribute(
                "placeholder",
                translate(key)
            );

        });


        const titles =
            document.querySelectorAll(
                "[data-i18n-title]"
            );


        titles.forEach(function (element) {

            const key =
                element.getAttribute(
                    "data-i18n-title"
                );


            element.setAttribute(
                "title",
                translate(key)
            );

        });


        const languageName =
            document.getElementById(
                "currentLanguageName"
            );


        const languageFlag =
            document.getElementById(
                "currentLanguageFlag"
            );


        if (languageName) {

            languageName.textContent =
                languages[currentLanguage].name;

        }


        if (languageFlag) {

            languageFlag.textContent =
                languages[currentLanguage].flag;

        }

    }


    /* =====================================================
       LANGUAGE SELECTOR
    ===================================================== */

    function createLanguageSelector() {

        if (
            document.getElementById(
                "misukiLanguageSelector"
            )
        ) {
            return;
        }


        const hamburger =
            document.querySelector(".hamburger");


        if (!hamburger) {
            return;
        }


        const wrapper =
            document.createElement("div");


        wrapper.id =
            "misukiLanguageSelector";


        wrapper.className =
            "language-selector";


        wrapper.innerHTML = `

            <button
                type="button"
                class="language-button"
                id="languageButton"
                aria-label="${translate("language")}"
                aria-expanded="false"
            >

                <span
                    id="currentLanguageFlag"
                >
                    ${languages[currentLanguage].flag}
                </span>

                <span
                    id="currentLanguageName"
                >
                    ${languages[currentLanguage].name}
                </span>

                <span class="language-arrow">
                    ▾
                </span>

            </button>


            <div
                class="language-dropdown"
                id="languageDropdown"
            >

                ${Object.keys(languages).map(
                    function (code) {

                        return `

                            <button
                                type="button"
                                class="language-option"
                                data-language="${code}"
                            >

                                <span>
                                    ${languages[code].flag}
                                </span>

                                <span>
                                    ${languages[code].name}
                                </span>

                            </button>

                        `;

                    }
                ).join("")}

            </div>

        `;


        hamburger.parentNode.insertBefore(
            wrapper,
            hamburger
        );


        const button =
            document.getElementById(
                "languageButton"
            );


        const dropdown =
            document.getElementById(
                "languageDropdown"
            );


        button.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();


                const isOpen =
                    dropdown.classList.contains(
                        "show"
                    );


                dropdown.classList.toggle(
                    "show",
                    !isOpen
                );


                button.setAttribute(
                    "aria-expanded",
                    String(!isOpen)
                );

            }
        );


        const options =
            document.querySelectorAll(
                ".language-option"
            );


        options.forEach(function (option) {

            option.addEventListener(
                "click",
                function () {

                    const language =
                        option.getAttribute(
                            "data-language"
                        );


                    setLanguage(language);


                    dropdown.classList.remove(
                        "show"
                    );


                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }
            );

        });


        document.addEventListener(
            "click",
            function (event) {

                if (
                    !wrapper.contains(
                        event.target
                    )
                ) {

                    dropdown.classList.remove(
                        "show"
                    );

                    button.setAttribute(
                        "aria-expanded",
                        "false"
                    );

                }

            }
        );

    }


    /* =====================================================
       SET LANGUAGE
    ===================================================== */

    function setLanguage(language) {

        if (!languages[language]) {
            return;
        }


        currentLanguage =
            language;


        localStorage.setItem(
            "misuki_language",
            language
        );


        applyTranslations();


        document.dispatchEvent(
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


    /* =====================================================
       PUBLIC API
    ===================================================== */

    window.MisukiTranslation = {

        setLanguage: setLanguage,

        getLanguage: function () {
            return currentLanguage;
        },

        translate: translate,

        languages: languages

    };


    /* =====================================================
       INITIALIZE
    ===================================================== */

    function initTranslation() {

        createLanguageSelector();

        applyTranslations();

        console.log(
            "🌍 Misuki translation initialized:",
            currentLanguage
        );

    }


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initTranslation
        );

    } else {

        initTranslation();

    }


})();