from flask import Flask, render_template
import json
from flask import jsonify
from datetime import date
from datetime import datetime, timedelta
import requests
from collections import OrderedDict
from operator import itemgetter

url_canteen = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
url_canteen_day = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen?day=')
weekly_meal = {}  # global list

app = Flask(__name__)


@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods=['GET'])
def get_weekly_meal():
    global weekly_meal
    if date.today().strftime("%d/%m/%Y") in weekly_meal.keys():
        return jsonify(weekly_meal )
    else:
        data = requests.get(url_canteen)
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        return jsonify(weekly_meal)

@app.route('/canteen/<day>/<month>/<year>', methods=['GET'])
def check_meal(day, month, year):
    global weekly_meal
    if day[0:1] == '0':
        day=day[1:2]
    try:
        return jsonify(weekly_meal[str(day + '/' + month + '/' + year)])
    except:
        print(url_canteen_day + str(day + '/' + month + '/' + year))
        data = requests.get(url_canteen_day + str(day + '/' + month + '/' + year))
        if data.text =='[]':
            return jsonify({'errorCode' : 404, 'message' : 'Route not found'})
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        return jsonify(weekly_meal[str(day + '/' + month + '/' + year)])



if __name__ == '__main__':
    app.run(port=5001)
