document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("button.card-fav-button").forEach((button) => {
        button.onclick = () => toggleLike(button);
    })
})


function toggleLike(button) {
    if (button.classList.contains("card-fav-button-filled")) {
        button.classList.remove("card-fav-button-filled");
    }
    else {
        button.classList.add("card-fav-button-filled");
    }
}