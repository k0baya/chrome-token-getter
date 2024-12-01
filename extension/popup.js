document.addEventListener('DOMContentLoaded', function () {
    chrome.storage.local.get(['remoteurl', 'location', 'codeVerifier'], function (data) {
        const accessTokenDiv = document.getElementById('accessToken');
        const refreshTokenDiv = document.getElementById('refreshToken');
        const sessionDiv = document.getElementById('session');
        
        if (data.remoteurl && data.location && data.codeVerifier) {
            const apiUrl = data.remoteurl.endsWith('/') ? `${data.remoteurl}auth/session` : `${data.remoteurl}/auth/session`;
            
            fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    location: data.location,
                    codeVerifier: data.codeVerifier
                })
            })
            .then(response => response.json())
            .then(result => {
                accessTokenDiv.textContent = result.access_token || 'No accessToken found';
                refreshTokenDiv.textContent = result.refresh_token || 'No refresh_token found';
                sessionDiv.textContent = JSON.stringify(result, null, 2);
            })
            .catch(error => {
                sessionDiv.textContent = 'Error fetching session: ' + error.message;
            });
        } else {
            sessionDiv.textContent = 'No URL or codeVerifier found';
        }
    });

    document.getElementById('closePrompt').addEventListener('click', function() {
        document.querySelector('.prompt-box').style.display = 'none';
    });
});