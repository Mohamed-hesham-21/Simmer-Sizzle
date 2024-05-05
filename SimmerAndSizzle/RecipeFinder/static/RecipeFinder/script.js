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

function Recipe(id, name, description, cuisine, course, prepTime, cookTime, servings, carbs, protein, fats, ingredients=[], steps=[]) {
    this.id = id;
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

function Cuisine(name, info) {
    this.name = name;
    this.info = info;
}

function loadRecipes() {
    let mainView = document.querySelector(".main-view");
    let cardView = document.createElement("div");
    cardView.className = "card-view";
    mainView.appendChild(cardView);
    const recipes = JSON.parse(localStorage.getItem("recipes"));
    displayRecipeCards(cardView, recipes);
}

function loadFavourites() {
    let mainView = document.querySelector(".main-view");
    let cardView = document.createElement("div");
    cardView.className = "card-view";
    mainView.appendChild(cardView);
    const recipes = JSON.parse(localStorage.getItem("recipes"));
    let favourites = [];
    recipes.forEach(recipe => {
        if (recipe.liked)
            favourites.push(recipe);
    });
    displayRecipeCards(cardView, favourites);
}

function displayRecipeCards(container, recipes){
    recipes.forEach(recipe => {
        if (recipe.deleted)
            return;
        let card = document.createElement("div");
        card.className = "card-container";
        card.innerHTML = `
            <div class="card">
                <button data-id="${recipe.id}" class="card-fav-button${(recipe.liked ? " card-fav-button-filled" : "")}"></button>
                <img src="${(recipe.image ? recipe.image : "static/food.jpg")}" alt="simmer & sizzle">
                <div class="card-content">
                    <h3>${recipe.name}</h3>
                    <p>${recipe.description.slice(0, 100) + (recipe.description.length > 100 ? "..." : "")}</p>
                    <a href="recipe.html?id=${recipe.id}">
                        <button class="cool-button button-peach">Read More</button>
                    </a>
                </div>
            </div>
        `;
        let likeButton = card.querySelector("button");
        likeButton.onclick = () => toggleLike(likeButton);
        container.appendChild(card);
    })
}

function displayRecommendations(recipe) {
    const allRecipes = JSON.parse(localStorage.getItem("recipes"));
    let recipes = [];
    allRecipes.forEach(item => {
        if ((item.cuisine == recipe.cuisine || item.course == recipe.course) && item.id != recipe.id)
            recipes.push(item);
    });
    let container = document.querySelector("#recommendations-container");
    displayRecipeCards(container, recipes);
}

function toggleLike(button) {
    let recipes = JSON.parse(localStorage.getItem("recipes"));
    if (button.classList.contains("card-fav-button-filled")) {
        button.classList.remove("card-fav-button-filled");
        recipes[button.dataset.id].liked = false;
    }
    else {
        button.classList.add("card-fav-button-filled");
        recipes[button.dataset.id].liked = true;
    }
    
    localStorage.setItem("recipes", JSON.stringify(recipes));
}

function toggleSave(button) {
    let recipes = JSON.parse(localStorage.getItem("recipes"));
    if (button.innerHTML == "Save")
        button.innerHTML = "Unsave", recipes[button.dataset.id].liked = true;
    else
        button.innerHTML = "Save", recipes[button.dataset.id].liked = false;

    localStorage.setItem("recipes", JSON.stringify(recipes));
}

function setupRecipeForm() {
    let form = document.querySelector("#new-recipe-form");
    const cuisines = cuisineNames();
    const courses = JSON.parse(localStorage.getItem("courses"));
    const units = JSON.parse(localStorage.getItem("units"));

    displayOptionList(form.querySelector("[name=cuisine]"), cuisines);
    displayOptionList(form.querySelector("[name=course]"), courses);
    displayOptionList(form.querySelector("[name=unit]"), units);
}

function setupEditRecipeForm(recipe) {
    setupRecipeForm();
    let form = document.querySelector("#new-recipe-form");
    if (recipe.image)
        form.querySelector("[name=recipe-image]").setAttribute("src" , recipe.image);
    form.querySelector("[name=name]").value = recipe.name;
    form.querySelector("[name=description]").value = recipe.description;
    form.querySelector("[name=cuisine]").value = recipe.cuisine;
    form.querySelector("[name=course]").value = recipe.course;

    form.querySelector("[name=prepTime]").value = recipe.prepTime;
    form.querySelector("[name=cookTime]").value = recipe.cookTime;
    form.querySelector("[name=servings]").value = recipe.servings;

    form.querySelector("[name=carbs]").value = recipe.carbs;
    form.querySelector("[name=protein]").value = recipe.protein;
    form.querySelector("[name=fats]").value = recipe.fats;

    recipe.ingredients.forEach(ingredient => {
        let item = addItem("ingredient-list", `${ingredient.quantity} ${ingredient.unit} of ${ingredient.name}`);
        item.dataset.name = ingredient.name;
        item.dataset.quantity = ingredient.quantity;
        item.dataset.unit = ingredient.unit;
    });
    recipe.steps.forEach(step => addItem("step-list", step));
}


function displayOptionList(container, items) {
    items.forEach(item => {
        let option = document.createElement("option");
        option.value = item, option.innerHTML = item;
        container.appendChild(option);
    });
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
    let recipes = JSON.parse(localStorage.getItem("recipes"));
    let recipe = new Recipe(recipes.length, name, description, cuisine, course, prepTime, cookTime, servings, carbs, protein, fats, ingredients, steps);
    return recipe;
}

function addRecipe() {
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
            recipes.push(recipe);
            localStorage.setItem("recipes", JSON.stringify(recipes));
            window.location.href += `/../recipe.html?id=${recipe.id}`;
        });
        }
        catch(err) {
            recipes.push(recipe);
            localStorage.setItem("recipes", JSON.stringify(recipes));
            window.location.href += `/../recipe.html?id=${recipe.id}`;
        }
    }
    catch(err) {
        displayErrorMessage(err.message);
    }
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


function cuisineNames() {
    const cuisines = JSON.parse(localStorage.getItem("cuisines"));
    let names = [];
    cuisines.forEach(cuisine => {
        names.push(cuisine.name);
    });
    return names;
}

function validateRecipe(recipe) {
    const cuisines = cuisineNames();
    const courses = JSON.parse(localStorage.getItem("courses"));
    if (!recipe.name) 
        return "Missing recipe name";
    if (recipe.name.length > 100)
        return "Recipe name is too long";

    if (!recipe.description)
        return "Missing recipe description";
    if (recipe.description.length > 1000)
        return "Recipe description is too long";

    if (!cuisines.includes(recipe.cuisine))
        return "Invalid cuisine";
    if (!courses.includes(recipe.course))
        return "Invalid course";
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
    if (!units.includes(ingredient.unit))
        return "Invalid unit";
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

function displayRecipe(recipe) {
    let linkItems = [recipe.cuisine, recipe.course, recipe.name];
    displayLinkHistory(linkItems);
    document.querySelector("#recipe-image").setAttribute("src" , (recipe.image ? recipe.image : "static/food.jpg"));
    document.querySelector("#Recipe_Name").innerHTML = recipe.name;
    document.querySelector("#Recipe_Description").innerHTML = recipe.description;
    document.querySelector("#PrepTime").innerHTML = `${recipe.prepTime} mins`
    document.querySelector("#CookTime").innerHTML =  `${recipe.cookTime} mins`;
    document.querySelector("#TotalTime").innerHTML = `${recipe.prepTime + recipe.cookTime} mins`;
    document.querySelector("#Servings").innerHTML = `${recipe.servings}`;

    document.querySelector("#carbs").innerHTML = `${recipe.carbs}`;
    document.querySelector("#protein").innerHTML = `${recipe.protein}`;
    document.querySelector("#fats").innerHTML = `${recipe.fats}`;
    document.querySelector("#calories").innerHTML = `${(recipe.carbs + recipe.protein) * 4 + recipe.fats * 9}`;
    
    let ingredients = document.querySelector("#Ingredients");
    for (const ingredient of recipe.ingredients) {
        ingredients.innerHTML += 
        `<li><input type="checkbox" class="cool-form checkbox-bg"> <span>${ingredient.quantity}  ${ingredient.unit} of ${ingredient.name} </span></li>`;
    }
    let steps = document.querySelector("#Steps");
    for (const step of recipe.steps) {
        steps.innerHTML += `<li> ${step} </li>`;
    }
}


function displayLinkHistory(linkItems) {
    let linkList = document.querySelector("#link-history");
    linkItems.forEach(item => {
        linkList.innerHTML += `<li><a href="#" class="navbar-link-item norm-link"> ${item} </a></li>`
    })
}

function displayCuisine(cuisine, id) {
    let mainView = document.querySelector(".main-view");
    displayLinkHistory([cuisine.name]);
    const recipes = JSON.parse(localStorage.getItem("recipes"));
    const courses = JSON.parse(localStorage.getItem("courses"));
    mainView.innerHTML += `
        <div class="category-header"> ${cuisine.name} </div>
        <div class="cool-text-container"> ${cuisine.info} </div>
    `;
    let idx = 0;
    courses.forEach(course => {
        let container = document.createElement("div");
        container.className = "category-container";
        container.innerHTML = `
            <div class="row">
                <div class="fancy-header"> ${course} </div> 
                <a href="course.html?course=${idx++}&cuisine=${id}">
                    <button class="bland-button space"> See more </button>
                </a>
            </div>
        `;
        let currentRecipes = [];
        recipes.forEach(recipe => {
            if (recipe.cuisine == cuisine.name && recipe.course == course)
                currentRecipes.push(recipe);
        });
        let cardView = document.createElement("div");
        cardView.className = "card-view";
        container.appendChild(cardView);
        displayRecipeCards(cardView, currentRecipes);
        mainView.appendChild(container);
    });
}

function displayCourse(cuisine, course) {
    let mainView = document.querySelector(".main-view");
    displayLinkHistory([cuisine.name, course]);
    const allRecipes = JSON.parse(localStorage.getItem("recipes"));
    let recipes = [];
    allRecipes.forEach(recipe => {
        if (recipe.cuisine == cuisine.name && recipe.course == course)
            recipes.push(recipe);
    });
    let container = document.createElement("div");
    container.className = "card-view";
    displayRecipeCards(container, recipes);
    mainView.appendChild(container);
}


function displayIngredient(ingredient) {
    let mainView = document.querySelector(".main-view");
    mainView.innerHTML += `
        <div class="category-header"> Recipes with ${ingredient} </div>
    `;
    const allRecipes = JSON.parse(localStorage.getItem("recipes"));
    let recipes = [];
    allRecipes.forEach(recipe => {
        let found = false;
        recipe.ingredients.forEach(ing => {
            if (ing.name.toLowerCase() == ingredient.toLowerCase())
                found = true;
        })
        if (found)
            recipes.push(recipe);
    });
    let container = document.createElement("div");
    container.className = "card-view";
    displayRecipeCards(container, recipes);
    mainView.appendChild(container);
}


function searchRecipes(query) {
    let mainView = document.querySelector(".main-view");
    mainView.innerHTML += `
        <div class="category-header"> Search: ${query} </div>
    `;
    const allRecipes = JSON.parse(localStorage.getItem("recipes"));
    query = query.toLowerCase();
    let recipes = [];
    allRecipes.forEach(recipe => {
        let match = false;
        if (recipe.name.toLowerCase().includes(query) || recipe.cuisine.toLowerCase().includes(query) || recipe.course.toLowerCase().includes(query))
            match = true;
        recipe.ingredients.forEach(ingredient => {
            if (ingredient.name.toLowerCase().includes(query))
                match = true;
        });
        if (match)
            recipes.push(recipe);
    });
    let container = document.createElement("div");
    container.className = "card-view";
    displayRecipeCards(container, recipes);
    mainView.appendChild(container);
}


function setup() {
    let cuisines = [
        {
            "name": "Egyptian",
            "info": "Mother of all nations <3",
        },
        {
            "name": "Mexican",
            "info": "A lot of spicy food!",
        },
        {
            "name": "Other",
            "info": "Other not very populary cuisines",
        }
    ];
    let units = ["g", "kg", "lbs", "ml", "l", "cup", "teaspoon", "tablespoon", "loaf"];
    let courses = ["Main course", "Appetizer", "Dessert"];
    localStorage.setItem("cuisines", JSON.stringify(cuisines));
    localStorage.setItem("units", JSON.stringify(units));
    localStorage.setItem("courses", JSON.stringify(courses));

    if (!JSON.parse(localStorage.getItem("recipes")))
        localStorage.setItem("recipes", JSON.stringify([]));
}