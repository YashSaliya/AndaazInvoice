  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-app.js";
  import { getFirestore } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-firestore.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  export const firebaseConfig = {
    apiKey: "AIzaSyCWzp6-kj52hdmmhDfR810nJLLfJkrxS5I",
    authDomain: "ng-test-fb229.firebaseapp.com",
    databaseURL: "https://ng-test-fb229-default-rtdb.firebaseio.com",
    projectId: "ng-test-fb229",
    storageBucket: "ng-test-fb229.appspot.com",
    messagingSenderId: "841168642654",
    appId: "1:841168642654:web:c9a1ad16dddda7bfa88acf"
  };

  // Initialize Firebase
export const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);




