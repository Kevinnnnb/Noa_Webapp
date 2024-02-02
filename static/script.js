function submitForm(event,realSubmit) {
    event.preventDefault();
    // Read in file
    var file = document.getElementById('img').files[0];

    // Ensure it's an image
    if(file.type.match(/image.*/)) {
        console.log('An image has been loaded');
        console.log(file.type);
        
        // Load the image
        var reader = new FileReader();
        reader.onload = function (readerEvent) {
            if (file.type.match(/image.gif/)){
                console.log("Is gif");
                var myGif = gifDecode();
                var subReader = new FileReader();
                subReader.readAsDataURL(file);
                subReader.onload = function(){
                    console.log(subReader.result);
                    myGif.load(subReader.result);
                }
                
                myGif.onload = function(event){     // fires when loading is complete
                    //event.type   = "load"
                    //event.path   array containing a reference to the gif
                    // Resize the image
                var canvas = document.getElementById('preview'),
                max_size = 300,// TODO : pull max size from a site config
                width = myGif.width,
                height = myGif.height;
                if (width > height) {
                    // if (width > max_size) {
                        height *= max_size / width;
                        width = max_size;
                    // }
                } else {
                    // if (height > max_size) {
                        width *= max_size / height;
                        height = max_size;
                    // }
                }
                canvas.width = height;
                canvas.height = width;

                var ctx = canvas.getContext('2d');
                // ctx.translate(-width/2,-height/2);
                ctx.rotate(90 * Math.PI / 180);
                ctx.translate(0,-height);
                var count = 0;
                var gif = new GIF({
                    workers: 2,
                    quality: 100
                  });
                myGif.frames.forEach((item) => {
                    ctx.drawImage(item.image, 0, 0, width, height);
                    gif.options.height = canvas.height;
                    gif.options.width = canvas.width;
                    gif.addFrame(ctx, {copy: true,delay:item.delay});
                    console.log("Working");
                })
                gif.on('finished', function(blob) {
                    // window.open(URL.createObjectURL(blob));
                    // var dataUrl = canvas.toDataURL('image/gif');
                    // var resizedImage = dataURLToBlob(dataUrl);
                    console.log("Done and sending");
                    var newFile = new File([blob], "image.gif" ,{type:"image/gif"});
                    document.getElementById("preview").src = newFile;

                    count += 1;
                    console.log(newFile);
                    if(realSubmit){
                    var data = new FormData();
                    data.append('file', newFile);
                    try {
                        const response =  fetch("/upload", {
                        method: "POST",
                        // Set the FormData instance as the request body
                        body: data,
                        });
                    } catch (e) {
                        console.error(e);
                    }
                }
                  });
                  gif.render();
                }
                
            }else{
                var image = document.getElementById("preview");
                image.onload = function (imageEvent) {

                    // Resize the image
                    var canvas = document.getElementById('preview'),
                        max_size = 300,// TODO : pull max size from a site config
                        width = image.width,
                        height = image.height;
                    if (width > height) {
                        // if (width > max_size) {
                            height *= max_size / width;
                            width = max_size;
                        // }
                    } else {
                        // if (height > max_size) {
                            width *= max_size / height;
                            height = max_size;
                        // }
                    }
                    canvas.width = height;
                    canvas.height = width;
                    var ctx = canvas.getContext('2d');
                    // ctx.translate(-width/2,-height/2);
                    ctx.rotate(90 * Math.PI / 180);
                    ctx.translate(0,-height);
                    ctx.drawImage(image, 0, 0, width, height);
                    
                    
                    var dataUrl = canvas.toDataURL('image/png');
                    var resizedImage = dataURLToBlob(dataUrl);
                    var file = new File([resizedImage], "image.png" ,{type:"image/png"});
                    console.log(file);
                    if(realSubmit){
                    var data = new FormData();
                    data.append('file', file);
                    try {
                        const response =  fetch("/upload", {
                        method: "POST",
                        // Set the FormData instance as the request body
                        body: data,
                        });
                    } catch (e) {
                        console.error(e);
                    }
                    document.getElementById("preview").src = file;
                }
                    
                }
                image.src = readerEvent.target.result;
            }
        }
        reader.readAsDataURL(file);
    }
    return false;
};

/* Utility function to convert a canvas to a BLOB */
var dataURLToBlob = function(dataURL) {
    var BASE64_MARKER = ';base64,';
    if (dataURL.indexOf(BASE64_MARKER) == -1) {
        var parts = dataURL.split(',');
        var contentType = parts[0].split(':')[1];
        var raw = parts[1];

        return new Blob([raw], {type: contentType});
    }

    var parts = dataURL.split(BASE64_MARKER);
    var contentType = parts[0].split(':')[1];
    var raw = window.atob(parts[1]);
    var rawLength = raw.length;

    var uInt8Array = new Uint8Array(rawLength);

    for (var i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }

    return new Blob([uInt8Array], {filename:"image.png",type: contentType});
}
/* End Utility function to convert a canvas to a BLOB      */
















/*=========================================================================
End of gif reader

*/