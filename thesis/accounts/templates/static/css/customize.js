let canvas = new fabric.Canvas('tshirt-canvas');
let paintMode = false;

function togglePaintMode() {
    paintMode = !paintMode;
    if (paintMode) {
        canvas.isDrawingMode = true;
        updateBrushColor(document.getElementById("brush-color").value);
        canvas.freeDrawingBrush.width = parseInt(document.getElementById("brush-size").value, 10) || 1;
        canvas.selection = false; // Disable object selection in paint mode
    } else {
        canvas.isDrawingMode = false;
        canvas.selection = true; // Enable object selection
    }
}

document.getElementById("toggle-paint-mode").addEventListener("click", function() {
    togglePaintMode();
});

document.getElementById("tshirt-color").addEventListener("change", function(){
    document.getElementById("tshirt-div").style.backgroundColor = this.value;
    if (!paintMode) {
        updateBrushColor(document.getElementById("brush-color").value);
    }
}, false);

document.getElementById("brush-color").addEventListener("input", function() {
    updateBrushColor(this.value);
});

document.getElementById("brush-size").addEventListener("change", function(){
    if (paintMode) {
        canvas.freeDrawingBrush.width = parseInt(this.value, 10) || 1;
    }
}, false);

document.getElementById("delete-paint-btn").addEventListener("click", function() {
    deletePaint();
});

document.getElementById('tshirt-custompicture').addEventListener("change", function(e){
    var reader = new FileReader();
    
    reader.onload = function (event){
        var imgObj = new Image();
        imgObj.src = event.target.result;

        imgObj.onload = function () {
            var img = new fabric.Image(imgObj);

            img.scaleToHeight(300);
            img.scaleToWidth(300); 
            canvas.centerObject(img);
            canvas.add(img);
            canvas.renderAll();
        };
    };

    if(e.target.files[0]){
        reader.readAsDataURL(e.target.files[0]);
    }
}, false);

document.addEventListener("keydown", function(e) {
    var keyCode = e.keyCode;

    if(keyCode == 46){
        console.log("Removing selected element on Fabric.js on DELETE key !");
        canvas.remove(canvas.getActiveObject());
    }
}, false);

document.getElementById('add-text-btn').addEventListener('click', function() {
    var textInput = document.getElementById('text-input').value.trim(); // Trim to remove spaces
    if (!textInput) {
        alert('Please enter text to add.');
        return; // Stop if input is empty
    }

    var font = document.getElementById('font-select').value || 'Arial'; // Default to Arial if empty
    var fontSize = parseInt(document.getElementById('font-size').value, 10) || 20; // Default to 20
    var textColor = document.getElementById('text-color').value || '#000000'; // Default to black

    var text = new fabric.Text(textInput, {
        fontFamily: font,
        fontSize: fontSize,
        fill: textColor,
        left: 100,
        top: 100
    });

    canvas.add(text);
    canvas.renderAll();
});


// Update color of selected text object
document.getElementById("text-color").addEventListener("input", function() {
    var activeObject = canvas.getActiveObject();
    if (activeObject && activeObject.type === 'text') {
        activeObject.set("fill", this.value); // Update color of selected text
        canvas.renderAll();
    }
});

function updateBrushColor(color) {
    canvas.freeDrawingBrush.color = color;
}

function deletePaint() {
    var objects = canvas.getObjects();
    var paintObjects = objects.filter(function(obj) {
        return obj.type === 'path';
    });
    paintObjects.forEach(function(obj) {
        canvas.remove(obj);
    });
    canvas.renderAll();
}