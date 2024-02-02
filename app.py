from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time
app = Flask(__name__)

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
        os.remove("test.txt") # one file at a time
    return "deleted"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("Got upload")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return "No image data"
            # return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return "No selected file"
            # return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join('./', filename))
            with open('test.txt', 'w') as file:
                file.write(os.path.join('./', filename))
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
            os.remove("test.txt") # one file at a time
        try:
            response = make_response(send_file(fileName, download_name=os.path.basename(fileName)))
            response.headers['imgName'] = os.path.basename(fileName)
            return response
        except Exception as e:
            return str(e)
    return make_response("No new file",304)