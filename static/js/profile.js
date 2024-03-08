import {getCookie} from "./cookie.js";

const emailUrl = `http://127.0.0.1:8000/accounts/email/verified/`
const sendEmailButton = document.getElementById("send-email")
const profileDiv = document.getElementById('profile')

async function sendEmail() {
    const response = await fetch(emailUrl, {
        method: "POST",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken')
        }
    })
    if (!response.ok) {
        throw new Error('Something went wrong, try again')
    }
    const data = await response.json()
    if (data.status === 'Wait') {
        profileDiv.insertAdjacentHTML('afterbegin',
            `<p class='alert alert-warning' id='alert'>You have to wait before send a new mail.</p>`
        )
        setTimeout(() => {
            profileDiv.firstChild.remove()
        }, 3000)
    } else if (data.status === 'Success') {
        profileDiv.insertAdjacentHTML('afterbegin',
            `<p class='alert alert-success' id='alert'>You have to wait before send a new mail.</p>`
        )
        setTimeout(() => {
            profileDiv.firstChild.remove()
        }, 3000)
    }
}

function ifAlertExists() {
    const alert = document.getElementById('alert')
    if (alert !== null) {
        return true
    }
    return false
}

sendEmailButton.addEventListener('click', (e) => {
    if (!ifAlertExists()) {
        sendEmail()
    }
})


