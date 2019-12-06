from flask import  Flask, request, jsonify, render_template
import json
import pickle


app = Flask(__name__)

id_secretariat = 0
@app.route('/secretariat/ident/', methods=['POST'])
@app.route('/secretariat/ident', methods=['POST'])
def get_office():
    if len(offices) == 0 :
        return " There are no Office infrmation yet"
    if request.method == "POST":
        ident=request.form['ident']
    return jsonify(offices[ident].__dict__)


@app.route('/secretariat/edit/', methods=['POST'])
@app.route('/secretariat/edit', methods=['POST'])
def edit_office():

    content = request.json
    new_office = json.loads(content)

    try:
        for key in new_office:
            offices[new_office['name']].key = new_office[key]
    except KeyError:
        return 400


@app.route('/secretariat/delete/ident/', methods=['POST'])
@app.route('/secretariat/delete/ident', methods=['POST'])
def delete_office():
    if len(offices) == 0 :
        return " There are no Offices to remove"
    if request.method == "POST":
        ident=request.form['id']
        try:
            offices.pop(ident)
            with open('secretariates.pkl', 'wb') as f:
                pickle.dump((id_secretariat,offices), f)


        except KeyError:
            return 400
        list_secretariates=[]
        for i in offices.keys():
            list_secretariates.append(offices[i].__dict__)
    return jsonify(list_secretariates)

@app.route('/secretariat/add/', methods=['POST'])
def add_office():
    global id_secretariat
    if request.method == "POST":
        name = request.form['name']
        opening_hours = request.form['open']
        location = request.form['location']
        description = request.form['description']
    try:
        offices[str(id_secretariat)]=Office(str(name), str(opening_hours), str(location), str(description))
        id_secretariat=id_secretariat+1;
        with open('secretariates.pkl', 'wb') as f:
            pickle.dump((id_secretariat, offices), f)

        return jsonify(offices[str(id_secretariat - 1)].__dict__)
    except KeyError:
        return 400


class Office:
    def __init__(self, name, op_h, loc, description):
        self.name = name
        self.opening_hours = op_h
        self.location = loc
        self.description = description
        self.id = str(id_secretariat)


if __name__ == '__main__':
    try:
        with open('secretariates.pkl', 'rb') as f:
            (id_secretariat, offices) = pickle.load(f)
        f.close()
    except:
        offices = {}
    app.run(port=5003)