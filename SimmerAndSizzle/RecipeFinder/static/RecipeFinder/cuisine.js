document.addEventListener("DOMContentLoaded", () => {
    let search = window.location.search;
    let start = search.indexOf("id=") + 3;
    let cuisineID = "";
    for (let i = start; i >= 0 && i < search.length; i++) {
        if (isNaN(search[i]))
            break;
        cuisineID += search[i];
    }
    cuisineID = Number(cuisineID);
    const cuisine = JSON.parse(localStorage.getItem("cuisines"))[cuisineID];
    displayCuisine(cuisine, cuisineID);
});