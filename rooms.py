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

            if key == 'events':
                rooms_by_id[str(id)].update({'events': {}})
                for item in room_info[key]:
                    if item['day'] in (rooms_by_id[str(id)]['events']):
                        print('OLA')
                        rooms_by_id[str(id)]['events'][item['day']].append(item)
                    else:
                        rooms_by_id[str(id)]['events'].update({item['day']: []})
                        rooms_by_id[str(id)]['events'][item['day']].append(item)
                    print(rooms_by_id)
        return 'schedule added to the room'
    else:
        print(rooms_by_id[str(id)])
        return 'A sala ja existia na database'


if __name__ == '__main__':
    app.run()
