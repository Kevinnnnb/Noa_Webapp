from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
import sqlite3

app = Flask(__name__)
last_uploaded_file = None
user_input = ""
last_update_time = 0
app.secret_key = "bZe60lQsBBurONE6dMVXeKkl4JDwQ4iRZLzJEdY4SMUtD4R7VqsaiVrwWaoo9NhP"

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

@app.route('/sign_in')
def sign_in():
    return render_template('sign_in.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    try:
        with sqlite3.connect('static/users.db') as conn:
            c = conn.cursor()
            # Vérifie si l'utilisateur ou l'email existe déjà
            c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
            existing_user = c.fetchone()
            if existing_user:
                flash('Username or email already exists')
                return redirect(url_for('sign_in'))
            # Insère le nouvel utilisateur
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    return redirect(url_for('home'))

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

@app.route('/coeur')
def coeur():
    gif_path = os.path.join('static', 'image.gif')
    # Remplacez 'your_gif.gif' par le nom de votre GIF
    if os.path.exists(gif_path):
        return send_file(gif_path, mimetype='image/gif')
    else:
        return "GIF not found", 404

@app.route('/database')
def database():
    password = request.args.get('password')
    if password != 'uc9z37h8mn':
        return Response('Unauthorized', 401)
    conn = sqlite3.connect('static/users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    data = c.fetchall()
    conn.close()
    return render_template('database.html', data=data)
