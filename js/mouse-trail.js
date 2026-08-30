/* =========================================================
   MISUKI — MOUSE TRAIL + PAGE TRANSITIONS
   ========================================================= */

(function () {

    "use strict";


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

    let lastX = 0;
    let lastY = 0;

    let mouseReady = false;

    let lastTrailTime = 0;

    const TRAIL_INTERVAL = 22;


    document.addEventListener(
        "mousemove",
        function (event) {

            if (!isHome()) {
                return;
            }


            const x =
                event.clientX;

            const y =
                event.clientY;


            if (!mouseReady) {

                lastX = x;
                lastY = y;

                mouseReady = true;

                return;
            }


            const now =
                performance.now();


            if (
                now - lastTrailTime <
                TRAIL_INTERVAL
            ) {
                return;
            }


            const dx =
                x - lastX;

            const dy =
                y - lastY;


            const distance =
                Math.sqrt(
                    dx * dx +
                    dy * dy
                );


            if (distance < 2) {
                return;
            }


            /*
             * Criar segmentos contínuos
             * entre a posição anterior
             * e a atual.
             */

            const steps =
                Math.max(
                    1,
                    Math.ceil(
                        distance / 7
                    )
                );


            for (
                let i = 1;
                i <= steps;
                i++
            ) {

                const progress =
                    i / steps;


                const trailX =
                    lastX +
                    (x - lastX) *
                    progress;


                const trailY =
                    lastY +
                    (y - lastY) *
                    progress;


                createTrail(
                    trailX,
                    trailY
                );
            }


            lastX = x;
            lastY = y;

            lastTrailTime = now;

        },
        {
            passive: true
        }
    );


    function createTrail(x, y) {

        if (!isHome()) {
            return;
        }


        const element =
            document.createElement(
                "span"
            );


        element.className =
            "misuki-mouse-trail";


        element.style.left =
            x + "px";

        element.style.top =
            y + "px";


        document.body.appendChild(
            element
        );


        requestAnimationFrame(
            function () {

                element.style.opacity =
                    "0";

            }
        );


        setTimeout(
            function () {

                element.remove();

            },
            500
        );
    }


    /* =====================================================
       PAGE TRANSITION
       ===================================================== */

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

        createTransition();


        document.documentElement.classList.remove(
            "misuki-page-ready"
        );


        document.documentElement.classList.add(
            "misuki-page-enter"
        );


        setTimeout(
            function () {

                window.location.href =
                    url;

            },
            350
        );
    }


    /* =====================================================
       LINK INTERCEPTION
       ===================================================== */

    document.addEventListener(
        "click",
        function (event) {

            if (
                event.defaultPrevented ||
                event.button !== 0 ||
                event.metaKey ||
                event.ctrlKey ||
                event.shiftKey ||
                event.altKey
            ) {
                return;
            }


            const link =
                event.target.closest("a");


            if (!link) {
                return;
            }


            const href =
                link.getAttribute("href");


            if (
                !href ||
                href.startsWith("#") ||
                href.startsWith("javascript:") ||
                href.startsWith("mailto:") ||
                href.startsWith("tel:")
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


            if (
                link.hasAttribute("download")
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
       PAGESHOW
       ===================================================== */

    window.addEventListener(
        "pageshow",
        function () {

            pageEnter();

            mouseReady = false;

        }
    );


    /* =====================================================
       INIT
       ===================================================== */

    function init() {

        createTransition();

        pageEnter();

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            init
        );

    } else {

        init();

    }

})();