document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');

    // Configure marked.js to create clickable links
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();

        if (message) {
            // Add user message to chat
            appendMessage('user', message);

            // Send message to server
            socket.emit('message', message);

            // Clear input
            userInput.value = '';
        }
    });

    // Handle server responses
    socket.on('response', function(data) {
        appendMessage('bot', data.message);
        scrollToBottom();
    });

    // Handle errors
    socket.on('error', function(data) {
        appendMessage('bot', data.message);
        scrollToBottom();
    });

    function appendMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Parse markdown for bot messages only
        if (type === 'bot') {
            // Convert asterisks to proper markdown
            content = content.replace(/\*\*(.*?)\*\*/g, '**$1**'); // Bold
            content = content.replace(/(?<!\*)\*(?!\*)([^\*]+)(?<!\*)\*(?!\*)/g, '_$1_'); // Italic
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});