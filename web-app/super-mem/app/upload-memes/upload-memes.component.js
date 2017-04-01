angular.module('uploadMemes').component('uploadMemes', {
    templateUrl: 'upload-memes/upload-memes.template.html',

    controller: ['$routeParams', '$route', '$firebaseObject', '$firebaseArray', function uploadMemesController($routeParams, $route, $firebaseObject, $firebaseArray) {
        var self = this;
        var user = firebase.auth().currentUser;
        self.uploadMemesRef = firebase.database().ref().child("users").child(user.uid).child("upload-memes");
    }]
});