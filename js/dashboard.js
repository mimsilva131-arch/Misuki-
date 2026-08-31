function openMenu() {

    const menu = document.getElementById("menu");
    const overlay = document.getElementById("overlay");
    const hamburger = document.getElementById("hamburger");

    if (!menu || !overlay) {
        return;
    }

    /* ABRIR MENU */
    menu.classList.add("open");
    overlay.classList.add("show");

    /* ESCONDER AS 3 BARRAS */
    if (hamburger) {
        hamburger.style.display = "none";
    }

    /* BLOQUEAR SCROLL */
    document.body.style.overflow = "hidden";
}


function closeMenu() {

    const menu = document.getElementById("menu");
    const overlay = document.getElementById("overlay");
    const hamburger = document.getElementById("hamburger");

    if (!menu || !overlay) {
        return;
    }

    /* FECHAR MENU */
    menu.classList.remove("open");
    overlay.classList.remove("show");

    /* MOSTRAR AS 3 BARRAS NOVAMENTE */
    if (hamburger) {
        hamburger.style.display = "flex";
    }

    /* LIBERTAR SCROLL */
    document.body.style.overflow = "";
}


document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {
            closeMenu();
        }

    }
);