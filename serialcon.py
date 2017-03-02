import serial
import sys
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
                        print("[SER INFO] SER Listening")
			self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout = 2)
			if self.serial_conn:
				self.connected = True
			print("[SER INFO] Established connection to serial port")
		except Exception, e:
			print("[SER ERROR] Unable to establish connection. %s"  % e)
                        self.connected = False
                        return self.close()

	def is_connected(self):
		return self.connected

	def close(self):
		if self.serial_conn:
			self.serial_conn.close()
			self.connected = False
			print("[SER INFO] Connection to serial port closed.")
                return 2

	def receive(self):
		try:
			data = self.serial_conn.readline()
                        print("[SER INFO] SER Recv %s " % str(data) )
			return data
		except Exception, e:
			print("[SER ERROR] Error receiving from arduino.")
                        self.connected = False
                        return self.close()

	def send(self, payload):
		try:
			#might need to convert string to bytes
			payload = payload.encode('utf-8')
			self.serial_conn.write(payload)
                        print("[SER INFO] Sent %s " % str(payload))
		except Exception, e:
			print("[SER ERROR] Error sending payload to Arduino.")
			print(e)
                        self.connected = False
                        return self.close()

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
                

		

	
