/* =========================================================
   MISUKI - BOTTOM NAVIGATION
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const bottomNav = document.querySelector(".bottom-nav");

    if (!bottomNav) {
        return;
    }

    const currentPath = window.location.pathname;

    const items = bottomNav.querySelectorAll(".bottom-nav-item[data-path]");

    items.forEach((item) => {

        const path = item.dataset.path;

        if (!path) {
            return;
        }

        /*
         * Home
         */
        if (path === "/" && currentPath === "/") {
            item.classList.add("active");
            return;
        }

        /*
         * Other pages
         */
        if (path !== "/" && currentPath === path) {
            item.classList.add("active");
            return;
        }

        /*
         * Dashboard sub-pages
         * Example:
         * /dashboard
         * /manage/123
         */
        if (path === "/dashboard" && currentPath.startsWith("/manage/")) {
            item.classList.add("active");
        }

    });

    /*
     * Connect the bottom "Menu" button
     * to the existing hamburger menu.
     */

    const menuButton = bottomNav.querySelector(".bottom-nav-menu");
    const hamburger = document.getElementById("hamburger");

    if (menuButton && hamburger) {

        menuButton.addEventListener("click", () => {
            hamburger.click();
        });

    }

});