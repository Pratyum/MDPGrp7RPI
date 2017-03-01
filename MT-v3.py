import threading
import time

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

wifiCon = None
btCon = None
serialCon = None
conCheck = None

class globalCheck():
    def __init__(self):
        self.bt = False
        self.wifi = False
        self.serial = False
        
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
            test = self.function()
            if (test == 2):
                #if kill thread
                print("GOT 2, KILLING " + self.threadName +" THREAD NOW")
                self.running = False
            
    def stop(self):
        self.running = False

def wifiReceive():
    #Incoming Data from Algo
    if (conCheck.wifi is False):
        print("wifiReceive(): Detected wifiCon down. ")
        print("wifiReceive(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    if (wifiCon is not None):
        if wifiCon.is_connected():
            
            tempBuffer = wifiCon.receive()
            if tempBuffer == 2:
                conCheck.wifi = False
                time.sleep(15)
                return
                    
            if(str(tempBuffer)[0] == 'a'):
                #send to robot
                serialQueue.append(tempBuffer[1:])
            elif(str(tempBuffer)[0] == 'b'):
                #send to android
                btQueue.append(tempBuffer[1:])
            else:
                try:
                    print("| ERROR ERROR | WIFI RECEIVE: " + tempBuffer)
                except Exception:
                    pass

            print("%s: Message From Wifi: %s" %(time.ctime(), tempBuffer))        
    time.sleep(.5)        
        
def wifiSend():
    #Outgoing Data to Algo
    if (conCheck.wifi is False):
        print("wifiSend(): Detected wifiCon down. ")
        print("wifiSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    wifiCon.send('')
    temp = wifiCon.send('')
    if temp == 2:
        conCheck.wifi = False
        time.sleep(15)
        return
    
    
    time.sleep(.5)
    if (wifiCon is not None):
        if wifiCon.is_connected():
            if( len(wifiQueue) > 0 ):
                message = wifiQueue.popleft()
                temp = wifiCon.send(message)

                print("%s - wifiSend(): Message to Algo: %s" %(time.ctime(), message))
    else:
        print("wifiSend(): Detected wifiCon down. ")
        print("wifiSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
def setWifiCon():
    #establish wifi connection
    global wifiCon
    if wifiCon is None:
        wifiCon = Tcpcon()
        wifiCon.listen()
        print("Wifi Connection Up!")
    else: 
        time.sleep(50)
        
conCheck = globalCheck()        

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])
        
    wifi_conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
    wifi_conThread.daemon = True
    wifi_conThread.start()

    connectionThreadCounter = 0 #connection thread counter must be three to signify that all three connections are up 
    
    while(connectionThreadCounter != 1):
        if wifiCon is not None:
            if (wifiCon.is_connected()):
                
                wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
                wifiSend_Thread.daemon = True
                wifiSend_Thread.start()
                print('Wifi Send Started')
                
                wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
                wifiReceive_Thread.daemon = True
                wifiReceive_Thread.start()
                print('Wifi receive started')
                
                conCheck.wifi = True
                connectionThreadCounter += 1
            

    time.sleep(.5)
    print("Threadings for all components up! Thread Count: " + str(threading.activeCount()))
    totalCount = threading.activeCount()
    
    while True:
        if (conCheck.wifi is False):
            print("Wifi Connection Thread detected to be dead!")
            wifi_conThread.stop()
            wifiSend_Thread.stop()
            wifiReceive_Thread.stop()
            print("Wifi Threads Killed")
            time.sleep(3)
            
            wifiCon = None
            print("Resetting wifi connection...")
            wifi_conThread = RPIThread(function = setWifiCon(), name = 'wifi-conThread')
            wifi_conThread.daemon = True
            wifi_conThread.start()
            
            while wifiCon is None:
                time.sleep(.1)
            while not wifiCon.isConnect():
                time.sleep(.1)
                
            print("Wifi Connctions Up")
            
            wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
            wifiSend_Thread.daemon = True
            wifiSend_Thread.start()
            print('Wifi Send Started')
            wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
            wifiReceive_Thread.daemon = True
            wifiReceive_Thread.start()
            print('Wifi receive started')
            conCheck.wifi = True
            
        time.sleep(3)
        continue

except KeyboardInterrupt:    
    print("Threads killed")

