
/* =========================================================
   MISUKI — REVIEWS.JS
   REVIEWS PAGE
   ========================================================= */

(function () {

    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {


            /* =================================================
               REVIEW FORM
            ================================================== */

            const form =
                document.querySelector(
                    'form[action="/reviews"]'
                );


            if (form) {

                form.addEventListener(
                    "submit",
                    function () {

                        const button =
                            form.querySelector(
                                'button[type="submit"]'
                            );


                        if (!button) {
                            return;
                        }


                        /*
                         * Evita múltiplos envios
                         * enquanto o pedido está a ser processado.
                         */

                        button.disabled = true;

                        button.style.opacity = "0.7";

                        button.style.cursor = "wait";

                        button.textContent =
                            "⭐ Submitting...";

                    }
                );

            }


            /* =================================================
               REVIEW TEXTAREA
            ================================================== */

            const textarea =
                document.querySelector(
                    'textarea[name="review"]'
                );


            if (textarea) {

                textarea.addEventListener(
                    "input",
                    function () {

                        /*
                         * Mantém o limite definido
                         * pelo HTML.
                         */

                        if (
                            this.value.length >
                            this.maxLength
                        ) {

                            this.value =
                                this.value.substring(
                                    0,
                                    this.maxLength
                                );

                        }

                    }
                );

            }


            /* =================================================
               RATING SELECT
            ================================================== */

            const rating =
                document.querySelector(
                    'select[name="rating"]'
                );


            if (rating) {

                rating.addEventListener(
                    "change",
                    function () {

                        this.classList.add(
                            "review-rating-selected"
                        );

                    }
                );

            }


        }
    );


})();

