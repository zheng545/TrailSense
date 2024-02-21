from time import sleep, ticks_ms
from ili9341 import Display, color565
from machine import Pin, SPI, Timer
from xglcd_font import XglcdFont
from Deloce18x24 import Deloce18x24

display_mode = 'arrow'
press_count = 0
last_press_time = 0
debounce_time = 50

def draw_arrow(display, degrees):
    display.clear()
    for degree in degrees:
        if display_mode != 'arrow':
            return #Exit if button is pressed
        display.draw_arrow(120, 160, 100, color565(255, 0, 255), degree)
        sleep(2)  # Fetch data every 2 seconds
        display.clear()

def show_data(display, data):
    display.clear()
    espresso_dolce = XglcdFont(Deloce18x24, 18, 24)
    for data1 in data:
        if display_mode != 'data':
            return
        display.draw_text(2, 66, f'Sensor Data: {data1}', espresso_dolce, color565(0, 255, 255))
        sleep(2)  # Fetch data every 2 seconds
        display.clear()    
    
def button_press_handler(display, pin):
    global display_mode, press_count, last_press_time
    current_time = ticks_ms()
    if current_time - last_press_time > debounce_time:
        if current_time - last_press_time < 2000:
            press_count += 1
            if press_count >= 3:
                display.cleanup()
                while True:
                    sleep(1)
                return
        else:
            press_count = 1
            display_mode = 'data' if display_mode == 'arrow' else 'arrow'
    last_press_time = current_time

    
def LCD():
    global display_mode
    spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23))
    display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(4))
    degrees = [0, 30, 40, 70, 160, 90, 180, 270] # Data from the sensor
    sensor_data = [0.1, 2, 3] # Data from the sensor

    button = Pin(14, Pin.IN, Pin.PULL_UP)  # Use Pin.PULL_DOWN for external pull-down
    button.irq(trigger=Pin.IRQ_FALLING, handler=lambda pin: button_press_handler(display, pin))

    while True:
        if display_mode == 'data':
            show_data(display, sensor_data)
        else:
            draw_arrow(display, degrees)

LCD()
