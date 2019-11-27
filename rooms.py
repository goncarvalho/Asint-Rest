from flask import Flask
from flask import jsonify
import json
from datetime import date
from flask import render_template
from datetime import datetime, timedelta
import requests
from operator import itemgetter

url_spaces= str('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces')
days_of_week = []
app = Flask(__name__)
rooms_by_id = {}
ids = {}


@app.route('/spaces/<id>/<day>/<month>/<year>', methods=['GET'])
def get_space_day(id,day,month,year):
    response = get_spaces(id, day,month,year)
    return response


# id FA1 2448131363667
@app.route('/spaces/<id>/', methods=['GET'])
@app.route('/spaces/<id>', methods=['GET'])
def get_spaces(id, day = None,month = None,year=None):
    global ids
    # if day != None and month != None and year != None:
    #     if str(id) in ids.keys():
    #         if str(day + '/'+ month + '/'+year) in ids[str(id)]:
    #             print (rooms_by_id[str(id)]['events'][str(day + '/'+ month + '/'+year)])
    #             resp = jsonify(rooms_by_id[str(id)]['events'][str(day + '/' + month + '/' + year)])
    #             return resp
    #         else:
    #             ids[str(id)]+list_days_of_week(str(day + '/'+ month + '/'+year))
    #             data = requests.get(url_spaces + '/' + str(id) + '?day=' + str(day + '/'+ month + '/'+year))
    #             room_info = data.json()
    #             save_into_database(room_info, id)
    #             resp = jsonify(rooms_by_id[str(id)]['events'][str(day + '/' + month + '/' + year)])
    #             return resp
    #
    #     else:
    #         ids[str(id)]=list_days_of_week(str(day + '/'+ month + '/'+year))
    #         data = requests.get(url_spaces + '/' + str(id) + '?day=' + str(day + '/' + month + '/' + year))
    #         room_info = data.json()
    #         save_into_database(room_info,id)
    #         resp = jsonify(rooms_by_id[str(id)]['events'][str(day + '/'+ month + '/'+year)])
    #         return resp
    #
    # else:
    #     # data = requests.get(url_spaces + '/' + str(id))
    #     # room_info = data.json()
    #     if str(id) in ids.keys():
    #         if date.today().strftime("%d/%m/%Y") in ids[str(id)]:
    #             print(rooms_by_id[str(id)])
    #         else:
    #             ids[str(id)]+list_days_of_week(date.today().strftime("%d/%m/%Y"))
    #             data = requests.get(url_spaces + '/' + str(id))
    #             room_info = data.json()
    #             save_into_database(room_info,id)
    #             print("HEYy")
    #     else:
    #         ids[str(id)] = list_days_of_week(date.today().strftime("%d/%m/%Y"))
    #         data = requests.get(url_spaces + '/' + str(id))
    #         room_info = data.json()
    #         save_into_database(room_info, id)
    #         print(ids)
    # resp = jsonify(rooms_by_id[str(id)])
    # return resp

    if day != None and month != None and year != None:
        if str(id) in ids.keys():
            if str(day + '/'+ month + '/'+year) not in ids[str(id)]:
                ids[str(id)]+list_days_of_week(str(day + '/'+ month + '/'+year))
                data = requests.get(url_spaces + '/' + str(id) + '?day=' + str(day + '/'+ month + '/'+year))
                room_info = data.json()
                save_into_database(room_info, id)
        else:
            ids[str(id)]=list_days_of_week(str(day + '/'+ month + '/'+year))
            data = requests.get(url_spaces + '/' + str(id) + '?day=' + str(day + '/' + month + '/' + year))
            room_info = data.json()
            save_into_database(room_info,id)
        resp = jsonify(rooms_by_id[str(id)]['events'][str(day + '/'+ month + '/'+year)])
        return resp
    else:
        if str(id) in ids.keys():
            if date.today().strftime("%d/%m/%Y") not in ids[str(id)]:
                ids[str(id)]+list_days_of_week(date.today().strftime("%d/%m/%Y"))
                data = requests.get(url_spaces + '/' + str(id))
                room_info = data.json()
                save_into_database(room_info, id)
        else:
            ids[str(id)] = list_days_of_week(date.today().strftime("%d/%m/%Y"))
            data = requests.get(url_spaces + '/' + str(id))
            room_info = data.json()
            save_into_database(room_info, id)
        resp = jsonify(rooms_by_id[str(id)])
        return resp




def save_into_database(room_info, id):
    global rooms_by_id
    if room_info['type'] == 'ROOM':
        id_parent_space = room_info['parentSpace']['id']
        floor = requests.get(url_spaces + '/' + str(id_parent_space))
        if str(id) not in rooms_by_id:
            while floor.json()['parentSpace']['type'] != 'BUILDING':
                floor = requests.get(url_spaces + '/' + str(floor.json()['parentSpace']['id']))
            rooms_by_id[str(id)] = ({'building': floor.json()['parentSpace']['name'],
                                     'campus': floor.json()['parentSpace']['topLevelSpace']['name']})

            rooms_by_id[str(id)].update({'events': {}})
        for item in room_info['events']:
            if item['day'] in (rooms_by_id[str(id)]['events']):
                rooms_by_id[str(id)]['events'][item['day']].append(item)
            else:
                rooms_by_id[str(id)]['events'].update({item['day']: []})
                rooms_by_id[str(id)]['events'][item['day']].append(item)
            print(rooms_by_id)
    else:
        return 404

def list_days_of_week(day):
    global days_of_week
    #day = date.today().strftime("%d/%m/%Y")
    dt = datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    print(str(start))
    days_of_week.append(start.strftime('%d/%m/%Y'))
    for i in range(4):
        days_of_week.append((start + timedelta(days=i+1)).strftime('%d/%m/%Y'))
    return days_of_week


if __name__ == '__main__':
    app.run(port=5002)
