document.addEventListener("DOMContentLoaded", () => {
    let itemList = [];
    document.querySelectorAll("#ingredient-list > li").forEach(item => itemList.push(item));
    document.querySelectorAll("#step-list > li").forEach(item => itemList.push(item));
    itemList.forEach(item => {
        item.querySelector("button").onclick = () => item.remove();
    });

    document.querySelector("#new-recipe-form").onsubmit = () => saveRecipe(true);
    document.querySelector("#delete-recipe-button").onclick = deleteRecipe;
    document.querySelector("#cancel-button").onclick = () => {
        history.back()
    }
});