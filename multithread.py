import thread #or just '_thread' for python3
import time
import serial #sudo pip/pip3 install pyserial

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

#establish serial connection
serialCon = Seriouscon()
serialCon.listen()
time.sleep(3)

#establish bluetooth connection
btCon = BTcon()
btCon.listen()

#establish wifi connection
wifiCon = Tcpcon()
wifiCon.listen()

print("Connections running")

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
                print("| ERROR ERROR | BT RECEIVE: " + tempBuffer)
                
            print("%s: Message from Bluetooth: %s" %(time.ctime(), tempBuffer))
        time.sleep(0.5)

def wifiSend():
    #Outgoing data to Algo
    while True:
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
                print("|Error - WIFI RECEIVE: " + tempBuffer)
                
            print("%s: Message From Wifi: %s" %(time.ctime(), tempBuffer))
        time.sleep(0.5)


serialQueue = deque([])
btQueue = deque([])
wifiQueue = deque([])

thread.start_new_thread(wifiSend, ())
thread.start_new_thread(wifiReceive, ())
thread.start_new_thread(btSend, ())
thread.start_new_thread(btReceive, ())
thread.start_new_thread(serialSend, ())
thread.start_new_thread(serialReceive, ())

while True:
    time.sleep(1)
    pass
