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
    let targetX = 0;
    let targetY = 0;

    let mouseReady = false;
    let animationFrame = null;
    let lastTrailTime = 0;

    const TRAIL_INTERVAL = 16;
    const TRAIL_SPACING = 5;
    const FOLLOW_SPEED = 0.34;

    document.addEventListener(
        "mousemove",
        function (event) {

            if (!isHome()) {
                return;
            }

            targetX = event.clientX;
            targetY = event.clientY;

            if (!mouseReady) {
                lastX = targetX;
                lastY = targetY;
                mouseReady = true;
            }

            if (animationFrame === null) {
                animationFrame = requestAnimationFrame(updateTrail);
            }
        },
        { passive: true }
    );

    function updateTrail(now) {

        animationFrame = null;

        if (!mouseReady || !isHome()) {
            return;
        }

        lastX += (targetX - lastX) * FOLLOW_SPEED;
        lastY += (targetY - lastY) * FOLLOW_SPEED;

        const dx = targetX - lastX;
        const dy = targetY - lastY;
        const distance = Math.hypot(dx, dy);

        if (
            now - lastTrailTime >= TRAIL_INTERVAL &&
            distance > 1.2
        ) {
            const angle = Math.atan2(dy, dx) * 180 / Math.PI;
            const steps = Math.max(1, Math.ceil(distance / TRAIL_SPACING));

            for (let i = 1; i <= steps; i++) {
                const progress = i / steps;

                createTrail(
                    lastX + dx * progress,
                    lastY + dy * progress,
                    angle,
                    Math.max(5, Math.min(18, distance / steps))
                );
            }

            lastTrailTime = now;
        }

        if (
            Math.abs(targetX - lastX) > 0.5 ||
            Math.abs(targetY - lastY) > 0.5
        ) {
            animationFrame = requestAnimationFrame(updateTrail);
        }
    }


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