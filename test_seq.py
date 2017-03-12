import threading
import time
import sys

from btcon import *
from serialcon import *
from tcpcon import *
from collections import deque

globalcheckdelay = 5
wifi_delay = 0.01
btread_delay = 120
btsend_delay = 1
serial_delay = 0.01

wifiCon = None
btCon = None
serialCon = None
conCheck = None

class globalCheck():
    def __init__(self):
        self.bt = False
        self.wifi = False
        self.serial = False #Not used for now 
        


def wifiReceive():
    #Incoming Data from Algo
        
    if wifiCon:
        if wifiCon.is_connected():
            tempBuffer = wifiCon.receive()
            if tempBuffer == 2:
                return
            if(str(tempBuffer)[0] == 'a'):
                #send to robot
                serialQueue.append(tempBuffer[1:])
            elif(str(tempBuffer)[0] == 'b'):
                #send to android
                btQueue.append(tempBuffer[1:])
            else:
                try:
                    return
                except Exception:
                    pass              
        
def wifiSend():
    #Outgoing Data to Algo    
    try:
        wifiCon.send('')
        temp = wifiCon.send('')
        if temp == 2:
            return
    except Exception, e:
        print("wifiSend() Exception: " + str(e))
        return
    
    if (wifiCon):
        if wifiCon.is_connected():
            if( len(wifiQueue) > 0 ):
                message = wifiQueue.popleft()
                temp = wifiCon.send(message)
    else:
        return
 
def btSend():
    #Outgoing Data to Android

    if (btCon):
        if btCon.is_connected():
            if( len(btQueue) > 0 ):
                message = btQueue.popleft()
                temp = btCon.send(message)
                if temp == 2: 
                    return
    else:
        return
        
def btReceive():
    #Incoming Data from Android 
  
    if (btCon):
        if btCon.is_connected():
            tempBuffer = btCon.receive()
            
            if(tempBuffer != ''):
                if tempBuffer == 2:
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
                        return
                    except Exception:
                        return        
#                print("%s - btReceive(): Message from Bluetooth: %s" %(time.ctime(), tempBuffer))
    else:
        #serialConnection down, sleep and wait for something to happen
        return
#    time.sleep(120)
        


def serialTransmit():
    #Outgoing Data to Arduino
    
    if serialCon is not None:
        if (serialCon.is_connected()):
            if (len(serialQueue) > 0):
                message = serialQueue.popleft()
                serialCon.send(message)
                ###
                #Incoming data from Arduino
            tempBuffer = serialCon.receive()
            print('tempBuffer from Serial: ' + str(tempBuffer))
            if (tempBuffer is not '' or tempBuffer is not None or len(tempBuffer) != 0):
                wifiQueue.append(tempBuffer)                  
        else:
            #serialConnection down, sleep and wait for something to happen
            return   
        
###START###       Set Connections Methods         ###START###
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
        print("setBTCon(): Bluetooth Connection Up!")
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
###END###       Set Connections Methods         ###END###

       

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])
    
    #Listeners up    
    setSerialCon()
    setBTCon()
    setWifiCon()
    print("Listeners up. All connected.")

    
    while True:
        if serialCon:
            if serialCon.is_connected():
                serialTransmit()
            else:
                sys.exit()
            
        if wifiCon:
            if wifiCon.is_connected():
                wifiSend()
                wifiReceive()
            else:
                sys.exit()
            
        if btCon:
            if btCon.is_connected():
                btSend()
                btReceive()
            else:
                sys.exit()
    time.sleep(.5)

    

except KeyboardInterrupt:    
    btCon.close()
    wifiCon.close()
    serialCon.close()
    print("Threads killed")

