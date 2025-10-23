// static/feedback.js

document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll(".fb-unique-item");
    if (!items) return;

    items.forEach(item => {
        item.addEventListener("mouseenter", () => {
            item.style.background = "rgba(255,255,255,0.1)";
        });
        item.addEventListener("mouseleave", () => {
            item.style.background = "transparent";
        });
    });
});
