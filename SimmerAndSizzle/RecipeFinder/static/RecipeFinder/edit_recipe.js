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

    setup();
    setupEditRecipeForm(recipe);
    document.querySelector("#new-step-button").onclick = addStep;
    document.querySelector("#new-ingredient-button").onclick = addIngredient;
    
    document.querySelector("#new-recipe-form").onsubmit = () => editRecipe(recipeID);
    document.querySelector("#delete-recipe-button").onclick = () => deleteRecipe(recipeID);
    document.getElementById('input-image').addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('uploaded-image').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
})