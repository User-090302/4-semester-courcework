from flask import Flask, jsonify, request
import json

def rednderHtml(html: str, replaces = {}):
    mainHTLM = html
    for k,v in replaces.items():
        mainHTLM = mainHTLM.replace(k,v)
    return mainHTLM

def loadHtml(path):
    with open(path, 'r') as file:
        return file.read()


class WebServer:
    def __init__(self, host='0.0.0.0', port=80):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.service()
        self._setup_routes()

        

    def service(self): pass
    def _setup_routes(self): pass
    def getStatus(self):

        return {
            "status": "active",
            "host": self.host,
            "port": self.port
        }
    
    def processData(self, data):
        
        return {
            "received": data,
            "processed": True,
            "message": "Data processed successfully"
        }
    
    def run(self):

        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False
        )
    


