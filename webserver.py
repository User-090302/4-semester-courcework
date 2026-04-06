from flask import Flask, jsonify, request
import threading
import time
from collectors import RamCollector, CPUCollector, NetCollector, FansCollector, DisksCollector


class WebServer:
    def __init__(self, host='0.0.0.0', port=5000, debug=False):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self.debug = debug
        self._setup_routes()

        self. THRs = []
        self.ram = RamCollector(2)
        self.cpu = CPUCollector(2)
        self.net = NetCollector(2)
        self.fans = FansCollector(2)
        self.disks = DisksCollector(2)
        #self.__initTHR(self.ram, self.cpu)
        #self.__startTHRs()
        #self.__listenTHRs(self.ram, self.cpu)
        self.THRs.append(threading.Thread(target=self.fans.run, daemon=True))
        self.THRs.append(threading.Thread(target=self.disks.run, daemon=True))
        self.THRs.append(threading.Thread(target=self.net.run, daemon=True))
        self.THRs.append(threading.Thread(target=self.cpu.run, daemon=True))
        self.THRs.append(threading.Thread(target=self.ram.run, daemon=True))
        for i in self.THRs: i.start()

        self.mainTemplate = ""
        with open("./htms/default.htm", 'r') as file:
            self.mainTemplate = file.read()

        
    def _setup_routes(self):
        
        @self.app.route('/')
        def home():
            resStr = self.cpu.returnData()
            
            resStr += self.ram.returnData()
            resStr += self.net.returnData()
            resStr += self.fans.returnData()
            resStr += self.disks.returnData()
            return self.mainTemplate.replace("%items%",resStr)
        
    def get_status(self):
        """Метод для получения статуса (можно переопределить)"""
        return {
            "status": "active",
            "host": self.host,
            "port": self.port
        }
    
    def process_data(self, data):
        """Метод для обработки данных (можно переопределить)"""
        return {
            "received": data,
            "processed": True,
            "message": "Data processed successfully"
        }
    
    def run(self):
        """Запуск сервера"""
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug
        )
    
    def run_background(self):
        """Запуск сервера в фоновом потоке"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

# Использование
if __name__ == '__main__':
    server = WebServer(port=5001)
    server.run()
