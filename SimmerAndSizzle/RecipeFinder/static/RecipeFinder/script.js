// document.addEventListener("DOMContentLoaded", () => {
//     if (document.querySelector("button.card-fav-button")) {
//         document.querySelectorAll("button.card-fav-button").forEach((button) => {
//             button.onclick = () => toggleLike(button);
//         });
//     }
//     let container = document.querySelector("#cuisine-list");
//     const cuisines = cuisineNames();
//     let idx = 0;
//     cuisines.forEach(cuisine => {
//         container.innerHTML += `
//         <a href="cuisine.html?id=${idx++}" class="navbar-link-item norm-link"> ${cuisine} </a>
//         `;
//     });
// });

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

function toggleLike(button) {
    if (button.classList.contains("card-fav-button-filled"))
        button.classList.remove("card-fav-button-filled");
    else
        button.classList.add("card-fav-button-filled");
    fetch(`${window.location.origin}/api/recipes/${button.dataset.id}/like`, {
        method: "POST",
    });
}

function toggleSave(button) {
    let recipes = JSON.parse(localStorage.getItem("recipes"));
    if (button.innerHTML == "Save")
        button.innerHTML = "Unsave", recipes[button.dataset.id].liked = true;
    else
        button.innerHTML = "Save", recipes[button.dataset.id].liked = false;

    localStorage.setItem("recipes", JSON.stringify(recipes));
}

function addStep() {
    let inputField = document.querySelector("#new-step-content");
    let content = inputField.value;

    const msg = validateStep(content);
    if (msg) {
        displayErrorMessage(msg);
        return;
    }

    addItem("step-list", content);
    inputField.value = "";
    inputField.focus();
}

function addIngredient() {
    let nameField = document.querySelector("#new-ingredient-name");
    let name = nameField.value;
    let quantity = Number(document.querySelector("#new-ingredient-quantity").value);
    let unit = document.querySelector("#new-ingredient-unit").value;

    const msg = validateIngredient(new Ingredient(name, quantity, unit));
    if (msg) {
        displayErrorMessage(msg);
        return;
    }

    let item = addItem("ingredient-list", `${quantity} ${unit} of ${name}`);
    item.dataset.name = name;
    item.dataset.quantity = quantity;
    item.dataset.unit = unit;
    nameField.value = "";
    nameField.focus();
}

function addItem(listID, content) {
    const list = document.querySelector(`#${listID}`);

    let newItem = document.createElement("li");
    let contentSpan = document.createElement("span");
    let removeButton = document.createElement("button");

    removeButton.onclick = () => removeButton.parentNode.remove();
    contentSpan.innerHTML = content;
    newItem.append(contentSpan, removeButton);
    list.appendChild(newItem); 
    return newItem
}

function getRecipeFromForm() {
    let form = document.querySelector("#new-recipe-form");
    let name = form.querySelector("[name=name]").value;
    let description = form.querySelector("[name=description]").value;
    let cuisine = form.querySelector("[name=cuisine]").value;
    let course = form.querySelector("[name=course]").value;
    let prepTime = Number(form.querySelector("[name=prepTime]").value);
    let cookTime = Number(form.querySelector("[name=cookTime]").value);
    let servings = Number(form.querySelector("[name=servings]").value);

    let carbs = Number(form.querySelector("[name=carbs]").value);
    let protein = Number(form.querySelector("[name=protein]").value);
    let fats = Number(form.querySelector("[name=fats]").value);

    let ingredientList = form.querySelector("#ingredient-list");
    let ingredients = [];
    for (let i = 0; i < ingredientList.children.length; i++) {
        let item = ingredientList.children.item(i);
        const name = item.dataset.name;
        const quantity = item.dataset.quantity;
        const unit = item.dataset.unit;
        const ingredient = new Ingredient(name, quantity, unit);
        ingredients.push(ingredient);
    }

    let stepList = form.querySelector("#step-list");
    let steps = [];
    for (let i = 0; i < stepList.children.length; i++) {
        let item = stepList.children.item(i);
        const content = item.innerText;
        steps.push(content);
    }
    let recipe = new Recipe(name, description, cuisine, course, prepTime, cookTime, servings, carbs, protein, fats, ingredients, steps);
    return recipe;
}

function addRecipe() {
    try {
        let recipe = getRecipeFromForm();
        let msg = validateRecipe(recipe);
        if (msg) {
            displayErrorMessage(msg);
            return false;
        }
        
        let imageInput = document.querySelector("#input-image");
        try {
            const reader = new FileReader();
            reader.readAsDataURL(imageInput.files[0]);
            reader.addEventListener("load" , () => {
                recipe.image = reader.result.split(",")[1];
            });
            sendRecipe(recipe);
        }
        catch(err) {
            sendRecipe(recipe);
        }
        return false;
    }
    catch(err) {
        displayErrorMessage(err.message);
    }
    return false;
}

function sendRecipe(recipe) {
    console.log(recipe);
    fetch('api/add_recipe', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe: recipe
        }),
    }).then(response => response.json()).then((response) => {
        if ("error" in response) {
            displayErrorMessage(response["error"]);
        }
        else {
            // window.location.href += `/../recipes/${response["recipe_id"]}`;
        }
    });
    return false;
}

function editRecipe(id) {
    try {
        let recipes = JSON.parse(localStorage.getItem("recipes"));
        let recipe = getRecipeFromForm();
        let msg = validateRecipe(recipe);
        if (msg) {
            displayErrorMessage(msg);
            return false;
        }
        let image;
        let getImage = document.querySelector("#input-image");
        const reader = new FileReader();
        try {
            reader.readAsDataURL(getImage.files[0]);
            reader.addEventListener("load" , () => {
            image = reader.result;
            recipe.image = image;
            recipe.id = id;
            recipes[id] = recipe;
            localStorage.setItem("recipes", JSON.stringify(recipes));
        });
        }
        catch(err) {
            recipe.image = recipes[id].image;
            recipe.id = id;
            recipes[id] = recipe;
            localStorage.setItem("recipes", JSON.stringify(recipes));
        }
    }
    catch(err) {
        displayErrorMessage(err.message);
    }
    return false;
}

function deleteRecipe(id) {
    let recipes = JSON.parse(localStorage.getItem("recipes"));
    recipes[id].deleted = true;
    localStorage.setItem("recipes", JSON.stringify(recipes));
}

function validateRecipe(recipe) {
    if (!recipe.name) 
        return "Missing recipe name";
    if (recipe.name.length > 100)
        return "Recipe name is too long";

    if (!recipe.description)
        return "Missing recipe description";
    if (recipe.description.length > 1000)
        return "Recipe description is too long";

    if (recipe.prepTime < 0)
        return "Invalid prep time";
    if (recipe.carbs < 0)
        return "Invalid carbs";
    if (recipe.protein < 0)
        return "Invalid protein";
    if (recipe.fats < 0)
        return "Invalid fats";
    if (recipe.cookTime <= 0)
        return "Invalid cook time";
    if (recipe.servings <= 0)
        return "Invalid servings";
    if (recipe.ingredients.length == 0)
        return "Ingredients list can't be empty";
    if (recipe.steps.length == 0)
        return "Steps list can't be empty";
    return "";
}

function validateIngredient(ingredient) {
    const units = JSON.parse(localStorage.getItem("units"));
    if (!ingredient.name)
        return "Ingredient name can't be empty";
    if (ingredient.name.length > 25)
        return "Ingredient name is too long";
    let valid = true;
    for (let i = 0; i < ingredient.name.length; i++)    
        if (!(/[a-zA-Z ]/.test(ingredient.name[i])))
            valid = false;
    if (!valid)
        return "Ingredient name can contain only alphabetic characters";
    if (ingredient.quantity <= 0)   
        return "Invalid quantity";
    return "";
}

function validateStep(step) {
    if (!step)
        return "step can't be empty";
    if (step.length > 500)
        return "step is too long";
    return "";
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

function validateLogin(username, password) {
    if (!username)
        return "Please provide your username";
    if (!password)
        return "Please provide your password";
    return "";
}

function validateRegister(username, email, password, confirmation) {
    if (!username)
        return "Please provide a username";
    if (!email)
        return "Please provide an e-mail";
    if (!email.match(/^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/))
        return "Invalid e-mail";
    if (!password)
        return "Please provide a password";
    if (!confirmation)
        return "Please rewrite your password";
    if (password != confirmation)
        return "Passwords don't match";
    return "";
}

function login() {
    const form = document.querySelector("#auth-form");
    let username = form.querySelector("[name=username]").value;
    let password = form.querySelector("[name=password]").value;
    
    const msg = validateLogin(username, password);
    if (msg) {
        displayErrorMessage(msg);
        return false;
    }
    fetch('api/login', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    }).then(response => response.json()).then((response) => {
        if ("error" in response) {
            displayErrorMessage(response["error"]);
        }
        else {
            window.location.href += "/..";
        }
    });
    return false;
}

function register() {
    const form = document.querySelector("#auth-form");
    let username = form.querySelector("[name=username]").value;
    let email = form.querySelector("[name=email]").value;
    let password = form.querySelector("[name=password]").value;
    let confirmation = form.querySelector("[name=confirmation]").value;
    let isAdmin = (form.querySelector("[name=is_admin]").value == 'on' ? true : false);

    const msg = validateRegister(username, email, password, confirmation);
    if (msg) {
        displayErrorMessage(msg);
        return false;
    }
    fetch('api/register', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            confirmation: confirmation,
            isAdmin: isAdmin,
        }),
    }).then(response => response.json()).then((response) => {
        if ("error" in response) {
            displayErrorMessage(response["error"]);
        }
        else {
            window.location.href += "/..";
        }
    });
    return false;
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
                if ((window.innerHeight + window.scrollY >= document.body.offsetHeight) && this.cont)
                    this.loadCards()
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
                this.cont = false;
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