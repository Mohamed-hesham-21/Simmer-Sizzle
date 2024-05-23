document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#auth-form").onsubmit = login;
});

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

function validateLogin(username, password) {
    if (!username)
        return "Please provide your username";
    if (!password)
        return "Please provide your password";
    return "";
}
