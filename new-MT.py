#import thread #or just '_thread' for python3
from threading import Thread as thread
import threading
import time
import serial #sudo pip/pip3 install pyserial

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

class RPIThread(threading.Thread):
    def __init__(self, function, name):
        self.name = name
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
        time.sleep(0.5)
        if (len(serialQueue) > 0):
            message = serialQueue.popleft()
            serialCon.send(message)
            print("%s: Message to serial: %s" % (time.ctime(), message))

def btSend():
    #Outgoing Data to Android 
    while True:
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
        
        #TODO: send 2 blank messages to check if TCP Connection still alive
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

wifiSend-Thread = RPIThread(function = wifiSend, name='wifiSend')
wifiSend-Thread.start()
wifiReceive-Thread = RPIThread(function = wifiReceive, name='wifiReceive')
wifiReceive-Thread.start()

btSend-Thread = RPIThread(function = btSend, name='btSend')


thread(name='wifiSend', target=wifiSend).start()
thread(name='wifiReceive', target=wifiReceive).start() 
thread.start_new_thread(wifiSend, ())
thread.start_new_thread(wifiReceive, ())
thread.start_new_thread(btSend, ())
thread.start_new_thread(btReceive, ())
thread.start_new_thread(serialSend, ())
thread.start_new_thread(serialReceive, ())

while True:
    try:
        if !('')
        
        
        time.sleep(1)
        pass
    except KeyboardInterrupt:
        #kill everything