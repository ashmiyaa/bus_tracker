const firebaseConfig = {
  apiKey: "AIzaSyAt2K47g68dusHtCCsfbj3JYc62qRmN6sA",
  authDomain: "icet-bus-tracker.firebaseapp.com",
  databaseURL: "https://icet-bus-tracker-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "icet-bus-tracker",
  storageBucket: "icet-bus-tracker.firebasestorage.app",
  messagingSenderId: "728890718928",
  appId: "1:728890718928:web:9af9f4f345ad17599bbcd5"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.database();