import network
from ntptime import settime
import urequests
import json

# Your Wi-Fi credentials
ssid = 'Nola'
password = '12345678'

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

while not wlan.isconnected():
    pass  # Wait for connection

print('Connected to Wi-Fi')

# Synchronize time using NTP
try:
    settime()  # Synchronizes the internal RTC
    print('Time synchronized with NTP server')
except:
    print('Could not synchronize time')

# Function to send data to Google Apps Script
def send_data(json_data):
    url = 'https://script.google.com/macros/s/AKfycbzapa4q3s66MCgfsdVaorlAkihti3ikpFR0LnaUsfOXeE4hvdmJM8z88Yf0f4Iw11ky/exec'  # Replace with your URL
    headers = {'Content-Type': 'application/json'}

    try:
        response = urequests.post(url, data=json_data, headers=headers)
        print(response.text)
        response.close()
    except Exception as e:
        print('Failed to send data')
        print(e)

# Example function to collect data
def collect_and_send_data():
    # Simulate sensor data collection
    data = {
        "timestamp": "2024-03-01T12:00:00Z",
        ####TEST
        # add actual sensor data here
    }
    
    json_data = json.dumps(data)
    send_data(json_data)

# Call the function to collect data and send it
collect_and_send_data()

