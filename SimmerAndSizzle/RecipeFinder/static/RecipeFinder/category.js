document.addEventListener("DOMContentLoaded",  async function() {
    let container = document.querySelector("#API");
    if (!container)
        return;
    container.parentNode.removeChild(container);
    let recipeAPI = JSON.parse(RecipeCardLoader.transformJSON(container.innerHTML))[0];
    let recipeCardLoader = new RecipeCardLoader(recipeAPI); 

    while (recipeCardLoader.cont && window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        await recipeCardLoader.loadCards();
    }
});