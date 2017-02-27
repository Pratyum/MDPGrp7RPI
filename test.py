#import _thread as thread#or just 'thread' for <python3
import threading
from threading import Thread as thread
import time
from random import randint 

from collections import deque
global counter 

class RPIThread(threading.Thread):
    def __init__(self, function):
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
    print("WIFI SEND UP")
    while True:
        time.sleep(2)
        if(len(wifiQueue) > 0):
            message = wifiQueue.popleft()
            mock_wifi_to_me.append(message)
#            print("%s: Message to Wifi: %s" %(time.ctime(), message))

def wifiReceive():
    print("WIFI RECEIVE UP")
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

v1 = RPIThread(function = wifiSend)
v1.start()
v2 = RPIThread(function = wifiReceive)
v2.start()
v3 = RPIThread(function = btSend)
#thread(name='wifiSend', target=wifiSend).start()
#thread(name='wifiReceive', target=wifiReceive).start()
#thread(name='btSend', target=btSend).start()
#thread(name='btReceive', target=btReceive).start() 
#thread(name='serialSend', target=serialSend).start()
#thread(name='serialReceive', target=serialReceive).start() 
#thread(name='mockWifi', target=mockWifi).start() 
#thread(name='mockSerial', target=mockSerial).start()
#thread(name='mockBt', target=mockBt).start()


threadName_list = ['wifiSend', 'wifiReceive', 'btSend', 'btReceive', 'serialSend', 'serialReceive', 'mockWifi', 'mockSerial', 'mockBt']
counter = 0
while counter < 100:
    try:
        #print("Loop " + str(counter) + ": " + str(threading.activeCount()))
        tempThreadNameList = []
        for tempThread in threading.enumerate(): 
            tempThreadNameList.append(tempThread.getName())

        differenceList = list(set(tempThreadNameList) - set(threadName_list))
        print("Loop :" + str(counter) + ", Difference: " + str(len(differenceList)))
        if (len(differenceList) > 0):
            print("Difference Thread is: " + str(differenceList))

        time.sleep(1)
        counter += 1
        pass
    
    except KeyboardInterrupt:
        v1.stop()
        v2.stop()
        print("killed all threads")
        sys.exit()
