import _thread as thread#or just 'thread' for <python3
import time
from random import randint 

from collections import deque

def serialReceive():
    while True:
        try:
            tempBuffer = mock_serialReceive.popleft()
            if(tempBuffer != ''):
                if(str(tempBuffer)[0] == 'e'):
                    wifiQueue.append(tempBuffer[1:])
                else:
                    print("| ERROR ERROR | Serial Receive: " + tempBuffer)
#                print("%s: Message from serial: %s" % (time.ctime(),tempBuffer[1:]))
                
            time.sleep(2)
        except IndexError:
            time.sleep(2)
            continue
        
def serialSend():
    while True:
        time.sleep(2)
        if(len(serialQueue) > 0):
            message = serialQueue.popleft()
            mock_serial_to_me.append(message)
#            print("%s: Message to serial: %s" % (time.ctime(), message))

def btSend():
    while True:
        time.sleep(2)
        if( len(btQueue) > 0):
            message = btQueue.popleft()
            mock_bt_to_me.append(message)
#            print("%s: Message to Bluetooth: %s" %(time.ctime(), message))

def btReceive():
    while True:
        try:
            tempBuffer = mock_btReceive.popleft()
            if(tempBuffer != ''):

                print()
                if (str(tempBuffer)[0] == 'c'):
                    #Send manual movement to robot
                    serialQueue.append(tempBuffer[1:])
                elif (str(tempBuffer)[0] == 'd'):
                    #Tell algo to start exploration/fastest path
                    wifiQueue.append(tempBuffer[1:])
                else:
                    print("| ERROR ERROR | BT RECEIVE: " + tempBuffer)
                                      
#                print("%s: Message from Bluetooth: %s" %(time.ctime(), tempBuffer[1:]))
                print()

            time.sleep(2)
        except IndexError:
            time.sleep(2)
            continue

def wifiSend():
    while True:
        time.sleep(2)
        if(len(wifiQueue) > 0):
            message = wifiQueue.popleft()
            mock_wifi_to_me.append(message)
#            print("%s: Message to Wifi: %s" %(time.ctime(), message))

def wifiReceive():
    while True:
        try:
            tempBuffer = mock_wifiReceive.popleft()
            if(tempBuffer != ''):
                if(str(tempBuffer)[0] == 'a'):
                    #send to robot
                    serialQueue.append(tempBuffer[1:])
                elif(str(tempBuffer)[0] == 'b'):
                    #send to android
                    btQueue.append(tempBuffer[1:])
                else:
                    print("|Error - WIFI RECEIVE: " + tempBuffer)

                #print("\n%s: Message From Wifi: %s\n" %(time.ctime(), tempBuffer[1:]))

            time.sleep(2)
        except IndexError:
            time.sleep(2)
            continue

def mockWifi():
    while True:
        number = randint(0,2)
        if(number == 0):
            #don't send
            pass
        elif(number == 1):
            mock_wifiReceive.append('aFROM_ALGO TO ARDUNIO')
        else:
            mock_wifiReceive.append('bFROM_ALGO TO ANDROID')

        if (len(mock_wifi_to_me) > 0):
            print("Algo receives: " + mock_wifi_to_me.popleft())
        time.sleep(5)
        

def mockSerial():
    while True:
        number = randint(0,1)
#        number = 0
        if(number == 0):
            #don't send
            pass
        if(number == 1):
            mock_serialReceive.append('eFROM_ARDUINO TO ALGO')
        
        if (len(mock_serial_to_me) > 0):
            print("Arduino Receives: " + mock_serial_to_me.popleft())
        time.sleep(5)

def mockBt():
    while True:
        number = randint(0,2)
#        number = 0
        if(number == 0):
            #don't send
            pass
        elif(number == 1):
            mock_btReceive.append('cFROM_ANDROID TO ARDUINO')
        else:
            mock_btReceive.append('dFROM_ANDROID TO ALGO')

        if (len(mock_bt_to_me) > 0):
            print("Android receives: " + mock_bt_to_me.popleft())
        time.sleep(5)

mock_wifiReceive = deque([])
mock_serialReceive = deque([])
mock_btReceive = deque([])

mock_wifi_to_me = deque([])
mock_serial_to_me = deque([])
mock_bt_to_me = deque([])

serialQueue = deque([])
btQueue = deque([])
wifiQueue = deque([])

thread.start_new_thread(wifiSend, ())
thread.start_new_thread(wifiReceive, ())
thread.start_new_thread(btSend, ())
thread.start_new_thread(btReceive, ())
thread.start_new_thread(serialSend, ())
thread.start_new_thread(serialReceive, ())
thread.start_new_thread(mockWifi, ())
thread.start_new_thread(mockSerial, ())
thread.start_new_thread(mockBt, ())

counter = 0
while counter < 100:
    
    time.sleep(1)
    pass
