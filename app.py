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
        os.remove("test.txt") # one file at a time
    return "deleted"

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Got upload")
    if request.method == 'POST':
        file = request.files.get('img')
        text = request.form.get('text')

        if not file and not text:
            return jsonify({"success": False, "message": "No image or text data"}), 400
        
        if file:
            if file.filename == '':
                return jsonify({"success": False, "message": "No selected file"}), 400
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('./', filename))
                with open('test.txt', 'w') as file:
                    file.write(os.path.join('./', filename))
                return jsonify({"success": True, "message": "Image uploaded successfully"})
        
        if text:
            with open('test.txt', 'w') as file:
                file.write(text)
            return jsonify({"success": True, "message": "Text uploaded successfully"})

    return jsonify({"success": False, "message": "Invalid request method"}), 405

@app.route('/longPoll', methods=['GET'])
def return_files_tut():
    if os.path.exists("test.txt"):
        with open("test.txt", "r") as testFile:
            content = testFile.readline()
        if os.path.exists("test.txt"):
            os.remove("test.txt") # one file at a time
        if os.path.isfile(content):
            try:
                response = make_response(send_file(content, download_name=os.path.basename(content)))
                response.headers['imgName'] = os.path.basename(content)
                return response
            except Exception as e:
                return str(e)
        else:
            return jsonify({"text": content})

    return make_response("No new file", 304)

if __name__ == '__main__':
    app.run(debug=True)
