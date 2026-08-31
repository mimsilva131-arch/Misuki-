
/* =========================================================
   MISUKI — COOKIES.JS
   COOKIE BANNER
   ========================================================= */

(function () {

    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {


            /* =================================================
               ELEMENTS
            ================================================= */

            const banner =
                document.getElementById(
                    "misukiCookieBanner"
                );


            const accept =
                document.getElementById(
                    "misukiAccept"
                );


            const essential =
                document.getElementById(
                    "misukiEssential"
                );


            const deny =
                document.getElementById(
                    "misukiDeny"
                );


            const cookieName =
                "misuki_cookie_consent";


            /* =================================================
               SAFETY CHECK
            ================================================= */

            if (!banner) {

                return;

            }


            /* =================================================
               SHOW BANNER
            ================================================= */

            function showBanner() {

                banner.classList.add(
                    "show"
                );

            }


            /* =================================================
               HIDE BANNER
            ================================================= */

            function hideBanner() {

                banner.classList.remove(
                    "show"
                );

            }


            /* =================================================
               SAVE CONSENT
            ================================================= */

            function saveConsent(
                value
            ) {

                try {

                    localStorage.setItem(
                        cookieName,
                        value
                    );

                } catch (error) {

                    console.warn(
                        "Misuki cookies: unable to save consent.",
                        error
                    );

                }

            }


            /* =================================================
               SHOW ON EVERY PAGE LOAD
            ================================================= */

            /*
             * O banner aparece SEMPRE.
             *
             * A escolha anterior é guardada,
             * mas não impede o banner de aparecer
             * novamente quando a página é recarregada.
             */

            showBanner();


            /* =================================================
               ACCEPT ALL
            ================================================= */

            if (accept) {

                accept.addEventListener(
                    "click",
                    function () {

                        saveConsent(
                            "all"
                        );

                        hideBanner();

                    }
                );

            }


            /* =================================================
               ESSENTIAL ONLY
            ================================================= */

            if (essential) {

                essential.addEventListener(
                    "click",
                    function () {

                        saveConsent(
                            "essential"
                        );

                        hideBanner();

                    }
                );

            }


            /* =================================================
               DENY
            ================================================= */

            if (deny) {

                deny.addEventListener(
                    "click",
                    function () {

                        saveConsent(
                            "denied"
                        );

                        hideBanner();

                    }
                );

            }


        }
    );


})();

