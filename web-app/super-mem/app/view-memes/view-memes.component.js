'use strict';
angular.module('viewMemes').component('viewMemes', {
    templateUrl: 'view-memes/view-memes.template.html',

    controller: ['$routeParams', '$route', '$firebaseObject', '$firebaseArray', function viewMemesController($routeParams, $route, $firebaseObject, $firebaseArray) {
        var self = this;
        // var user = firebase.auth().currentUser;
        self.memesRef = firebase.database().ref().child("memes");
        self.memesArray = $firebaseArray(self.memesRef);

        self.memeView = document.getElementById("meme-repeat");
        self.memesArray.$loaded()
            .then(function (arr) {
                for (var i = 0; i < arr.length; i++) {
                    var meme = arr[i];
                    drawMemeOnPanel(meme);
                }
            })
            .catch(function (error) {
                console.log("Error:", error);
            });

        var drawMemeOnPanel = function (meme) {
            var memeContainer = document.createElement("div");
            memeContainer.className = "col-xs-12";
            memeContainer.style = "text-align:center;";
            // memeContainer.className = "col-lg-2 col-md-4 col-sm-6 col-xs-6";
            var panel = document.createElement("div");
            panel.className = "container-fluid panel";
            var superpanel = document.createElement("div");
            superpanel.style = "margin-top: 10px; margin-bottom: 10px;";
            var canvas = document.createElement("canvas");
            canvas.style = "border:1px solid #000000;";

            var width = meme.width || 300;
            var height = meme.height || 300;

            canvas.width = width;
            canvas.height = height;

            drawMeme(canvas, meme);

            // canvas.style += " width: 300px;";
            // canvas.style += " height: 300px;";
            superpanel.appendChild(canvas);

            var button = document.createElement("a");
            button.className = "btn btn-info";
            button.innerHTML = "Download .meme file";
            button.addEventListener("click", function () {
                self.toJSON = '';
                self.toJSON = angular.toJson(meme);
                var blob = new Blob([self.toJSON], {type: "application/json;charset=utf-8;"});
                var downloadLink = angular.element('<a></a>');
                downloadLink.attr('href', window.URL.createObjectURL(blob));
                downloadLink.attr('download', meme.$id + '.meme');
                downloadLink[0].click();
            });

            var deleteButton = document.createElement("a");
            deleteButton.className = "btn btn-danger";
            deleteButton.innerHTML = "Delete Meme";
            deleteButton.addEventListener("click", function () {
                // self.toJSON = '';
                // self.toJSON = angular.toJson(meme);
                // var blob = new Blob([self.toJSON], {type: "application/json;charset=utf-8;"});
                // var downloadLink = angular.element('<a></a>');
                // downloadLink.attr('href', window.URL.createObjectURL(blob));
                // downloadLink.attr('download', meme.$id + '.meme');
                // downloadLink[0].click();
                var thisMemeRef = self.memesRef.child(meme.$id);
                thisMemeRef.set(null);
                self.memeView.removeChild(memeContainer);
            });

            panel.appendChild(superpanel);
            panel.appendChild(button);
            panel.appendChild(deleteButton);
            memeContainer.appendChild(panel);
            self.memeView.appendChild(memeContainer)
        };
    }]
});