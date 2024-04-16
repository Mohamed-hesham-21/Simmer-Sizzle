document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("button.card-fav-button").forEach((button) => {
        button.onclick = () => toggleLike(button);
    });
    document.querySelector("#new-step-button").onclick = addStep;
    document.querySelector("#new-ingredient-button").onclick = addIngredient;
    
    document.querySelector("#ingredient-list").querySelectorAll("li").forEach(item => {
        item.querySelector("button").onclick = () => item.remove();
    });
    document.querySelector("#step-list").querySelectorAll("li").forEach(item => {
        item.querySelector("button").onclick = () => item.remove();
    });
})


function toggleLike(button) {
    if (button.classList.contains("card-fav-button-filled")) {
        button.classList.remove("card-fav-button-filled");
    }
    else {
        button.classList.add("card-fav-button-filled");
    }
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
}

function addStep() {
    let inputField = document.querySelector("#new-step-content");
    let content = inputField.value;
    inputField.value = "";
    inputField.focus();
    if (!content)
        return;
    addItem("step-list", content);
}


function addIngredient() {
    let name = document.querySelector("#new-ingredient-name").value;
    let quantity = document.querySelector("#new-ingredient-quantity").value;
    let unit = document.querySelector("#new-ingredient-unit").value;

    if (!name || !quantity || !unit)
        return;
    addItem("ingredient-list", `${quantity} ${unit} of ${name}`);
}