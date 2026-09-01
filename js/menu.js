
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

        if (!hamburger || !menu || !overlay || !menuClose) {
            console.warn("⚠️ Misuki menu elements not found.");
            return;
        }


        /* =================================================
           OPEN MENU
        ================================================= */

        function openMenu(event) {

            if (event) {
                event.preventDefault();
            }

            menu.classList.add("open");
            overlay.classList.add("show");
            document.body.classList.add("menu-open");

            hamburger.setAttribute(
                "aria-expanded",
                "true"
            );

            menu.setAttribute(
                "aria-hidden",
                "false"
            );

        }


        /* =================================================
           CLOSE MENU
        ================================================= */

        function closeMenu(event) {

            if (event) {
                event.preventDefault();
            }

            menu.classList.remove("open");
            overlay.classList.remove("show");
            document.body.classList.remove("menu-open");

            hamburger.setAttribute(
                "aria-expanded",
                "false"
            );

            menu.setAttribute(
                "aria-hidden",
                "true"
            );

        }


        /* =================================================
           TOGGLE MENU
        ================================================= */

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


        /* =================================================
           HAMBURGER
        ================================================= */

        hamburger.addEventListener(
            "click",
            toggleMenu
        );


        /* =================================================
           CLOSE BUTTON
        ================================================= */

        menuClose.addEventListener(
            "click",
            closeMenu
        );


        /* =================================================
           OVERLAY
        ================================================= */

        overlay.addEventListener(
            "click",
            closeMenu
        );


        /* =================================================
           ESC
        ================================================= */

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape" &&
                    menu.classList.contains("open")
                ) {

                    closeMenu();

                }

            }
        );


        /* =================================================
           MENU LINKS
        ================================================= */

        const links = menu.querySelectorAll("a");

        links.forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function () {

                        closeMenu();

                    }
                );

            }
        );


        /* =================================================
           INITIAL STATE
        ================================================= */

        closeMenu();


        /* =================================================
           DEBUG
        ================================================= */

        console.log(
            "✅ Misuki menu initialized."
        );

    }


    /* =====================================================
       INITIALIZE
    ===================================================== */

    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initMenu
        );

    } else {

        initMenu();

    }

})();

