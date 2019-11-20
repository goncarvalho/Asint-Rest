from flask import Flask
import json
from datetime import date
from datetime import datetime, timedelta
import requests
from operator import itemgetter

url_canteen = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen')
url_canteen_day = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/canteen?day=')
weekly_meal = {}  # global list
days_of_week = []

app = Flask(__name__)


@app.route('/canteen/', methods=['GET'])
@app.route('/canteen', methods=['GET'])
def get_weekly_meal():
    global weekly_meal
    try :
        for days in days_of_week:
            print(weekly_meal[days])
        return 'ok'
    except:
        data = requests.get(url_canteen)
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        for days in days_of_week:
            print(weekly_meal[days])
        return "NICE"


@app.route('/canteen/<day>/<month>/<year>', methods=['GET'])
def check_meal(day, month, year):
    global weekly_meal
    try:
        print(weekly_meal[str(day + '/' + month + '/' + year)])
    except:
        data=requests.get(str(url_canteen_day + day + '/' + month + '/' + year))
        for item in data.json():
            weekly_meal[item['day']] = item['meal']
        print(weekly_meal)
        return "added nex week"

def list_days_of_week():
    global days_of_week
    day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    print(str(start))
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i)).strftime('%d/%m/%Y'))
    print (days_of_week)


if __name__ == '__main__':
    print(weekly_meal)
    list_days_of_week()
    app.run()


#day = '22/11/2019'
#dt = datetime.strptime(day, '%d/%m/%Y')
#start = dt - timedelta(days=dt.weekday())
#end = start + timedelta(days=4)
#print(start)
#print(end)