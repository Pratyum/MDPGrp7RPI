import socket
import sys

TCP_IP = "0.0.0.0" #change this
TCP_LISTEN_PORT = 13377
BUFFER_SIZE = 512

class Tcpcon(object):
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
			self.tcpip_sock.bind((self.listen_addr, self.listen_port))
			self.tcpip_sock.listen(1)
			print("[INFO]: TCPIP Socket Listening.\n")
			#listening, accept incoming connections
			self.client_conn, self.outbound_addr = self.tcpip_sock.accept()
			print "[INFO]: connected to: ", str(self.client_conn)
			print "[INFO]: connected on: ", self.outbound_addr
			if self.client_conn:
				self.connected = True
		except Exception, e:
			print "[ERROR]: Can't establish connection.", str(e)
                        self.close()
                        sys.exit()

	def close(self):
		if self.tcpip_sock: #listening
			self.tcpip_sock.close()
			print "[INFO]: Stopping tcpip listener"
                        self.connected = False
		if self.client_conn:
			self.client_conn.close()
			print "[INFO]: Closing client connection"
                        self.connected = False

	def receive(self):
		"""
		Receive message from algo software
		"""

		try:
			inst = self.client_conn.recv(BUFFER_SIZE)
			return inst
		except Exception, e:
			print "[ERROR]: ", str(e)
			print "[ERROR]: Error receiving data from algo software."
                        self.close()
                        sys.exit()

	def send(self, payload):
		"""
		Send msg to algo software
		"""
		try:
			self.client_conn.sendto(payload, self.outbound_addr)
                        print('sent')
		except Exception, e:
			print "[ERROR]: ", str(e)
			print "[ERROR]: Error sending."
                        self.close()
                        sys.exit()


if __name__=="__main__":
	tcpsk = Tcpcon()
	tcpsk.listen()
	if tcpsk.is_connected():
                print "Connected."
	        print "recving"
                while tcpsk.is_connected():
                        payload = tcpsk.receive()
	                if payload:
	            	        print payload.rstrip()
                                tcpsk.send("feedback: " + payload)
                        s = raw_input('->> ')
                        tcpsk.send("from server: "+s)
        print("Closing connection")
        tcpsk.close()

