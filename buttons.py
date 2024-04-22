from machine import Pin
import time

left_button = Pin(13, Pin.IN, Pin.PULL_UP)
center_button = Pin(12, Pin.IN, Pin.PULL_UP)
right_button = Pin(14, Pin.IN, Pin.PULL_UP)

num = 0

while True:
    left_first = left_button.value()
    right_first = right_button.value()
    center_first = center_button.value()
    time.sleep(0.01)
    left_second = left_button.value()
    right_second = right_button.value()
    center_second = center_button.value()
    if center_first and not center_second:
        press_time = time.ticks_ms()
    if not center_first and center_second:
        release_time = time.ticks_ms()
        if(time.ticks_diff(release_time, press_time) > 1000):
            num += 10
        else:
            num = 0
    if left_first and not left_second:
        num -= 1
    if right_first and not right_second:
        num += 1
    print(num)
