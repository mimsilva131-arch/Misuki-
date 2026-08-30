function openMenu() {


const menu = document.getElementById("menu");
const overlay = document.getElementById("overlay");

if (!menu || !overlay) {
    return;
}

menu.classList.add("open");
overlay.classList.add("show");

document.body.style.overflow = "hidden";


}

function closeMenu() {


const menu = document.getElementById("menu");
const overlay = document.getElementById("overlay");

if (!menu || !overlay) {
    return;
}

menu.classList.remove("open");
overlay.classList.remove("show");

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
