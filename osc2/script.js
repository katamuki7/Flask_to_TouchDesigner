var osc = require("node-osc");
var firebase = require("firebase");


var firebaseConfig = {
  API_KEY
}
var dt = Date.now();

var app = firebase.initializeApp(firebaseConfig);
var oscClient = new osc.Client("localhost", 7000);
var messagesRef = app
  .database()
  .ref()
  .child("ems");


  messagesRef.on("child_added", function(snapshot) {
    var msg = snapshot.val();
  if (msg.em) {
    console.log("追加されたぞ", msg);
    oscClient.send("/", msg.em, function() {});
    return;
  }

  if (!msg.em) {
    console.log("URL or name is empty", msg);
    return;
  }

  oscClient.send("/", msg.em, function() {});
});



//var config = require("./config.js");
//var firebaseConfig = config.config;

/*
messagesRef.on("child_added", function(snapshot) {
  var msg = snapshot.val();
  if (dt > msg.time) {
    return;
  }
//  console.log("追加されたぞ", msg);
  oscClient.send("/", msg.url, msg.name, function() {});
});
*/