# import network
# 
# def connect_to_wifi(ssid, password):
#     sta_if = network.WLAN(network.STA_IF)
#     if not sta_if.isconnected():
#         print('Connecting to network...')
#         sta_if.active(True)
#         sta_if.connect(ssid, password)
#         while not sta_if.isconnected():
#             pass
#     print('Network config:', sta_if.ifconfig())
# 
# connect_to_wifi('C206', 'aprilsurface086')

# import uhttpd
# from uhttpd.http_file_handler import StaticFileHandler
# 
# def index(req, resp):
#     yield from resp.awrite("Hello, world from uhttpd on ESP32!")
# 
# handlers = [('/', index)]
# server = uhttpd.Server(handlers, port=8080)
# server.run()

# main.py

try:
    import usocket as socket
except:
    import socket

# def web_page():
#     html = """
#     <html>
#     <head>
#         <title>ESP32 Web Server</title>
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.css" />
#     </head>
#     <body>
#         <h1>ESP32 Web Server</h1>
#         <div id="map" style="width: 800px; height: 600px;"></div>
#         <script src="http://cdn.leafletjs.com/leaflet/v0.7.7/leaflet.js"></script>
#         <script>
#         var map = L.map('map').setView([51.505, -0.09], 13);
#         L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
#             maxZoom: 19
#         }).addTo(map);
#         var route1 = [[51.5, -0.09], [51.51, -0.1]];
#         var route2 = [[51.5, -0.08], [51.52, -0.1]];
#         for (var i = 0; i < route1.length; i++) {
#             L.marker(route1[i]).addTo(map)
#                 .bindPopup('Planned Route ' + i)
#                 .openPopup();
#         }
#         for (var i = 0; i < route2.length; i++) {
#             L.marker(route2[i]).addTo(map)
#                 .bindPopup('Actual Route ' + i)
#                 .openPopup();
#         }
#         </script>
#     </body>
#     </html>
#     """
#     return html

def web_page():
  html = """
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
    <body><h1>Hello, World! Feb 20, 2024 </h1></body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    print('Content = %s' % str(request))
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()
