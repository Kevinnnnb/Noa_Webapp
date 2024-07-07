from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/loadTest')
def load_test():
    with open('test.txt', 'w') as file:
        file.write("save test")
    return "wrote file"

@app.route('/deleteFile')
def delete_file():
    if os.path.exists("test.txt"):
        os.remove("test.txt")
    return "deleted"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("Got upload")
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No image data"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            with open('last_image.txt', 'w') as file:
                file.write(file_path)
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
def long_poll():
    if os.path.exists("test.txt"):
        with open("test.txt", "r") as testFile:
            fileName = testFile.readline().strip()
        if os.path.exists("test.txt"):
            os.remove("test.txt")
        try:
            response = make_response(send_file(fileName, download_name=os.path.basename(fileName)))
            response.headers['imgName'] = os.path.basename(fileName)
            return response
        except Exception as e:
            return str(e)
    return make_response("No new file", 304)

@app.route('/last_image', methods=['GET'])
def last_image():
    if os.path.exists('last_image.txt'):
        with open('last_image.txt', 'r') as f:
            file_path = f.readline().strip()
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return "Aucune image trouvée", 404
    return "Aucune image n'a été envoyée actuellement", 404

if __name__ == "__main__":
    app.run(debug=True)
