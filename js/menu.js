
/* =========================================================
   MISUKI — MENU.JS
   SIDE MENU
   ========================================================= */

(function () {

    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            const hamburger =
                document.getElementById(
                    "hamburger"
                );


            const menu =
                document.getElementById(
                    "menu"
                );


            const overlay =
                document.getElementById(
                    "overlay"
                );


            const menuClose =
                document.getElementById(
                    "menuClose"
                );


            if (
                !hamburger ||
                !menu ||
                !overlay ||
                !menuClose
            ) {

                return;

            }


            /* =================================================
               OPEN MENU
            ================================================== */

            function openMenu() {

                menu.classList.add(
                    "open"
                );


                overlay.classList.add(
                    "show"
                );


                document.body.classList.add(
                    "menu-open"
                );


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
            ================================================== */

            function closeMenu() {

                menu.classList.remove(
                    "open"
                );


                overlay.classList.remove(
                    "show"
                );


                document.body.classList.remove(
                    "menu-open"
                );


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
               HAMBURGER
            ================================================== */

            hamburger.addEventListener(
                "click",
                openMenu
            );


            /* =================================================
               X
            ================================================== */

            menuClose.addEventListener(
                "click",
                closeMenu
            );


            /* =================================================
               OVERLAY
            ================================================== */

            overlay.addEventListener(
                "click",
                closeMenu
            );


            /* =================================================
               ESC
            ================================================== */

            document.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Escape"
                    ) {

                        closeMenu();

                    }

                }
            );


            /* =================================================
               MENU LINKS
            ================================================== */

            menu
                .querySelectorAll("a")
                .forEach(
                    function (link) {

                        link.addEventListener(
                            "click",
                            closeMenu
                        );

                    }
                );

        }
    );

})();

