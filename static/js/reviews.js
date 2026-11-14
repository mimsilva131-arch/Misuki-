document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".review-actions").forEach((actions) => {
        const button = actions.querySelector(".review-actions-button");
        const menu = actions.querySelector(".review-actions-menu");
        if (!button || !menu) return;

        button.addEventListener("click", (event) => {
            event.stopPropagation();
            const open = !menu.hidden;
            document.querySelectorAll(".review-actions-menu").forEach((other) => { other.hidden = true; });
            document.querySelectorAll(".review-actions-button").forEach((other) => other.setAttribute("aria-expanded", "false"));
            menu.hidden = open;
            button.setAttribute("aria-expanded", String(!open));
        });

        const card = actions.closest(".review-card");
        const edit = actions.querySelector(".review-action-edit");
        const editForm = card ? card.querySelector(".review-edit-form") : null;
        const text = card ? card.querySelector(".review-text") : null;

        if (edit && editForm && text) {
            edit.addEventListener("click", () => {
                menu.hidden = true;
                button.setAttribute("aria-expanded", "false");
                text.hidden = true;
                editForm.hidden = false;
                const textarea = editForm.querySelector("textarea");
                if (textarea) {
                    textarea.focus();
                    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
                }
            });

            const cancel = editForm.querySelector(".review-edit-cancel");
            if (cancel) {
                cancel.addEventListener("click", () => {
                    editForm.hidden = true;
                    text.hidden = false;
                });
            }
        }
    });

    document.addEventListener("click", () => {
        document.querySelectorAll(".review-actions-menu").forEach((menu) => { menu.hidden = true; });
        document.querySelectorAll(".review-actions-button").forEach((button) => button.setAttribute("aria-expanded", "false"));
    });
});