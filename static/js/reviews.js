document.addEventListener("DOMContentLoaded", () => {
    const closeAllReviewMenus = () => {
        document.querySelectorAll(".review-actions-menu").forEach((menu) => {
            menu.hidden = true;
        });
        document.querySelectorAll(".review-actions-button").forEach((button) => {
            button.setAttribute("aria-expanded", "false");
        });
    };

    document.addEventListener("click", (event) => {
        const button = event.target.closest(".review-actions-button");

        if (button) {
            event.preventDefault();
            event.stopPropagation();

            const actions = button.closest(".review-actions");
            const menu = actions?.querySelector(".review-actions-menu");
            if (!menu) return;

            const wasOpen = menu.hidden === false;
            closeAllReviewMenus();

            if (!wasOpen) {
                menu.hidden = false;
                button.setAttribute("aria-expanded", "true");
            }
            return;
        }

        if (!event.target.closest(".review-actions-menu")) {
            closeAllReviewMenus();
        }
    });

    document.querySelectorAll(".review-actions-menu").forEach((menu) => {
        menu.addEventListener("click", (event) => event.stopPropagation());
    });

    document.addEventListener("click", (event) => {
        const edit = event.target.closest(".review-action-edit");
        if (!edit) return;

        const card = edit.closest(".review-card");
        const actions = edit.closest(".review-actions");
        const editForm = card?.querySelector(".review-edit-form");
        const text = card?.querySelector(".review-text");

        if (!editForm || !text) return;

        actions?.querySelector(".review-actions-menu")?.setAttribute("hidden", "");
        actions?.querySelector(".review-actions-button")?.setAttribute("aria-expanded", "false");
        text.hidden = true;
        editForm.hidden = false;

        const textarea = editForm.querySelector("textarea");
        if (textarea) {
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        }
    });

    document.addEventListener("click", (event) => {
        const cancel = event.target.closest(".review-edit-cancel");
        if (!cancel) return;

        const card = cancel.closest(".review-card");
        const form = cancel.closest(".review-edit-form");
        const text = card?.querySelector(".review-text");

        if (form && text) {
            form.hidden = true;
            text.hidden = false;
        }
    });
});
