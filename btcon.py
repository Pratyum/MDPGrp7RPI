from bluetooth import *
import sys
#ref: https://people.csail.mit.edu/albert/bluez-intro/x232.html

BUFFER_SIZE = 512
CHAN = 1 #dont change this
class BTcon(object):
    def __init__(self):
        self.server_sock = None
        self.channel = CHAN
        self.connected = False
        self.client_sock = None
        self.outbound_addr = None

    def is_connected(self):
        return self.connected

    def listen(self):
        try:
            self.server_sock = BluetoothSocket( RFCOMM )
            self.server_sock.bind( ("",self.channel) )
            self.server_sock.listen(1)
            print ("[BT INFO]: Bluetooth listening on channel %d" % self.channel)
            self.client_sock, self.outbound_addr = self.server_sock.accept() 
            print ("[BT INFO]: connected to: ", str(self.client_sock))
            print ("[BT INFO]: connected on: ", self.outbound_addr)
            if self.client_sock:
                self.connected = True
                self.send("ESTABED")
        except Exception, e:
            print "[BT ERROR]: Can't establish connection.", str(e)
            #self.connected = False
            return self.close()

    def close(self):
        if self.server_sock:
            self.server_sock.close()
            print("[BT INFO] Stopping BT listener.")
            self.connected = False
        if self.client_sock:
            self.client_sock.close()
            print("[BT INFO] Closing client connection")
            self.connected = False
        return 2
        
    def receive(self):
        try:
            inst = self.client_sock.recv(BUFFER_SIZE)
            print "[BT INFO]: Received: ", inst
            return inst
        except BluetoothError, be:
            print "[BT ERROR]: Error receiving data from BLUETOOTH.", be
            #self.connected = False
            return self.close()

    def send(self, payload):
        try:
            self.client_sock.send(payload)
            print ("[BT INFO] Sent: %s"% payload)
        except BluetoothError, be:
            print("[BT ERROR] Error sending to BLUETOOTH.")
            print (be)
            #self.connected = False
            return self.close()



##sort of unit testing
if __name__ == "__main__":
    btconn = BTcon()
    btconn.listen()
    print("[INFO] BT listening.")
    try:
        if btconn.is_connected():
            msg = "much connection so estab"
            print("Writing %s" % msg)
            btconn.send(msg)        
            incoming = btconn.receive()
            print("RECV %s" % incoming)
    except KeyboardInterrupt:
        btconn.close()
