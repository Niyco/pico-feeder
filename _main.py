import webserver

server = webserver.WebServer('webpage/')
server.config(html_path='index.html', ssid='Pico Feeder', password='password')
server.start()