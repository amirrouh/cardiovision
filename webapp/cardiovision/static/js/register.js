// To detect when a user start typing in the field
const usernameField = document.querySelector('#usernameField');
const feedbackArea = document.querySelector('.invalid-feedback');
const emailField = document.querySelector('#emailField');
const emailfeedbackArea = document.querySelector('.emailfeedbackArea');
const passwordField = document.querySelector('#passwordField');
const usernamesuccessOutput = document.querySelector('.usernamesuccessOutput');
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const submitBtn = document.querySelector('.submit-btn');



const handleToggleInput = (e) => {
    if (showPasswordToggle.textContent === 'Show Password') {
        showPasswordToggle.textContent = 'Hide Password';

        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = 'Show Password';
        passwordField.setAttribute("type", "password");
    }

};



showPasswordToggle.addEventListener('click', handleToggleInput);



emailField.addEventListener('focusout', (e) => {
    const emailVar = e.target.value;


    emailField.classList.remove('is-invalid');
    feedbackArea.style.display = "none";

    if (emailVar.length > 0) {
        // Fetch api to server
        fetch('/authentication/validate-email', {
            body: JSON.stringify({ email: emailVar }),
            method: "POST",
        })
            .then(res => res.json())
            .then(data => {
                console.log('data', data);
                // check for username error
                if (data.email_error) {
                    submitBtn.setAttribute('disabled', 'disabled');
                    submitBtn.disabled = true;
                    emailField.classList.add('is-invalid');
                    feedbackArea.style.display = "block";
                    feedbackArea.innerHTML = `<p>${data.email_error}</p>`
                } else {
                    submitBtn.removeAttribute('disabled');
                }
            });
    }
});


usernameField.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value;

    usernamesuccessOutput.style.display = 'block';

    usernameField.classList.remove('is-invalid');
    feedbackArea.style.display = "none";

    if (usernameVal.length > 0) {
        // Fetch api to server
        fetch('/authentication/validate-username', {
            body: JSON.stringify({ username: usernameVal }),
            method: "POST",
        })
            .then(res => res.json())
            .then(data => {
                console.log('data', data);
                usernamesuccessOutput.style.display = 'none';
                // check for username error
                if (data.username_error) {
                    usernameField.classList.add('is-invalid');
                    feedbackArea.style.display = "block";
                    feedbackArea.innerHTML = `<p>${data.username_error}</p>`
                    submitBtn.disabled = true;
                } else {
                    submitBtn.removeAttribute('disabled');
                }
            });
    }
});
