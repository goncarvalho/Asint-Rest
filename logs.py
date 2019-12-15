from flask import  Flask, request, jsonify
import pickle

app = Flask(__name__)

# To use just send requests.post('http://127.0.0.1:5004/logs', json=data), with data being json


@app.route('/logs/addlog/', methods=['POST'])
@app.route('/logs/addlog', methods=['POST'])
def add_log_entry():
    if request.method == "POST":
        logs.append(request.form)


if __name__ == '__main__':
    try:
        with open('logs.pkl', 'rb') as f:
            (id_secretariat, offices) = pickle.load(f)
        f.close()
    except:
        logs = []
    app.run(port=5004)
