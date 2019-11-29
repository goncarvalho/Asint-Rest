from flask import  Flask, request, jsonify
import json

office = {}

app = Flask(__name__)


@app.route('/secretariat/<ident>/', methods=['GET'])
@app.route('/secretariat/<ident>', methods=['GET'])
def get_office(ident):

    return jsonify(office[ident])


@app.route('/secretariat/edit/', methods=['POST'])
@app.route('/secretariat/edit', methods=['POST'])
def edit_office():

    content = request.json
    new_office = json.loads(content)

    try:
        for key in new_office:
            office[new_office['name']].key = new_office[key]
    except KeyError:
        return 400


@app.route('/secretariat/delete/<name>/', methods=['POST'])
@app.route('/secretariat/delete/<name>', methods=['POST'])
def delete_office(name):

    try:
        office.pop(name)
    except KeyError:
        return 400


@app.route('/secretariat/add/', methods=['POST'])
@app.route('/secretariat/add', methods=['POST'])
def add_office():

    content = request.json
    new_office = json.loads(content)

    try:
        office[new_office['name']] = Office(new_office['name'],     new_office['operating_hours'],
                                            new_office['location'], new_office['description'])
    except KeyError:
        return 400


class Office:

    def __init__(self, name, op_h, loc, description):
        self.name = name
        self.opening_hours = op_h
        self.location = loc
        self.description = description


if __name__ == '__main__':
    app.run(port=5003)
