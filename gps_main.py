from machine import Pin
from machine import UART
import time

gpsModule = UART(2, baudrate=9600, rx=16, tx=17)
GPSData = {}

def getGPS(gpsModule):
    global GPSData
    GPSData = {}
    timeout = time.time() + 8 
    while True:
        gpsModule.readline()
        buff = str(gpsModule.readline())
        print(buff)
        parts = buff.split(',')
        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7] and parts[9] and parts[10]):
                GPSData = {}
                GPSData["Latitude"] = convertToDegree(parts[2]) + " " + parts[3]
                GPSData["Longitude"] = convertToDegree(parts[4]) + " " + parts[5]
                GPSData["Satellites"] = parts[7]
                GPSData["GPStime"] = parts[1][0:2] + ":" + parts[1][2:4] + ":" + parts[1][4:6]
                break              
        if (time.time() > timeout):
            break
        time.sleep_ms(500)

def convertToDegree(RawDegrees):
    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100) 
    nexttwodigits = RawAsFloat - float(firstdigits*100) 
    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted) 
    return str(Converted)

while True:
    getGPS(gpsModule)
    print(GPSData)
