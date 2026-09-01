/* =========================================================
MISUKI — MENU.JS
SIDE MENU
========================================================= */

(function () {


"use strict";

function initMenu() {

    const hamburger = document.getElementById("hamburger");
    const menu = document.getElementById("menu");
    const overlay = document.getElementById("overlay");
    const menuClose = document.getElementById("menuClose");

    if (!hamburger || !menu || !overlay || !menuClose) {
        console.warn("⚠️ Misuki menu elements not found.");
        return;
    }

    function openMenu(event) {

        if (event) {
            event.preventDefault();
        }

        menu.classList.add("open");
        overlay.classList.add("show");
        document.body.classList.add("menu-open");

        hamburger.setAttribute("aria-expanded", "true");
        menu.setAttribute("aria-hidden", "false");

    }

    function closeMenu(event) {

        if (event) {
            event.preventDefault();
        }

        menu.classList.remove("open");
        overlay.classList.remove("show");
        document.body.classList.remove("menu-open");

        hamburger.setAttribute("aria-expanded", "false");
        menu.setAttribute("aria-hidden", "true");

    }

    function toggleMenu(event) {

        if (event) {
            event.preventDefault();
        }

        if (menu.classList.contains("open")) {
            closeMenu();
        } else {
            openMenu();
        }

    }

    hamburger.addEventListener("click", toggleMenu);

    menuClose.addEventListener("click", closeMenu);

    overlay.addEventListener("click", closeMenu);

    document.addEventListener("keydown", function (event) {

        if (
            event.key === "Escape" &&
            menu.classList.contains("open")
        ) {
            closeMenu();
        }

    });

    const links = menu.querySelectorAll("a");

    links.forEach(function (link) {

        link.addEventListener("click", function () {
            closeMenu();
        });

    });

    closeMenu();

    console.log("✅ Misuki menu initialized.");

}

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initMenu
    );

} else {

    initMenu();

}


})();
