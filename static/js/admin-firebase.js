// admin-firebase.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-messaging.js";

const firebaseConfig = {
  apiKey: "AIzaSyB1NSVarttEhUHtt0fGbj0m-vkp8I9wD-4",
  authDomain: "docacademy-notifications.firebaseapp.com",
  projectId: "docacademy-notifications",
  messagingSenderId: "1059328650722",
  appId: "1:1059328650722:web:3735cedac4a4cf828d5dbb"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// طلب إذن الإشعارات
Notification.requestPermission().then(permission => {
  if (permission === 'granted') {
    getToken(messaging, { vapidKey: "BHRHOL6nd4XZ3mFojAeVm_SIw72ncJ2YixLzAOPLHZSbEqbpKR6vdPq3oIcCezpTRDjKKaaU8FYN8v2uUX2A2m8" })
      .then((token) => {
        // إرسال token للسيرفر
        fetch('/save-fcm-token/', {
          method: 'POST',
          credentials: 'same-origin',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: token })
        });
      })
      .catch((err) => console.log('Error getting FCM token: ', err));
  }
});

// استقبال الرسائل أثناء عمل التطبيق
onMessage(messaging, payload => {
  console.log('Message received: ', payload);
  alert(`${payload.notification.title}\n${payload.notification.body}`);
});
