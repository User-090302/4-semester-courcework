import threading
from threadWork import threadWork
import web 
from flask import Flask, jsonify, request
import collectors 
import json5

with open("./config.jsonc", "r") as file: 
    info = json5.load(file)
# ==== STETTINGS ====
UPDATE = info['setts']['update']
HOST   = info['setts']['ip']
PORT   = info['setts']['port']
MODE   = info['setts']['mode']


class WebServer(web.WebServer):
    
    def returnHtmlData(self, Collector):
        if Collector != None: return Collector.returnHTML()
    def returnApiData(self, Collector):
        if Collector != None: return Collector.returnData()

    def service(self, arr = []):
        THRWork = threadWork()
        
        self.arr = [i for i in arr if i]
        THRWork.initTHR(arr)
        THRWork.startTHRs()
    def _setup_routes(self):
        self.mainPage = web.loadHtml(info['path']['mainP'])
        
        @self.app.route('/page')
        def homePage():
            li =   ""
            for i in self.arr:
                li +=  self.returnHtmlData(i)
            
            return self.mainPage.replace("%items%", li)
        @self.app.route("/api/v.0.1.2/stats")
        def returnAllData():
            result = {}
            for i in self.arr:
                if i is None: continue
                name = i.__class__.__name__.replace('Collector', '').lower()
                result[name] = i.returnData()
            return jsonify(result)

class core:
    def __init__(self):
        self.__loadInfo()

    
        self.work = WebServer(host=HOST, port=PORT)
        self.work.service(self.mainInfo)


    def __loadInfo(self):
        self.cpu     = collectors.CPUCollector  (UPDATE)   if info['enabled']['cpu']    else None
        self.ram     = collectors.RamCollector  (UPDATE)   if info['enabled']['ram']    else None
        self.net     = collectors.NetCollector  (UPDATE)   if info['enabled']['net']    else None
        self.disks   = collectors.DisksCollector(UPDATE)   if info['enabled']['disks']  else None
        self.fans    = collectors.FansCollector  (UPDATE)  if info['enabled']['disks']  else None
        self.mainInfo = [self.cpu, self.ram, self.net, self.disks, self.fans]
    def start(self):
        self.work.run()

if __name__ == "__main__":
    programm = core()
    programm.start()