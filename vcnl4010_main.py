from machine import SoftI2C
from machine import Pin
from vcnl4010 import *
from time import sleep
  
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

vcnl = VCNL4010(i2c)
vcnl.startup()

for i in range(10):
  print("Ambient:", vcnl.readAmbientLux() * VCNL4010_AMBIENT_LUX_SCALE, "lux")
  print("Proximity:", vcnl.readProximity() * 256 / 65555)
  sleep(5)