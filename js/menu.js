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

            // Start warming the menu destinations as soon as the menu opens,
            // not only after hover. This makes an immediate click much faster.
            if (typeof prefetchMenuPage === "function") {
                menu.querySelectorAll("a").forEach(prefetchMenuPage);
            }

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

                if (language) {
                    // Update the closed selector immediately. The translation
                    // engine is allowed to translate the page afterwards, but
                    // it must never own the visible selected-language state.
                    syncLanguageButton(language);

                    try {
                        localStorage.setItem("misuki_language", language);
                    } catch (error) {
                        console.warn("Misuki: could not persist language.", error);
                    }

                    if (
                        window.MisukiTranslation &&
                        typeof window.MisukiTranslation.setLanguage === "function"
                    ) {
                        window.MisukiTranslation.setLanguage(language);
                    }

                    // Re-apply after the translation pass as a final guard.
                    requestAnimationFrame(function () {
                        syncLanguageButton(language);
                    });
                    setTimeout(function () {
                        syncLanguageButton(language);
                    }, 150);
                }

                // Close the selector and then explicitly restore the selected
                // language on the closed button. This prevents translation
                // updates from briefly resetting it to English.
                const applyClosedLanguage = function () {
                    const saved = window.MisukiTranslation &&
                        typeof window.MisukiTranslation.getLanguage === "function"
                        ? window.MisukiTranslation.getLanguage()
                        : (localStorage.getItem("misuki_language") || language);

                    hardCloseLanguage();
                    syncLanguageButton(saved || language);

                    if (languageButton) {
                        languageButton.setAttribute(
                            "data-current-language",
                            saved || language
                        );
                    }
                };

                applyClosedLanguage();
                requestAnimationFrame(applyClosedLanguage);
                setTimeout(applyClosedLanguage, 100);
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

        // Warm internal menu pages before the user clicks them. This keeps the
        // navigation itself immediate, while the browser can fetch the next
        // HTML in the background (especially helpful on Render's free instance).
        const prefetchedUrls = new Set();

        function prefetchMenuPage(link) {
            if (!link || !link.href) return;
            if (link.target === "_blank" || link.hasAttribute("download")) return;

            const url = new URL(link.href, window.location.href);
            if (url.origin !== window.location.origin) return;
            if (prefetchedUrls.has(url.href)) return;
            if (url.pathname === "/login" || url.pathname === "/logout") return;

            prefetchedUrls.add(url.href);

            const prefetch = document.createElement("link");
            prefetch.rel = "prefetch";
            prefetch.as = "document";
            prefetch.href = url.href;
            document.head.appendChild(prefetch);
        }

        menu.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("pointerenter", function () {
                prefetchMenuPage(link);
            }, { passive: true });

            link.addEventListener("touchstart", function () {
                prefetchMenuPage(link);
            }, { passive: true, once: true });

            link.addEventListener("click", function () {
                // Never wait for animation, translation, or prefetch work here.
                closeMenu();
            });
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
            hardCloseLanguage();
        });

        hardCloseMenu();
        hardCloseLanguage();
        const initialLanguage = window.MisukiTranslation &&
            typeof window.MisukiTranslation.getLanguage === "function"
            ? window.MisukiTranslation.getLanguage()
            : "en";
        syncLanguageButton(initialLanguage);

        syncLanguageButton(
            window.MisukiTranslation &&
            typeof window.MisukiTranslation.getLanguage === "function"
                ? window.MisukiTranslation.getLanguage()
                : "en"
        );
        console.log("✅ Misuki menu initialized.");
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initMenu, { once: true });
    } else {
        initMenu();
    }
})();
