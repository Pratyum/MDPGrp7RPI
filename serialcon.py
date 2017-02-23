import serial

#ref http://playground.arduino.cc/interfacing/python

BAUD_RATE = 9600
ARDUINO_DEV = '' #/dev/something

class Seriouscon(object):
	def __ini__(self):
		self.serial_port = ARDUINO_DEV
		self.baud_rate = BAUD_RATE
		self.serial_conn = None
		self.connected = False

	def listen(self):
		"""
		Establish serial connection
		"""
		try:
			self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout = 2)
			if self.serial_conn:
				self.connected = True
			print("[INFO] Established connection to serial port")
		except Exception, e:
			print("[ERROR] Unable to establish connection. %s" %e)

	def is_connected(self):
		return self.connected

	def close(self):
		if self.serial_conn:
			self.serial_conn.close()
			self.connected = False
			print("[INFO] Connection to serial port closed.")

	def receive(self):
		try:
			data = self.serial_conn.readline()
			return data
		except Exception, e:
			print("[ERROR] Error receiving from arduino.")

	def send(self, payload):
		try:
			self.serial_conn.write(payload)
		except Exception, e:
			print("[ERROR] Error sending payload to Arduino.")
			print(e)

#for testing
if __name__ == "__main__":
	sercon = Seriouscon()
	sercon.listen()
	if sercon.is_connected():
#		data = "ABC"
		print("sending to serial")
#		sercon.send(data)
                lol = 0
		while lol < 10:
                        sercon.send(str(lol))
                        recv = sercon.receive()
			print("Received %s" % recv)
                        lol += 1
		sercon.close()
		exit()
		
	#arduino sends something
	#so recv it
	
