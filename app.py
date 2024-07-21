'''
A noter que la version du 12 juillet 2024 à 23h fonctionne nickel si jamais je casse tout
'''
from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time
import sqlite3

app = Flask(__name__)
last_uploaded_file = None
user_input = ""
last_update_time = 0

# Variables pour les statistiques
message_count = 0
image_count = 0

def validate(username, password):
    conn = sqlite3.connect('static/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return bool(result)

@app.route('/login')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if validate(username, password):
        return render_template("/bonjour.html")
    else:
        return render_template("/login_rate.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('static/users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
        existing_user = c.fetchone()
        
        if existing_user:
            conn.close()
            return render_template('sign_in.html', error="Nom d'utilisateur ou email déjà pris")
        
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('home'))
    
    return render_template('sign_in.html')

@app.route("/")
def log():
    return render_template("acceuil.html")

@app.route("/aide")
def config():
    return render_template("config.html")

@app.route('/home')
def adieuuuu():
    return render_template('bonjour.html')

@app.route('/message')
def index():
    global message_count
    message_count += 1
    return render_template('text.html', user_input=user_input)

@app.route('/update_input', methods=['POST'])
def update_input():
    global user_input, last_update_time, message_count
    user_input = request.form['user_input']
    last_update_time = time.time()
    return render_template('text.html', user_input=user_input)

@app.route('/get_user_input', methods=['GET'])
def get_user_input():
    global user_input
    return jsonify({'user_input': user_input})

@app.route('/poll', methods=['GET'])
def poll():
    global user_input
    return jsonify({'user_input': user_input})

@app.route('/delete_user_input', methods=['GET'])
def delete_user_input():
    global user_input
    user_input = ""
    return jsonify({'message': 'User input has been reset', 'user_input': user_input})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global message_count, image_count
    if request.method == 'POST':
        if 'reset' in request.form:
            message_count = 0
            image_count = 0
    return render_template('admin.html', message_count=message_count, image_count=image_count)

@app.route('/images')
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
    global last_uploaded_file, image_count
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No image data"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static', filename)
            file.save(file_path)
            last_uploaded_file = filename
            with open('test.txt', 'w') as file:
                file.write(file_path)
            image_count += 1
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
    if os.path.exists("test.txt"):
        testFile = open("test.txt", "r")
        fileName = testFile.readline()
        if os.path.exists("test.txt"):
            os.remove("test.txt")
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
        return render_template("/pasimage.html")

@app.route("/messages")
def message():
    global user_input
    if user_input != "":
        return render_template("message.html", user_input=user_input)
    else:
        return render_template("/pasimage.html")
