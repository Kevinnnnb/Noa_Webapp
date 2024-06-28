from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)

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
        os.remove("test.txt")  # one file at a time
    return "deleted"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("Got upload")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files and 'text' not in request.form:
            return "No image or text data"

        if 'file' in request.files:
            file = request.files['file']
            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                return "No selected file"
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('./', filename))
                with open('test.txt', 'w') as file:
                    file.write(os.path.join('./', filename))
                return "done"
        elif 'text' in request.form:
            text = request.form['text']
            with open('test.txt', 'w') as file:
                file.write("text:" + text)
            return "done"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File or Text</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=text name=text>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/longPoll', methods=['GET'])
def return_files_tut():
    if os.path.exists("test.txt"):
        with open("test.txt", "r") as testFile:
            content = testFile.readline().strip()
        if os.path.exists("test.txt"):
            os.remove("test.txt")  # one file at a time
        if content.startswith("text:"):
            text_content = content[5:]  # Extract the text after "text:"
            response = make_response(text_content)
            response.headers['Content-Type'] = 'text/plain'
            return response
        else:
            fileName = content
            try:
                response = make_response(send_file(fileName, download_name=os.path.basename(fileName)))
                response.headers['imgName'] = os.path.basename(fileName)
                return response
            except Exception as e:
                return str(e)
    return make_response("No new file", 304)

if __name__ == '__main__':
    app.run(debug=True)
