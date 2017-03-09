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
        self.serial = False #Not used for now 
        
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
            
    def stop(self):
        self.running = False

def wifiReceive():
    #Incoming Data from Algo
    if (conCheck.wifi is False):
        print("wifiReceive(): Detected wifiCon down. ")
        print("wifiReceive(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    if (wifiCon is not None):
        if wifiCon.is_connected():
            
            tempBuffer = wifiCon.receive()
            if tempBuffer == 2:
                conCheck.wifi = False
                time.sleep(15)
                return
                    
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
    time.sleep(.5)        
        
def wifiSend():
    #Outgoing Data to Algo
    if (conCheck.wifi is False):
        print("wifiSend(): Detected wifiCon down. ")
        print("wifiSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
        
    try:
        wifiCon.send('')
        temp = wifiCon.send('')
        if temp == 2:
            conCheck.wifi = False
            time.sleep(15)
            return
    except Exception, e:
        print("wifiSend() Exception: " + str(e))
        conCheck.wifi = False
        time.sleep(15)
        return
    
    
    time.sleep(.5)
    if (wifiCon is not None):
        if wifiCon.is_connected():
            if( len(wifiQueue) > 0 ):
                message = wifiQueue.popleft()
                temp = wifiCon.send(message)

                print("%s - wifiSend(): Message to Algo: %s" %(time.ctime(), message))
    else:
        print("wifiSend(): Detected wifiCon down. ")
        print("wifiSend(): Sleep 15 Seconds and wait")
        time.sleep(15)
 
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
        
def serialReceive():
    #Incoming data from Arduino
    if serialCon is not None:
        if (serialCon.is_connected()):
            tempBuffer = serialCon.receive()
            
            wifiQueue.append(tempBuffer)                
            print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))
        else:
            #serialConnection down, sleep and wait for something to happen
            print("serialSend() detects serialCon down. ")
            time.sleep(10)

    time.sleep(0.5)

def serialSend():
    #Outgoing Data to Arduino
    time.sleep(0.5)
    if serialCon is not None:
        if (serialCon.is_connected()):
            if (len(serialQueue) > 0):
                message = serialQueue.popleft()
                serialCon.send(message)

                print("%s: Message to serial: %s" % (time.ctime(), message))
        else:
            #serialConnection down, sleep and wait for something to happen
            print("serialSend() detects serialCon down. ")
            time.sleep(10)        
        
        
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

conCheck = globalCheck()        

try:
    #Queues for messages     
    serialQueue = deque([])
    btQueue = deque([])
    wifiQueue = deque([])
        
    serial_conThread = RPIThread(function = setSerialCon, name = 'serial-conThread')
    serial_conThread.daemon = True
    serial_conThread.start()
    
    wifi_conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
    wifi_conThread.daemon = True
    wifi_conThread.start()

    bt_conThread = RPIThread(function = setBTCon, name = 'bt-conThread')
    bt_conThread.daemon = True
    bt_conThread.start()
    
    connectionThreadCounter = 0 #connection thread counter must be three to signify that all three connections are up 
    
    while(connectionThreadCounter != 3):
        if serial_conThread is not None:
            if serialCon.is_connected() and conCheck.serial is False:
                conCheck.serial = True
                
                serialSend_Thread = RPIThread(function = serialSend, name='serialSend-Thread')
                serialSend_Thread.daemon = True
                serialSend_Thread.start()
                print('serial send started')
                
                serialReceive_Thread = RPIThread(function = serialReceive, name='serialReceive-Thread')
                serialReceive_Thread.daemon = True
                serialReceive_Thread.start()
                print("serial receive started")
            
                connectionThreadCounter += 1
            
        if wifiCon is not None:
            if (wifiCon.is_connected() and conCheck.wifi is False):
                conCheck.wifi = True
                
                wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
                wifiSend_Thread.daemon = True
                wifiSend_Thread.start()
                print('Wifi Send Started')
                
                wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
                wifiReceive_Thread.daemon = True
                wifiReceive_Thread.start()
                print('Wifi receive started')
                
                connectionThreadCounter += 1
            
        if btCon is not None:
            if (btCon.is_connected() and conCheck.bt is False):
                conCheck.bt = True    
                
                btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
                btSend_Thread.daemon = True
                btSend_Thread.start()
                print("bt send Started")
                
                btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
                btReceive_Thread.daemon = True
                btReceive_Thread.start()
                print("bt receive Started")
                
                connectionThreadCounter += 1
            
    time.sleep(.5)
    print("Threadings for all components up! Thread Count: " + str(threading.activeCount()))
    totalCount = threading.activeCount()
    
    while True:
        if (conCheck.wifi is False):
            print("Wifi Connection Thread detected to be dead!")
            wifi_conThread.stop()
            wifiSend_Thread.stop()
            wifiReceive_Thread.stop()
            print("Wifi Threads Killed")
            time.sleep(3)
            
            wifiCon = None
            print("Resetting wifi connection...")
            wifi_conThread = RPIThread(function = setWifiCon, name = 'wifi-conThread')
            wifi_conThread.daemon = True
            wifi_conThread.start()
            
            while wifiCon is None:
                time.sleep(.1)
            while not wifiCon.is_connected():
                time.sleep(.1)
                
            print("Wifi Connctions Up")
            conCheck.wifi = True
            
            wifiSend_Thread = RPIThread(function = wifiSend, name='wifiSend-Thread')
            wifiSend_Thread.daemon = True
            wifiSend_Thread.start()
            print('Wifi Send Started')
            wifiReceive_Thread = RPIThread(function = wifiReceive, name='wifiReceive-Thread')
            wifiReceive_Thread.daemon = True
            wifiReceive_Thread.start()
            print('Wifi receive started')
            
            
        if(conCheck.bt is False):
            print("Bluetooth Connetion Thread detected to be dead!")
            bt_conThread.stop()
            btSend_Thread.stop()
            btReceive_Thread.stop()
            print("BT Threads killed")
            time.sleep(3)
            
            btCon = None
            print("Resetting bt connection...")
            bt_conThread = RPIThread(function = setBTCon, name = 'bt-conThread')
            bt_conThread.daemon = True
            bt_conThread.start()
            while(btCon is None):
                time.sleep(.1)
            while (not btCon.is_connected()):
                time.sleep(.1)
            
            print("Bluetooth Connections up")
            conCheck.bt = True
            
            btSend_Thread = RPIThread(function = btSend, name='btSend-Thread')
            btSend_Thread.daemon = True
            btSend_Thread.start()
            print("btSend up!")
            btReceive_Thread = RPIThread(function = btReceive, name='btReceive-Thread')
            btReceive_Thread.daemon = True
            btReceive_Thread.start()
            print("btReceive up!")
            
        time.sleep(3)
        continue

except KeyboardInterrupt:    
    btCon.close()
    wifiCon.close()
    serialCon.close()
    print("Threads killed")

