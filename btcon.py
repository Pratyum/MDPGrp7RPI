from bluetooth import *

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
			print ("[INFO]: Bluetooth listening on channel %d" % self.channel)
			self.client_sock, self.outbound_addr = self.server_sock.accept() 
			print "[INFO]: connected to: ", str(self.client_sock)
			print "[INFO]: connected on: ", self.outbound_addr
			if self.client_sock:
				self.connected = True
		except Exception, e:
			print "[ERROR]: Can't establish connection.", str(e)

	def close(self):
		if self.server_sock:
			self.server_sock.close()
			print("[INFO] Stopping BT listener.")
		if self.client_sock:
			self.client_sock.close()
			print("[INFO] Closing client connection")

	def receive(self):
		try:
			inst = self.client_sock.recv(BUFFER_SIZE)
			print "[INFO]: Received: ", inst
			return inst
		except BluetoothError, be:
			print "[ERROR]: Error receiving data from BLUETOOTH.", be
			self.listen()

	def send(self, payload):
		try:
			self.client_sock.send(payload)
		except BluetoothError, be:
			print("[ERROR] Error sending to BLUETOOTH.")
			print (be)
			self.listen()



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
                        
		        incoming = bt.receive()
		        print("RECV %s" % incoming)
        except KeyboardInterrupt:
	        btconn.close()
