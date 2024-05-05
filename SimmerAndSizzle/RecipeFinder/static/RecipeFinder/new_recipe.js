document.addEventListener("DOMContentLoaded", () => {
    // setupRecipeForm();
    document.querySelector("#new-step-button").onclick = addStep;
    document.querySelector("#new-ingredient-button").onclick = addIngredient;
    
    document.querySelector("#new-recipe-form").onsubmit = addRecipe;
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
});