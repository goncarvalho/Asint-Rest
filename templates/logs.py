from flask import  Flask, request, jsonify
import json
from datetime import date
from datetime import datetime, timedelta

app = Flask(__name__)
list_of_logs=[]

@app.route('/<path:path>/')
def save_log(path):
    global list_of_logs


if __name__ == '__main__':
    app.run(port = 4001)