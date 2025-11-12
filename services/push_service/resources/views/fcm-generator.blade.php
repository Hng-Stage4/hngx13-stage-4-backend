<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FCM Token Generator</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    background: white;
    padding: 40px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    max-width: 600px;
    width: 100%;
}

h1 {
    color: #333;
    margin-bottom: 10px;
    font-size: 28px;
}

.subtitle {
    color: #666;
    margin-bottom: 30px;
    font-size: 14px;
}

.step {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    border-left: 4px solid #667eea;
}

.step-title {
    font-weight: bold;
    color: #667eea;
    margin-bottom: 8px;
}

.input-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    color: #555;
    font-weight: 500;
}

input {
    width: 100%;
    padding: 12px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.3s;
}

input:focus {
    outline: none;
    border-color: #667eea;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 14px 30px;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
}

button:active {
    transform: translateY(0);
}

button:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
}

.token-display {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin-top: 20px;
    display: none;
    border: 2px dashed #667eea;
}

.token-display.show {
    display: block;
}

.token-text {
    background: white;
    padding: 15px;
    border-radius: 8px;
    word-break: break-all;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #333;
    margin-bottom: 15px;
    max-height: 150px;
    overflow-y: auto;
}

.copy-btn {
    background: #28a745;
    padding: 10px 20px;
    width: auto;
    font-size: 14px;
}

.copy-btn:hover {
    box-shadow: 0 10px 20px rgba(40, 167, 69, 0.4);
}

.status {
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: none;
}

.status.show {
    display: block;
}

.status.error {
    background: #fee;
    color: #c33;
    border-left: 4px solid #c33;
}

.status.success {
    background: #efe;
    color: #3c3;
    border-left: 4px solid #3c3;
}

.status.info {
    background: #eef;
    color: #33c;
    border-left: 4px solid #33c;
}

code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
}
</style>
</head>
<body>
<div class="container">
    <h1>🔥 FCM Token Generator</h1>
    <p class="subtitle">Get your Firebase Cloud Messaging token for testing</p>

    <div class="step">
        <div class="step-title">Step 1: Add Your Firebase Config</div>
        <p style="font-size: 13px; color: #666;">Go to Firebase Console → Project Settings → General → Your apps → Web app config</p>
    </div>

    <div class="input-group">
        <label for="apiKey">API Key</label>
        <input type="text" id="apiKey" placeholder="AIzaSyC...">
    </div>
    <div class="input-group">
        <label for="projectId">Project ID</label>
        <input type="text" id="projectId" placeholder="my-project-12345">
    </div>
    <div class="input-group">
        <label for="messagingSenderId">Messaging Sender ID</label>
        <input type="text" id="messagingSenderId" placeholder="123456789">
    </div>
    <div class="input-group">
        <label for="appId">App ID</label>
        <input type="text" id="appId" placeholder="1:123456789:web:abc123">
    </div>
    <div class="input-group">
        <label for="vapidKey">VAPID Key (for Web Push)</label>
        <input type="text" id="vapidKey" placeholder="BK...">
    </div>

    <div class="status" id="status"></div>

    <button id="getTokenBtn" onclick="initializeFirebase()">Generate FCM Token</button>

    <div class="token-display" id="tokenDisplay">
        <h3 style="margin-bottom: 15px; color: #333;">✅ Your FCM Token:</h3>
        <div class="token-text" id="tokenText"></div>
        <button class="copy-btn" onclick="copyToken()">📋 Copy Token</button>
    </div>
</div>

<script type="module">
import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import { getMessaging, getToken } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js';
import { onMessage } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging.js';

window.initializeFirebase = async function() {
    const apiKey = document.getElementById('apiKey').value.trim();
    const projectId = document.getElementById('projectId').value.trim();
    const messagingSenderId = document.getElementById('messagingSenderId').value.trim();
    const appId = document.getElementById('appId').value.trim();
    const vapidKey = document.getElementById('vapidKey').value.trim();

    const statusDiv = document.getElementById('status');
    const tokenDisplay = document.getElementById('tokenDisplay');
    const getTokenBtn = document.getElementById('getTokenBtn');

    if (!apiKey || !projectId || !messagingSenderId || !appId || !vapidKey) {
        showStatus('Please fill in all fields', 'error');
        return;
    }

    try {
        getTokenBtn.disabled = true;
        getTokenBtn.textContent = 'Initializing...';

        const firebaseConfig = {
            apiKey,
            authDomain: `${projectId}.firebaseapp.com`,
            projectId,
            storageBucket: `${projectId}.appspot.com`,
            messagingSenderId,
            appId
        };

        const app = initializeApp(firebaseConfig);
        const messaging = getMessaging(app);

        // Handle foreground messages
        onMessage(messaging, (payload) => {
            console.log('Foreground message received: ', payload);

            // Show notification manually if browser supports it
            if (payload.notification && Notification.permission === 'granted') {
                new Notification(payload.notification.title, {
                    body: payload.notification.body,
                    icon: '/firebase-logo.png'
                });
            }
        });

        showStatus('Registering service worker...', 'info');
        const swRegistration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');

        // Wait for the SW to be active
        await navigator.serviceWorker.ready;

        showStatus('Requesting notification permission...', 'info');
        const permission = await Notification.requestPermission();

        if (permission === 'granted') {
            showStatus('Getting your FCM token...', 'info');

            const token = await getToken(messaging, {
                vapidKey,
                serviceWorkerRegistration: swRegistration
            });

            if (token) {
                document.getElementById('tokenText').textContent = token;
                tokenDisplay.classList.add('show');
                showStatus('Token generated successfully! 🎉', 'success');
                getTokenBtn.textContent = '✅ Token Generated';
            } else {
                showStatus('Failed to get token. Check VAPID key.', 'error');
                getTokenBtn.disabled = false;
                getTokenBtn.textContent = 'Try Again';
            }
        } else {
            showStatus('Notification permission denied.', 'error');
            getTokenBtn.disabled = false;
            getTokenBtn.textContent = 'Try Again';
        }
    } catch (error) {
        console.error(error);
        showStatus(`Error: ${error.message}`, 'error');
        getTokenBtn.disabled = false;
        getTokenBtn.textContent = 'Try Again';
    }
};

window.copyToken = function() {
    const tokenText = document.getElementById('tokenText').textContent;
    navigator.clipboard.writeText(tokenText).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = originalText; }, 2000);
    });
};

function showStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type} show`;
}
</script>
</body>
</html>
