from flask import render_template, redirect, Flask, jsonify
from datetime import date
from datetime import datetime, timedelta
import requests
from flask import request
import logging.config
namespace = {'api' : 'http://127.0.0.1:5000/'}


days_of_week = []

app = Flask(__name__)
logger = logging.getLogger("myapp")


# PAGES
@app.errorhandler(404)
def meal_not_found(error):
    return render_template('NoInfoMeal_404.html', title='404'), 404


@app.route('/spaces/<path:id>', methods=['GET'])
def get_space_api(id):
    r = requests.get(namespace['api'] + 'spaces' + '/' + id)
    data = r.json()
    #return jsonify(data)
    return render_template("RoomsTemplate.html", rooms_events = data, days_of_week = days_of_week)


@app.route('/spaces/<id>/<path:date>', methods=['GET'])
def get_space_api_day(id,date):
    r = requests.get(namespace['api'] + 'spaces' + '/' + str(id) + '/' + date)
    data = r.json()
    return render_template("RoomsTemplate.html", rooms_events = data, days_of_week = [date])


@app.route('/secretariat/')
def rendersecretariates():
    return render_template('SecretariatsTemplate.html')


@app.route('/secretariat/add', methods=['POST'])
def add_secretariat_api():
    if request.method == "POST":
        r = requests.post(namespace['api'] +  'secretariat' + '/add', request.form)
        return render_template('AddSecretariateResponse.html', secretariate_added = r.json())

@app.route('/secretariat/ident', methods=['POST'])
def show_secretariat_api():
    if request.method == "POST":
        r = requests.post(namespace['api'] +  'secretariat' + '/ident', request.form)
        return render_template('ShowSecretariate_id.html', secretariateid = r.json())

@app.route('/secretariat/delete/ident', methods=['POST'])
def remove_secretariat_api():
    if request.method == "POST":
        r = requests.post(namespace['api'] +  'secretariat' + '/delete/ident', request.form)
        return render_template('ShowSecretariatesAfterRemove.html', secretariate_added = r.json())

@app.route('/canteen/', methods=['GET'])
def get_canteen_api():
    r = requests.get(namespace['api'] + 'canteen')
    data = r.json()
    return render_template("CanteenTemplate.html", weekly_menu=data)


@app.route('/canteen/<path:date>', methods=['GET'])
def get_canteen_day_api(date):
    r = requests.get(namespace['api'] + 'canteen' + '/' + date)
    data = r.json()
    try:
        if data['errorCode'] == 404:
            return meal_not_found(404)
    except:
        return render_template("CanteenTemplate.html", weekly_menu=data)

@app.route('/')
def mainpage():
    return render_template('MainPage.html')
    #return render_template('SecretariatsTemplate.html')

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
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i + 1)).strftime('%d/%m/%Y'))
    # print(days_of_week)

if __name__ == '__main__':
    list_days_of_week()
    app.run(port=3000)