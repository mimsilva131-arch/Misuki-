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

    const TRAIL_INTERVAL = 30;
    const MAX_TRAIL_ELEMENTS = 16;
    const trailElements = [];

    document.addEventListener(
        "mousemove",
        function (event) {

            if (
                !isHome() ||
                window.matchMedia("(max-width: 800px), (hover: none), (pointer: coarse)").matches
            ) {
                return;
            }

            const x = event.clientX;
            const y = event.clientY;

            if (!mouseReady) {
                lastX = x;
                lastY = y;
                mouseReady = true;
                return;
            }

            const dx = x - lastX;
            const dy = y - lastY;
            const distance = Math.hypot(dx, dy);

            if (
                distance < 1 ||
                performance.now() - lastTrailTime < TRAIL_INTERVAL
            ) {
                return;
            }

            const angle =
                Math.atan2(dy, dx) * 180 / Math.PI;

            createTrail(
                x,
                y,
                angle,
                Math.max(
                    6,
                    Math.min(
                        20,
                        distance
                    )
                )
            );

            lastX = x;
            lastY = y;
            lastTrailTime = performance.now();

        },
        { passive: true }
    );


    function createTrail(
        x,
        y,
        angle,
        length
    ) {

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

        element.style.width =
            length + "px";

        element.style.setProperty(
            "--trail-angle",
            angle + "deg"
        );


        document.body.appendChild(element);
        trailElements.push(element);

        if (trailElements.length > MAX_TRAIL_ELEMENTS) {
            const oldest = trailElements.shift();
            if (oldest && oldest.parentNode) {
                oldest.remove();
            }
        }

        requestAnimationFrame(function () {
            element.style.opacity = "0";
        });

        setTimeout(function () {
            const index = trailElements.indexOf(element);
            if (index !== -1) {
                trailElements.splice(index, 1);
            }
            if (element.parentNode) {
                element.remove();
            }
        }, 500);
    }

    /* =====================================================
       PAGE TRANSITION
       ===================================================== */

    /* Page navigation is intentionally left to the browser.
       There is no artificial full-screen fade or timeout anymore:
       clicking a menu link starts navigation immediately. */

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