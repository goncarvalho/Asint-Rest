from flask import Flask
import json
from datetime import date
from datetime import datetime, timedelta
import requests
from operator import itemgetter

url_spaces= str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces')
days_of_week = []
app = Flask(__name__)
rooms_by_id = {}
ids = []

# id FA1 2448131363667
@app.route('/spaces/<id>/', methods=['GET'])
@app.route('/spaces/<id>', methods=['GET'])
def get_spaces(id):
    global rooms_by_id
    global ids
    data = requests.get(url_spaces + '/' + str(id))
    room_info = data.json()
    if id not in ids:
        ids.append(id)
    # talvez checkar se é uma room ou outra coisa
        for key in room_info:
            if key == 'parentSpace':
                id_parent_space = room_info[key]['id']
                floor = requests.get(url_spaces + '/' + str(id_parent_space))
                while floor.json()['parentSpace']['type'] != 'BUILDING':
                    floor = requests.get(url_spaces + '/' + str(floor.json()['parentSpace']['id']))
                rooms_by_id[str(id)] = ({'building': floor.json()['parentSpace']['name'],
                                         'campus': floor.json()['parentSpace']['topLevelSpace']['name']})

            pass

            if key == 'events':
                rooms_by_id[str(id)].update({'events': room_info['events']})
                print(rooms_by_id)
        return 'schedule added to the room'
    else:
        print(rooms_by_id[str(id)])
        return 'A sala ja existia na database'


def list_days_of_week():
    global days_of_week
    day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    print(str(start))
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i+1)).strftime('%d/%m/%Y'))
    print(days_of_week)


if __name__ == '__main__':
    list_days_of_week()
    app.run()
