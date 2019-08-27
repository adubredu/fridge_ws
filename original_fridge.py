#Developed by Charles Frankel
import time
import RPi.GPIO as GPIO

###SETUP

##Pin Assignments
flickSensor = 38	#Button Sensor
flickLED = 40		#Indicator for flick motion
flickPIN = 36		#flick motor PWM
flickMOS = 32		#control of servo power MOSFET
swingLED = 12		#indicator for swing motion
swingPIN = 18
swingMOS = 16
outputPins = [flickLED,flickPIN,flickMOS,swingLED,swingPIN,swingMOS]	#list of output pins
#swingSensor = 16	#not used atm

##Setup Pins
GPIO.setmode(GPIO.BOARD)   # use the BOARD pin-numbering system
GPIO.setup(flickSensor,GPIO.IN)
GPIO.setup(outputPins,GPIO.OUT)
#Set MOSs Off
GPIO.output(flickMOS,GPIO.LOW)
GPIO.output(swingMOS,GPIO.LOW)

##PWM parameters
#Duty Cycle parameters
flickStart = 2.6
flickEnd = 5
swingStart = 6.1
swingShut = 6.3
swingEnd = 2.7
#Initialize PWM Pins
p = GPIO.PWM(flickPIN,50)	#flick PWM
p.start(flickStart)
q = GPIO.PWM(swingPIN,50)	#swing PWM
q.start(swingStart)

#Swing parameters (Adjust these for different swing motion, like speed/time)
swingDiff = swingStart - swingEnd
swingTimeOpen = 2.75 #time it takes to swing door
swingTimeClose = 1.4
swingSteps = 30


###MAIN CODE

##Functions
#Flick Motion
def flick():
	GPIO.output(flickLED,GPIO.HIGH)
	GPIO.output(flickMOS,GPIO.HIGH)	#turn on fServo
	time.sleep(0.5)
	p.ChangeDutyCycle(flickEnd)	#extend flick
	time.sleep(1)
	p.ChangeDutyCycle(flickStart)	#return f to 0
	time.sleep(0.5)
	print("Flick is returned")
	GPIO.output(flickLED,GPIO.LOW)	#turn off fLED
	GPIO.output(flickMOS,GPIO.LOW)	#turn off fServo

#Swing Motion
#Swing Open
def swingOpen():
	GPIO.output(swingLED,GPIO.HIGH)
	GPIO.output(swingMOS,GPIO.HIGH)	#turn on sServo
	time.sleep(0.5)
	for i in range (1,swingSteps):	#gradual swing open
		q.ChangeDutyCycle(swingStart - i*swingDiff/swingSteps)
		time.sleep(swingTimeOpen/swingSteps)
	time.sleep(1)
	GPIO.output(swingMOS,GPIO.LOW)	#turn off sServo
#Swing wait for close #SECOND INPUT#
def waitForClose():	#Currently, same input button
			#Close command (same button for now)
	while (GPIO.input(flickSensor)==0):
		time.sleep(0.05)

#Swing Close
def swingClose():
	GPIO.output(swingMOS,GPIO.HIGH)	#turn on sServo
	time.sleep(0.25)
	for i in range(1,swingSteps):	#gradual swing close
		q.ChangeDutyCycle(swingEnd + i*swingDiff/swingSteps)
		time.sleep(swingTimeClose/swingSteps)
	q.ChangeDutyCycle(swingShut)	#make sure it's shut?
	time.sleep(0.25)
	GPIO.output(swingLED,GPIO.LOW)	#turn off sLED
	GPIO.output(swingMOS,GPIO.LOW)	#turn off sServo

#Waiting for input print (NOT needed in final version)
waitPrintCnt = 1	#So 'Waiting...' print is slower that loop speed
waitPrintMod = 10	#Modulus for 'Waiting...' print

##Running Code
try:
	while(1):
		#Flick wait for open input (On button Press now) #FIRST INPUT#
		if(GPIO.input(flickSensor)):

			##FLICK
			print("Button is pressed.")
			flick()

			##SWING

			#Swing Open
			print("Starting swing")
			swingOpen()
			print("waiting for swing close input")
			time.sleep(0.25)

			#Wait for close input #SECOND INPUT#
			waitForClose()

			#Swing Close
			print("Swing Closing")
			swingClose()
			print("Swing is closed")
		else:
			GPIO.output(flickLED,GPIO.LOW)
			if(waitPrintCnt % waitPrintMod == 0):
				print("Waiting...")
				waitPrintCnt = waitPrintCnt % waitPrintMod
			waitPrintCnt = waitPrintCnt + 1

		time.sleep(0.05)           # sleep for 0.05 s

except KeyboardInterrupt:
	p.stop()
	q.stop()
	GPIO.cleanup()
