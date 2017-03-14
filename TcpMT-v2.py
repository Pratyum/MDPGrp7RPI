import threading
import time

from andcon import *
from serialcon import *
from tcpcon import * 
from collections import deque


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
            print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer)) 

        elif (str(tempBuffer)[0] == 'b'):
            andQueue.append(tempBuffer[1:])
            print("%s: Message From Algo: %s" %(time.ctime(), tempBuffer))       
        else:
            print("|algoSend Error| : Message format error")

    except Exception:
        print("algoRead Error")
        
        algoRead_thread.stop()
        algoSend_thread.stop()
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
            print("%s - algoSend(): Message to Algo: %s" %(time.ctime(), message))
            
    except Exception:
        print("algoSend Error")
        
        algoRead_thread.stop()
        algoSend_thread.stop()
        algoConCon()
        
        time.sleep(1)
        pass
        
def serialSend():
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
    try:
        tempBuffer = serialCon.receive()
        if (tempBuffer is not '' or tempBuffer is not None or len(tempBuffer) != 0):
            algoQueue.append(tempBuffer)
            print("%s: Message from serial: %s" % (time.ctime(),tempBuffer))

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
            print("%s: Message From Android: %s" %(time.ctime(), tempBuffer)) 

        elif (str(tempBuffer)[0] == 'd'):
            algoQueue.append(tempBuffer[1:])
            print("%s: Message From Android: %s" %(time.ctime(), tempBuffer))       
        else:
            print("|andSend Error| : Message format error")

    except Exception:
        print("andRead Error")
        
        andRead_thread.stop()
        andSend_thread.stop()
        andConCon()
        
        time.sleep(1)
        pass
        
def andSend():
    try:
        andCon.send('')
        andCon.send('')
        
        if len(andQueue) > 0:
            message = andQueue.popleft()
            andCon.send(message)
            print("%s - andSend(): Message to Android: %s" %(time.ctime(), message))

        time.sleep(1)

    except Exception:
        print("andSend Error")
        
        andRead_thread.stop()
        andSend_thread.stop()
        andConCon()
        
        time.sleep(1)
        pass

def serialConCon():
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
    andCon = ANDcon()
    andCon.listen()
    print("Android Connection Up")
    
    andRead_thread = RPIThread(function=andRead)
    andRead_thread.daemon = True
    andRead_thread.start()

    andSend_thread = RPIThread(function=andSend)
    andSend_thread.daemon = True
    andSend_thread.start()
    
def algoConCon():
    algoCon = Tcpcon()
    algoCon.listen()
    print("Algo Connection Up")

    algoSend_thread = RPIThread(function=algoSend)
    algoSend_thread.daemon = True
    algoSend_thread.start()

    algoRead_thread = RPIThread(function=algoRead)
    algoRead_thread.daemon = True
    algoRead_thread.start()
    
try:
    serialConCon()
    andConCon()
    algoConCon()
    
    serialQueue = deque([])
    andQueue = deque([])
    algoQueue = deque([])

    while True:
        time.sleep(100)
        pass
    
except KeyboardInterrupt:
    print("Threads Killed")