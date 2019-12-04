from flask import Flask, render_template
import json
from flask import jsonify
from datetime import date
from datetime import datetime, timedelta
import requests
from collections import OrderedDict
from operator import itemgetter

url_canteen = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
url_canteen_day = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen?day="
weekly_meal = {}  # global list
days_of_week=[]

app = Flask(__name__)



@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods=['GET'])
def get_weekly_meal():
    global weekly_meal
    aux={}
    if date.today().strftime("%d/%m/%Y")[0:1] == '0':
        date_today = date.today().strftime("%d/%m/%Y")[1:]
    else:
        date_today = date.today().strftime("%d/%m/%Y")
    if date_today in weekly_meal.keys():
        for item in days_of_week:
            aux[item] = weekly_meal[item];
        return jsonify(aux)
    else:
        data = requests.get(url_canteen)
        if data.text == '[]':
            return jsonify({'errorCode': 404, 'message': 'Route not found'})
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
            aux[item['day']] = item['meal']
        return jsonify(aux)


@app.route('/canteen/<path:date>', methods=['GET'])
def check_meal(date):
    global weekly_meal
    aux={}
    if date[0:1] == '0':
        date = date[1:]
    if date in weekly_meal.keys():
        aux[date]=weekly_meal[date]
        return jsonify(aux)
    else:
        data = requests.get(url_canteen_day + date)
        if data.text == '[]':
            return jsonify({'errorCode': 404, 'message': 'Route not found'})
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        aux[date] = weekly_meal[date]
        return jsonify(aux)





def list_days_of_week():
    global days_of_week
    day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    print(str(start))
    if start.strftime('%d/%m/%Y')[0:1] == '0':
        days_of_week.append(start.strftime('%d/%m/%Y')[1:])
        for i in range(4):
            days_of_week.append((start + timedelta(days=i + 1)).strftime('%d/%m/%Y')[1:])
    else :
        days_of_week.append(start.strftime('%d/%m/%Y'))
        for i in range(4):
            days_of_week.append((start + timedelta(days=i + 1)).strftime('%d/%m/%Y'))
    # print(days_of_week)

if __name__ == '__main__':
    list_days_of_week()
    app.run(port=5001)
