const url = window.location.href.replace('http', 'ws')
const chatWebsocket = new WebSocket(url)
const chatBox = document.getElementById('chat-box')


chatWebsocket.onmessage = (events) => {
    let data = JSON.parse(events.data)
    if (data['type'] === 'text') {
        let chatBox = document.getElementById('chat-box')
        if (data['from_user'] === 'me') {
            chatBox.insertAdjacentHTML('beforeend', `<div class="message-container">
                                <div class="message message-user">
                                    <p>${data['message']}</p>
                                </div>
                            </div>`)
        } else {
            chatBox.insertAdjacentHTML('beforeend', `<div class="message-container">
                                <div class="message message-friend">
                                    <p>${data['message']}</p>
                                </div>
                            </div>`)
        }
        chatBox.scrollTo(0, chatBox.scrollHeight)
    } else if (data['type'] === 'user.status') {
        let status = data['status']
        const statusElement = document.getElementById('status')
        const statusFromElement = statusElement.textContent
        if (statusFromElement !== status) {
            statusElement.textContent = status
            if (status === 'offline') {
                statusElement.style.color = 'gray'
            } else {
                statusElement.style.color = 'green'
            }
        }
    }

}

let messageForm = document.getElementById('form-message')

messageForm.addEventListener('submit', (e) => {
    e.preventDefault()
    let message = e.target.message.value
    if (message) {
        chatWebsocket.send(JSON.stringify(message))
    }
    messageForm.reset()
})


window.addEventListener("load", (e) => {
    const chatBox = document.getElementById('chat-box')
    const newMessage = document.getElementById('new-message')
    if (newMessage) {
        chatBox.scrollTo(0, newMessage.offsetTop - 150)
    } else {
        chatBox.scrollTo(0, chatBox.scrollHeight)
    }
})

const chatBoxListener = (e) => {
    let currentHeight = e.target.scrollTop / (chatBox.scrollHeight - chatBox.clientHeight) * 100
    if (currentHeight <= 25) {
        const firstMessage = chatBox.firstElementChild.id
        chatBox.removeEventListener("scroll", chatBoxListener)
        fetch(`http://127.0.0.1:8000/api/v1${window.location.pathname}?before=${firstMessage.replace('message_', '')}`).then((response) => {
            return response.json()
        }).then(
            (data) => {
                if (data.messages.length >= 1) {
                    insertNewMessages(data.messages)
                    chatBox.addEventListener('scroll', chatBoxListener)
                } else {
                    chatBox.removeEventListener('scroll', chatBoxListener)
                }
            }
        )
    }
}

chatBox.addEventListener('scroll', chatBoxListener)

function insertNewMessages(messages) {
    messages.forEach((message) => {
        if (message.from_user === 'me') {
            chatBox.insertAdjacentHTML(
                'afterbegin',
                `<div class="message-container" id="message_${message.pk}">
                    <div class="message message-user">
                        <p>${message.message}</p>
                    </div>
                  </div>`
            )

        } else {
            chatBox.insertAdjacentHTML(
                'afterbegin',
                `<div class="message-container" id="message_${message.pk}">
                    <div class="message message-friend">
                        <p>${message.message}</p>
                    </div>
                  </div>`
            )
        }
    })
}


function insertAfterNewMessages(messages) {
    messages.forEach((message) => {
        if (message.from_user === 'me') {
            chatBox.insertAdjacentHTML(
                'beforeend',
                `<div class="message-container" id="message_${message.pk}">
                    <div class="message message-user">
                        <p>${message.message}</p>
                    </div>
                  </div>`
            )

        } else {
            chatBox.insertAdjacentHTML(
                'beforeend',
                `<div class="message-container" id="message_${message.pk}">
                    <div class="message message-friend">
                        <p>${message.message}</p>
                    </div>
                  </div>`
            )
        }
    })
}

const chatBoxAfterListener = (e) => {
    let currentHeightScroll = e.target.scrollTop / (chatBox.scrollHeight - chatBox.clientHeight) * 100
    if (75 <= currentHeightScroll) {
        const lastMessage = chatBox.lastElementChild.id
        console.log(lastMessage)
        chatBox.removeEventListener("scroll", chatBoxAfterListener)
        fetch(`http://127.0.0.1:8000/api/v1${window.location.pathname}?after=${lastMessage.replace('message_', '')}`).then((response) => {
            return response.json()
        }).then(
            (data) => {
                if (data.messages.length >= 1) {
                    insertAfterNewMessages(data.messages)
                    chatBox.addEventListener('scroll', chatBoxAfterListener)
                } else {
                    chatBox.removeEventListener('scroll', chatBoxAfterListener)
                }
            }
        )
    }
}


chatBox.addEventListener('scroll', chatBoxAfterListener)
