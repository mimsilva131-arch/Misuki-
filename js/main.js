
/* =========================================================
   MISUKI — MAIN.JS
   PAGE TRANSITIONS
   ========================================================= */

(function () {

    "use strict";


    /* =====================================================
       MENU
       ===================================================== */

    window.openMenu = function () {

        const menu =
            document.getElementById("menu");

        const overlay =
            document.getElementById("overlay");

        const hamburger =
            document.querySelector(".hamburger");

        const closeButton =
            document.querySelector(".menu-close");


        if (
            !menu ||
            !overlay ||
            !hamburger
        ) {
            return;
        }


        /* =================================================
           ABRIR MENU
        ================================================= */

        menu.classList.add("open");
        menu.classList.add("active");

        overlay.classList.add("show");
        overlay.classList.add("active");

        document.body.classList.add("menu-open");


        /* =================================================
           STATEMENT:

           ENQUANTO O MENU ESTÁ ABERTO E A CRUZ EXISTE,
           AS TRÊS BARRAS DO HAMBURGER NÃO PODEM APARECER.
        ================================================= */

        hamburger.classList.add("hidden");

        hamburger.style.display = "none";

        hamburger.style.visibility = "hidden";

        hamburger.style.opacity = "0";

        hamburger.style.pointerEvents = "none";

        hamburger.setAttribute(
            "aria-hidden",
            "true"
        );


        /* =================================================
           GARANTIR QUE A CRUZ ESTÁ VISÍVEL
        ================================================= */

        if (closeButton) {

            closeButton.style.display =
                "flex";

            closeButton.style.visibility =
                "visible";

            closeButton.style.opacity =
                "1";

            closeButton.style.pointerEvents =
                "auto";

        }

    };


    /* =====================================================
       FECHAR MENU
       ===================================================== */

    window.closeMenu = function () {

        const menu =
            document.getElementById("menu");

        const overlay =
            document.getElementById("overlay");

        const hamburger =
            document.querySelector(".hamburger");

        const closeButton =
            document.querySelector(".menu-close");


        if (
            !menu ||
            !overlay ||
            !hamburger
        ) {
            return;
        }


        /* =================================================
           FECHAR MENU
        ================================================= */

        menu.classList.remove("open");
        menu.classList.remove("active");

        overlay.classList.remove("show");
        overlay.classList.remove("active");

        document.body.classList.remove("menu-open");


        /* =================================================
           ESCONDER A CRUZ
        ================================================= */

        if (closeButton) {

            closeButton.style.display =
                "";

            closeButton.style.visibility =
                "";

            closeButton.style.opacity =
                "";

            closeButton.style.pointerEvents =
                "";

        }


        /* =================================================
           STATEMENT:

           O MENU ESTÁ FECHADO.
           A CRUZ JÁ NÃO ESTÁ VISÍVEL.
           AGORA E SÓ AGORA O HAMBURGER VOLTA.
        ================================================= */

        hamburger.classList.remove("hidden");

        hamburger.style.display =
            "flex";

        hamburger.style.visibility =
            "visible";

        hamburger.style.opacity =
            "1";

        hamburger.style.pointerEvents =
            "auto";

        hamburger.removeAttribute(
            "aria-hidden"
        );

    };


    /* =====================================================
       ESC FECHA O MENU
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape"
            ) {

                window.closeMenu();

            }

        }
    );


    /* =====================================================
       HOME
    ===================================================== */

    function isHome() {

        const path =
            window.location.pathname;

        return (
            path === "/" ||
            path === ""
        );

    }


    /* =====================================================
       PAGE TRANSITION
    ===================================================== */

    let navigating = false;


    function createTransition() {

        if (
            document.getElementById(
                "misuki-page-transition"
            )
        ) {

            return;

        }


        const transition =
            document.createElement(
                "div"
            );


        transition.id =
            "misuki-page-transition";


        document.body.appendChild(
            transition
        );

    }


    function pageEnter() {

        createTransition();


        document.documentElement.classList.add(
            "misuki-page-enter"
        );


        requestAnimationFrame(function () {
            document.documentElement.classList.remove("misuki-page-enter");
            document.documentElement.classList.add("misuki-page-ready");
        });

    }


    function pageLeave(url) {

        if (navigating) {
            return;
        }


        navigating = true;


        window.closeMenu();


        


        createTransition();


        document.documentElement.classList.remove(
            "misuki-page-ready"
        );


        document.documentElement.classList.add(
            "misuki-page-leaving"
        );


        setTimeout(function () {
                window.location.href = url;
            }, 140);

    }


    /* =====================================================
       INTERNAL LINKS
    ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                event.defaultPrevented ||
                event.button !== 0 ||
                event.ctrlKey ||
                event.shiftKey ||
                event.altKey ||
                event.metaKey
            ) {

                return;

            }


            const link =
                event.target.closest("a");


            if (!link) {
                return;
            }


            const href =
                link.getAttribute(
                    "href"
                );


            if (!href) {
                return;
            }


            if (
                href.startsWith("#") ||
                href.startsWith("mailto:") ||
                href.startsWith("tel:") ||
                href.startsWith("javascript:")
            ) {

                return;

            }


            if (
                link.hasAttribute(
                    "download"
                )
            ) {

                return;

            }


            let url;


            try {

                url =
                    new URL(
                        href,
                        window.location.href
                    );

            } catch {

                return;

            }


            if (
                url.origin !==
                window.location.origin
            ) {

                return;

            }


            if (
                url.href ===
                window.location.href
            ) {

                return;

            }


            event.preventDefault();


            pageLeave(
                url.href
            );

        }
    );


    /* =====================================================
       PAGE SHOW
    ===================================================== */

    window.addEventListener(
        "pageshow",
        function () {

            navigating = false;


            /* =============================================
               GARANTIR ESTADO INICIAL DO HAMBURGER
            ============================================= */

            const hamburger =
                document.querySelector(
                    ".hamburger"
                );


            const menu =
                document.getElementById(
                    "menu"
                );


            if (
                hamburger &&
                menu &&
                !menu.classList.contains(
                    "open"
                ) &&
                !menu.classList.contains(
                    "active"
                )
            ) {

                hamburger.classList.remove(
                    "hidden"
                );


                hamburger.style.display =
                    "flex";


                hamburger.style.visibility =
                    "visible";


                hamburger.style.opacity =
                    "1";


                hamburger.style.pointerEvents =
                    "auto";


                hamburger.removeAttribute(
                    "aria-hidden"
                );

            }


            pageEnter();

        }
    );


    /* =====================================================
       INIT
    ===================================================== */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            pageEnter,
            {
                once: true
            }
        );

    } else {

        pageEnter();

    }


})();

