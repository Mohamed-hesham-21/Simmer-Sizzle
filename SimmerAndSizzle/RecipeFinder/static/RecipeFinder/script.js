document.addEventListener("DOMContentLoaded", () => {
    if (document.querySelector("#recipe-save-button")) {
        const button = document.querySelector("#recipe-save-button");
        button.onclick = () => toggleSave(button);
    }
});

function Recipe(name, description, cuisine, course, prepTime, cookTime, servings, carbs, protein, fats, ingredients=[], steps=[]) {
    this.name = name;
    this.description = description;
    this.cuisine = cuisine;
    this.course = course;

    this.prepTime = prepTime;
    this.cookTime = cookTime;
    this.servings = servings;

    this.carbs = carbs;
    this.protein = protein;
    this.fats = fats;

    this.ingredients = ingredients;
    this.steps = steps;
    this.liked = this.deleted = false;
    this.image = null;
}

function Ingredient(name, quantity, unit) {
    this.name = name;
    this.quantity = quantity;
    this.unit = unit;
}

async function toggleLike(button) {
    await sendLikeRequest(button.dataset.id);
    if (button.classList.contains("card-fav-button-filled"))
        button.classList.remove("card-fav-button-filled");
    else
        button.classList.add("card-fav-button-filled");
}

async function toggleSave(button) {
    await sendLikeRequest(getRecipeID())
    let diff = 1;
    if (button.innerHTML == 'Save')
        button.innerHTML = 'Unsave';
    else
        button.innerHTML = 'Save', diff *= -1;
    let countContainer = document.querySelector("#likes-count");
    countContainer.innerHTML = Number(countContainer.innerHTML) + diff;
}

async function sendLikeRequest(recipeID) {
    await fetch(`${window.location.origin}/api/recipes/${recipeID}/like`, {
        method: "POST",
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    }).then(response => response.json()).then(response => {
        if ("error" in response)
            window.location.href = window.location.origin + "/login";
    });
}

function displayErrorMessage(msg) {
    let container = document.querySelector("#error-container");
    let alert = document.createElement("div");
    alert.className = "cool-alert";
    alert.innerHTML = msg;
    container.innerHTML = "";
    container.appendChild(alert);
    setTimeout(function() {
        alert.style.display = 'block';
        setTimeout(function() {
            alert.style.animation = 'slideOut 0.3s forwards';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300); //hide animation
        }, 3000); // Hide stays
    }, 500); //display after 
}

async function getDataFromServer(keyword)
{
    const response = await fetch(window.location.origin + `/api/${keyword}`);
    return response.json();
}

class RecipeCardLoader {
    constructor(recipeAPI, infiniteScroll=true) {
        this.recipeAPI = recipeAPI;
        this.container = document.querySelector(`#${recipeAPI["id"]}`);
        this.cont = true;
        this.recipeAPI["request"]["page"] = 1;
        if (infiniteScroll) {
            window.onscroll = () => {
                if ((window.innerHeight + window.scrollY + 100 >= document.body.offsetHeight - document.body.clientHeight) && this.cont)
                    this.loadCards(), console.log("yay")
            };
        }
    }
    static transformJSON(str) {
        return str.replaceAll(`"`, ``).replaceAll(`'`, `"`);
    }
    async loadCards() {
        await fetch(window.location.origin + "/api/recipes", {
            method: "POST",
            body: JSON.stringify(this.recipeAPI["request"]),
        }).then(response => response.json()).then(response => {
            if ("recipeList" in response)
                this.displayCards(response["recipeList"]);
            else
                console.log(response), this.cont = false;
        });
        this.recipeAPI["request"]["page"]++;
    }
    displayCards(recipes){
        recipes.forEach(recipe => {
            let card = document.createElement("div");
            card.className = "card-container";
            card.innerHTML = `
                <div class="card">
                    <button data-id="${recipe.id}" class="card-fav-button${(recipe.liked ? " card-fav-button-filled" : "")}"></button>
                    <img src="${recipe.imageURL}" alt="simmer & sizzle">
                    <div class="card-content">
                        <h3>${recipe.name}</h3>
                        <p>${recipe.description.slice(0, 100) + (recipe.description.length > 100 ? "..." : "")}</p>
                        <a href="${recipe.url}">
                            <button class="cool-button button-peach">Read More</button>
                        </a>
                    </div>
                </div>
            `;
            let likeButton = card.querySelector("button");
            likeButton.onclick = () => toggleLike(likeButton);
            this.container.appendChild(card);
        })
    }
}

function getRecipeID() {
    return Number(document.querySelector("#recipe_id").innerHTML);
}
