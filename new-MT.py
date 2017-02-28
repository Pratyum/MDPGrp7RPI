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
                if tempBuffer == 2:
                    return 2
                
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
                temp = serialCon.send(message)
                if temp == 2:
                    return 2
                
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
                temp = btCon.send(message)
                if temp == 2: 
                    return 2
                
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
                if tempBuffer == 2:
                    return 2
                
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

    #Additional Code for reference tomorrow
    '''
    
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

connectionCheck = False

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
        
def serialConnections():
    if (connectionCheck is False):
        #Assume serial connection is always up
        #If all connections not up, sleep and continue
        time.sleep(5)
        continue       
        
    else:
        tempBuffer = serialCon.receive()
        if (tempBuffer != ''):    
            wifiQueue.append(tempBuffer[1:])                
            print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))
    
        if (len(serialQueue) > 0):
                message = serialQueue.popleft()
                temp = serialCon.send(message)
                print("%s: Message to serial: %s" % (time.ctime(), message))
    
    time.sleep(.5)

def btConnections():
    if(btCon.is_connected() is False):
        #
    
    if():
        #check connection up, else
        pass
    else:        
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
        
        if( len(btQueue) > 0 ):
            message = btQueue.popleft()
            temp = btCon.send(message)
            print("%s: Message to Bluetooth: %s" %(time.ctime(), message))
    
    time.sleep(.5)
    
def wifiConnections():
    if():
        pass
    else:
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
    
            if(len(wifiQueue) > 0):
                message = wifiQueue.popleft()
                wifiCon.send(message)
                print("%s: Message to Wifi: %s" %(time.ctime(), message))
                
    time.sleep(.5)
                
                
                
                
from bt import *
from sr import *
from pc import *
import time
import threading
import sys
import collections

#The following headers are used in the transfer of data. 'p' is used to signify pc/algorithm. 'h' is to signify the arduino/robot. 'a' is to signify the android tablet
#All messages will only read after the header which is set to reading from position 1 of the string, since position 0 will be the header. 

#tLock = threading.RLock()
#jobs = Queue.queue()

class Main(threading.Thread):

        def __init__(self):
            
            threading.Thread.__init__(self)

            self.sr_thread = SerialAPI()
            self.bt_thread = AndroidAPI()
            self.pc_thread = PCAPI()
		
            # Initialize the threads and their respective connections to the various devices
              
            self.sr_thread.connect_to_serial()
            self.bt_thread.connect_to_android()
            self.pc_thread.start_pc_comm()
            time.sleep(3)


        #Returns the position of the "|" terminator
        def findTerm(self,s):
            
            return [i for i, ltr in enumerate(s) if ltr == '|']

        #Functions handling all communication to and from the algorithm
        
        def writePC(self, msg_to_pc):
            
            if self.pc_thread.pc_connected() and msg_to_pc:
                
                self.pc_thread.write_to_PC(msg_to_pc)
                #print "Sent to algorithm: %s" % msg_to_pc
                return True
                    
            return False
        
        def writeAndroidtoPC(self, msg_to_pc):
            
            if self.pc_thread.pc_connected() and msg_to_pc:
                #tLock.acquire()
                output_msg = msg_to_pc + "\n"     #add a \n to send message to pc as algorithmn is using bufferedreader and needs a \n character to know when to stop reading, without the \n, all data will be stuck inside the socket
                
                self.pc_thread.write_to_PC(output_msg)
                
                #print "Sent to algorithm: %s" % msg_to_pc
                
                return True
				#tLock.release()
            
            return False

            #+2 added to termIndex to account for the \n when writing to bufferedreader to the PC to signify end of line.

        def readPC(self):
                
            while True:
                    
                read_PC_msg = self.pc_thread.read_from_PC()

                if self.pc_thread.pc_connected() and read_PC_msg:
                        
                    term  = self.findTerm(read_PC_msg)    #find the "|" terminators to signify end of message
                    start = 0

                    for termIndex in term:
                            
                        # Handling PC to Android communication                             
                        if(read_PC_msg[start].lower() == 'a'):              

                        #print "\nMessage from Algo to Android: %s" % read_PC_msg [start +1 : termIndex+2]
                         pc_msgSent = self.writeBT(read_PC_msg [start +1 : termIndex+2] )

                        #Handling PC to Arduino communication
                        
                        elif(read_PC_msg[start].lower() == 'h'):
                                
                           #print "\nMessage from Algo to Arduino: %s" % read_PC_msg [start +1 : termIndex+2 ] 
                            pc_msgSent = self.writeSR( read_PC_msg [start +1 : termIndex+2 ] )                                 
                                    
                        else:
                            print "Wrong header [%s] from PC: %s" %(read_PC_msg[start] ,read_PC_msg[start:barIndex+1])

                        start = termIndex + 2
                                        
            # Functions handling all communication to and from the arduino board
            
        def writeSR(self, msg_to_sr):
                
            if self.sr_thread.sr_connected() and msg_to_sr:
                    
                self.sr_thread.write_to_serial(msg_to_sr)
                #print "Sent to arduino: %s" % msg_to_sr
                return True
                
            return False

            
        def readSR(self):
               while True:                   
                    read_SR_msg = self.sr_thread.read_from_serial()

                    if self.sr_thread.sr_connected() and read_SR_msg:
                            
                        #Handling Arduino to PC communication
                        
                        if(read_SR_msg[0].lower() == 'p'):
                               
                            #print "\nMessage from arduino to algorithm: %s" % read_SR_msg[1:]
                            sr_msgSent = self.writePC(read_SR_msg[1:])   

                                    
                        #Handling Arduino to Android communication  
                                    
                        elif(read_SR_msg[0].lower() == 'a'):
                                
                            #print "\nMessage from Arduino to Android : %s" % read_SR_msg[1:]
                            self.writeBT(read_SR_msg[1:])           

                        else:
                            
                            print "Wrong header from arduino"      
										
										

        # Functions handling all communication to and from the Android tablet
        
        def writeBT(self, msg_to_bt):
                
                if self.bt_thread.bt_is_connect() and msg_to_bt:
                        #tLock.acquire()
                        self.bt_thread.write_to_bt(msg_to_bt)
                        #print "Sent to android: %s" % msg_to_bt
                        return True
						#tLock.release()
                return False

        
        def readBT(self):
                
                while True:
                        read_BT_msg = self.bt_thread.read_from_bt()

                        if  self.bt_thread.bt_is_connect() and read_BT_msg :
                                
                                # Handling Android to PC communication   
                                if(read_BT_msg[0].lower() == 'p'):      

                                       # print "\nMessage from Android to Algorithm: %s\n" % read_BT_msg[1:]
                                        bt_msgSent = self.writeAndroidtoPC(read_BT_msg[1:])   


                                # Handling Android to Arduino communication       
                                elif(read_BT_msg[0].lower() == 'h'):

                                       # print "\nMessage from Android to Arduino: %s" % read_BT_msg[1:]
                                        bt_msgSent = self.writeSR(read_BT_msg[1:])
                                 
                                else:
                                    
                                        print "Wrong header from Android" 
                                        

                   

        def initialize_threads(self):

                # Two threads were created for each channel of communication, with read and write threads, making for a total of 6 threads. 
                wt_pc = threading.Thread(target = self.writePC, args = ('Startup',), name = "pc_write_thread")
                rt_pc = threading.Thread(target = self.readPC, name = "pc_read_thread")
                
                wt_bt = threading.Thread(target = self.writeBT, args = ('Startup',), name = "bt_write_thread")
                rt_bt = threading.Thread(target = self.readBT, name = "bt_read_thread")

                wt_sr = threading.Thread(target = self.writeSR, args = ('Startup',), name = "sr_write_thread")
                rt_sr = threading.Thread(target = self.readSR, name = "sr_read_thread")

                #All threads were set as daemons in order to automatically kill them off when the main program (multi_program) is killed.
                wt_pc.daemon = True
                rt_pc.daemon = True
                
                wt_bt.daemon = True
                rt_bt.daemon = True
				
                wt_sr.daemon = True
                rt_sr.daemon = True
        
                wt_pc.start()
                rt_pc.start()

                wt_bt.start()
                rt_bt.start()
				
                wt_sr.start()
                rt_sr.start()
				
                print "All threads up and running"


        def close_every_socket(self):
		
                sr_thread.close_every_sr_socket()
                pc_thread.close_every_pc_socket()
                bt_thread.close_every_bt_socket()
                print "Threads closing"


        def keep_main_alive(self):
                while True:
                        time.sleep(1)



if __name__ == "__main__":
        test = Main()
        test.initialize_threads()
        test.keep_main_alive()
        test.close_every_socket()
                
                
                
                
                
                

    
    
    
    
    '''
