from flask import render_template, redirect, Flask, jsonify, request
from datetime import date
from datetime import datetime, timedelta
import requests
import logging.config
namespace = {'logs' : 'http://127.0.0.1:4001/' , 'spaces': 'http://127.0.0.1:5002/', 'canteen': 'http://127.0.0.1:5001/',
             'secretariat': 'http://127.0.0.1:5003/'}


app = Flask(__name__)


@app.route('/<path:path>/', methods=['POST', 'GET'])
def api(path):
    microservices = path.split('/')
    if request.method == 'GET':
        r= requests.get(namespace[microservices[0]] + path )
        return jsonify(r.json())
    else:
        r= requests.post((namespace[microservices[0]] + path), request.form)
        return jsonify(r.json())




if __name__ == '__main__':
    app.run()
