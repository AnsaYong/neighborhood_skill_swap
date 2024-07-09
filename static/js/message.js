console.log('message.js loaded');
document.getElementById('message-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const url = form.action;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
        },
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const messageHistory = document.getElementById('message-history');
            const newMessage = document.createElement('div');
            newMessage.classList.add('message');
            if (data.message.sender == '{{ request.user.username }}') {
                newMessage.classList.add('sent-message');
            } else {
                newMessage.classList.add('received-message');
            }
            newMessage.innerHTML = `<strong>${data.message.sender}:</strong> ${data.message.content} <br>
                <small class="text-muted">${data.message.timestamp}</small>`;
            messageHistory.appendChild(newMessage);
            form.reset();
            messageHistory.scrollTop = messageHistory.scrollHeight; // Scroll to bottom
        } else {
            alert('Error sending message');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error sending message');
    });
});