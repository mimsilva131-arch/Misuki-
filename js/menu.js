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
            if (name) name.textContent = info.name;
            languageButton.dataset.currentLanguage = language;
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

        document.addEventListener("click", function (event) {
            const languageOption = event.target.closest("#languageDropdown [data-lang]");

            if (languageOption && languageDropdown && languageDropdown.contains(languageOption)) {
                event.preventDefault();
                event.stopPropagation();

                const language = languageOption.getAttribute("data-lang");

                if (
                    language &&
                    window.MisukiTranslation &&
                    typeof window.MisukiTranslation.setLanguage === "function"
                ) {
                    window.MisukiTranslation.setLanguage(language);
                }

                // Always read the saved value after translation and before closing.
                syncLanguageButton(language);
                hardCloseLanguage();
                return;
            }

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

        menu.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                closeMenu();
            });
        });

        window.addEventListener("misukiLanguageChanged", function (event) {
            syncLanguageButton(
                event && event.detail && event.detail.language
                    ? event.detail.language
                    : null
            );
            hardCloseLanguage();
        });

        hardCloseMenu();
        hardCloseLanguage();
        syncLanguageButton();

        console.log("✅ Misuki menu initialized.");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMenu, { once: true });
    } else {
        initMenu();
    }
})();
