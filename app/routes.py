from flask import render_template, request, redirect, url_for, jsonify
from app import db
from app.models import Stats
from app import create_app

app = create_app()

last_uploaded_file = None  # Variable globale pour stocker le dernier fichier téléchargé
user_input = ""  # Variable pour stocker l'entrée utilisateur
last_update_time = 0

@app.route('/home')
def home():
    return render_template('bonjour.html')

@app.route('/message')
def index():
    stats = Stats.query.get(1)
    stats.increment_message_count()
    return render_template('text.html', user_input=user_input)

@app.route('/update_input', methods=['POST'])
def update_input():
    global user_input, last_update_time
    user_input = request.form['user_input']
    last_update_time = time.time()
    stats = Stats.query.get(1)
    stats.increment_message_count()
    return render_template('text.html', user_input=user_input)

@app.route('/get_user_input', methods=['GET'])
def get_user_input():
    global user_input
    return jsonify({'user_input': user_input})

@app.route('/poll', methods=['GET'])
def poll():
    global user_input
    return jsonify({'user_input': user_input})

@app.route('/delete_user_input',  methods=['GET'])
def delete_user_input():
    global user_input
    user_input = ""
    return jsonify({'message': 'User input has been reset', 'user_input': user_input})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    stats = Stats.query.get(1)
    if request.method == 'POST':
        if 'reset' in request.form:
            stats.reset_stats()
    return render_template('admin.html', message_count=stats.message_count, image_count=stats.image_count)

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
            file.save(file_path)
            last_uploaded_file = filename
            with open('test.txt', 'w') as file:
                file.write(file_path)
            stats = Stats.query.get(1)
            stats.increment_image_count()
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
        return "quelque chose c'est mal passé, recharge la page "
