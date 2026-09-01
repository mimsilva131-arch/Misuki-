/* =========================================================
   MISUKI - COOKIE BANNER
   ========================================================= */

(function () {

    "use strict";

    const COOKIE_NAME = "misuki_cookie_consent";

    const banner = document.getElementById("misukiCookieBanner");
    const accept = document.getElementById("misukiAccept");
    const essential = document.getElementById("misukiEssential");
    const deny = document.getElementById("misukiDeny");


    /* =====================================================
       CHECK BANNER
    ===================================================== */

    if (!banner) {
        return;
    }


    /* =====================================================
       CHECK CURRENT BROWSER SESSION
    ===================================================== */

    let savedConsent = null;

    try {

        savedConsent = sessionStorage.getItem(COOKIE_NAME);

    } catch (error) {

        console.warn(
            "Misuki Cookies: sessionStorage unavailable.",
            error
        );

    }


    /* =====================================================
       ALREADY CHOSEN DURING THIS SESSION
    ===================================================== */

    if (
        savedConsent === "all" ||
        savedConsent === "essential" ||
        savedConsent === "denied"
    ) {

        banner.style.display = "none";

        return;
    }


    /* =====================================================
       SHOW BANNER
    ===================================================== */

    banner.style.display = "block";


    /* =====================================================
       SAVE SESSION CONSENT
    ===================================================== */

    function saveConsent(value) {

        try {

            sessionStorage.setItem(
                COOKIE_NAME,
                value
            );

        } catch (error) {

            console.warn(
                "Misuki Cookies: unable to save session consent.",
                error
            );

        }

        banner.style.display = "none";
    }


    /* =====================================================
       ACCEPT ALL
    ===================================================== */

    if (accept) {

        accept.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                saveConsent("all");

            }
        );

    }


    /* =====================================================
       ESSENTIAL ONLY
    ===================================================== */

    if (essential) {

        essential.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                saveConsent("essential");

            }
        );

    }


    /* =====================================================
       DENY
    ===================================================== */

    if (deny) {

        deny.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                saveConsent("denied");

            }
        );

    }

})();