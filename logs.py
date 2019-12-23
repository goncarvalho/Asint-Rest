from flask import  Flask, request, jsonify
import pickle

app = Flask(__name__)

# To use just send requests.post('http://127.0.0.1:5004/addlog', json=data)
try:
    with open('logs.pkl', 'rb') as f:
        logs = pickle.load(f)
    f.close()
except FileNotFoundError:
    logs = []


@app.route('/addlog/', methods=['POST'])
@app.route('/addlog', methods=['POST'])
def add_log_entry():
    if request.method == "POST":
        logs.append(request.json)
        with open('logs.pkl', 'wb') as fd:
            pickle.dump(logs, fd)
        fd.close()
        return jsonify(request.json)


@app.route('/getlog/', methods=['GET'])
def get_logs():
    return jsonify(logs)


if __name__ == '__main__':
    app.run(port=5004)
