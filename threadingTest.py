import threading
import time
import sys

class RPIThread(threading.Thread):
    def __init__(self, function, name):
        self.threadName = name
        self.running = False
        self.function = function
        super(RPIThread, self).__init__()
        
    def start(self):
        self.running = True
        super(RPIThread, self).start()
        
    def run(self):
        while self.running:
            self.function()
            
    def stop(self):
        self.running = False
        
def mockFunction1():
    pass

def mockFunction():
    print("Mock Function! ")
    time.sleep(5)
        
def mockWifiReceive():
    print("Mock Wifi Receive!")
    time.sleep(20)
    
def mockWifiSend():
    print("Mock Wifi Send!")
    time.sleep(20)
    
def mockWifiCon():
    print("Mock Wifi Connection established!")
    time.sleep(10)
    print("Mock Wifi Connection Kill")
    sys.exit()

threadList = ['mockWifiReceive', 'mockWifiSend', 'mockWifiCon']
mwr = RPIThread(function=mockWifiReceive, name='mockWifiReceive')
mwr.start()

mws = RPIThread(function=mockWifiSend, name='mockWifiSend')
mws.start()

mwc = RPIThread(function=mockWifiCon, name='mockWifiCon')
mwc.start()

dummyThread = RPIThread(function=mockFunction, name='test')

totalCount = threading.activeCount()

while True:
    print(threading.activeCount())
    time.sleep(5)
    if(threading.activeCount() != totalCount):
        #some thread died
        print("thread died, checking...")
        
        tempThreadList = []
        for tempThread in threading.enumerate():
            if (isinstance(tempThread, type(dummyThread))):
                tempThreadList.append(tempThread.threadName)

        differenceList = list(set(threadList) - set(tempThreadList))
        for i in differenceList:
            if (i == 'mockWifiCon'):
                print("\n\nwifi Connection died!\n\n")
                mws.stop()
                mwr.stop()
                print(str(threading.activeCount()))
                time.sleep(10)
                print(str(threading.activeCount()))
                
                print("Stopped all connections! No of threads running: "+str(threading.activeCount()))
                mwr = RPIThread(function=mockWifiReceive, name='mockWifiReceive')
                mwr.start()

                mws = RPIThread(function=mockWifiSend, name='mockWifiSend')
                mws.start()
        
                mwc = RPIThread(function=mockWifiCon, name='mockWifiCon')
                mwc.start()
                        
        
    
print(threading.enumerate())
print(str(len(threading.enumerate())))

'''
while True:
    if (threading.activeCount() != totalCount):       
        for i in threading.enumerate():
            try:
                if (isinstance(i, type(dummyThread))):
                    if i.threadName == 'testname':
                        print('GOT THE OBJECT')
            except AttributeError:
                print("error")
                pass
        #    print(type(i))
        time.sleep(10)

print('out from sleep')
#test1.stop()
#test1.exit()
#test2.stop()
#test2.exit()
'''

print(threading.enumerate())
print(str(len(threading.enumerate())))
