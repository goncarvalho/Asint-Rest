from flask import Flask, jsonify, request
from datetime import date
from datetime import datetime, timedelta
import requests

url_spaces = str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces')
days_of_week = []
app = Flask(__name__)
rooms_by_id = {}
ids = {}

namespace = {'logs': 'http://127.0.0.1:5004/'}

@app.before_request
def before_request():
    requests.post(namespace['logs'] + 'addlog', json={'request': request.url,
                                                      'user': request.host,
                                                      'timestamp': datetime.now().isoformat()})


@app.route('/spaces/<ident>/<path:date>', methods=['GET'])
def get_space_day(ident, date):

    response = get_spaces(ident, date)
    return response


# id FA1 2448131363667
@app.route('/spaces/<ident>/', methods=['GET'])
@app.route('/spaces/<ident>', methods=['GET'])
def get_spaces(ident, day=None):
    global ids
    try:
        if day is not None:
            if str(ident) in ids.keys():
                if day not in ids[str(ident)]:
                    ids[str(ident)]+list_days_of_week(day)
                    data = requests.get(url_spaces + '/' + str(ident) + '?day=' + day)
                    room_info = data.json()
                    save_into_database(room_info, ident)
            else:
                ids[str(ident)] = list_days_of_week(day)
                data = requests.get(url_spaces + '/' + str(ident) + '?day=' + day)
                room_info = data.json()
                save_into_database(room_info, ident)
            return jsonify(rooms_by_id[str(ident)])
        else:
            if str(ident) in ids.keys():
                if date.today().strftime("%d/%m/%Y") not in ids[str(ident)]:
                    ids[str(ident)]+list_days_of_week(date.today().strftime("%d/%m/%Y"))
                    data = requests.get(url_spaces + '/' + str(ident))
                    room_info = data.json()
                    save_into_database(room_info, ident)
            else:
                ids[str(ident)] = list_days_of_week(date.today().strftime("%d/%m/%Y"))
                data = requests.get(url_spaces + '/' + str(ident))
                room_info = data.json()
                save_into_database(room_info, ident)
            return jsonify(rooms_by_id[str(ident)])
    except:
        return 404

def save_into_database(room_info, ident):
    global rooms_by_id
    if room_info['type'] == 'ROOM':
        id_parent_space = room_info['parentSpace']['id']
        floor = requests.get(url_spaces + '/' + str(id_parent_space))
        if str(ident) not in rooms_by_id:
            while floor.json()['parentSpace']['type'] != 'BUILDING':
                floor = requests.get(url_spaces + '/' + str(floor.json()['parentSpace']['id']))
            rooms_by_id[str(ident)] = ({'building': floor.json()['parentSpace']['name'],
                                        'campus': floor.json()['parentSpace']['topLevelSpace']['name']})

            rooms_by_id[str(ident)].update({'events': {}})
        for item in room_info['events']:
            if item['day'] in (rooms_by_id[str(ident)]['events']):
                rooms_by_id[str(ident)]['events'][item['day']].append(item)
            else:
                rooms_by_id[str(ident)]['events'].update({item['day']: []})
                rooms_by_id[str(ident)]['events'][item['day']].append(item)
    else:
        return 404


def list_days_of_week(day):
    global days_of_week
    #day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i+1)).strftime('%d/%m/%Y'))
    return days_of_week


if __name__ == '__main__':
    app.run(port=5002)
