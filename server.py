from datetime import date
from datetime import datetime, timedelta

import logging
from time import strftime

from flask import render_template, redirect, Flask, jsonify, request, Response, url_for, abort, session
from flask_principal import Principal, Identity, Permission, RoleNeed, identity_loaded, identity_changed, \
    AnonymousIdentity
import requests

namespace = {'logs': 'http://127.0.0.1:4001/', 'spaces': 'http://127.0.0.1:5002/', 'canteen': 'http://127.0.0.1:5001/',
             'secretariat': 'http://127.0.0.1:5003/', 'server': 'http://127.0.0.1:5000/'}

logger = logging.getLogger('serverlog')
logger.setLevel(logging.INFO)
# %(remote_addr)s used %(method)s about %(full_path)s with %(status_code)s
formatter = logging.Formatter('%(levelname)s - %(name)s - [%(asctime)s] - %(message)s')

file_handler = logging.FileHandler('server.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class User:
    def __init__(self, ident, password, roles, token=None):
        self.id = ident
        self.password = password
        self.roles = roles
        self.token = token




# Flask
app = Flask(__name__)
app.secret_key = "super secret key"
principals = Principal(app)
admin_permission = Permission(RoleNeed('administrator'))
fenix_permission = Permission(RoleNeed('fenix'))
guest_permission = Permission(RoleNeed('guest'))

# Fenix
client_id= "1695915081465942"
clientSecret = "7/gdOaXo4k575kv/sGyAGj7kzTXXPFUZgqXFWXn9g6ymEYWt5JIKwjACv8Hb54K+V9OuzDZhgQsKy/TQYzcyEw=="
fenixLoginpage= "https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id=%s&redirect_uri=%s"
fenixacesstokenpage = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'
redirect_fenix_uri = "http://127.0.0.1:5000/istAuth"

# username : User
users = {}
days_of_week = []
users['administrador'] = User("administrador", "1234", ['guest', 'administrator'])

"""API"""


@app.route('/<path:path>/', methods=['POST', 'GET'])
def api(path):
    microservices = path.split('/')

    try:
        route = namespace[microservices[0]]
    except KeyError:
        return render_template('NoInfoMeal_404.html', title='404'), 404

    if request.method == 'GET':
        r = requests.get(namespace[microservices[0]] + path)
        return jsonify(r.json())
    else:
        r = requests.post((namespace[microservices[0]] + path), request.form)
        return jsonify(r.json())


"""Available web pages"""


@app.route('/')
@guest_permission.require(http_exception=403)
def main_page():
    return render_template('MainPage.html')

# Login page
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']

        if username == 'guest':
            identity_changed.send(app, identity=Identity("guest"))
            logger.info('New guest session')
            return redirect(session['redirected_from'])

        elif username == 'fenix':
            redirect_page = fenixLoginpage % (client_id, redirect_fenix_uri)
            return redirect(redirect_page)

        else:
            try:
                password = request.form['password']
                if users[username].password == password:
                    identity_changed.send(app, identity=Identity(username))

            except:
                pass
            return redirect(session['redirected_from'])

    else:
        return render_template('Login.html')

# Logout
@app.route("/logout")
def logout():
    for key in ['identity.name', 'identity.auth_type', 'redirected_from']:
        try:
            del session[key]
        except:
            pass

    identity_changed.send(app, identity=AnonymousIdentity())
    return Response('<p>Logged out</p>')


@app.route('/istAuth')
def fenix_authentication():
    code = request.args['code']
    print("code "+request.args['code'])

    payload = {'client_id': client_id, 'client_secret': clientSecret, 'redirect_uri': redirect_fenix_uri, 'code': code,
               'grant_type': 'authorization_code'}

    response = requests.post(fenixacesstokenpage, params=payload)
    print(response.url)
    print(response.status_code)
    if response.status_code == 200:

        r_token = response.json()
        params = {'access_token': r_token['access_token']}
        resp = requests.get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person", params=params)
        r_info = resp.json()
        login_name = r_info['username']
        user_token = r_token['access_token']

        users[login_name] = User(login_name, None, ['guest', 'fenix'], token=user_token)
        identity_changed.send(app, identity=Identity(login_name))

        return redirect(url_for('main_page'))
    else:
        return abort(403)


@app.errorhandler(403)
def page_not_found(e):
    try:
        logout()
    finally:
        session['redirected_from'] = request.url
        return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(error):
    return render_template('NoInfoMeal_404.html', title='404'), 404


@app.route('/resources/spaces/<path:id>', methods=['GET'])
def get_space_api(id):
    r = requests.get(namespace['server'] + 'spaces' + '/' + id)
    logger.info(
        '{} - - Room ID = {} Schedule using {} in {} with response code {}'.format(request.remote_addr,
                                                                                              id,
                                                                                              request.method,
                                                                                              request.full_path,
                                                                                              r.status_code))
    data = r.json()
    return render_template("RoomsTemplate.html", rooms_events = data, days_of_week = days_of_week)


@app.route('/resources/spaces/<id>/<path:date>', methods=['GET'])
def get_space_api_day(id,date):
    r = requests.get(namespace['server'] + 'spaces' + '/' + str(id) + '/' + date)
    logger.info(
        '{} - - Room ID = {} Schedule for day {} using {} in {} with response code {}'.format(request.remote_addr,
                                                                                              id,date,
                                                                                              request.method,
                                                                                              request.full_path,
                                                                                              r.status_code))
    data = r.json()
    return render_template("RoomsTemplate.html", rooms_events = data, days_of_week = [date])


@app.route('/resources/secretariat/')
def render_secretariates():
    return render_template('SecretariatsTemplate.html')


@app.route('/resources/secretariat/add', methods=['POST'])
@admin_permission.require(http_exception=403)
def add_secretariat():
    if request.method == "POST":
        r = requests.post(namespace['server'] +  'secretariat' + '/add', request.form)
        return render_template('AddSecretariateResponse.html', secretariate_added=r.json())


@app.route('/resources/secretariat/ident', methods=['POST'])
def show_secretariat():
    if request.method == "POST":
        r = requests.post(namespace['server'] + 'secretariat' + '/ident', request.form)
        logger.info(
            '{} - - Secretariate ID = {} Information using {} in {} with response code {}'.format(request.remote_addr,
                                                                                             request.form['ident'],
                                                                                             request.method,
                                                                                             request.full_path,
                                                                                             r.status_code))
        return render_template('ShowSecretariate_id.html', secretariateid = r.json())


@app.route('/resources/secretariat/delete/ident', methods=['POST'])
@admin_permission.require(http_exception=403)
def remove_secretariat():
    if request.method == "POST":
        r = requests.post(namespace['server'] + 'secretariat' + '/delete/ident', request.form)
        return render_template('ShowSecretariatesAfterRemove.html', secretariate_added = r.json())


@app.route('/resources/secretariat/edit', methods=['POST'])
@admin_permission.require(http_exception=403)
def edit_secretariat():
    if request.method == "POST":
        r = requests.post(namespace['server'] + 'secretariat' + '/edit', request.form)
        return render_template('AddSecretariateResponse.html', secretariate_added=r.json())


@app.route('/resources/canteen/', methods=['GET'])
def get_canteen_():
    r = requests.get(namespace['server'] + 'canteen')
    logger.info('{} - - Weekly Canteen Schedule using {} in {} with response code {}'.format(request.remote_addr, request.method, request.full_path, r.status_code))
    data = r.json()
    return render_template("CanteenTemplate.html", weekly_menu=data)

@app.route('/resources/canteen/<path:c_date>', methods=['GET'])
def get_canteen_day(c_date):
    r = requests.get(namespace['server'] + 'canteen' + '/' + c_date)
    logger.info('{} - - Canteen Schedule for day {} using {} in {} with response code {}'.format(request.remote_addr, c_date,
                                                                                             request.method,
                                                                                             request.full_path,
                                                                                             r.status_code))
    data = r.json()
    try:
        if data['errorCode'] == 404:
            return not_found(404)
    except:
        return render_template("CanteenTemplate.html", weekly_menu=data)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):

    if identity.id == "guest":
        identity.provides.add(RoleNeed('guest'))
    try:
        for role in users[identity.id].roles:
            identity.provides.add(RoleNeed(role))

    except:
        "No user"


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
    app.run()
