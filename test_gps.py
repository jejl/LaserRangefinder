import serial
import time
import string
import pynmea2


while True:
	port="/dev/ttyS0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()
	if newdata[0:1] == b'$':
		msg = newdata.decode("utf-8")
		# print("msg {}".format(msg))
		newmsg = pynmea2.parse(msg)
		if newmsg.is_valid:
			print("$ newmsg {}".format(repr(newmsg)))
			print("\n")
	else:
		msg = newdata.decode("utf-8")
		print("  newmsg {}".format(newdata))
		# print("msg {}".format(msg))
		# newmsg = pynmea2.parse(msg)
		# print("  newmsg {}".format(repr(newmsg)))
# if newdata[0:6] == b'$GPRMC':
	# 	newmsg=pynmea2.parse(newdata.decode("utf-8"))
	# 	lat=newmsg.latitude
	# 	lng=newmsg.longitude
	# 	gps = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
	# 	print(gps)