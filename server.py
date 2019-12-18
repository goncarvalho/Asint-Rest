from datetime import date
from datetime import datetime, timedelta
from expiringdict import ExpiringDict
from json2html import *

import random
import string
import pickle

from flask import render_template, redirect, Flask, jsonify, request, Response, url_for, abort, session
from flask_principal import Principal, Identity, Permission, RoleNeed, identity_loaded, identity_changed, \
    AnonymousIdentity
import requests


class User:
    def __init__(self, ident, password, roles, secret=None, token=None):
        self.id = ident
        self.password = password
        self.roles = roles
        self.token = token
        self.secret = secret


class Secret:
    def __init__(self, ident, secret):
        self.id = ident
        self.secret = secret
        self.users_used = []


# Namespace database
try:
    with open('namespace.pkl', 'rb') as f:
        namespace = pickle.load(f)
    f.close()
except FileNotFoundError:
    namespace = {'logs': 'http://127.0.0.1:5004/addlog', 'spaces': 'http://127.0.0.1:5002/',
                 'canteen': 'http://127.0.0.1:5001/',
                 'secretariat': 'http://127.0.0.1:5003/', 'server': 'http://127.0.0.1:5000/'}

# User database
try:
    with open('users.pkl', 'rb') as f:
        users = pickle.load(f)
    f.close()
except FileNotFoundError:
    users = {'administrador': User("administrador", "1234", ['guest', 'administrator'])}

# Fenix Settings
try:
    with open('fenix_settings.pkl', 'rb') as f:
        client_id, clientSecret, fenixLoginpage, fenixacesstokenpage, redirect_fenix_uri = pickle.load(f)
    f.close()
except FileNotFoundError:
    client_id = "1695915081465942"
    clientSecret = "7/gdOaXo4k575kv/sGyAGj7kzTXXPFUZgqXFWXn9g6ymEYWt5JIKwjACv8Hb54K+V9OuzDZhgQsKy/TQYzcyEw=="
    fenixLoginpage = "https://fenix.tecnico.ulisboa.pt/oauth/userdialog?client_id=%s&redirect_uri=%s"
    fenixacesstokenpage = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'
    redirect_fenix_uri = "http://127.0.0.1:5000/istAuth"

# Flask
app = Flask(__name__)
app._static_folder = 'Static'
app.secret_key = "super secret key"
principals = Principal(app)
admin_permission = Permission(RoleNeed('administrator'))
fenix_permission = Permission(RoleNeed('fenix'))
guest_permission = Permission(RoleNeed('guest'))

secrets = ExpiringDict(max_len=100, max_age_seconds=15)
secret_len = 4
days_of_week = []


"""API"""


@app.route('/<path:path>/', methods=['POST', 'GET'])
def api(path):

    micro_services = path.split('/')

    if str(micro_services[0]) in namespace:
        if request.method == 'GET':
            r = requests.get(namespace[micro_services[0]] + path)
            requests.post(namespace['logs'], json={'request': namespace[micro_services[0]] + path,
                                                   'user': session['identity.id'],
                                                   'timestamp': datetime.now().isoformat()})
            return jsonify(r.json())
        else:
            r = requests.post((namespace[micro_services[0]] + path), request.form)
            requests.post(namespace['logs'], json={'request': namespace[micro_services[0]] + path,
                                                   'user': session['identity.id'],
                                                   'timestamp': datetime.now().isoformat()})
            return jsonify(r.json())
    else:
        return render_template('NoInfoMeal_404.html', title='404'), 404


"""Available web pages"""


@app.route('/')
@guest_permission.require(http_exception=403)
def main_page():
    return render_template('MainPage.html')


@app.route('/admin')
@guest_permission.require(http_exception=401)
def adm_page():
    return render_template('AdminPage.html')

# Login page
@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']

        if username == 'guest':
            identity_changed.send(app, identity=Identity("guest"))
            return redirect(session['redirected_from'])

        elif username == 'fenix':
            redirect_page = fenixLoginpage % (client_id, redirect_fenix_uri)
            return redirect(redirect_page)
    else:
        return render_template('Login.html')

# Login page
@app.route('/logAdmin', methods=['POST', 'GET'])
def login_adm():
    if request.method == 'POST':
        username = request.form['username']
        try:
            password = request.form['password']
            if users[username].password == password:
                identity_changed.send(app, identity=Identity(username))
        except:
            pass
        return redirect(url_for('adm_page'))
    else:
        return render_template('LoginAdmin.html')

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


@app.route('/secret', methods=['GET'])
@fenix_permission.require(http_exception=403)
def show_secret():
    return render_template('getsecret.html')


@app.route('/getsecret', methods=['GET'])
@fenix_permission.require(http_exception=403)
def get_secret():

    # creates random character sequence as a secret
    if users[session['identity.id']].secret is None:
        secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(secret_len))
        users[session['identity.id']].secret = secret
        secrets[secret] = Secret(session['identity.id'], secret)
    elif users[session['identity.id']].secret in secrets:
        secret = users[session['identity.id']].secret
    else:
        secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(secret_len))
        users[session['identity.id']].secret = secret
        secrets[secret] = Secret(session['identity.id'], secret)

    return jsonify(secrets.get(secret).__dict__)


@fenix_permission.require(http_exception=403)
@app.route('/validate', methods=['GET', 'POST'])
def validate_secret():
    if request.method == 'POST':
        secret = request.form['secret']

        if secret in secrets:
            data = secrets.get(secret)
            # add this user to the pool of users that have used this secret
            params = {'access_token': users[session['identity.id']].token}
            resp = requests.get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person", params=params)
            if resp.status_code == 200:
                r_info = resp.json()
                secrets[secret].users_used.append(r_info)

            # show the user corresponding to this secret
            params = {'access_token': users[data.id].token}
            resp = requests.get("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person", params=params)
            if resp.status_code == 200:
                r_info = resp.json()
                return jsonify(r_info)

        else:
            return jsonify("No user!")
    else:
        #return render_template('PostSecret.html')
        return Response('''
        <form action="" method="post">
            <p><input type=text name=secret>
        </form>
        ''')


@app.route('/scanQR', methods=['GET'])
def render_scanqr():
    return render_template('qr_read.html')


@app.route('/resources/<path:path>/', methods=['GET'])
def get_micro_service_info(path):

    micro_services = path.split('/')
    if str(micro_services[0]) in namespace:
        if request.method == 'GET':
            r = requests.get(namespace[micro_services[0]] + path)
            data = r.json()
            return render_template(json2html.convert(json=data))
    else:
        return render_template('NoInfoMeal_404.html', title='404'), 404


@app.route('/resources/spaces/<path:ident>', methods=['GET'])
def get_space_api(ident):
    r = requests.get(namespace['spaces'] + 'spaces' + '/' + ident)
    data = r.json()
    return render_template("RoomsTemplate.html", rooms_events=data, days_of_week=days_of_week)


@app.route('/resources/spaces/<ident>/<path:day>', methods=['GET'])
def get_space_api_day(ident, day):
    r = requests.get(namespace['spaces'] + 'spaces' + '/' + str(ident) + '/' + day)
    data = r.json()
    return render_template("RoomsTemplate.html", rooms_events=data, days_of_week=[day])


# SECRETARIAT

@app.route('/resources/secretariat/')
def render_secretariats():
    return render_template('SecretariatsTemplate.html')


@app.route('/resources/secretariat/ident', methods=['POST', 'GET'])
def render_secretariat_id_form():
    if request.method == 'GET':
        return render_template('Secretariate_ID_form.html')
    if request.method == "POST":
        r = requests.post(namespace['secretariat'] + 'secretariat' + '/ident', request.form)
        if r.status_code == 404:
            return abort(404)
        return render_template('Secretariate_ID_show.html', secretariateid=r.json())


@app.route('/resources/secretariat/add', methods=['POST', 'GET'])
@admin_permission.require(http_exception=401)
def render_secretariat_add_form():
    if request.method == 'GET':
        return render_template('Secretariate_Add_form.html')
    if request.method == "POST":
        r = requests.post(namespace['secretariat'] +  'secretariat' + '/add', request.form)
        return render_template('Secretariate_Add_show.html', secretariate_added=r.json())


@app.route('/resources/secretariat/delete/ident', methods=['POST', 'GET'])
@admin_permission.require(http_exception=401)
def render_secretariat_remove_form():
    if request.method == 'GET':
        return render_template('Secretariate_Remove_form.html')
    if request.method == "POST":
        r = requests.post(namespace['secretariat'] + 'secretariat' + '/delete/ident', request.form)
        return render_template('Secretariates_Remove_showleft.html', secretariate_added=r.json())


@app.route('/resources/secretariat/edit', methods=['POST', 'GET'])
@admin_permission.require(http_exception=401)
def render_secretariat_edit_form():
    if request.method == 'GET':
        return render_template('Secretariate_Edit_form.html')
    elif request.method == 'POST':
        requests.post(namespace['secretariat'] + 'secretariat' + '/edit', request.form)
        return render_template('SecretariatsTemplate.html')


@app.route('/resources/canteen/', methods=['GET'])
def get_canteen_():
    r = requests.get(namespace['canteen'] + 'canteen')
    data = r.json()
    return render_template("CanteenTemplate.html", weekly_menu=data)


@app.route('/resources/canteen/<path:c_date>', methods=['GET'])
def get_canteen_day(c_date):
    r = requests.get(namespace['canteen'] + 'canteen' + '/' + c_date)
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


@app.errorhandler(401)
def unauthorized(e):
    try:
        logout()
    finally:
        session['redirected_from'] = request.url
        return redirect(url_for('login_adm'))


@app.errorhandler(403)
def forbidden(e):
    try:
        logout()
    finally:
        session['redirected_from'] = request.url
        return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(e):
    return render_template('NoInfoMeal_404.html', title='404'), 404


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
