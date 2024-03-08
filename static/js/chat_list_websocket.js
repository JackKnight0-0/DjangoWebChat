const url = `ws://${window.location.host}/`

const globalWebsocket = new WebSocket(url)

globalWebsocket.onmessage = (message) => {
    const data = JSON.parse(message.data)
    if (data['type'] === 'new.update') {
        const from_user = data['from_user']
        const message = data['message']
        const date = document.getElementById('date')
        const blockText = document.getElementById(`text-${from_user}`)
        const newMessageCount = document.getElementById('new-message-count')
        const userInfo = document.getElementById('user-info')
        if (newMessageCount && Number.parseInt(newMessageCount.textContent) < 99) {
            newMessageCount.innerText = Number.parseInt(newMessageCount.textContent) + 1
        } else if (!newMessageCount) {
            userInfo.insertAdjacentHTML("beforeend", `<div class="rounded-circle text-center" 
                                             style="margin-right: 10vh; width: 30px; height: 30px; background: gray"><p
                                                style="color: white" id="new-message-count">1</p></div>`)
        }
        const newDate = new Date()
        date.innerText = `${newDate.getHours()}:${newDate.getMinutes()}`
        blockText.textContent = message
    }

}