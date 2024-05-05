document.addEventListener("DOMContentLoaded", () => {
    let search = window.location.search;
    let start = search.indexOf("id=") + 3;
    let recipeID = "";
    for (let i = start; i >= 0 && i < search.length; i++) {
        if (isNaN(search[i]))
            break;
        recipeID += search[i];
    }
    recipeID = Number(recipeID);
    const recipe = JSON.parse(localStorage.getItem("recipes"))[recipeID];

    let button = document.querySelector("#recipe-save-button");
    button.innerHTML = (recipe.liked ? "Unsave" : "Save");
    button.dataset.id = recipeID;
    button.onclick = () => toggleSave(button);

    document.querySelector("#recipe-edit-button"). onclick = function() {
        window.location.search = "";
        window.location.href = window.location.href.replace("?", `/../edit_recipe.html?id=${recipeID}`);
    }

    displayRecipe(recipe);
    displayRecommendations(recipe);
});