document.addEventListener("DOMContentLoaded",  async function() {
    console.log("hey");
    let recipeAPI = {
        "id": "filtered-recipes-container",
        "request": {
            "order_by": "date_added",
        }
    };
    loadCards(recipeAPI);
    document.querySelector("#reset-btn").onclick = () => loadCards(recipeAPI);
    document.querySelector("#apply-btn").onclick =  applyFilters;
});

async function loadCards(recipeAPI) {
    document.querySelector(`#${recipeAPI["id"]}`).innerHTML = "";
    let recipeCardLoader = new RecipeCardLoader(recipeAPI); 
    while (recipeCardLoader.cont && window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        await recipeCardLoader.loadCards();
    }
}

async function applyFilters() {
    let cuisine = document.querySelector("#cuisine").value;
    let order = document.querySelector("#sort").value;
    let courses = [];
    document.querySelectorAll(".filter-option-course").forEach(option => {
        if (option.checked)
            courses.push(option.dataset.course);
    });
    recipeAPI = {
        "id": "filtered-recipes-container",
        "request": {
            "cuisine": cuisine,
            "course": courses,
            "order_by": order,
        }
    }
    loadCards(recipeAPI);
}