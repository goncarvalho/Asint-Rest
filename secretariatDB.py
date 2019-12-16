from flask import Flask, request, jsonify
import pickle
from datetime import datetime
import requests

class Office:
    def __init__(self, name, op_h, loc, description):
        self.name = name
        self.opening_hours = op_h
        self.location = loc
        self.description = description
        self.id = str(id_secretariat)


app = Flask(__name__)

namespace = {'logs': 'http://127.0.0.1:5004/addlog'}

try:
    with open('secretariates.pkl', 'rb') as f:
        (id_secretariat, offices) = pickle.load(f)
    f.close()
except FileNotFoundError:
    offices = {}
    id_secretariat = 0


@app.route('/secretariat/ident/', methods=['POST'])
@app.route('/secretariat/ident', methods=['POST'])
def get_office():

    requests.post(namespace['logs'], json={'request': '/secretariat/' + request.form['ident'],
                                           'user': request.host,
                                           'timestamp': datetime.now()})
    if len(offices) == 0:
        return " There are no Office infrmation yet"
    if request.method == "POST":
        ident = request.form['ident']
    return jsonify(offices[ident].__dict__)


@app.route('/secretariat/edit/', methods=['POST'])
@app.route('/secretariat/edit', methods=['POST'])
def edit_office():

    requests.post(namespace['logs'], json={'request': '/secretariat/edit' + request.form['ident'],
                                           'user': request.host,
                                           'timestamp': datetime.now()})

    if len(offices) == 0 :
        return " There are no Office infrmation yet"
    if request.method == "POST":
        ident = request.form['ident']
    for key in request.form :
        if len(request.form[key]) != 0 :
            offices[ident].__dict__[key] = request.form[key]
    return jsonify(offices[ident].__dict__)


@app.route('/secretariat/delete/ident/', methods=['POST'])
@app.route('/secretariat/delete/ident', methods=['POST'])
def delete_office():

    requests.post(namespace['logs'], json={'request': '/secretariat/delete' + request.form['ident'],
                                           'user': request.host,
                                           'timestamp': datetime.now()})
    list_secretariates = []
    if len(offices) == 0:
        return " There are no Offices to remove"
    if request.method == "POST":
        ident=request.form['id']
        try:
            offices.pop(ident)
            with open('secretariates.pkl', 'wb') as f:
                pickle.dump((id_secretariat, offices), f)


        except KeyError:
            return 400
        for i in offices.keys():
            list_secretariates.append(offices[i].__dict__)
    return jsonify(list_secretariates)


@app.route('/secretariat/add/', methods=['POST'])
def add_office():

    requests.post(namespace['logs'], json={'request': '/secretariat/add' + request.form['ident'],
                                           'user': request.host,
                                           'timestamp': datetime.now()})
    global id_secretariat
    if request.method == "POST":
        name = request.form['name']
        opening_hours = request.form['open']
        location = request.form['location']
        description = request.form['description']
    try:
        offices[str(id_secretariat)] = Office(str(name), str(opening_hours), str(location), str(description))
        id_secretariat += 1

        with open('secretariates.pkl', 'wb') as fd:
            pickle.dump((id_secretariat, offices), fd)
        fd.close()
        return jsonify(offices[str(id_secretariat - 1)].__dict__)

    except KeyError:
        return 400


if __name__ == '__main__':
    app.run(port=5003)
