# # This file is executed on every boot (including wake-boot from deepsleep)
# #import esp
# #esp.osdebug(None)
# #import webrepl
# #webrepl.start()

import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'MicroPython-AP'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password, authmode=3)

while not ap.active():
    pass

print('Connection successful')
print(ap.ifconfig())

