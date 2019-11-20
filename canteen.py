from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import json
import requests

url_canteen = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
weekly_meal = []  # global list

app = Flask(__name__)


@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods=['GET'])
def get_weekly_meal():
    global weekly_meal
    if bool(weekly_meal) is False:
        data = requests.get(url_canteen)
        weekly_meal = data.json()
        return print(weekly_meal)
    else:
        return "for you"
    return "got the meal for you"


@app.route('/canteen/<day>/<month>/<year>', methods=['GET'])
def check_meal(day, month, year):
    global weekly_meal

    if bool(weekly_meal) is False:
        get_weekly_meal()
    else:
        for item in weekly_meal:
            if item['day'] == str(day + '/' + month + '/' + year):
                print(item)
                break
            else:
                data = requests.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
                weekly_meal.append(data.json())
                return "Not yet assigned or the format is not correct dd/mm/yyyy"

    return "Touche"


def provide_meal_day():
    pass


if __name__ == '__main__':
    print(weekly_meal)
    app.run()
