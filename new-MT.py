import threading
import time
import serial #sudo pip/pip3 install pyserial

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

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

def mockFunction():
    #Mock Function to create Dummy RPIThread object for comparison
    pass

def serialReceive():
    #Incoming data from Arduino
    while True:
        tempBuffer = serialCon.receive()
        if (tempBuffer != ''):
            wifiQueue.append(tempBuffer[1:])                
            print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))
            
        time.sleep(0.5)

def serialSend():
    #Outgoing Data to Arduino
    while True:
        try:
            #check if connection still alive
            serialCon.send("")
        except Exception:
            time.sleep(.5)
            continue
        
        time.sleep(0.5)
        if (len(serialQueue) > 0):
            message = serialQueue.popleft()
            serialCon.send(message)
            print("%s: Message to serial: %s" % (time.ctime(), message))

def btSend():
    #Outgoing Data to Android
    while True:
        try:
            #check if connection still alive
            btCon.send('')
        except Exception:
            time.sleep(.5)
            continue
        
        time.sleep(0.5)
        if( len(btQueue) > 0 ):
            message = btQueue.popleft()
            btCon.send(message)
            print("%s: Message to Bluetooth: %s" %(time.ctime(), message))

def btReceive():
    #Incoming Data from Android 
    while True:
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
        time.sleep(0.5)

def wifiSend():
    #Outgoing data to Algo
    while True:
        try:
            #TODO: send 2 blank messages to check if TCP Connection still alive
            wifiCon.send('')
            wifiCon.send('')
        except Exception:
            time.sleep(.5)
            continue
        
        time.sleep(0.5)
        if(len(wifiQueue) > 0):
            message = wifiQueue.popleft()
            wifiCon.send(message)
            print("%s: Message to Wifi: %s" %(time.ctime(), message))

def wifiReceive():
    #Incoming data from Algo
    while True:
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
        time.sleep(0.5)

def setSerialCon():
    #establish serial connection
    serialCon = Seriouscon()
    serialCon.listen()
    time.sleep(3)
    print("Serial Connection Up!")

def setBTCon():
    #establish bluetooth connection
    btCon = BTcon()
    btCon.listen()
    time.sleep(1)
    print("Bluetooth Connection Up!")

def setWifiCon():
    #establish wifi connection
    wifiCon = Tcpcon()
    wifiCon.listen()
    time.sleep(1)
    print("Wifi Connection Up!")
    
#Queues for messages     
serialQueue = deque([])
btQueue = deque([])
wifiQueue = deque([])


wifi-conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
wifi-conThread.start()
bt-conThread = RPIThread(function = setBTCon(), name = 'bt-conThread')
bt-conThread.start()
serial-conThread = RPIThread(function = setSerialCon, name = 'serial-conThread')
serial-conThread.start()
print("Threading for connections up!")

wifiSend-Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
wifiSend-Thread.start()
wifiReceive-Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
wifiReceive-Thread.start()

btSend-Thread = RPIThread(function = btSend, name='btSend-Thread')
btSend-Thread.start()
btReceive-Thread = RPIThread(function = btReceive, name='btReceive-Thread')
btReceive-Thread.start()

serialSend-Thread = RPIThread(function = serialSend, name='serialSend-Thread')
serialSend-Thread.start()
serialReceive-Thread = RPIThread(function = serialReceive, name='serialReceive-Thread')
serialReceive-Thread.start()
print("Threadings for all components up!")

dummyThread = RPIThread(function = mockFunction, name='test')
totalCount = threading.activeCount()


while True:
    try:
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
                    wifiSend-Thread.stop()
                    wifiReceive-Thread.stop()
                    print("wifiSend() & wifiReceive() Threads killed...")
                    time.sleep(5)

                    wifiSend-Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
                    wifiSend-Thread.start()
                    wifiReceive-Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
                    wifiReceive-Thread.start()
                    wifi-conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
                    wifi-conThread.start()
                    print("Wifi connections up")
                    
                elif( i == 'bt-conThread'):
                    print("Bluetooth Connetion Thread detected to be dead!")
                    btSend-Thread.stop()
                    btReceive-Thread.stop()
                    print("btSend() & btReceive() Threads killed...")
                    time.sleep(5)

                    btSend-Thread = RPIThread(function = btSend, name='btSend-Thread')
                    btSend-Thread.start()
                    btReceive-Thread = RPIThread(function = btReceive, name='btReceive-Thread')
                    btReceive-Thread.start()
                    bt-conThread = RPIThread(function = setBTCon(), name = 'bt-conThread')
                    bt-conThread.start()
                    print("Bluetooth Connections up")

                elif( i == "serial-conThread"):
                    print("Serial Connection Thread detected to be dead!")
                    serialSend-Thread.stop()
                    serialReceive-Thread.stop()
                    print("serialSend() & serialReceive() Threads killed...")
                    time.sleep(5)
                    
                    serialSend-Thread = RPIThread(function = serialSend, name='serialSend-Thread')
                    serialSend-Thread.start()
                    serialReceive-Thread = RPIThread(function = serialReceive, name='serialReceive-Thread')
                    serialReceive-Thread.start()
                    serial-conThread = RPIThread(function = setSerialCon, name = 'serial-conThread')
                    serial-conThread.start()
                    print("Serial Connections up!")
        
        
        time.sleep(1)
        pass
    
    except KeyboardInterrupt:
        print("Killing threads...")
        for i in threading.enumerate():
            #Kill all RPIThread threads
            if (isinstance(i, type(dummyThread))):
                i.stop()
        time.sleep(5)
        print("Threads killed")
        #kill everything
