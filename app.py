from flask import Flask, render_template
import os
import time
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/longPoll')
def long_poll():
    while not(os.path.exists("test.txt")):
        time.sleep(1)
    testFile = open("test.txt","r")
    return "done"

@app.route('/loadTest')
def load_test():
    with open('test.txt', 'w') as file:
        file.write("save test")
    return "wrote file"

@app.route('/deleteFile')
def load_test():
    if os.path.exists("test.txt"):
        os.remove("test.txt") # one file at a time
    return "deleted"
