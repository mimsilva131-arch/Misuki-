/* =========================================================
   MISUKI — REVIEWS.JS
   REVIEW ACTIONS + REVIEW FORM
   ========================================================= */

(function () {
    "use strict";

    function closeAllReviewMenus() {
        document.querySelectorAll(".review-actions-menu").forEach(function (menu) {
            menu.hidden = true;
        });

        document.querySelectorAll(".review-actions-button").forEach(function (button) {
            button.setAttribute("aria-expanded", "false");
        });
    }

    function initReviews() {
        const form = document.querySelector('form[action="/reviews"]');

        if (form) {
            form.addEventListener("submit", function () {
                const button = form.querySelector('button[type="submit"]');
                if (!button) return;

                button.disabled = true;
                button.style.opacity = "0.7";
                button.style.cursor = "wait";
                // Close any open three-dot menu immediately when saving.
                closeAllReviewMenus();

                // Keep the translated label instead of replacing the button
                // with an untranslated loading string.
                const label = button.querySelector("[data-i18n]");
                if (label) {
                    label.textContent = "Guardar";
                } else {
                    button.textContent = "Guardar";
                }
            });
        }

        const textarea = document.querySelector('textarea[name="review"]');
        if (textarea) {
            textarea.addEventListener("input", function () {
                if (this.value.length > this.maxLength) {
                    this.value = this.value.substring(0, this.maxLength);
                }
            });
        }

        const rating = document.querySelector('select[name="rating"]');
        if (rating) {
            rating.addEventListener("change", function () {
                this.classList.add("review-rating-selected");
            });
        }

        // Delegated handlers keep this working even if review cards are re-rendered.
        document.addEventListener("click", function (event) {
            const actionButton = event.target.closest(".review-actions-button");

            if (actionButton) {
                event.preventDefault();
                event.stopPropagation();

                const actions = actionButton.closest(".review-actions");
                const menu = actions && actions.querySelector(".review-actions-menu");

                if (!menu) return;

                const wasOpen = !menu.hidden;
                closeAllReviewMenus();

                if (!wasOpen) {
                    menu.hidden = false;
                    actionButton.setAttribute("aria-expanded", "true");
                }
                return;
            }

            const editButton = event.target.closest(".review-action-edit");
            if (editButton) {
                event.preventDefault();
                event.stopPropagation();

                const card = editButton.closest(".review-card");
                const actions = card && card.querySelector(".review-actions");
                const editForm = card && card.querySelector(".review-edit-form");
                const reviewText = card && card.querySelector(".review-text");

                if (!editForm) return;

                if (actions) {
                    const menu = actions.querySelector(".review-actions-menu");
                    const button = actions.querySelector(".review-actions-button");
                    if (menu) menu.hidden = true;
                    if (button) button.setAttribute("aria-expanded", "false");
                }

                if (reviewText) reviewText.hidden = true;
                editForm.hidden = false;

                const editTextarea = editForm.querySelector("textarea");
                if (editTextarea) {
                    editTextarea.focus();
                    editTextarea.setSelectionRange(
                        editTextarea.value.length,
                        editTextarea.value.length
                    );
                }
                return;
            }

            const cancelButton = event.target.closest(".review-edit-cancel");
            if (cancelButton) {
                event.preventDefault();

                const card = cancelButton.closest(".review-card");
                const editForm = card && card.querySelector(".review-edit-form");
                const reviewText = card && card.querySelector(".review-text");

                if (editForm) editForm.hidden = true;
                if (reviewText) reviewText.hidden = false;
                return;
            }

            if (!event.target.closest(".review-actions")) {
                closeAllReviewMenus();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeAllReviewMenus();
            }
        });

        closeAllReviewMenus();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initReviews, { once: true });
    } else {
        initReviews();
    }
})();
