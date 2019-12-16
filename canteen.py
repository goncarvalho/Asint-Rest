from flask import Flask, jsonify, request
from datetime import date
from datetime import datetime, timedelta
import requests


url_canteen = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
url_canteen_day = "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen?day="

namespace = {'logs': 'http://127.0.0.1:5004/addlog'}

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


weekly_meal = {}  # global list
days_of_week = []
list_days_of_week()

app = Flask(__name__)


@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods=['GET'])
def get_weekly_meal():
    global weekly_meal
    aux = {}

    requests.post(namespace['logs'], json={'request': '/canteen',
                                           'user': request.host,
                                           'timestamp': datetime.now()})

    if date.today().strftime("%d/%m/%Y")[0:1] == '0':
        date_today = date.today().strftime("%d/%m/%Y")[1:]
    else:
        date_today = date.today().strftime("%d/%m/%Y")
    if date_today in weekly_meal.keys():
        for item in days_of_week:
            try:
                aux[item] = weekly_meal[item]
            except KeyError:
                # This most likely means the menu doesn't have 5 days. getting information from FENIX again:
                aux = {}
                data = requests.get(url_canteen)
                for item2 in data.json():
                    weekly_meal[item2['day']] = item2['meal']
                    aux[item2['day']] = item2['meal']
                return jsonify(aux)

        return jsonify(aux)
    else:
        data = requests.get(url_canteen)
        if data.text == '[]':
            return jsonify({'errorCode': 404, 'message': 'Route not found'})
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
            aux[item['day']] = item['meal']
        return jsonify(aux)


@app.route('/canteen/<path:day>', methods=['GET'])
def check_meal(day):
    global weekly_meal
    aux = {}

    requests.post(namespace['logs'], json={'request': '/canteen/' + day,
                                           'user': request.host,
                                           'timestamp': datetime.now()})

    if day[0:1] == '0':
        day = day[1:]
    if date in weekly_meal.keys():
        aux[day] = weekly_meal[day]
        return jsonify(aux)
    else:
        data = requests.get(url_canteen_day + day)
        if data.text == '[]':
            return jsonify({'errorCode': 404, 'message': 'Route not found'})
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        try:
            aux[day] = weekly_meal[day]
        except KeyError:
            return jsonify({'errorCode': 404, 'message': 'Day not in system'})
        return jsonify(aux)


if __name__ == '__main__':
    list_days_of_week()
    app.run(port=5001)
