
/* =========================================================
   MISUKI — MAIN.JS
   MENU + MOUSE TRAIL + PAGE TRANSITIONS
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
       MOUSE TRAIL
    ===================================================== */

    let previousX = null;
    let previousY = null;

    let trailLastTime = 0;

    const TRAIL_DELAY = 10;
    const TRAIL_DISTANCE = 3;


    document.addEventListener(
        "mousemove",
        function (event) {

            if (!isHome()) {
                return;
            }


            const mouseX =
                event.clientX;

            const mouseY =
                event.clientY;


            if (
                previousX === null ||
                previousY === null
            ) {

                previousX = mouseX;
                previousY = mouseY;

                return;

            }


            const now =
                performance.now();


            if (
                now - trailLastTime <
                TRAIL_DELAY
            ) {
                return;
            }


            const dx =
                mouseX - previousX;

            const dy =
                mouseY - previousY;


            const distance =
                Math.hypot(
                    dx,
                    dy
                );


            if (
                distance <
                TRAIL_DISTANCE
            ) {
                return;
            }


            createTrail(
                previousX,
                previousY,
                mouseX,
                mouseY,
                distance
            );


            previousX = mouseX;
            previousY = mouseY;

            trailLastTime = now;

        },
        {
            passive: true
        }
    );


    /* =====================================================
       CRIAR RASTO
    ===================================================== */

    function createTrail(
        x1,
        y1,
        x2,
        y2,
        distance
    ) {

        if (!isHome()) {
            return;
        }


        const line =
            document.createElement(
                "span"
            );


        line.className =
            "misuki-mouse-trail";


        const angle =
            Math.atan2(
                y2 - y1,
                x2 - x1
            ) *
            180 /
            Math.PI;


        line.style.left =
            x1 + "px";


        line.style.top =
            y1 + "px";


        line.style.width =
            Math.max(
                distance,
                4
            ) + "px";

        line.style.height = "1px";


        line.style.setProperty(
            "--trail-angle",
            angle + "deg"
        );


        document.body.appendChild(
            line
        );


        requestAnimationFrame(
            function () {

                line.classList.add(
                    "fade"
                );

            }
        );


        setTimeout(
            function () {

                if (
                    line.parentNode
                ) {

                    line.remove();

                }

            },
            450
        );

    }


    /* =====================================================
       RESET DO RASTO
    ===================================================== */

    function resetMouse() {

        previousX = null;
        previousY = null;

        trailLastTime = 0;


        document
            .querySelectorAll(
                ".misuki-mouse-trail"
            )
            .forEach(
                function (trail) {

                    trail.remove();

                }
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


        requestAnimationFrame(
            function () {

                requestAnimationFrame(
                    function () {

                        document.documentElement.classList.remove(
                            "misuki-page-enter"
                        );


                        document.documentElement.classList.add(
                            "misuki-page-ready"
                        );

                    }
                );

            }
        );

    }


    function pageLeave(url) {

        if (navigating) {
            return;
        }


        navigating = true;


        window.closeMenu();


        resetMouse();


        createTransition();


        document.documentElement.classList.remove(
            "misuki-page-ready"
        );


        document.documentElement.classList.add(
            "misuki-page-leaving"
        );


        setTimeout(
            function () {

                window.location.href =
                    url;

            },
            300
        );

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


            resetMouse();


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

