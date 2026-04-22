document.addEventListener("DOMContentLoaded", function(){
    const aiBubble = document.getElementById('aiBubble');
    const aiChatBox = document.getElementById('aiChatBox');
    const closeAiChat = document.getElementById('closeAiChat');

    closeAiChat.addEventListener("click", () => {
        aiChatBox.classList.remove("open");
    });

    aiBubble.addEventListener("click", () => {
        aiChatBox.classList.toggle("open");
    });

});
 

function sendMessage() {
    const input = document.getElementById('aiInput');
    const message = input.value;

    if (!message) return;

    // Display user message
    const messagesDiv = document.getElementById('aiMessages');
    messagesDiv.innerHTML += `<div class="user-message">${message}</div>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    input.value = "";
    showTypingIndicator();
    const startTime = Date.now();

    fetch("/ai", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        const elapsed = Date.now() - startTime;
        const minDelay =800;
        setTimeout(() => {
            hideTypingIndicator();
            messagesDiv.innerHTML += `<div class="ai-message">${data.response}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }, Math.max(minDelay - elapsed, 0));

    });
    
}

function showTypingIndicator(){
    const messagesDiv = document.getElementById('aiMessages');
    const typingDiv = document.createElement("div");
    typingDiv.id = "typingIndicator";
    typingDiv.className = "ai-message";
    typingDiv.textContent = "AI is typing";
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
function hideTypingIndicator(){
    const typing = document.getElementById("typingIndicator");
    if (typing) typing.remove();
}