angular.module('uploadMemes').component('uploadMemes', {
    templateUrl: 'upload-memes/upload-memes.template.html',

    controller: ['$scope', '$routeParams', '$route', '$firebaseObject', '$firebaseArray', function uploadMemesController($scope, $routeParams, $route, $firebaseObject, $firebaseArray) {
        var self = this;
        var user = firebase.auth().currentUser;
        // self.uploadMemesRef = firebase.database().ref().child("users").child(user.uid).child("upload-memes");
        self.memeFile = null;
        self.rawMemeData = null;
        $scope.fileNameChanged = function (ele) {
            self.memeFile = ele.files[0];
            console.log(self.memeFile);
            var reader = new FileReader();
            reader.onload = function(progressEvent){
                self.rawMemeData = this.result;
                console.log(self.rawMemeData);
            };
            reader.readAsText(self.memeFile);
        }
    }]
});