from flask import Flask, render_template, request, jsonify, current_app
from flask_cors import CORS
import monogo
import threading
import time
import logging
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] : %(message)s',
    )
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler("log.txt")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s, %(name)s, [%(levelname)s] : %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

FLASK_SERVER_IP = 'localhost'
FLASK_SERVER_PORT = 50002


app = Flask(__name__)
CORS(app, resources=r'/*')

app.record_all_record = {}

@app.route('/')
def index():
    return render_template('index.html')


def recall_success_upload_record():
    while 1:
        db = monogo.Database()
        response = db.recall_success_upload_record()
        app.record_all_record = {}
        recall_list = []

        for obj in response:
            obj['_id'] = str(obj['_id'])
            recall_list.append(obj)

        app.record_all_record = {'action':'recall_record',
                                 'payload':recall_list
                                 }
        logger.info("flask app record updated.")
        time.sleep(10)


def recall_record_by_username(user_name):
    db = monogo.Database()
    response = db.recall_user_record(user_name)
    user_record_recall_list = []

    for obj in response:
        obj['_id'] = str(obj['_id'])
        user_record_recall_list.append(obj)

    record_all_record = {'action': 'recall_record',
                         'payload': user_record_recall_list
                         }

    return record_all_record


@app.route("/json", methods=['GET', 'POST'])
def handle_ajax():
    app.logger.debug("JSON received.")
    app.logger.debug(request.get_json(force=True))
    request_json = request.get_json(force=True)
    if request_json:
        action = request_json['action']
        if action == 'recall_record':
            record = current_app.record_all_record
            return jsonify(record)
        if action == 'recall_record_by_username':
            record = recall_record_by_username(request_json['user_name'])
            return jsonify(record)

    else:
        return "no json data received."

if __name__ == '__main__':
    counter_th = threading.Thread(target=recall_success_upload_record, args=(), daemon=True)
    counter_th.start()
    app.run(host=FLASK_SERVER_IP, port=FLASK_SERVER_PORT)