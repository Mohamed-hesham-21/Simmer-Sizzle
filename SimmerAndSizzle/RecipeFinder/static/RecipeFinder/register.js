document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#auth-form").onsubmit = register;
});

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