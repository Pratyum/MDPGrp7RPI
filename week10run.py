import threading
import time
import sys

from andcon import *
from serialcon import *
from tcpcon import * 
from godcon import *
from collections import deque

bool_check = False
serialCon = None
algoCon = None
andCon = None
godCon = None
andRead_thread = None
andSend_thread = None
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

        elif (str(tempBuffer)[0] == 'b'):
            checkIndex = tempBuffer.find('|')
            if tempBuffer[checkIndex+1] == 'a':
                andQueue.append(tempBuffer[1:checkIndex+1])
                serialQueue.append(tempBuffer[checkIndex+2:])
		
	    else:
	        andQueue.append(tempBuffer[1:])
        
        elif (tempBuffer == 2):
            raise AttributeError("HI")
        else:
            print("|algoSend Error| : Message format error")

    except IndexError:
	andQueue.append(tempBuffer[1:])
	
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

        except Exception:
            print("serialReceive Error")
            time.sleep(1)
            pass

    
def andRead():
    try:
        tempBuffer = andCon.receive() 
        if (str(tempBuffer)[0] == 'c'):
            #send to robot
            serialQueue.append(tempBuffer[1:])
            
        elif (str(tempBuffer)[0] == 'd'):
            algoQueue.append(tempBuffer[1:])
            
        elif (tempBuffer == 2):
            raise AttributeError("HI")
            
        else:
            print("|andSend Error| : Message format error")

    except Exception:
        print("andRead Error")
        global andRead_thread
        global andSend_thread
        global andCon
        
        andRead_thread.stop()
        andSend_thread.stop()
        andCon = None 
        
        andConCon()
        
        time.sleep(1)
        pass
        
def andSend():
    try:
        andCon.send('')
        andCon.send('')
        
        if len(andQueue) > 0:
            message = andQueue.popleft()
            andCon.send(message + "\n")

        time.sleep(0.5)

    except Exception:
        print("andSend Error")
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
    
    andRead_thread = RPIThread(function=andRead)
    andRead_thread.daemon = True
    andRead_thread.start()

    andSend_thread = RPIThread(function=andSend)
    andSend_thread.daemon = True
    andSend_thread.start()
    
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
    
def godConCon():
    global godCon
    
    godCon = Godcon()
    godCon.listen()
    
    
try:
    global godCon
    
    serialQueue = deque([])
    andQueue = deque([])
    algoQueue = deque([])
    
    serialConCon()
    andConCon()
    algoConCon()
    godConCon()

    print("All Connections Up!")
    print("Ready to go!")
    print("Boh Bi A+ 300/300 10 Seconds!")
    
    while True:
        try:
            tempBuffer = godCon.receive()
            serialQueue.append(tempBuffer)
            pass
        
        except Exception:
            time.sleep(2)
            
            godCon = None
            godConCon()
            
    
except KeyboardInterrupt:
    print("Threads Killed")
