document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('saveButton').addEventListener('click', () => {
        let remoteUrl = document.getElementById('remoteUrlInput').value;
        chrome.storage.local.set({ remoteurl: remoteUrl }, () => {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = 'Remote URL saved successfully.';
            messageDiv.classList.add('show');
            setTimeout(() => {
                messageDiv.classList.remove('show');
            }, 3000); // Hide the message after 3 seconds
        });
    });
});