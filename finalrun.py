import threading
import time
import sys

from andcon import *
from serialcon import *
from tcpcon import * 
from collections import deque

serialCon = None
algoCon = None
andCon = None
andThread_thread = None 
algoRead_thread = None
algoSend_thread = None 


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
            test = self.function()
            
    def stop(self):
        self.running = False   
        
def algoRead():
    try:
        tempBuffer = algoCon.receive() 
        if (str(tempBuffer)[0] == 'a'):
            #send to robot
            serialQueue.append(tempBuffer[1:])
            #print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer)) 

        elif (str(tempBuffer)[0] == 'b'):
            checkIndex = tempBuffer.find('|')
            if tempBuffer[checkIndex+1] == 'a':
                andQueue.append(tempBuffer[1:checkIndex+1])
                serialQueue.append(tempBuffer[checkIndex+2:])
		#print("################################################")
        #        print("############### Detected and Split! ############")
		#print("################################################")
		#print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer))       
	    else:
	        andQueue.append(tempBuffer[1:])
		#print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer))
        
        elif (tempBuffer == 2):
            raise AttributeError("HI")
        else:
            print("|algoSend Error| : Message format error")

    except IndexError:
	andQueue.append(tempBuffer[1:])
	#print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer))
	
    except Exception:
#	print(e)
        print("algoRead Error")
        
        global algoCon
        global algoRead_thread
        global algoSend_thread
        
        algoRead_thread.stop()
        algoSend_thread.stop()
        algoCon = None
        
        algoConCon()
        
        time.sleep(1)
        pass
        
def algoSend():
    try:
        algoCon.send('')
        algoCon.send('')
        
        if len(algoQueue) > 0:
            message = algoQueue.popleft()
            algoCon.send(message)
            #print("%s: Message to Algo: %s" %(time.ctime(), message))
            
    except Exception:
        print("algoSend Error")        
        time.sleep(1)
        pass
        
def serialSend():
    while True:
        try:
            #outgoing data to robot
            if (len(serialQueue) > 0):
                message = serialQueue.popleft()
                serialCon.send(message)
                print("%s: Message to serial: %s" % (time.ctime(), message))

        except Exception:
            print("serialSend Error")
            time.sleep(1)
            pass
    
def serialReceive(): 
    while True:
        try:
            tempBuffer = serialCon.receive()
            if tempBuffer == 2:
                sys.exit("NO SERIAL CONNECTION")
                    
            elif tempBuffer != '':
                algoQueue.append(tempBuffer)
                #print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))

        except Exception:
            print("serialReceive Error")
            time.sleep(1)
            pass

def andThread():
    try:
        tempBuffer = andCon.receive()
        if (tempBuffer != ''):
            if (str(tempBuffer)[0] == 'c'):
                #send to robot
                serialQueue.append(tempBuffer[1:])
                #print("%s: Message From Android: %s" %(time.ctime(), tempBuffer)) 

            elif (str(tempBuffer)[0] == 'd'):
                algoQueue.append(tempBuffer[1:])
                time.sleep(1)
                #print("%s: Message From Android: %s" %(time.ctime(), tempBuffer))

            elif (tempBuffer == 2):
                raise AttributeError("HI")

            else:
                print("|andSend Error| : Message format error")
        
        andCon.send('')
        andCon.send('')
        
        if len(andQueue) > 0:
            message = andQueue.popleft()
            andCon.send(message + "\n")
            #print("%s: Message to Android: %s" %(time.ctime(), message))

        time.sleep(0.8)
        
    except Exception:
        print("andRead Error")
        global andThread_thread
        global andCon
        
        andThread_thread.stop()
        andCon = None 
        
        andConCon()
        
        time.sleep(1)
        pass
    
def serialConCon():
    global serialCon
    serialCon = Seriouscon()
    serialCon.listen()
    time.sleep(3)
    print("Serial Connection Up")
    
    serialSend_thread = threading.Thread(target=serialSend)
    serialSend_thread.daemon = True
    serialSend_thread.start()

    serialReceive_thread = threading.Thread(target=serialReceive)
    serialReceive_thread.daemon = True
    serialReceive_thread.start()

def andConCon():
    global andCon
    global andRead_thread
    global andSend_thread
    
    print("Waiting for Android Connection...")
    andCon = ANDcon()
    andCon.listen()
    print("Android Connection Up\n\n")
    
    andThread_thread = RPIThread(function=andThread)
    andThread_thread.daemon = True
    andThread_thread.start()
    
def algoConCon():
    global algoCon
    global algoRead_thread
    global algoSend_thread
    
    print("Waiting for Algo Connection...")
    algoCon = Tcpcon()
    algoCon.listen()
    print("Algo Connection Up\n\n")

    algoSend_thread = RPIThread(function=algoSend)
    algoSend_thread.daemon = True
    algoSend_thread.start()

    algoRead_thread = RPIThread(function=algoRead)
    algoRead_thread.daemon = True
    algoRead_thread.start()
    
try:
    serialQueue = deque([])
    andQueue = deque([])
    algoQueue = deque([])
    
    serialConCon()
    andConCon()
    algoConCon()

    while True:
        time.sleep(8888) 
        pass
    
except KeyboardInterrupt:
    print("Threads Killed")
