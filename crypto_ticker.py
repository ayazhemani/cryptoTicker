import RPi.GPIO as GPIO
import time
from datetime import datetime
import requests, json
GPIO.setwarnings(False)

LATCH = 11 # CS
CLK = 12
dataBit = 7 # DIN

GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH, GPIO.OUT) # P0 
GPIO.setup(CLK, GPIO.OUT) # P1 
GPIO.setup(dataBit, GPIO.OUT) # P7

GPIO.output(LATCH, 0)
GPIO.output(CLK, 0)

def pulseCLK():
    GPIO.output(CLK, 1)
    # time.sleep(.001) 
    GPIO.output(CLK, 0)
    return

def pulseCS():
    GPIO.output(LATCH, 1)
    # time.sleep(.001)
    GPIO.output(LATCH, 0)
    return

def ssrOut(value):
    for  x in range(0,8):
        temp = value & 0x80
        GPIO.output(dataBit, int(temp == 0x80))
        pulseCLK()
        value = value << 0x01 # shift left       
    return 

def display(on):
    ssrOut(0x0C) 
    ssrOut(on); 
    pulseCS()

# initialize MAX7219 4 digits BCD
def initMAX7219():
    
    # set decode mode
    ssrOut(0x09) # address
    ssrOut(0xFF) # 4-bit BCD decode eight digits
    pulseCS();

    # set intensity
    ssrOut(0x0A) # address
    ssrOut(0x04) # 9/32s
    pulseCS()

    # set scan limit 0-7
    ssrOut(0x0B); # address
    ssrOut(0x07) # 8 digits
    pulseCS()

    display(1)

    for x in range(0,9):
        ssrOut(x)
        ssrOut(0x0f)
        pulseCS()
    return


def writeMAX7219(data, location):
    ssrOut(location)
    ssrOut(data)
    pulseCS()
    return

def writeTicker(value):
	initMAX7219()
	dollars = int(value)
	cents = int(value*100 - dollars*100)
	for k in range(3, len(str(dollars))+3):
		digit = dollars % 10
		if k==3: digit+=128
		writeMAX7219(digit, k)
		dollars = dollars / 10 
	for k in range(1, 3):
		digit = cents % 10
		writeMAX7219(digit, k)
		cents = cents / 10 

def loopTicker():
	val=0
	while 1:
		r=requests.get('http://api.coindesk.com/v1/bpi/currentprice.json')
		if abs(float(val)-(r.json()['bpi']['USD']['rate_float']))>.1: print str(datetime.now()), (r.json()['bpi']['USD']['rate_float'])
		val='%.2f' % (r.json()['bpi']['USD']['rate_float'])
		writeTicker(float(val))
		time.sleep(1)

#initMAX7219()
loopTicker()

exit