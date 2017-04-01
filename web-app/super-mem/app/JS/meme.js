var drawMeme = function (canvas, meme) {
    // Canvas Logic
    var ctx = canvas.getContext("2d");

    var keys = Object.keys(meme.objects);
    for (var j = 0; j < keys.length; j++) {
        var element = meme.objects[keys[j]];
        drawElement(ctx, element);
    }
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