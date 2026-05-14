from datetime import datetime, timedelta
import time
import psutil as psu
import subprocess

def debug(msg):
#    print(msg)
    pass

class collector:

    def readTemplate(self):
        pass

    def __init__(self, NewFrequency):
        self.bfG = lambda data: round( data  / 1024 / 1024 /1024, 3 )
        self.bfM = lambda data: round( data  / 1024 / 1024, 3 )
        self.readTemplate()
        self._lastRun = datetime.now()
        self._freq    = NewFrequency
        self.data     = self.GetNames()
        self.dataJ    = self.GetData()
        self.dataH    = self.RenderForHtml()

    def run(self):
        while True:                                    
            if datetime.now()>self._lastRun+timedelta(seconds = self._freq):
                self._lastRun = datetime.now()
                self.dataJ = self.GetData()
                self.dataH = self.RenderForHtml()

                #debug(self.dataD)
            time.sleep(0.5)
    
    def GetData(self):  
        pass

    def GetNames(self): 
        return None

    def returnData(self): 
        return self.dataJ
    def returnHTML(self):
        return self.dataH
    def RenderForHtml(self): 
        pass
class RamCollector(collector):

    def readTemplate(self):
        self.RAMItem= ""
        with open("./htms/ram.htm", 'r') as file:
            self.RAMItem= file.read()

    def GetData(self):
        # Init SWAP and Memory
        dataRAM = psu.virtual_memory()
        dataSwap = psu.swap_memory()
        return {
            "RAM": {
                "total":  self.bfG(dataRAM.total),
                "used":   self.bfG(dataRAM.used),
                "free":   self.bfG(dataRAM.free),
                },
            "SWAP": {
                "total": self.bfG(dataSwap.total),
                "used":  self.bfG(dataSwap.used),
                "free":  self.bfG(dataSwap.free)
                }
            }
        #Returned info
        
    def RenderForHtml(self):
        res = self.RAMItem
        res = res.replace("#RAMTotal#" ,"{:,.2f} Gb".format(self.dataJ["RAM"] ["total"]))
        res = res.replace("#RAMUsed#"  ,"{:,.2f} Gb".format(self.dataJ["RAM"] ["used"] ))
        res = res.replace("#RAMFree#"  ,"{:,.2f} Gb".format(self.dataJ["RAM"] ["free"] ))
        res = res.replace("#SWAPTotal#","{:,.2f} Gb".format(self.dataJ["SWAP"]["total"]))
        res = res.replace("#SWAPUsed#" ,"{:,.2f} Gb".format(self.dataJ["SWAP"]["used"] ))
        res = res.replace("#SWAPFree#" ,"{:,.2f} Gb".format(self.dataJ["SWAP"]["free"] )) 
        return res 
class CPUCollector(collector):

    def readTemplate(self):
        self.cpuItem= ""
        with open("./htms/cpu.htm", 'r') as file:
            self.cpuItem= file.read()

        self.cpuItem2 = ""
        with open("./htms/cpuitem.htm", 'r') as file:
            self.cpuItem2= file.read()


    def GetData(self):
        precents = psu.cpu_percent(interval=1, percpu=True)
        freq     = [i.current for i in psu.cpu_freq(percpu=True)]
        temps    = psu.sensors_temperatures(fahrenheit=False)["k10temp"][0].current            
        name = ""
        
        # trying get name
        for i in ['wmic cpu get name', "cat /proc/cpuinfo | grep 'model name'"]:
            
            try:
                name = subprocess.run(i, shell=True, capture_output=True, text=True ).stdout.split(':')[1].strip()
           
            except Exception: # If core not working in this commands
                continue
        result = {
            "name": name,
            "temp": temps,
            "cores": [
                {
                    "core":    i,
                    "freq":    freq[i]//1000,
                    "percent": precents[i]

                } for i in range(len(precents))]
        }
        return result
    def RenderForHtml(self):

        self.cpuItem=self.cpuItem.replace("#CPUName#",self.dataJ["name"])
        self.cpuItem=self.cpuItem.replace("#CPUTemp#",str(self.dataJ["temp"]))
        cpuCoresInfo = ""
        for i in range(len(self.dataJ['cores'])):
            localData = self.cpuItem2
            localData = localData.replace("#CPUCoreIndex#", f"{i}")
            localData = localData.replace('#CPUCoreFreq#', str(self.dataJ["cores"][i]["freq"]//1000))
            localData = localData.replace('#CPUCorePrecent#', str(self.dataJ["cores"][i]["percent"])) 
            cpuCoresInfo +=  localData
        result = self.cpuItem.replace("##CPUCoresInfo##", cpuCoresInfo)

        return result

class NetCollector(collector):
    def readTemplate(self):
        self.netItem1= ""
        with open("./htms/nets.htm", 'r') as file:
            self.netItem1= file.read()

        self.netItem2= ""
        with open("./htms/netitem.htm", 'r') as file:
            self.netItem2= file.read()

    def GetData(self):
        data1 = { k:[v.bytes_sent, v.bytes_recv] for k,v in psu.net_io_counters(pernic=True).items()}
        time.sleep(1)
        data2 = { k:[v.bytes_sent, v.bytes_recv] for k,v in psu.net_io_counters(pernic=True).items()}
        
        addr = {}
        for iface, addrs in psu.net_if_addrs().items():
            for snic in addrs:
                if snic.family == 2:  
                    addr[iface] = snic.address
        

        return { k: 
            {
                "addr":        addr[k],
                "speedInput":  self.bfM(data2[k][0]- data1[k][0]), 
                "speedOutput": self.bfM(data2[k][1]- data1[k][1]),
                "sent":        self.bfM(data2[k][0]),
                'recv':        self.bfM(data2[k][1])

            } for k,v in data2.items()

        }
    def RenderForHtml(self):
        netIntstr = ""
        for k,v in self.dataJ.items():
            sh = self.netItem2
            sh = sh.replace("#interfaceName#", k            )
            sh = sh.replace("#IPAddr#",   v["addr"]         )
            sh = sh.replace("#speedOut#", str(v["speedOutput"]))
            sh = sh.replace("#speedInp#", str(v["speedInput"]))
            sh = sh.replace("#recv#",     str(v["sent"])    )
            sh = sh.replace("#sent#",     str(v["recv"])    )
            netIntstr += sh

        result = self.netItem1.replace("##NetInterfaces##", netIntstr)
        return result

class DisksCollector(collector):
    def readTemplate(self):
        self.diskItem1= ""
        with open("./htms/disks.htm", 'r') as file:
            self.diskItem1= file.read()

        self.diskItem2= ""
        with open("./htms/disksitem.htm", 'r') as file:
            self.diskItem2= file.read()
        
    def GetNames(self):
            return {i.device:{"mount": i.mountpoint, "fs": i.fstype} for i in psu.disk_partitions()}
    def GetData(self):
        mountpoints = [v["mount"] for k, v in self.data.items()]

        results = {}
        for i,v in self.data.items():
            i = i.replace("/dev/", '')
            j = psu.disk_usage(v["mount"])
            ko = psu.disk_io_counters(perdisk=True)[i]
            time.sleep(1)
            kn = psu.disk_io_counters(perdisk=True)[i]
            results[i] = {  "total":    (j.total), 
                            "used":     (j.used), 
                            "speed":{   
                                "read": (kn.read_bytes - ko.read_bytes),
                                "write":(kn.write_bytes - ko.write_bytes)
                            },           
                            "free":     (j.free)
                            }
        return results
    def RenderForHtml(self):
        result = self.diskItem1

        disksData = ""
        for k,v in self.dataJ.items():
            sh = self.diskItem2
            sh = sh.replace("#diskName#"  , str(k)                         )
            sh = sh.replace("#TotalStore#", "{:,.2f} Gb".format(self.bfG(v["total"]        )))
            sh = sh.replace("#UsedStore#" , "{:,.2f} Gb".format(self.bfG(v["used"]         )))
            sh = sh.replace("#speedInp#"  , "{:,.2f} Mb/s".format(self.bfM(v["speed"]["read"]  )))
            sh = sh.replace("#speedOut#"  , "{:,.2f} Mb/s".format(self.bfM(v["speed"]["write"] )))
            sh = sh.replace("#percStore#" , "{:,.2f} %".format(round(v["free"]/v["total"],2)))
            disksData += sh
        result = result.replace("##Disks##", disksData)
        return result
    
class FansCollector(collector):
    def readTemplate(self):
        self.fanItem1= ""
        with open("./htms/fans.htm", 'r') as file:
            self.fanItem1= file.read()

        self.netItem2= ""
        with open("./htms/fansitem.htm", 'r') as file:
            self.fanItem2= file.read()
           

    def GetData(self):
        data = psu.sensors_fans()

        fans = {}
        result = {}
        for k,v in data.items():
            result[k] = [i.current for i in v]

        return result
    def RenderForHtml(self):
        fans_data = self.dataJ
        result = self.fanItem1
        dataFans = ""
        for k, speeds in fans_data.items():
            if len(speeds) > 1:
                for i, speed in enumerate(speeds):
                    fan_name = f"{k} {i}"
                    sh = self.fanItem2.replace("#fansIndex#", fan_name)
                    sh = sh.replace("#fanSpeed#", "{:,.0f} RPM".format(speed).replace(",", "&nbsp;"))
                    dataFans += sh
            else:
                sh = self.fanItem2.replace("#fansIndex#", k)
                sh = sh.replace("#fanSpeed#", "{:,.0f} RPM".format(speeds[0]).replace(",", "&nbsp;"))
                dataFans += sh
        return result.replace("##FansSpeedInfo##", dataFans)
        
        return result
