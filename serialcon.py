import serial

#ref http://playground.arduino.cc/interfacing/python

BAUD_RATE = 9600
ARDUINO_DEV = '/dev/ttyACM0' #/dev/something

class Seriouscon(object):
	def __init__(self):
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
			print("[ERROR] Unable to establish connection. %s"  % e)
                        self.listen()

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
                        self.close()
                        self.listen()

	def send(self, payload):
		try:
			#might need to convert string to bytes
			payload = payload.encode('utf-8')
			self.serial_conn.write(payload)

		except Exception, e:
			print("[ERROR] Error sending payload to Arduino.")
			print(e)
                        self.close()
                        self.listen()

#for testing
if __name__ == "__main__":
        import time
	sercon = Seriouscon()
        try:
                sercon.listen()
                time.sleep(3)
	        if sercon.is_connected():
		        data = "ABC\n"
		        print("sending to serial")
		        sercon.send(data)
                        lol = 0
		        while lol < 10:                        
			        recv = sercon.receive()
			        print("Received %s" % recv)
                                sercon.send(str(lol))
                                lol += 1
                        sercon.close()
        except (KeyboardInterrupt, SystemExit):
                sercon.close()
                

		

	
