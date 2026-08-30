document.addEventListener("DOMContentLoaded", () => {
    const hamburger = document.querySelector(".hamburger");
    const menu = document.querySelector(".menu");
    const closeButton = document.querySelector(".menu-close");
    const overlay = document.querySelector(".overlay");

    // Abrir menu
    function openMenu() {
        if (!menu) return;

        menu.classList.add("open");

        if (overlay) {
            overlay.classList.add("show");
        }

        document.body.style.overflow = "hidden";
    }

    // Fechar menu
    function closeMenu() {
        if (!menu) return;

        menu.classList.remove("open");

        if (overlay) {
            overlay.classList.remove("show");
        }

        document.body.style.overflow = "";
    }

    // Botão hamburger
    if (hamburger) {
        hamburger.addEventListener("click", openMenu);
    }

    // Botão X
    if (closeButton) {
        closeButton.addEventListener("click", closeMenu);
    }

    // Clicar fora do menu
    if (overlay) {
        overlay.addEventListener("click", closeMenu);
    }

    // Tecla ESC
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    // Fechar menu quando clicar num link
    if (menu) {
        const links = menu.querySelectorAll("a");

        links.forEach((link) => {
            link.addEventListener("click", closeMenu);
        });
    }
});