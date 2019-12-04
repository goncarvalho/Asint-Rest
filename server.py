from flask import render_template, redirect, Flask, jsonify
from datetime import date
from datetime import datetime, timedelta
import requests
namespace = {'spaces': 'http://127.0.0.1:5002/', 'canteen': 'http://127.0.0.1:5001/',
             'secretariats': 'http://127.0.0.1:5003/'}


days_of_week = []

app = Flask(__name__)


#api

@app.route('/<path:path>/', methods=['GET'])
def api(path):
    microservices = path.split('/')
    r= requests.get(namespace[microservices[0]] + path )
    data = r.json()
    return jsonify(data)



@app.errorhandler(404)
def meal_not_found(error):
    return render_template('NoInfoMeal_404.html', title='404'), 404


@app.route('/getSpaces/<path:id>', methods=['GET'])
def get_space_api(id):
    r = requests.get(namespace['rooms'] + id)
    data = r.json()
    return jsonify(data)


@app.route('/getSpaces/<id>/<path:date>', methods=['GET'])
def get_space_api_day(id,date):
    r = requests.get(namespace['rooms'] + str(id) + '/' + date)
    data = r.json()
    return jsonify(data) # html


@app.route('/getCanteen/', methods=['GET'])
def get_canteen_api():
    r = requests.get(namespace['canteen'])
    data = r.json()
    return render_template("CanteenTemplate.html.html", weekly_menu=data)


@app.route('/getCanteen/<path:date>', methods=['GET'])
def get_canteen_day_api(day, month, year):
    r = requests.get(namespace['canteen'] + date)
    data = r.json()
    try:
        if data['errorCode'] == 404:
            return meal_not_found(404)
    except:
        return render_template("CanteenTemplate.html.html", weekly_menu=data)


@app.route('/admin', methods=['GET'])
@app.route('/admin/', methods=['GET'])
def launch_admin():


    # authenticate user first before rendering html with administration tools
    return NotImplementedError


if __name__ == '__main__':
    app.run()
