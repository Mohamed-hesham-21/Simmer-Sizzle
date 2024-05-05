document.addEventListener("DOMContentLoaded", () => {
    let search = window.location.search;
    let start = search.indexOf("q=") + 2;
    let query = "";
    for (let i = start; i >= 0 && i < search.length; i++) {
        if (!(/[a-zA-Z+]/.test(search[i])))
            break;
        query += (search[i] == '+' ? " " : search[i]);
    }
    searchRecipes(query);
});