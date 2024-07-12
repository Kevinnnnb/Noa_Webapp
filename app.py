'''
L'idée de ce code c'est de faire en sorte que on va prendre le code qui fonctionne bien
pour le display et le poll d'îmage donc on va pas le toucher et ensuite on construira l'autre app web
qui permet de saisir des strings et de les fusiuonner en une seule app web (plus pratique pour le hosting) et aussi 
pour l'intro d'une nouvelle db pour gérer eventuellement les logs mais ça on verra.

A noter que la version du 12 juillet 2024 à 23h fonctionne nickel si jamais je casse tout
'''

from flask import Flask, flash, request, redirect, url_for, render_template, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import os
import time
import threading

app = Flask(__name__)
last_uploaded_file = None  # Variable globale pour stocker le dernier fichier téléchargé
user_input = ""  # Variable pour stocker l'entrée utilisateur
last_update_time = 0

#route d'acceuil
@app.route('/home')
def adieuuuu():
    return render_template('bonjour.html') #ne pas oublier de push ce code

#reoute d'input user pour les strings
@app.route('/message')
def index():
    return render_template('text.html',user_input=user_input)

#route d'accès pour l'esp32
@app.route('/update_input', methods=['POST'])
def update_input():
    global user_input, last_update_time
    user_input = request.form['user_input']
    last_update_time = time.time()
    return render_template('text.html', user_input=user_input)

@app.route('/get_user_input', methods=['GET'])
def get_user_input():
    global user_input
    return jsonify({'user_input': user_input})




'''
Attention depuis ici on touche plus hein ...
'''

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
    global last_uploaded_file  # Utiliser la variable globale
    print("Got upload")
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return "No image data"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static', filename)
            file.save(file_path)
            last_uploaded_file = filename  # Mettre à jour le dernier fichier téléchargé
            with open('test.txt', 'w') as file:
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
        return "Si tu ne vois aucune image qui s'affiche n'hésite pas à rafraichir la page"
