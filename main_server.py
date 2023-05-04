import json

from flask import Flask, request
from gevent import pywsgi
from multiprocessing import Process
import os
from newbing import NewBing

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return 'ok'

@app.route('/', methods=['POST'])
def ask_bing():
    ask_obj = request.get_data()
    ask_str = json.loads(ask_obj)['ask']
    new_bing = NewBing(ask_str)
    str = new_bing.answer()
    return str

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        gevent_server = pywsgi.WSGIServer(('0.0.0.0', int(20345)), app)
        multi_process = 1
        if multi_process == str(True):
            gevent_server.start()
            processes = 4


            def server_forever():
                gevent_server.start_accepting()
                gevent_server._stop_event.wait()


            for i in range(int(processes) - 1):
                p = Process(target=server_forever)
                p.start()
        else:
            gevent_server.serve_forever()
    except ssl.SSLError as err:
        pass
