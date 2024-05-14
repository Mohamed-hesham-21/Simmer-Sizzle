document.addEventListener("DOMContentLoaded", function(){
    let container = document.querySelector("#API");
    if (!container)
        return;
    container.parentNode.removeChild(container);
    let recipesAPI = JSON.parse(RecipeCardLoader.transformJSON(container.innerHTML));
    recipesAPI.forEach(function(recipeAPI){
        let tempCardLoader = new RecipeCardLoader(recipeAPI, false);
        tempCardLoader.loadCards();
    });
});