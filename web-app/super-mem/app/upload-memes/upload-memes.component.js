angular.module('uploadMemes').component('uploadMemes', {
    templateUrl: 'upload-memes/upload-memes.template.html',

    controller: ['$scope', '$routeParams', '$route', '$firebaseObject', '$firebaseArray', function uploadMemesController($scope, $routeParams, $route, $firebaseObject, $firebaseArray) {
        var self = this;
        var user = firebase.auth().currentUser;
        self.memesRef = firebase.database().ref().child("memes");
        self.memeFile = null;
        self.rawMemeData = null;
        self.meme = null;
        self.errorText = document.getElementById("errorText");
        // console.log(self.errorText);
        $scope.fileNameChanged = function (ele) {
            self.memeFile = ele.files[0];
            // self.errorText = self.memeFile.name;
            var reader = new FileReader();
            reader.onload = function(progressEvent){
                var rawMemeData = this.result;
                rawMemeData = rawMemeData.replace(/,"$id":"(\\"|[^"])*","$priority":"(\\"[^"])*"/, '');

                var splitString = self.memeFile.name.split(".");
                if (splitString[splitString.length - 1] !== "meme") {
                    self.errorText.innerHTML = "Please Choose a .meme File";
                    return;
                }

                self.meme = JSON.parse(rawMemeData);
                var chooseFileControls = document.getElementById("choose-file-controls");
                var mainView = document.getElementById("main-view");
                mainView.removeChild(chooseFileControls);
                drawMemeOnPanel(self.meme);
            };
            reader.readAsText(self.memeFile);
        };



        self.memeView = document.getElementById("meme-view");
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
            canvas.style = "border:1px solid #DDDDDD;";

            drawMeme(canvas, meme);

            // canvas.style += " width: 300px;";
            // canvas.style += " height: 300px;";
            superpanel.appendChild(canvas);

            var button = document.createElement("a");
            button.className = "btn btn-info";
            button.innerHTML = "Upload meme to database";
            button.addEventListener("click", function () {
                sanitizedMeme = meme;
                delete sanitizedMeme.$id;
                delete sanitizedMeme.$priority;
                self.memesRef.push(meme);
                $route.reload();
            });

            panel.appendChild(superpanel);
            panel.appendChild(button);
            memeContainer.appendChild(panel);
            self.memeView.appendChild(memeContainer)
        };
    }]
});