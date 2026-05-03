
import threading
import time

class threadWork:
    def __init__(self):
        self. THRs = []
        
    def initTHR(self, thrs = []):
        for i in range(len(thrs)):
            self.THRs.append( threading.Thread(target=thrs[i].run, daemon=True))
    def startTHRs(self):
        try: 
            for i in self.THRs:
                if i is None: continue
                else:
                    i.start()
            return True
        except Exception as e:
            print(f"какая то ошибка с потоками: \n {e}")
            return False
    def startTHR(self, index):
        try:
            self.THRs[index].start()
            return True
        except Exception:
            return False

    


