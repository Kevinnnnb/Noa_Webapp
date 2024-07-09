from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time
from PIL import Image


app = Flask(__name__)
last_uploaded_file = None  # Variable globale pour stocker le dernier fichier téléchargé

@app.route('/')
def hello_world():
    return render_template('index.html')

# @app.route('/longPoll')
# def long_poll():
#     while not(os.path.exists("test.txt")):
#         time.sleep(1)
#     testFile = open("test.txt","r")
#     return "done"

@app.route('/loadTest')
def load_test():
    with open('test.txt', 'w') as file:
        file.write("save test")
    return "wrote file"

@app.route('/deleteFile')
def delete_file():
    if os.path.exists("test.txt"):
        os.remove("test.txt")  # one file at a time
    return "deleted"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global last_uploaded_file
    print("Got upload")
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No image data"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static', filename)
            # Save the file temporarily
            temp_path = os.path.join('static', 'temp_' + filename)
            file.save(temp_path)

            # Optimize the image
            with Image.open(temp_path) as img:
                img = img.convert("RGB")  # Convert to RGB format
                optimized_path = os.path.join('static', 'optimized_' + filename)
                img.save(optimized_path, "JPEG", quality=95)  # Save as JPEG with higher quality

            # Remove the temporary file
            os.remove(temp_path)
            
            last_uploaded_file = 'optimized_' + filename  # Update the last uploaded file
            with open('test.txt', 'w') as file:
                file.write(optimized_path)
            return "done"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/longPoll', methods=['GET'])
def return_files_tut():
    if (os.path.exists("test.txt")):
        testFile = open("test.txt","r")
        fileName = testFile.readline()
        if os.path.exists("test.txt"):
            os.remove("test.txt")  # one file at a time
        try:
            response = make_response(send_file(fileName, download_name=os.path.basename(fileName)))
            response.headers['imgName'] = os.path.basename(fileName)
            return response
        except Exception as e:
            return str(e)
    return make_response("No new file", 304)

@app.route('/image')
def show_image():
    global last_uploaded_file
    if last_uploaded_file:
        return render_template('image.html', image_file=last_uploaded_file)
    else:
        return "aucune image n'a été envoyé pour l'instant"
