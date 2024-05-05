document.addEventListener("DOMContentLoaded", () => {
    let search = window.location.search;
    let start = search.indexOf("cuisine=") + 8;
    let cuisineID = "";
    for (let i = start; i >= 0 && i < search.length; i++) {
        if (isNaN(search[i]))
            break;
        cuisineID += search[i];
    }
    cuisineID = Number(cuisineID);
    const cuisine = JSON.parse(localStorage.getItem("cuisines"))[cuisineID];

    start = search.indexOf("course=") + 7;
    let courseID = "";
    for (let i = start; i >= 0 && i < search.length; i++) {
        if (isNaN(search[i]))
            break;
        courseID += search[i];
    }
    courseID = Number(courseID);
    const course = JSON.parse(localStorage.getItem("courses"))[courseID];
    displayCourse(cuisine, course);
});