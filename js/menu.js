/* =========================================================
   MISUKI — MENU.JS
   SIDE MENU + LANGUAGE SELECTOR
   Single controller: the two menus can never be open together.
   ========================================================= */

(function () {
    "use strict";

    function initMenu() {
        const hamburger = document.getElementById("hamburger");
        const menu = document.getElementById("menu");
        const overlay = document.getElementById("overlay");
        const menuClose = document.getElementById("menuClose");
        const languageSelector = document.getElementById("languageSelector");
        const languageButton = document.getElementById("languageButton");
        const languageDropdown = document.getElementById("languageDropdown");

        if (!hamburger || !menu || !overlay || !menuClose) {
            console.warn("⚠️ Misuki menu elements not found.");
            return;
        }

        function hardCloseLanguage() {
            if (!languageSelector || !languageDropdown || !languageButton) return;

            languageSelector.classList.remove("open", "active");
            languageDropdown.classList.remove("show");
            languageDropdown.style.display = "none";
            languageDropdown.setAttribute("aria-hidden", "true");
            languageButton.setAttribute("aria-expanded", "false");
        }

        function hardCloseMenu() {
            menu.classList.remove("open", "active");
            overlay.classList.remove("show", "active");
            document.body.classList.remove("menu-open");
            hamburger.setAttribute("aria-expanded", "false");
            menu.setAttribute("aria-hidden", "true");
        }

        function syncLanguageButton(languageOverride) {
            if (
                !languageButton ||
                !window.MisukiTranslation ||
                typeof window.MisukiTranslation.getLanguage !== "function"
            ) return;

            const language = languageOverride || window.MisukiTranslation.getLanguage();
            if (!["en", "pt", "de", "es", "fr"].includes(language)) return;
            const infoMap = {
                en: { name: "English", short: "EN", flag: "🇬🇧" },
                pt: { name: "Português", short: "PT", flag: "🇵🇹" },
                de: { name: "Deutsch", short: "DE", flag: "🇩🇪" },
                es: { name: "Español", short: "ES", flag: "🇪🇸" },
                fr: { name: "Français", short: "FR", flag: "🇫🇷" }
            };
            const info = infoMap[language] || infoMap.en;

            const flag = languageButton.querySelector(".language-flag");
            const short = languageButton.querySelector(".language-short");
            const name = languageButton.querySelector(".language-name");

            if (flag) flag.textContent = info.flag;
            if (short) short.textContent = info.short;
            if (name) {
                name.textContent = info.name;
                name.setAttribute("data-current-language-name", language);
            }
            languageButton.dataset.currentLanguage = language;
            languageButton.setAttribute("data-language", language);
            languageButton.setAttribute("aria-label", info.name);
            languageButton.setAttribute("title", info.name);

        }

        function openMenu(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            // Mutual exclusion is enforced before anything is shown.
            hardCloseLanguage();

            menu.classList.add("open");
            overlay.classList.add("show");
            document.body.classList.add("menu-open");

            hamburger.setAttribute("aria-expanded", "true");
            menu.setAttribute("aria-hidden", "false");
            syncLanguageButton();

            window.dispatchEvent(new CustomEvent("misukiMenuOpened"));
        }

        function closeMenu(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            hardCloseMenu();
        }

        function openLanguageSelector(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            if (!languageSelector || !languageButton || !languageDropdown) return;

            const wasOpen = languageSelector.classList.contains("open");

            // Close the side menu completely before touching the language menu.
            hardCloseMenu();
            hardCloseLanguage();

            if (!wasOpen) {
                syncLanguageButton();
                languageSelector.classList.add("open", "active");
                languageDropdown.classList.add("show");
                languageDropdown.style.display = "flex";
                languageDropdown.setAttribute("aria-hidden", "false");
                languageButton.setAttribute("aria-expanded", "true");
            }
        }

        function toggleMenu(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            if (menu.classList.contains("open")) {
                closeMenu();
            } else {
                openMenu();
            }
        }

        window.MisukiMenu = {
            open: openMenu,
            close: closeMenu,
            toggle: toggleMenu,
            isOpen: function () {
                return menu.classList.contains("open");
            },
            closeLanguageSelector: hardCloseLanguage,
            syncLanguageButton: syncLanguageButton
        };

        hamburger.addEventListener("click", toggleMenu);
        menuClose.addEventListener("click", closeMenu);

        if (languageButton) {
            languageButton.addEventListener("click", openLanguageSelector);
        }

        function selectLanguage(languageOption) {
            if (!languageOption || !languageDropdown) return;

            const language = languageOption.getAttribute("data-lang");
            if (!language || !["en", "pt", "de", "es", "fr"].includes(language)) return;

            syncLanguageButton(language);

            languageDropdown.querySelectorAll("[data-lang]").forEach(function (option) {
                const selected = option.getAttribute("data-lang") === language;
                option.classList.toggle("selected", selected);
                option.setAttribute("aria-selected", selected ? "true" : "false");
            });

            try {
                localStorage.setItem("misuki_language", language);
            } catch (error) {
                console.warn("Misuki: could not persist language.", error);
            }

            if (window.MisukiTranslation &&
                typeof window.MisukiTranslation.setLanguage === "function") {
                window.MisukiTranslation.setLanguage(language);
            }

            hardCloseLanguage();
            syncLanguageButton(language);
            syncLanguageOptions(language);
        }



        function syncLanguageOptions(languageOverride) {
            if (!languageDropdown) return;
            const language = languageOverride ||
                (window.MisukiTranslation && typeof window.MisukiTranslation.getLanguage === "function"
                    ? window.MisukiTranslation.getLanguage()
                    : "en");

            languageDropdown.querySelectorAll("[data-lang]").forEach(function (option) {
                const selected = option.getAttribute("data-lang") === language;
                option.classList.toggle("selected", selected);
                option.setAttribute("aria-selected", selected ? "true" : "false");
            });
        }

        if (languageDropdown) {
            languageDropdown.querySelectorAll("[data-lang]").forEach(function (option) {
                option.addEventListener("click", function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    selectLanguage(option);
                });
            });
        }

        document.addEventListener("click", function (event) {
            if (
                languageSelector &&
                !languageSelector.contains(event.target) &&
                !event.target.closest("#hamburger")
            ) {
                hardCloseLanguage();
            }
        });

        overlay.addEventListener("click", closeMenu);

        document.addEventListener("keydown", function (event) {
            if (event.key !== "Escape") return;

            if (menu.classList.contains("open")) {
                closeMenu();
            } else if (languageSelector && languageSelector.classList.contains("open")) {
                hardCloseLanguage();
            }
        });

        window.addEventListener("misukiLanguageChanged", function (event) {
            const changedLanguage = event && event.detail && event.detail.language
                ? event.detail.language
                : null;
            const currentLanguage = changedLanguage ||
                (window.MisukiTranslation && typeof window.MisukiTranslation.getLanguage === "function"
                    ? window.MisukiTranslation.getLanguage()
                    : (localStorage.getItem("misuki_language") || "en"));
            syncLanguageButton(currentLanguage);
            syncLanguageOptions(currentLanguage);
            hardCloseLanguage();
        });

        hardCloseMenu();
        hardCloseLanguage();
        const initialLanguage = window.MisukiTranslation &&
            typeof window.MisukiTranslation.getLanguage === "function"
            ? window.MisukiTranslation.getLanguage()
            : "en";
        syncLanguageButton(initialLanguage);
        syncLanguageOptions(initialLanguage);

        console.log("✅ Misuki menu initialized.");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMenu, { once: true });
    } else {
        initMenu();
    }
})();
