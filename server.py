import json
from flask import render_template

namespace={'rooms': 'http://127.0.0.1:5002/spaces/' , 'canteen': 'http://127.0.0.1:5001/canteen/'}

from flask import Flask
from flask import jsonify
import requests

app = Flask(__name__)

@app.route('/')
def mainpagerooms():
    return render_template("roomformtemplate.html")

@app.route('/spaces/<id>', methods=['GET'])
def get_space_api(id):
    r = requests.get(namespace['rooms'] + str(id))
    data = r.json()
    return jsonify(data)

@app.route('/spaces/<id>/<day>/<month>/<year>', methods=['GET'])
def get_space_api_day(id, day, month, year):
    r = requests.get(namespace['rooms'] + str(id) + '/' + str(day + '/'+ month + '/'+year))
    data = r.json()
    return jsonify(data)

@app.route('/canteen/', methods=['GET'])
def get_canteen_api():
    r = requests.get(namespace['canteen'])
    data = r.json()
    return jsonify(data)

if __name__ == '__main__':
    app.run()