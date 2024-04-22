from machine import SoftI2C
from machine import Pin
from machine import sleep
import mpu6050

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
mpu = mpu6050.accel(i2c)

for i in range(10):
    mpu_values = mpu.get_values()
    mpu_values["AcX"] = mpu_values["AcX"] / 16384 * 9.81
    mpu_values["AcY"] = mpu_values["AcY"] / 16384 * 9.81
    mpu_values["AcZ"] = mpu_values["AcZ"] / 16384 * 9.81
    print(mpu_values)
    sleep(500)
