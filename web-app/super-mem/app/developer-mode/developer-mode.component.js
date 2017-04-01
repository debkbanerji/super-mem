angular.module('developerMode').component('developerMode', {
    templateUrl: 'developer-mode/developer-mode.template.html',

    controller: ['$routeParams', '$route', '$firebaseObject', '$firebaseArray', function developerModeController($routeParams, $route, $firebaseObject, $firebaseArray) {
        var self = this;
        //var user = firebase.auth().currentUser;
        //self.developerModeRef = firebase.database().ref().child("users").child(user.uid).child("developer-mode");
        self.memesRef = firebase.database().ref().child("memes");
        self.memesArray = $firebaseArray(self.memesRef);
    }]
});