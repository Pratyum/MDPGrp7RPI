import socket
import sys

TCP_IP = "0.0.0.0" #change this
TCP_LISTEN_PORT = 13388
BUFFER_SIZE = 512

class ANDcon(object):
    def __init__(self):
        self.listen_addr = TCP_IP
        self.listen_port = TCP_LISTEN_PORT
        self.connected = False
        self.outbound_addr = None
        self.client_conn = None
        self.tcpip_sock = None

    def is_connected(self): #returns true if tcp listener is listening
        return self.connected

    def listen(self):
        """
        Start tcp communication server
        """
        try:
            self.tcpip_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpip_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcpip_sock.bind((self.listen_addr, self.listen_port))
            self.tcpip_sock.listen(1)
            print("[TCP INFO]: TCPIP Socket Listening.\n")
            #listening, accept incoming connections
            self.client_conn, self.outbound_addr = self.tcpip_sock.accept()
            print ("[TCP INFO]: connected to: %s" % str(self.client_conn))
            print ("[TCP INFO]: connected on: " , self.outbound_addr)
            if self.client_conn:
                self.connected = True
                self.send("ESTABED")
        except Exception, e:
            print ("[TCP ERROR]: Can't establish connection. %s" % str(e))
            self.connected = False
            return self.close()

    def close(self):
        if self.tcpip_sock: #listening
            self.tcpip_sock.close()
            print ("[TCP TCP INFO]: Stopping tcpip listener")
            self.connected = False
        if self.client_conn:
            self.client_conn.close()
            print ("[TCP INFO]: Closing client connection")
            self.connected = False
            return 2
        
    def receive(self):
        """
        Receive message from algo software
        """

        try:
            inst = self.client_conn.recv(BUFFER_SIZE)
            if inst:
                return inst
            else:
                raise AttributeError('Connection broke or empty recv payload.')
        except Exception, e:
            print ("[TCP ERROR]: %s " % str(e))
            print ("[TCP ERROR]: Error receiving data from algo software.")
            self.connected = False
            return self.close()

    def send(self, payload):
        """
        Send msg to algo software
        """
        try:
            self.client_conn.sendto(payload, self.outbound_addr)
            #print('[TCP INFO]sent')
        except Exception, e:
            print ("[TCP ERROR]: %s" % str(e))
            print ("[TCP ERROR]: Error sending.")
            self.connected = False
            return self.close()


if __name__=="__main__":
    tcpsk = ANDcon()
    tcpsk.listen()
    print("Listening on port: %s" % str(TCP_LISTEN_PORT))
    if tcpsk.is_connected():
        print( "Connected.")
        print("recving")
        while tcpsk.is_connected():
            payload = tcpsk.receive()
            if payload:
                print("feedback: "+ payload.rstrip())
                #tcpsk.send(payload)
            s = raw_input('->> ').rstrip()
            tcpsk.send(s)
    print("Closing connection")
    tcpsk.close()

