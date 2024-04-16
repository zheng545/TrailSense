from machine import Timer
from machine import Pin
from machine import SoftI2C
from machine import UART
from machine import SPI
import mpu6050
from bme680 import *
from vcnl4010 import *
import time
from ili9341 import Display, color565
from xglcd_font import XglcdFont
from Deloce18x24 import Deloce18x24

def getMPU6050Data():
    global MPUData
    MPUData = mpu.get_values()
    del MPUData["Tmp"]
    MPUData["AcX"] = MPUData["AcX"] / 16384 * 9.81
    MPUData["AcY"] = MPUData["AcY"] / 16384 * 9.81
    MPUData["AcZ"] = MPUData["AcZ"] / 16384 * 9.81

def getBME680Data():
    global BMEData
    BMEData["temp"] = str(round(bme.temperature, 2)) + ' C'
    BMEData["Humidity"] = str(round(bme.humidity, 2)) + ' %'
    BMEData["Pressure"] = str(round(bme.pressure, 2)) + ' hPa'
    BMEData["gas"] = str(round(bme.gas/1000, 2)) + ' KOhms'

def getVCNL4010Data():
    global VCNLData
    VCNLData["Ambient"] = vcnl.readAmbientLux() * VCNL4010_AMBIENT_LUX_SCALE
    VCNLData["Proximity"] = vcnl.readProximity() * 256 / 65555

def timer_interruption_handler(timer):
    global i2c_input_sensor
    if(i2c_input_sensor == 0):
        getMPU6050Data()
    elif(i2c_input_sensor == 1):
        getBME680Data()
    else:
        getVCNL4010Data()
    i2c_input_sensor = (i2c_input_sensor + 1) % 3

def left_button_interrupt_handler(pin):
    global output_sensor
    global last_left_press_time
    left_press_time = time.ticks_ms()
    if(time.ticks_diff(left_press_time, last_left_press_time) > debounce_time):
        last_left_press_time = left_press_time
        output_sensor = (output_sensor + 3) % 4
        if(output_sensor == 0):
            print("Gyro and acceleration info:")
        elif(output_sensor == 1):
            print("Temp, humidity, pressure, and gas info:")
        elif(output_sensor == 2):
            print("Ambient and proximity info:")
        else:
            print("GPS info")

def right_button_interrupt_handler(pin):
    global output_sensor
    global last_right_press_time
    right_press_time = time.ticks_ms()
    if(time.ticks_diff(right_press_time, last_right_press_time) > debounce_time):
        last_right_press_time = right_press_time
        output_sensor = (output_sensor + 1) % 4
        if(output_sensor == 0):
            print("Gyro and acceleration info:")
        elif(output_sensor == 1):
            print("Temp, humidity, pressure, and gas info:")
        elif(output_sensor == 2):
            print("Ambient and proximity info:")
        else:
            print("GPS info")

def center_button_interrupt_handler(pin):
    global press_time
    if(center_button.value() == 0):
        press_time = time.ticks_ms()
    else:
        release_time = time.ticks_ms()
        if(time.ticks_diff(release_time, press_time) > 1000):
            Pin(27, Pin.OUT).value(not Pin(27, Pin.OUT).value())
            pass
        else:
            if(output_sensor == 0):
                print(MPUData)
            elif(output_sensor == 1):
                print(BMEData)
            elif(output_sensor == 2):
                print(VCNLData)
            else:
                print(GPSData)
                
def convertToDegree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)                

def getGPS(gpsModule):
    global GPSData
    timeout = time.time() + 8 
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        #print(buff)
        parts = buff.split(',')
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[7] and parts[9] and parts[10]):
                GPSData = {}
                GPSData["Latitude"] = convertToDegree(parts[2]) + " " + parts[3]
                GPSData["Longitude"] = convertToDegree(parts[4]) + " " + parts[5]
                GPSData["Altitude"] = convertToDegree(parts[9]) + " " + parts[10]
                GPSData["Satellites"] = parts[7]
                GPSData["GPStime"] = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                break              
        if (time.time() > timeout):
            break
        sleep_ms(500)
        
def show_data(display, data1):
    start_x = 0
    start_y = 320
    display.clear()
    espresso_dolce = XglcdFont(Deloce18x24, 18, 24)
    for key, value in data1.items():
        display.draw_text(start_x, start_y, f'{key}: {value}', espresso_dolce, color565(255, 255, 255), landscape=True)
        start_x += 40
        time.sleep(2)  # Fetch data every 2 seconds
    display.clear()

# Sensor selection
i2c_input_sensor = 0
output_sensor = 0
# Buttons
press_time = 0
debounce_time = 150
last_left_press_time = 0
last_right_press_time = 0
# Sensor data
MPUData = {}
BMEData = {}
VCNLData = {}
GPSData = {}
# Button definition
left_button = Pin(13, Pin.IN, Pin.PULL_UP)
right_button = Pin(14, Pin.IN, Pin.PULL_UP)
center_button = Pin(12, Pin.IN, Pin.PULL_UP)
# I2C Devices definition
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
mpu = mpu6050.accel(i2c)
bme = BME680_I2C(i2c=i2c)
vcnl = VCNL4010(i2c)
vcnl.startup()
# Timer and timer interrupt config
timer_0 = Timer(0)
timer_0.init(mode=Timer.PERIODIC, period=1000, callback=timer_interruption_handler)
# Button GPIO interrupt config
left_button.irq(trigger=Pin.IRQ_FALLING, handler=left_button_interrupt_handler)
right_button.irq(trigger=Pin.IRQ_FALLING, handler=right_button_interrupt_handler)
center_button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=center_button_interrupt_handler)
# GPS definition
gpsModule = UART(2, baudrate=9600, rx=16, tx=17)
# Display definition
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(4))

while True:
    #getGPS(gpsModule)
    #print("a")
    if(output_sensor == 0):
        displayData = MPUData
    elif(output_sensor == 1):
        displayData = BMEData
    elif(output_sensor == 2):
        displayData = VCNLData
    else:
        displayData = GPSData
    show_data(display, displayData)

