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
                console.log(splitString[splitString.length - 1]);
                if (splitString[splitString.length - 1] !== "meme") {
                    self.errorText.innerHTML = "Please Choose a .meme File";
                    return;
                }

                self.meme = JSON.parse(rawMemeData);
                var chooseFileControls = document.getElementById("choose-file-controls");
                var mainView = document.getElementById("main-view");
                mainView.removeChild(chooseFileControls);
                drawMeme(self.meme);
            };
            reader.readAsText(self.memeFile);
        };



        self.memeView = document.getElementById("meme-view");
        var drawMeme = function (meme) {
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

            // Canvas Logic
            var ctx = canvas.getContext("2d");

            var keys = Object.keys(meme.objects);
            for (var j = 0; j < keys.length; j++) {
                var element = meme.objects[keys[j]];
                drawElement(ctx, element);
            }


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
        var drawElement = function (ctx, element) {
            if (element.type === "image") {
                var imageURL = element.data;
                var img = new Image();
                img.src = imageURL;
                img.onload = function (event) {
                    ctx.drawImage(img, element.x, element.y, element.width, element.height);
                };
            } else if (element.type === "text") {
                var correctedHeight = element.height * 0.4;
                ctx.font = "" + correctedHeight + "px Arial";
                ctx.fillStyle = 'black';
                ctx.fillText(element.data, element.x, element.y + correctedHeight, element.width);
            }
        };
    }]
});