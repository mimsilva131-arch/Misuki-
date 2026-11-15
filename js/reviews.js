
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


            /* =================================================
               REVIEW ACTION MENUS
            ================================================== */

            document.addEventListener("click", function (event) {
                const actionButton = event.target.closest(".review-actions-button");

                if (actionButton) {
                    event.preventDefault();
                    event.stopPropagation();

                    const actions = actionButton.closest(".review-actions");
                    if (!actions) return;

                    const menu = actions.querySelector(".review-actions-menu");
                    if (!menu) return;

                    document.querySelectorAll(".review-actions-menu:not([hidden])").forEach(function (openMenu) {
                        if (openMenu !== menu) {
                            openMenu.hidden = true;
                            const openButton = openMenu.parentElement?.querySelector(".review-actions-button");
                            openButton?.setAttribute("aria-expanded", "false");
                        }
                    });

                    menu.hidden = !menu.hidden;
                    actionButton.setAttribute("aria-expanded", menu.hidden ? "false" : "true");
                    return;
                }

                const editButton = event.target.closest(".review-action-edit");
                if (editButton) {
                    event.preventDefault();

                    const card = editButton.closest(".review-card");
                    const editForm = card?.querySelector(".review-edit-form");
                    const actionsMenu = card?.querySelector(".review-actions-menu");
                    const actionsButton = card?.querySelector(".review-actions-button");

                    if (!editForm) return;

                    editForm.hidden = false;
                    if (actionsMenu) actionsMenu.hidden = true;
                    if (actionsButton) actionsButton.setAttribute("aria-expanded", "false");
                    editForm.querySelector("textarea")?.focus();
                    return;
                }

                const cancelButton = event.target.closest(".review-edit-cancel");
                if (cancelButton) {
                    event.preventDefault();

                    const card = cancelButton.closest(".review-card");
                    const editForm = card?.querySelector(".review-edit-form");
                    if (editForm) editForm.hidden = true;
                    return;
                }

                if (!event.target.closest(".review-actions")) {
                    document.querySelectorAll(".review-actions-menu:not([hidden])").forEach(function (menu) {
                        menu.hidden = true;
                        const button = menu.parentElement?.querySelector(".review-actions-button");
                        button?.setAttribute("aria-expanded", "false");
                    });
                }
            });

            document.addEventListener("keydown", function (event) {
                if (event.key !== "Escape") return;

                document.querySelectorAll(".review-actions-menu:not([hidden])").forEach(function (menu) {
                    menu.hidden = true;
                    const button = menu.parentElement?.querySelector(".review-actions-button");
                    button?.setAttribute("aria-expanded", "false");
                });
            });


        }
    );


})();

