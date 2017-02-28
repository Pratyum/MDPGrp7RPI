import threading
import time
import serial #sudo pip/pip3 install pyserial

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
                print("GOT 2, KILLING" + self.threadName +"THREAD NOW")
                self.running = False
            
    def stop(self):
        self.running = False
        

def mockFunction():
    #Mock Function to create Dummy RPIThread object for comparison
    pass

def serialReceive():
    #Incoming data from Arduino
    while True:
        if (serialCon.is_connected()):
            tempBuffer = serialCon.receive()
            if (tempBuffer != ''):
                wifiQueue.append(tempBuffer[1:])                
                print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))
        else:
            #serialConnection down, sleep and wait for something to happen
            print("serialSend() detects serialCon down. ")
            time.sleep(10)
            
        time.sleep(0.5)

def serialSend():
    #Outgoing Data to Arduino
    while True:        
        time.sleep(0.5)
        if (serialCon.is_connected()):
            if (len(serialQueue) > 0):
                message = serialQueue.popleft()
                serialCon.send(message)
                print("%s: Message to serial: %s" % (time.ctime(), message))
        else:
            #serialConnection down, sleep and wait for something to happen
            print("serialSend() detects serialCon down. ")
            time.sleep(10)

def btSend():
    #Outgoing Data to Android
    while True:        
        time.sleep(5)
        if (btCon.is_connected() or btCon is not None):
            if( len(btQueue) > 0 ):
                message = btQueue.popleft()
                btCon.send(message)
                print("%s: Message to Bluetooth: %s" %(time.ctime(), message))
        else:
            print("btSend() detected btCon down. ")
            time.sleep(10)

def btReceive():
    #Incoming Data from Android 
    while True:
        if (btCon.is_connected() or btCon is not None):
            tempBuffer = btCon.receive()
            if(tempBuffer != ''):
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

                print("%s: Message from Bluetooth: %s" %(time.ctime(), tempBuffer))
        else:
            #serialConnection down, sleep and wait for something to happen
            print("btReceive() detects btCon down. ")
            time.sleep(10)
        time.sleep(5)

def wifiSend():
    #Outgoing data to Algo
    while True:
        try:
            #TODO: send 2 blank messages to check if TCP Connection still alive
            wifiCon.send('')
            wifiCon.send('')
        except Exception:
            wifi_conThread.stop()
            print("No of active threads running: " + threading.activeCount())
            print("Detected that TCP cannot send, stopping thread now")
            time.sleep(1)
            print("Thread stopped")
            print("No of active threads running: " + threading.activeCount())
            continue
        
        time.sleep(0.5)
        if(len(wifiQueue) > 0):
            message = wifiQueue.popleft()
            wifiCon.send(message)
            print("%s: Message to Wifi: %s" %(time.ctime(), message))

def wifiReceive():
    #Incoming data from Algo
    while True:
        if (wifiCon.is_connected()):
            tempBuffer = wifiCon.receive()
            if(tempBuffer != ''):
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
        else:
            #serialConnection down, sleep and wait for something to happen
            print("wifiReceive() detects wifiCon down. ")
            time.sleep(10)
        time.sleep(0.5)

def setSerialCon():
    #establish serial connection
    global serialCon
    if serialCon is None:
        serialCon = Seriouscon()
        serialCon.listen()
        time.sleep(3)
        print("Serial Connection Up!")
    else:
        time.sleep(50)

def setBTCon():
    #establish bluetooth connection
    global btCon
    if btCon is None:
        btCon = BTcon()
        btCon.listen()
        print("Bluetooth Connection Up!")
    else:
        time.sleep(50)

def setWifiCon():
    #establish wifi connection
    global wifiCon
    if wifiCon is None:
        wifiCon = Tcpcon()
        wifiCon.listen()
        print("Wifi Connection Up!")
    else: 
        time.sleep(50)
        
dummyThread = RPIThread(function = mockFunction, name='test')

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])


    wifi_conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
    wifi_conThread.start()
    bt_conThread = RPIThread(function = setBTCon(), name = 'bt-conThread')
    bt_conThread.start()
    serial_conThread = RPIThread(function = setSerialCon, name = 'serial-conThread')
    serial_conThread.start()

    connectionThreadCounter = 0 #connection thread counter must be three to signify that all three connections are up 

    while (connectionThreadCounter != 3):
        if wifi_conThread is not None and wifiCon.is_connected():
            wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
            wifiSend_Thread.start()
            print('Wifi Send Started')
            wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
            wifiReceive_Thread.start()
            print('Wifi receive started')
            connectionThreadCounter += 1

        if bt_conThread is not None and btCon.is_connected():
            btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
            btSend_Thread.start()
            print("bt send Started")
            btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
            btReceive_Thread.start()
            print("bt receive Started")
            connectionThreadCounter += 1

        if serial_conThread is not None and serialCon.is_connected():
            serialSend_Thread = RPIThread(function = serialSend, name='serialSend-Thread')
            serialSend_Thread.start()
            print('serial send started')
            serialReceive_Thread = RPIThread(function = serialReceive, name='serialReceive-Thread')
            serialReceive_Thread.start()
            print("serial receive started")
            connectionThreadCounter += 1

    while(threading.activeCount() != 11):
        #Check to ensure that pre-determined number of threads (9) + 2 main threads are up before starting 
        time.sleep(.5)
        continue

    time.sleep(5)
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
                if (i == 'wifi-conThread'):
                    print("Wifi Connection Thread detected to be dead!")
                    wifiSend_Thread.stop()
                    wifiReceive_Thread.stop()
                    print("wifiSend() & wifiReceive() Threads killed...")
                    time.sleep(5)

                    wifiCon = None
                    
                    print("resetting wifi connection...")
                    wifi_conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
                    wifi_conThread.start()
                    while (not wifiCon is not None and wifiCon.is_connected()):
                        time.sleep(.5)
                    
                    print("wifiCon up")
                    
                    wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
                    wifiSend_Thread.start()
                    print("wifiSend up")
                    wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
                    wifiReceive_Thread.start()
                    print("wifiReceive up")

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
                    

                if( i == "serial-conThread"):
                    print("Serial Connection Thread detected to be dead!")
                    serialSend_Thread.stop()
                    serialReceive_Thread.stop()
                    print("serialSend() & serialReceive() Threads killed...")
                    time.sleep(5)

                    serialCon = None 
                    
                    print('Resetting serial connection...')
                    serial_conThread = RPIThread(function = setSerialCon, name = 'serial-conThread')
                    serial_conThread.start()
                    while(not serialCon is not NOne and seiralCon.is_connected()):
                        time.sleep(.5)
                    print("Serial Connections up!")
                    
                    serialSend_Thread = RPIThread(function = serialSend, name='serialSend-Thread')
                    serialSend_Thread.start()
                    print("serialSend up!")
                    serialReceive_Thread = RPIThread(function = serialReceive, name='serialReceive-Thread')
                    serialReceive_Thread.start()
                    print("serialReceive up!")
                    

        time.sleep(1)
        continue
    
except KeyboardInterrupt:    
    print("Threads left: \n" + str(threading.enumerate()))
    print("Killing threads...")
    for i in threading.enumerate():
        #Kill all RPIThread threads
        if i is type(dummyThread): 
            print(i.threadName + " thread is killed")
            i.stop()
    time.sleep(5)
    print("Threads left: \n" + str(threading.enumerate()))
    print("Threads killed")
    #kill everything
