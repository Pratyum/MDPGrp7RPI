import threading
import time

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

wifiCon = None
btCon = None
serialCon = None

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
    time.sleep(5)
    if (btCon.is_connected() or btCon is not None):
        if( len(btQueue) > 0 ):
            message = btQueue.popleft()
            temp = btCon.send(message)
            if temp == 2: 
                return 2

            print("%s - btSend(): Message to Bluetooth: %s" %(time.ctime(), message))
    else:
        print("btSend(): Detected btCon down. ")
        print("btSend(): Sleep 15 Seconds and wait")
        time.sleep(15)

def btReceive():
    #Incoming Data from Android 
    if (btCon.is_connected() or btCon is not None):
        tempBuffer = btCon.receive()

        if(tempBuffer != ''):
            if tempBuffer == 2:
                return 2

            if (str(tempBuffer)[0] == 'c'):
                #Send manual movement to arduino
                serialQueue.append(tempBuffer[1:])
            elif (str(tempBuffer)[0] == 'd'):
                #Tell algo to start exploration/fastest path
                wifiQueue.append(tempBuffer[1:])
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
    time.sleep(5)
        
def setBTCon():
    #establish bluetooth connection
    global btCon
    if btCon is None:
        btCon = BTcon()
        btCon.listen()
        print("setBTCon(): Bluetooth Connection Up!")
    else:
        time.sleep(50)      
        
dummyThread = RPIThread(function = mockFunction, name='test')

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])
    
    threadList = ['bt-conThread', 'btSend-Thread', 'btReceive-Thread']
    
    #Bluetooth is thread 2
    bt_conThread = RPIThread(function = setBTCon, name = 'bt-conThread')
    bt_conThread.daemon = True
    bt_conThread.start()

    connectionThreadCounter = 0 #connection thread counter must be three to signify that all three connections are up 
    
    while(connectionThreadCounter != 1):
        if bt_conThread is not None and btCon.is_connected():
            btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
            btSend_Thread.daemon = True
            btSend_Thread.start()
            print("bt send Started")
            btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
            btReceive_Thread.daemon = True
            btReceive_Thread.start()
            print("bt receive Started")
            connectionThreadCounter += 1
            
    while (threading.activeCount() != 5):
        #Check to ensure that pre-determined number of threads (9) + 2 main threads are up before starting 
        time.sleep(.5)
        continue

    print("Threadings for all components up! Thread Count: " + threading.activeCount())
    totalCount = threading.activeCount()
    
    while True:

        if(threading.activeCount() != totalCount):
            print("Some Thread Died, Checking...")

            tempThreadList = []
            for tempThread in threading.enumerate():
                if (isinstance(tempThread, type(dummyThread))):
                    tempThreadList.append(tempThread.threadName)

            differenceList = list(set(threadList) - set(tempThreadList))
            for i in differenceList:

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

        time.sleep(1)
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



