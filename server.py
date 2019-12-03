from flask import render_template, redirect, Flask, jsonify
from datetime import date
from datetime import datetime, timedelta
import requests
namespace = {'rooms': 'http://127.0.0.1:5002/spaces/', 'canteen': 'http://127.0.0.1:5001/canteen/',
             'secretariats': 'http://127.0.0.1:5003/secretariat/',
             'server' : 'http://127.0.0.1:5000'}


days_of_week = []

app = Flask(__name__)


@app.errorhandler(404)
def meal_not_found(error):
    return render_template('NoInfoMeal_404.html', title='404'), 404


#API

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

# @app.route('/<microservice>/<str>')
# def html(microservice, str):
#     # Faz pedido
#
#     #printa pedido
#     return ()
@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods = ['GET'])
def get_canteen_api():
    r = requests.get(namespace['canteen'])
    data = r.json()
    return jsonify(data)


@app.route('/canteen/<path:date>', methods=['GET'])
def get_canteen_day_api(date):
    if date[0:1] == '0':
        date = date[1:]
    r = requests.get(namespace['canteen'] + date)
    data = r.json()
    try:
        if data['errorCode'] == 404:
            return meal_not_found(404)
    except:
        return jsonify(data)



#admin
@app.route('/admin', methods=['GET'])
@app.route('/admin/', methods=['GET'])
def launch_admin():

    # authenticate user first before rendering html with administration tools
    return NotImplementedError


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

#pages


@app.route('/')
def mainpagerooms():
    return render_template("MainPage.html")

@app.route('/getCanteen', methods=['GET'])
def getCanteen():
    r = requests.get(namespace['server']+'/canteen/')
    data = r.json()
    return render_template('CanteenTemplate.html', weekly_menu= data, days_of_week=days_of_week)

@app.route('/getCanteenDay/<path:date>', methods=['GET'])
def getCanteenByDay(date):
    r = requests.get(namespace['server'] + '/canteen/' + date)
    data = r.json()
    return render_template('CanteenTemplate.html', weekly_menu=data)


if __name__ == '__main__':
    list_days_of_week()
    app.run()
