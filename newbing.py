# coding=utf-8
import time

import requests
from pathlib import Path
import json
import websocket
import rel
import constants

class NewBing:
    response = ''
    ask_str = ''
    cnt = 0;

    def __init__(self, ask_str: str):
        self.headers = constants.header
        cur_path = str(Path(__file__).parent)
        cookie_str = ''
        with open(cur_path + "\\cookie.txt", encoding='utf-8') as f:
            cookie_str = f.read()
        self.headers['Cookie'] = cookie_str
        if len(ask_str) <=0:
            raise Exception("given ask string is empty!")
        self.ask_str = ask_str

    def pack(self, j):
        return json.dumps(j) + constants.end_of_stream

    def init(self):
        session = requests.Session()
        session.trust_env = False
        session.verify = False
        requests.packages.urllib3.disable_warnings()

        create_resp = session.get(constants.base_url + constants.create_conversation, headers=self.headers,
                                  proxies=constants.proxy)
        print(create_resp.status_code)
        conversation_id = ''
        client_id = ''
        conversation_sign = ''
        trace_id = ''
        cur_date = ''
        if create_resp.status_code == 200:
            create_resp_json = json.loads(create_resp.text)
            conversation_id = create_resp_json['conversationId']
            conversation_sign = create_resp_json['conversationSignature']
            client_id = create_resp_json['clientId']
            trace_id = create_resp.headers['X-Ceto-ref'].split("|")[0]
            cur_date = create_resp.headers['X-Ceto-ref'].split("|")[1]

        conversation_path = constants.base_url + '/generate?conversationId=' + \
                            conversation_id + '&clientId=' + client_id + '&conversationSignature=' + conversation_sign
        print(conversation_path)
        invocation_id = 1
        self.arg = {"arguments": [
            {
                "source": "cib",
                "optionsSets": ["nlu_direct_response_filter", "deepleo", "disable_emoji_spoken_text",
                                "enablemm", "h3imaginative", "clgalileo", "gencontentv3",
                                "rediscluster", "dlreldeav2", "enbfpr", "dv3sugg"],
                "allowedMessageTypes": ["Chat"],
                "sliceIds":
                    ["winmuid2tf", "contctxp2tf", "delayglobjscf", "0417bicunivs0", "ssoverlap0", "sswebtop1", "clarityconvcf",
                     "ttstmoutcf", "sbsvgoptcf", "anssupvbar", "winlongmsg2tf", "328cf", "418glpv6p", "321slocs0", "0329resps0",
                     "420bics0", "4252tfinances0", "0417redis", "420deav2", "425bfpr", "424jbfv1s0"],
                "verbosity": "verbose",
                "traceId": trace_id,
                "isStartOfSession": True,
                "message": {
                    "locale": "zh-CN",
                    "market": "zh-CN",
                    "region": "HK",
                    ## find it in your edge browser
                    "location": "",
                    "locationHints": [{
                        "country": "Hong Kong",
                        "state": "Central And Western District",
                        "city": "Central",
                        "timezoneoffset": 8,
                        "countryConfidence": 8,
                        "cityConfidence": 5,
                        "Center": {
                            ## find it in your edge browser, float
                            "Latitude": ,
                            "Longitude": 
                        },
                        "RegionType": 2,
                        "SourceType": 1
                    }],
                    "timestamp": cur_date,
                    "author": "user",
                    "inputMethod": "Keyboard",
                    "text": self.ask_str,
                    "messageType": "Chat",
                },
                "conversationSignature": conversation_sign,
                "participant": {"id": client_id},
                "conversationId": conversation_id,
            },
        ],
            "invocationId": str(invocation_id),
            "target": "chat",
            "type": 4,
        }

    def on_message(self, ws, message):
        self.cnt = self.cnt+1
        if self.cnt % 20 == 0 and '{"type":1,"target":"update","arguments"' in message:
            ## the make the web socket keep connectting
            ws.send(self.pack({"type": 6}))
        else:
            for st in message.split(constants.end_of_stream):
                if len(st) < 5:
                    continue
                o = json.loads(st)
                if 'type' in o and o['type'] == 1 and 'messages' in o['arguments'][0]:
                    self.response = o['arguments'][0]['messages'][0]['text']


    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        ## close the web socket, you could make it always running
        rel.abort()

    def on_open(self, ws):
        print("Opened connection")

    def get_result(self):
        resp = self.response;
        self.response = ''
        return resp

    def web_socket(self):
        self.headers['Sec-WebSocket-Extensions'] = "permessage-deflate; client_max_window_bits"
        self.headers['Sec-WebSocket-Version'] = "13"
        ws = websocket.WebSocketApp("wss://sydney.bing.com/sydney/ChatHub",on_open=self.on_open,
                                      on_message=self.on_message,
                                      on_error=self.on_error,
                                      on_close=self.on_close)
        ## here you can add some proxy setting
        ws.run_forever(dispatcher=rel, reconnect=5)
        ws.send(self.pack({"protocol": "json", "version": 1}))
        ws.send(self.pack({"type": 6}))
        ws.send(self.pack(self.arg))
        rel.signal(2, rel.abort)
        rel.dispatch()

    def answer(self):
        self.init()
        self.web_socket()

        l = len(self.response)
        if l > 0:
            return self.get_result()
