from machine import SoftI2C
from machine import Pin
from time import sleep
from bme680 import *

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
bme = BME680_I2C(i2c=i2c)

for i in range(10):
  try:
    temp = str(round(bme.temperature, 2)) + ' C'
    
    hum = str(round(bme.humidity, 2)) + ' %'
    
    pres = str(round(bme.pressure, 2)) + ' hPa'
    
    gas = str(round(bme.gas/1000, 2)) + ' KOhms'

    print('Temperature:', temp)
    print('Humidity:', hum)
    print('Pressure:', pres)
    print('Gas:', gas)
    print('-------')
  except OSError as e:
    print('Failed to read sensor.')
 
  sleep(5)