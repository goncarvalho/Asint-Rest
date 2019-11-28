import json
from flask import render_template
from datetime import date
from datetime import datetime, timedelta
namespace = {'rooms': 'http://127.0.0.1:5002/spaces/', 'canteen': 'http://127.0.0.1:5001/canteen/'}

from flask import Flask
from flask import jsonify
import requests

days_of_week = []

app = Flask(__name__)


@app.route('/')
def mainpagerooms():
    return render_template("roomformtemplate.html")


@app.errorhandler(404)
def meal_not_found(error):
    return render_template('NoInfoMeal_404.html', title='404'), 404


@app.route('/spaces/<id>', methods=['GET'])
def get_space_api(id):
    r = requests.get(namespace['rooms'] + str(id))
    data = r.json()
    return jsonify(data)


@app.route('/spaces/<id>/<day>/<month>/<year>', methods=['GET'])
def get_space_api_day(id, day, month, year):
    r = requests.get(namespace['rooms'] + str(id) + '/' + str(day + '/' + month + '/' + year))
    data = r.json()
    return jsonify(data)


@app.route('/canteen/', methods=['GET'])
def get_canteen_api():
    r = requests.get(namespace['canteen'])
    data = r.json()
    return render_template("WeeklyCanteenTemplate.html", weekly_menu=data, days_of_week = days_of_week)


@app.route('/canteen/<day>/<month>/<year>', methods=['GET'])
def get_canteen_day_api(day, month, year):
    r = requests.get(namespace['canteen'] + str(day + '/' + month + '/' + year))
    data = r.json()
    try:
        if data['errorCode'] == 404:
            return meal_not_found(404)
    except:
        return render_template("WeeklyCanteenTemplate.html", weekly_menu=data)


def list_days_of_week():
    global days_of_week
    day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    print(str(start))
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i + 1)).strftime('%d/%m/%Y'))
    # print(days_of_week)

if __name__ == '__main__':
    list_days_of_week()
    app.run()
