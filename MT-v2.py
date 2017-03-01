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

def mockFunction():
    #Mock Function to create Dummy RPIThread object for comparison
    pass


def btSend():
    #Outgoing Data to Android
    if (conCheck.bt is False):
        print("btSend(): Detected btCon down. ")
        print("btSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    time.sleep(.5)
    if (btCon is not None):
        if btCon.is_connected():
            if( len(btQueue) > 0 ):
                message = btQueue.popleft()
                temp = btCon.send(message)
                if temp == 2: 
                    conCheck.bt = False
                    return

                print("%s - btSend(): Message to Bluetooth: %s" %(time.ctime(), message))
    else:
        print("btSend(): Detected btCon down. ")
        print("btSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
        


def btReceive():
    #Incoming Data from Android 
    if (conCheck.bt is False):
        print("btReceive(): Detected btCon down. ")
        print("btReceive(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    if (btCon is not None):
        if btCon.is_connected():
            tempBuffer = btCon.receive()

            if(tempBuffer != ''):
                if tempBuffer == 2:
                    conCheck.bt = False
                    return

                if (str(tempBuffer)[0] == 'c'):
                    #Send manual movement to arduino
                    serialQueue.append(tempBuffer[1:])
                elif (str(tempBuffer)[0] == 'd'):
                    #Tell algo to start exploration/fastest path
                    wifiQueue.append(tempBuffer[1:])
                elif (str(tempBuffer)[0] == 'z'):
                    btQueue.append(tempBuffer[1:])
                else:
                    try:
                        print("| ERROR ERROR | BT RECEIVE: " + tempBuffer)
                    except Exception:
                        pass

                print("%s - btReceive(): Message from Bluetooth: %s" %(time.ctime(), tempBuffer))
    else:
        #serialConnection down, sleep and wait for something to happen
        print("btReceive(): Detects btCon down. ")
        print("btReceive(): Sleep 15 Seconds and wait")
        time.sleep(15)
    time.sleep(.5)
        
def setBTCon():
    #establish bluetooth connection
    global btCon
    if btCon is None:
        btCon = BTcon()
        btCon.listen()
        print("setBTCon(): Bluetooth Connection Up!")
    else:
        time.sleep(50)      
        

conCheck = globalCheck()        
dummyThread = RPIThread(function = mockFunction, name='test')

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])
        
    #Bluetooth is thread 2
    bt_conThread = RPIThread(function = setBTCon, name = 'bt-conThread')
    bt_conThread.daemon = True
    bt_conThread.start()

    connectionThreadCounter = 0 #connection thread counter must be three to signify that all three connections are up 
    
    while(connectionThreadCounter != 1):
        if btCon is not None:
            if (btCon.is_connected()):
                btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
                btSend_Thread.daemon = True
                btSend_Thread.start()
                print("bt send Started")
                btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
                btReceive_Thread.daemon = True
                btReceive_Thread.start()
                print("bt receive Started")
                conCheck.bt = True
                print("conCheck.bt is true")
                connectionThreadCounter += 1
                print("connectionThreadCounter count: " + str(connectionThreadCounter))
        

    time.sleep(.5)
    print("Threadings for all components up! Thread Count: " + str(threading.activeCount()))
    totalCount = threading.activeCount()
    
    while True:
        if(conCheck.bt is False):
            print("Bluetooth Connetion Thread detected to be dead!")
            bt_conThread.stop()
            btSend_Thread.stop()
            btReceive_Thread.stop()
            print("BT Threads killed")
            time.sleep(3)
            
            btCon = None
            print("Resetting bt connection...")
            bt_conThread = RPIThread(function = setBTCon(), name = 'bt-conThread')
            bt_conThread.daemon = True
            bt_conThread.start()
            while(btCon is None):
                time.sleep(.1)
            while (not btCon.is_connected()):
                time.sleep(.1)
            
            print("Bluetooth Connections up")

            btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
            btSend_Thread.daemon = True
            btSend_Thread.start()
            print("btSend up!")
            btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
            btReceive_Thread.daemon = True
            btReceive_Thread.start()
            print("btReceive up!")
            conCheck.bt = True
        
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
    print("Threads left: \n" + str(threading.enumerate()))
    print("Killing threads...")
#    for i in threading.enumerate():
#        #Kill all RPIThread threads
#        if i is type(dummyThread): 
#            print(i.threadName + " thread is killed")
#            i.stop()
#    time.sleep(5)
    print("Threads left: \n" + str(threading.enumerate()))
    print("Threads killed")
    #kill everything



    
    
    '''
    if(threading.activeCount() != totalCount):
            print("Some Thread Died, Checking...")
            print("totalCount = " + str(totalCount) + ", currentCount = " + str(threading.activeCount()))
            print(threading.enumerate())

            tempThreadList = []
            for tempThread in threading.enumerate():
                if (isinstance(tempThread, type(dummyThread))):
                    tempThreadList.append(tempThread.threadName)

            print("threadList :" + str(threadList))
            print("tempThreadList: " + str(tempThreadList))
            differenceList = list(set(threadList) - set(tempThreadList))
            print("differenceList: " + str(list(set(threadList) - set(tempThreadList))))
            for i in differenceList:
                print("Into the for loop!")
                if( i == 'bt-conThread'):
                    print("Bluetooth Connetion Thread detected to be dead!")
                    btSend_Thread.stop()
                    btReceive_Thread.stop()
                    print("btSend() & btReceive() Threads killed...")
                    time.sleep(5)
                    
                    btCon = None
                    print("Resetting bt connection...")
                    bt_conThread = RPIThread(function = setBTCon(), name = 'bt-conThread')
                    bt_conThread.start()
                    while(not btCon is not None and btCon.is_connected()):
                        time.sleep(.5)
                    print("Bluetooth Connections up")

                    btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
                    btSend_Thread.start()
                    print("btSend up!")
                    btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
                    btReceive_Thread.start()
                    print("btReceive up!")
    
    
    '''
