import network
import urequests as requests
import json

# Wi-Fi credentials
ssid = 'MyiPhone12'
password = 'abcdefgh'

# Google Apps Script execution URL
url = 'https://script.google.com/macros/s/AKfycbw3KMFPTUyAL28x0v8iv6WxMvgNxNmeDodNajs5dTMATo9QzHdzfp2rpPKkoUQniXwR/exec'

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

def main():
    connect_wifi()
    #sync_time()
    collect_and_send_data()

if __name__ == "__main__":
    main()

