/* =========================================================
   MISUKI — TRANSLATION.JS
   AUTOMATIC LANGUAGE SYSTEM
========================================================= */

(function () {

    "use strict";


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
       TRANSLATION DICTIONARY
    ===================================================== */

    const dictionary = {

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
            fr: "Support"
        },

        "Advertisement": {
            pt: "Publicidade",
            en: "Advertisement",
            de: "Werbung",
            es: "Publicidad",
            fr: "Publicité"
        },

        "Advertisement Admin": {
            pt: "Administração de publicidade",
            en: "Advertisement Admin",
            de: "Werbungsverwaltung",
            es: "Administración de publicidad",
            fr: "Administration de la publicité"
        },

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

        "Login with Discord": {
            pt: "Entrar com Discord",
            en: "Login with Discord",
            de: "Mit Discord anmelden",
            es: "Iniciar sesión con Discord",
            fr: "Se connecter avec Discord"
        },

        "Logout": {
            pt: "Sair",
            en: "Logout",
            de: "Abmelden",
            es: "Cerrar sesión",
            fr: "Déconnexion"
        },

        "Accept All": {
            pt: "Aceitar todos",
            en: "Accept All",
            de: "Alle akzeptieren",
            es: "Aceptar todas",
            fr: "Tout accepter"
        },

        "Essential Only": {
            pt: "Apenas essenciais",
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

        "Cookie Policy": {
            pt: "Política de Cookies",
            en: "Cookie Policy",
            de: "Cookie-Richtlinie",
            es: "Política de Cookies",
            fr: "Politique des cookies"
        },

        "Last updated: August 2026": {
            pt: "Última atualização: agosto de 2026",
            en: "Last updated: August 2026",
            de: "Zuletzt aktualisiert: August 2026",
            es: "Última actualización: agosto de 2026",
            fr: "Dernière mise à jour : août 2026"
        },

        "🍪 We use cookies": {
            pt: "🍪 Utilizamos cookies",
            en: "🍪 We use cookies",
            de: "🍪 Wir verwenden Cookies",
            es: "🍪 Usamos cookies",
            fr: "🍪 Nous utilisons des cookies"
        },

        "© 2026 Misuki. All rights reserved.": {
            pt: "© 2026 Misuki. Todos os direitos reservados.",
            en: "© 2026 Misuki. All rights reserved.",
            de: "© 2026 Misuki. Alle Rechte vorbehalten.",
            es: "© 2026 Misuki. Todos los derechos reservados.",
            fr: "© 2026 Misuki. Tous droits réservés."
        }

    };


    /* =====================================================
       PAGE TITLES
    ===================================================== */

    const pageTranslations = {

        "Privacy Policy": {
            pt: "Política de Privacidade",
            en: "Privacy Policy",
            de: "Datenschutzerklärung",
            es: "Política de Privacidad",
            fr: "Politique de confidentialité"
        },

        "Terms of Service": {
            pt: "Termos de Serviço",
            en: "Terms of Service",
            de: "Nutzungsbedingungen",
            es: "Términos de Servicio",
            fr: "Conditions d'utilisation"
        },

        "Data": {
            pt: "Dados",
            en: "Data",
            de: "Daten",
            es: "Datos",
            fr: "Données"
        }

    };


    /* =====================================================
       CURRENT LANGUAGE
    ===================================================== */

    let currentLanguage =
        localStorage.getItem("misuki_language");

    if (!languages[currentLanguage]) {
        currentLanguage = "en";
    }


    /* =====================================================
       TEXT NORMALIZATION
    ===================================================== */

    function cleanText(text) {

        return text
            .replace(/\s+/g, " ")
            .trim();

    }


    /* =====================================================
       GET TRANSLATION
    ===================================================== */

    function getTranslation(text) {

        const clean =
            cleanText(text);

        if (!clean) {
            return null;
        }

        if (
            dictionary[clean] &&
            dictionary[clean][currentLanguage]
        ) {

            return dictionary[clean][currentLanguage];

        }

        if (
            pageTranslations[clean] &&
            pageTranslations[clean][currentLanguage]
        ) {

            return pageTranslations[clean][currentLanguage];

        }

        return null;

    }


    /* =====================================================
       ORIGINAL TEXT STORAGE
    ===================================================== */

    const originalTexts =
        new WeakMap();


    function rememberTextNode(node) {

        if (!originalTexts.has(node)) {

            originalTexts.set(
                node,
                node.nodeValue
            );

        }

    }


    /* =====================================================
       TRANSLATE TEXT NODES
    ===================================================== */

    function translateTextNodes(root) {

        if (!root) {
            return;
        }

        const walker =
            document.createTreeWalker(
                root,
                NodeFilter.SHOW_TEXT
            );

        const nodes = [];

        let node;

        while (
            node = walker.nextNode()
        ) {

            nodes.push(node);

        }

        nodes.forEach(function (textNode) {

            const parent =
                textNode.parentElement;

            if (!parent) {
                return;
            }

            const tag =
                parent.tagName.toLowerCase();

            if (
                tag === "script" ||
                tag === "style" ||
                tag === "noscript" ||
                tag === "textarea"
            ) {

                return;

            }

            rememberTextNode(textNode);

            const source =
                originalTexts.get(textNode);

            const clean =
                cleanText(source);

            if (!clean) {
                return;
            }

            const translation =
                getTranslation(clean);

            if (!translation) {
                return;
            }

            const leading =
                source.match(/^\s*/)?.[0] || "";

            const trailing =
                source.match(/\s*$/)?.[0] || "";

            textNode.nodeValue =
                leading +
                translation +
                trailing;

        });

    }


    /* =====================================================
       TRANSLATE ATTRIBUTES
    ===================================================== */

    function translateAttributes() {

        document
            .querySelectorAll("[aria-label]")
            .forEach(function (element) {

                const value =
                    cleanText(
                        element.getAttribute(
                            "aria-label"
                        )
                    );

                const translation =
                    getTranslation(value);

                if (translation) {

                    element.setAttribute(
                        "aria-label",
                        translation
                    );

                }

            });


        document
            .querySelectorAll("[title]")
            .forEach(function (element) {

                const value =
                    cleanText(
                        element.getAttribute(
                            "title"
                        )
                    );

                const translation =
                    getTranslation(value);

                if (translation) {

                    element.setAttribute(
                        "title",
                        translation
                    );

                }

            });


        document
            .querySelectorAll("[placeholder]")
            .forEach(function (element) {

                const value =
                    cleanText(
                        element.getAttribute(
                            "placeholder"
                        )
                    );

                const translation =
                    getTranslation(value);

                if (translation) {

                    element.setAttribute(
                        "placeholder",
                        translation
                    );

                }

            });

    }


    /* =====================================================
       TRANSLATE DOCUMENT
    ===================================================== */

    function translateDocument() {

        translateTextNodes(
            document.body
        );

        translateAttributes();


        const title =
            cleanText(
                document.title
            );

        const titleTranslation =
            getTranslation(title);

        if (titleTranslation) {

            document.title =
                titleTranslation;

        }


        document.documentElement.lang =
            currentLanguage;

    }


    /* =====================================================
       CREATE LANGUAGE SELECTOR
    ===================================================== */

    function createSelector() {

        if (
            document.getElementById(
                "misukiLanguageSelector"
            )
        ) {

            return;

        }


        /* =================================================
           FIND HAMBURGER
        ================================================= */

        const hamburger =
            document.querySelector(
                ".hamburger"
            );

        if (!hamburger) {

            console.warn(
                "⚠️ Misuki: hamburger not found."
            );

            return;

        }


        /* =================================================
           CREATE ACTIONS GROUP
        ================================================= */

        const actions =
            document.createElement(
                "div"
            );

        actions.className =
            "misuki-menu-actions";

        actions.id =
            "misukiMenuActions";


        /* =================================================
           CREATE LANGUAGE WRAPPER
        ================================================= */

        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.id =
            "misukiLanguageSelector";

        wrapper.className =
            "misuki-language";


        /* =================================================
           CREATE SELECTOR HTML
        ================================================= */

        wrapper.innerHTML = `

            <button
                type="button"
                class="misuki-language-button"
                id="misukiLanguageButton"
                aria-expanded="false"
                aria-label="Language"
            >

                <span
                    class="misuki-language-flag"
                    id="misukiLanguageFlag"
                >
                    ${languages[currentLanguage].flag}
                </span>

                <span
                    class="misuki-language-short"
                    id="misukiLanguageShort"
                >
                    ${languages[currentLanguage].short}
                </span>

                <span
                    class="misuki-language-arrow"
                >
                    ▾
                </span>

            </button>


            <div
                class="misuki-language-dropdown"
                id="misukiLanguageDropdown"
            >

                ${Object.keys(languages)
                    .map(function (code) {

                        return `

                            <button
                                type="button"
                                class="misuki-language-option"
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

                    })
                    .join("")}

            </div>

        `;


        /* =================================================
           CRITICAL:
           LANGUAGE + HAMBURGER ARE PUT IN SAME GROUP
        ================================================= */

        hamburger.parentNode.insertBefore(
            actions,
            hamburger
        );

        actions.appendChild(
            wrapper
        );

        actions.appendChild(
            hamburger
        );


        /* =================================================
           ELEMENT REFERENCES
        ================================================= */

        const button =
            document.getElementById(
                "misukiLanguageButton"
            );

        const dropdown =
            document.getElementById(
                "misukiLanguageDropdown"
            );


        /* =================================================
           OPEN / CLOSE DROPDOWN
        ================================================= */

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


        /* =================================================
           LANGUAGE OPTIONS
        ================================================= */

        dropdown
            .querySelectorAll(
                ".misuki-language-option"
            )
            .forEach(function (option) {

                option.addEventListener(
                    "click",
                    function (event) {

                        event.preventDefault();
                        event.stopPropagation();

                        const language =
                            option.getAttribute(
                                "data-language"
                            );

                        setLanguage(
                            language
                        );

                    }
                );

            });


        /* =================================================
           CLOSE WHEN CLICKING OUTSIDE
        ================================================= */

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
       UPDATE LANGUAGE BUTTON
    ===================================================== */

    function updateSelector() {

        const language =
            languages[currentLanguage];

        const flag =
            document.getElementById(
                "misukiLanguageFlag"
            );

        const short =
            document.getElementById(
                "misukiLanguageShort"
            );

        if (flag) {

            flag.textContent =
                language.flag;

        }

        if (short) {

            short.textContent =
                language.short;

        }

    }


    /* =====================================================
       CHANGE LANGUAGE
    ===================================================== */

    function setLanguage(language) {

        if (
            !languages[language]
        ) {

            return;

        }

        currentLanguage =
            language;

        localStorage.setItem(
            "misuki_language",
            language
        );

        window.location.reload();

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

        }

    };


    /* =====================================================
       INITIALIZATION
    ===================================================== */

    function initTranslation() {

        createSelector();

        translateDocument();

        updateSelector();

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