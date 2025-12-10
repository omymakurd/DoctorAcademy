importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: "AIzaSyB1NSVarttEhUHtt0fGbj0m-vkp8I9wD-4",
  authDomain: "docacademy-notifications.firebaseapp.com",
  projectId: "docacademy-notifications",
  messagingSenderId: "1059328650722",
  appId: "1:1059328650722:web:3735cedac4a4cf828d5dbb"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  self.registration.showNotification(
    payload.notification.title,
    {
      body: payload.notification.body
    }
  );
});
