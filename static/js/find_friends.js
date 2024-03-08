import {getCookie} from "./cookie.js";

let searchInput = document.getElementById('searchFriend');
const foundFriendList = document.getElementById('foundFriends')
const foundFriendContainer = document.getElementById('foundFriendContainer')
searchInput.addEventListener("input", async function (event) {
    let url = `api/search/?q=` + event.target.value
    if (event.target.value) {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error('Something went wrong...')
        }
        const data = await response.json()
        const users = data.data
        if (users.length > 0) {
            foundFriendList.innerHTML = ''
            foundFriendContainer.style.display = ''
        }
        updateUserWithSuggestions(users)

    } else {
        foundFriendList.innerHTML = ''
        foundFriendContainer.style.display = 'none'
    }

})

function updateUserWithSuggestions(users) {
    users.forEach((user) => {
        foundFriendList.insertAdjacentHTML('beforeend', `<li class="list-group-item m-3">
    <a href="/accounts/profile/${user.username}/">
        <form method="post" action="/new/friend/${user.pk}/">
            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                    <div class="d-flex align-items-center justify-content-center">

                        <img src="${user.avatar}" alt="Avatar" class="avatar">
                        <div class="flex-grow-1 ">
                            <h5 class="mb-0"><strong>
                                ${user.username}</strong>
                            </h5>

                        </div>
                        <button class="btn btn-outline-primary align-self-end align-self-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                 fill="currentColor" class="bi bi-plus-circle-fill"
                                 viewBox="0 0 16 16">
                                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0M8.5 4.5a.5.5 0 0 0-1 0v3h-3a.5.5 0 0 0 0 1h3v3a.5.5 0 0 0 1 0v-3h3a.5.5 0 0 0 0-1h-3z"/>
                            </svg>
                        </button>
                    </div>
                </form>
                </a>
            </li>
`)
    })
}