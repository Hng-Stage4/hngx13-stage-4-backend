importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: "AIzaSyBmofN6RYNZXz6lWjh54Fm8Iu94IOyLYCY",
  authDomain: "hng-push-notification.firebaseapp.com",
  projectId: "hng-push-notification",
  storageBucket: "hng-push-notification.firebasestorage.app",
  messagingSenderId: "795956177225",
  appId: "1:795956177225:web:5e71f6ce99daf3718e1298"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png'
  };
  self.registration.showNotification(notificationTitle, notificationOptions);
});