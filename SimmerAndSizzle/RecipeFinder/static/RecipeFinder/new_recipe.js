document.addEventListener("DOMContentLoaded", function(){
    document.querySelector("#new-step-button").onclick = addStep;
    document.querySelector("#new-ingredient-button").onclick = addIngredient;
    
    document.querySelector("#new-recipe-form").onsubmit = () => saveRecipe();
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
    let modal = document.querySelector(`#cuisine-modal`);
    let name = modal.querySelector("[name=name]");
    let info = modal.querySelector("[name=info]");
    let addBtn = document.querySelector(`#add-cuisine-btn`);
    let closeBtn = modal.querySelector(".close");
    addBtn.onclick = () => modal.style.display = 'block';
    closeBtn.onclick = () => {
        modal.style.display = "none";
        name.value = "";
        info.value = "";
    }
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = "none";
            name.value = "";
            info.value = "";
        }
    };
    modal.querySelector("#new-cuisine-form").onsubmit = () => submitCuisine(modal);
});

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

function saveRecipe(edit=false) {
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
            reader.addEventListener("load" , (event) => {
            const imageData = event.target.result;
            recipe.image = imageData;
            sendRecipe(recipe, '/api/' + (edit ? `recipes/${getRecipeID()}/edit` : 'add_recipe'));
            });
        }
        catch(err) {
            sendRecipe(recipe, '/api/' + (edit ? `recipes/${getRecipeID()}/edit` : 'add_recipe'));
        }
        return false;
    }
    catch(err) {
        displayErrorMessage(err.message);
    }
    return false;
}

function sendRecipe(recipe, url) {
    fetch(window.location.origin + url, {
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
            window.location.href = window.location.origin + `/recipes/${response["recipe_id"]}`;
        }
    });
    return false;
}

function deleteRecipe() {
    const recipe_id = getRecipeID();
    fetch(window.location.origin + `/api/recipes/${recipe_id}/delete`, {
        method: "POST",
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    }).then(response => response.json()).then(response => {
        window.location.href = window.location.origin;
    });
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

function submitCuisine(modal) {
    let name = modal.querySelector("[name=name]");
    let info = modal.querySelector("[name=info]");
    fetch("api/add_cuisine", {
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        method: "POST",
        body: JSON.stringify({
            "name": name.value,
            "info": info.value,
        })
    }).then(response => response.json()).then(response => {
        if ("error" in response)
            displayErrorMessage(response["error"]);
        else {
            addCuisine(response["cuisine_id"], name);
            modal.style.display = "none";
            name.value = "";
            info.value = "";
        }
    });
    window.location.reload();
    return false;
}

function addCuisine(id, name) {
    let select = document.querySelector("[name=cuisine]");
    let option = document.createElement("option");
    option.value = id, option.innerHTML = name;
    select.appendChild(option);
}