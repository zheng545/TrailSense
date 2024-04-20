# LCD Display
from xglcd_font import XglcdFont
from Deloce18x24 import Deloce18x24
from ili9341 import Display, color565
# Sensors
import mpu6050
from bme680 import *
from vcnl4010 import *
# Network
import network
import urequests as requests
import json

import time
from math import radians, cos, sin, atan2, degrees
from machine import Timer, Pin, SoftI2C, UART, SPI, ADC

# Read from sensors
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
        time.sleep_ms(500)

def timer_interruption_handler(timer):
    global i2c_input_sensor
    if(i2c_input_sensor == 0):
        getMPU6050Data()
    elif(i2c_input_sensor == 1):
        getBME680Data()
    else:
        getVCNL4010Data()
    i2c_input_sensor = (i2c_input_sensor + 1) % 3
    
# Display data
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

# Button press handlers
def left_button_interrupt_handler(pin):
    global output_sensor
    global last_left_press_time
    selectedData = {}
    left_press_time = time.ticks_ms()
    if(time.ticks_diff(left_press_time, last_left_press_time) > debounce_time):
        last_left_press_time = left_press_time
        output_sensor = (output_sensor + 5) % 6
        if(output_sensor == 0):
            selectedData["Selected"] = "Gyro"
        elif(output_sensor == 1):
            selectedData["Selected"] = "Environment"
        elif(output_sensor == 2):
            selectedData["Selected"] = "Brightness"
        elif(output_sensor == 3):
            selectedData["Selected"] = "GPS"
        elif(output_sensor == 4):
            selectedData["Selected"] = "Pressure"
        else:
            selectedData["Selected"] = "Direction"
        show_data(display, selectedData)

def right_button_interrupt_handler(pin):
    global output_sensor
    global last_right_press_time
    selectedData = {}
    right_press_time = time.ticks_ms()
    if(time.ticks_diff(right_press_time, last_right_press_time) > debounce_time):
        last_right_press_time = right_press_time
        output_sensor = (output_sensor + 1) % 6
        if(output_sensor == 0):
            selectedData["Selected"] = "Gyro"
        elif(output_sensor == 1):
            selectedData["Selected"] = "Environment"
        elif(output_sensor == 2):
            selectedData["Selected"] = "Brightness"
        elif(output_sensor == 3):
            selectedData["Selected"] = "GPS"
        elif(output_sensor == 4):
            selectedData["Selected"] = "Pressure"
        else:
            selectedData["Selected"] = "Direction"
        show_data(display, selectedData)

def center_button_interrupt_handler(pin):
    global press_time
    if(center_button.value() == 0):
        press_time = time.ticks_ms()
    else:
        release_time = time.ticks_ms()
        if(time.ticks_diff(release_time, press_time) > 1000):
            print("SOS!!!")
        else:
            if(output_sensor == 0):
                displayData = MPUData
            elif(output_sensor == 1):
                displayData = BMEData
            elif(output_sensor == 2):
                displayData = VCNLData
            elif(output_sensor == 3):
                displayData = GPSData
            elif(output_sensor == 4):
                displayData = PressureData
            else:
                displayData = DirectionData
            show_data(display, displayData)

# Put data into one list
def changeformat():
    global CombinedData
    CombinedData = []
    CombinedData.append(MPUData)
    CombinedData.append(BMEData)
    CombinedData.append(VCNLData)
    CombinedData.append(GPSData)
    CombinedData.append(PressureData)
    CombinedData.append(DirectionData)

# GPS and location calculation
def calculate_initial_compass_bearing(pointA, pointB):
    lat1, lon1 = map(radians, pointA)
    lat2, lon2 = map(radians, pointB)
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    initial_bearing = atan2(x, y)
    return (degrees(initial_bearing) + 360) % 360

def find_closest_point(current_location):
    closest_point = None
    min_distance = float('inf')  # Use a proper distance calculation for actual use
    for point in planned_points:
        distance = calculate_initial_compass_bearing(current_location, point)  # This should be a distance calculation
        if distance < min_distance:
            min_distance = distance
            closest_point = point
    closest_long = round(closest_point[0], 2)
    closest_lat = round(closest_point[1], 2)
    closest_point = (closest_long, closest_lat)
    return closest_point

def get_geo_direction(deg):
    dir = "N/A"
    if(deg >= 22.5 and deg < 67.5):
        dir = "NE"
    elif(deg >= 67.5 and deg < 112.5):
        dir = "E"
    elif(deg >= 112.5 and deg < 157.5):
        dir = "SE"
    elif(deg >= 157.5 and deg < 202.5):
        dir = "S"
    elif(deg >= 202.5 and deg < 247.5):
        dir = "SW"
    elif(deg >= 247.5 and deg < 292.5):
        dir = "W"
    elif(deg >= 292.5 and deg < 337.5):
        dir = "NW"
    else:
        dir = "N"
    return dir

# Wifi connection
# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('Connected to Wi-Fi')

# Send data to Google Apps Script
def send_data(json_data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json_data, headers=headers)
        if response.status_code == 200:
            print('Data sent successfully')
        else:
            print('Failed to send data, response code:', response.status_code)
        print('Response content:', response.text)
        response.close()
    except Exception as e:
        print('Failed to send data:', str(e))

# Collect and send batch data
def collect_and_send_data():
    data_batch = [
        {
            "Timestamp": "2024-03-01T12:00:00Z",
            "PlannedLatitude": "51.508583",
            "PlannedLongitude": "-0.167461",
            "ActualLatitude": "51.508582",
            "ActualLongitude": "-0.167441",
            "Speed": "0.06",
            "Altitude": "31.66",
            "Humidity": "52.08",
            "Temperature": "23.47",
            "Pressure": "992.41",
            "Gas": "79.89"
        },
        {
            "Timestamp": "2024-03-01T12:05:00Z",
            "PlannedLatitude": "51.508583",
            "PlannedLongitude": "-0.167461",
            "ActualLatitude": "51.508582",
            "ActualLongitude": "-0.167441",
            "Speed": "0.06",
            "Altitude": "31.66",
            "Humidity": "53.00",
            "Temperature": "23.50",
            "Pressure": "993.00",
            "Gas": "80.00"
        }
    ]
    json_data = json.dumps(data_batch)
    send_data(json_data)
    
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
PressureData = {}
DirectionData = {}
CombinedData = []
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
# Pressure Sensor
pressure_sensor = ADC(Pin(27))
pressure_sensor.atten(ADC.ATTN_11DB)
# Display definition
spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(4))
# Distance calculation
planned_points = [
    (51.508583, -0.167461),  # Example point 1
    (51.509000, -0.167500)  # Example point 2
    # Add more points as necessary
]
current_location = (51.4680, 0.4551)
# Wifi info
# Wi-Fi credentials
ssid = 'Nola'
password = '12345678'
# Google Apps Script execution URL
url = 'https://script.google.com/macros/s/AKfycbw3KMFPTUyAL28x0v8iv6WxMvgNxNmeDodNajs5dTMATo9QzHdzfp2rpPKkoUQniXwR/exec'

while True:
    getGPS(gpsModule)
    PressureData["PressureData"] = pressure_sensor.read()
    closest_point = find_closest_point(current_location)
    bearing_to_destination = calculate_initial_compass_bearing(current_location, closest_point)
    geo_direction = get_geo_direction(bearing_to_destination)
    DirectionData["Destination"] = str(closest_point)
    DirectionData["Direction"] = geo_direction + " " + str(bearing_to_destination)
    #print(output_sensor)

#connect_wifi()
#collect_and_send_data()
