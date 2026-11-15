/* =========================================================
   MISUKI — MENU.JS
   SIDE MENU
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

        function openMenu(event) {

            if (event) {
                event.preventDefault();
            }

            closeLanguageSelector();

            menu.classList.add("open");
            overlay.classList.add("show");
            document.body.classList.add("menu-open");

            hamburger.setAttribute("aria-expanded", "true");
            menu.setAttribute("aria-hidden", "false");

            window.dispatchEvent(new CustomEvent("misukiMenuOpened"));

        }

        function closeLanguageSelector() {
            if (languageSelector) {
                languageSelector.classList.remove("open", "active");
            }
            if (languageDropdown) {
                languageDropdown.classList.remove("show");
                languageDropdown.style.display = "";
                languageDropdown.setAttribute("aria-hidden", "true");
            }
            if (languageButton) {
                languageButton.setAttribute("aria-expanded", "false");
            }
        }

        function openLanguageSelector(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            if (!languageSelector || !languageButton || !languageDropdown) {
                return;
            }

            const wasOpen = languageSelector.classList.contains("open");
            closeMenu();
            closeLanguageSelector();

            if (!wasOpen) {
                languageSelector.classList.add("open");
                languageDropdown.classList.add("show");
                languageDropdown.style.display = "flex";
                languageDropdown.setAttribute("aria-hidden", "false");
                languageButton.setAttribute("aria-expanded", "true");
            }
        }

        function closeMenu(event) {

            if (event) {
                event.preventDefault();
            }

            menu.classList.remove("open");
            overlay.classList.remove("show");
            document.body.classList.remove("menu-open");

            hamburger.setAttribute("aria-expanded", "false");
            menu.setAttribute("aria-hidden", "true");

        }

        function toggleMenu(event) {

            if (event) {
                event.preventDefault();
            }

            if (menu.classList.contains("open")) {
                closeMenu();
            } else {
                openMenu();
            }

        }

        // Expose only the controls needed by the language selector.
        // The two menus are mutually exclusive: opening one closes the other.
        window.MisukiMenu = {
            open: openMenu,
            close: closeMenu,
            toggle: toggleMenu,
            isOpen: function () {
                return menu.classList.contains("open");
            },
            closeLanguageSelector: closeLanguageSelector
        };

        hamburger.addEventListener("click", toggleMenu);

        menuClose.addEventListener("click", closeMenu);

        if (languageButton) {
            languageButton.addEventListener("click", openLanguageSelector);
        }

        document.addEventListener("click", function (event) {
            if (languageSelector && !languageSelector.contains(event.target)) {
                closeLanguageSelector();
            }
        });

        overlay.addEventListener("click", closeMenu);

        document.addEventListener("keydown", function (event) {

            if (
                event.key === "Escape" &&
                menu.classList.contains("open")
            ) {
                closeMenu();
            }

        });

        const links = menu.querySelectorAll("a");

        links.forEach(function (link) {

            link.addEventListener("click", function () {
                closeMenu();
            });

        });

        closeMenu();

        console.log("✅ Misuki menu initialized.");

    }

    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initMenu
        );

    } else {

        initMenu();

    }

})();