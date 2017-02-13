
import _thread #or just 'thread' for <python3
import time
import serial #sudo pip/pip3 install pyserial

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

#establish serial connection
serialCon = Seriouscon()
serialCon.listen()

#establish bluetooth connection
bToothCon = BTcon()
bToothCon.listen()

#establish wifi connection
wifiCon = Tcpcon()
wificon.listen()

print("Connections running")

def serialReceive():
    while True:
        tempBuffer = serialCon.receive()
        if (tempBuffer != ''):
            btQueue.append(tempBuffer)
            wifiQueue.append(tempBuffer)
            print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))
        time.sleep(0.5)

def serialSend():
    while True:
        time.sleep(0.5)
        if (len(serialQueue) > 0):
            message = serialQueue.popleft()
            serialCon.send(message)
            print("%s: Message to serial: %s" % (time.ctime(), message))

def btSend():
    while True:
        time.sleep(0.5)
        if( len(btQueue) > 0 ):
            message = btQueue.popleft()
            bToothCon.send(message)
            print("%s: Message to Bluetooth: %s" %(time.ctime(), message))

def btReceive():
    while True:
        tempBuffer = bToothCon.receive()
        if(tempBuffer != ''):
            serialQueue.append(tempBuffer)
            wifiQueue.append(tempBuffer)
            print("%s: Message from Bluetooth: %s" %s (time.ctime(), message))
        time.sleep(0.5)

def wifiSend():
    while True:
        time.sleep(0.5)
        if(len(wifiQueue) > 0):
            message = wifiQueue.popleft()
            wifiCon.send(message)
            print("%s: Message to Wifi: %s" %(time.ctime(), message))

def wifiReceive():
    while True:
        tempBuffer = wifiCon.receive()
        if(tempBuffer != ''):
            btQueue.append(tempBuffer)
            serialQueue.append(tempBuffer)
            print("%s: Message From Wifi: %s" %(time.ctime(), message))
        time.sleep(0.5)


serialQueue = deque([])
bToothQueue = deque([])
wifiQueue = deque([])

thread.start_new_thread(wifiSend, ())
thread.start_new_thread(wifiReceive, ())
thread.start_new_thread(btSend, ())
thread.start_new_thread(btReceive, ())
thread.start_new_thread(serialSend, ())
thread.start_new_thread(serialRecieve, ())

while True:
    time.sleep(1)
    pass