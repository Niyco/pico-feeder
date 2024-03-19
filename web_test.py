import network
import uasyncio, uasyncio.core
import usocket

async def dns_handler(socket, ip_address):
    while True:
        yield uasyncio.core._io_queue.queue_read(socket)
        request, client = socket.recvfrom(256)
        response = request[:2] + b'\x81\x80' + request[4:6] + request[4:6] + b'\x00\x00\x00\x00' + request[12:]
        response += b'\xC0\x0C\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04' + bytes(map(int, ip_address.split('.')))
        socket.sendto(response, client)

async def _handle_request(reader, writer):
    request_line = await reader.readline()
    method, path, _ = request_line.decode().split()
    host = None
    while True:
        header_line = await reader.readline()
        if header_line == b'\r\n':
            break
        name, value = header_line.decode().strip().split(': ', 1)
        if name.lower() == 'host':
            host = value

    if host != AP_DOMAIN:
        html = REDIRECT_HTML
    elif method == 'GET' and path == '/':
        html = INDEX_HTML

    writer.write(f'HTTP/1.1 {200} \r\n'.encode('ascii'))
    writer.write(f'Content-Type: text/html\r\n'.encode('ascii'))
    writer.write(f'Content-Length: {len(html)}\r\n'.encode('ascii'))
    writer.write('\r\n'.encode('ascii'))
    writer.write(html)

    await writer.drain()
    writer.close()
    await writer.wait_closed()
    
    print(method, path)

AP_NAME = 'pi pico'
AP_DOMAIN = 'pipico.net'
REDIRECT_HTML = f'''<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta http-equiv='refresh' content='0;url=http://{AP_DOMAIN}'></head><body></body></html>'''
INDEX_HTML = '''<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head><body><h1>Hello World!</h1></body></html>'''

ap = network.WLAN(network.AP_IF)
ap.config(essid=AP_NAME)
ap.config(security=0)
ap.active(True)

dns_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM)
dns_socket.setblocking(False)
dns_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
dns_socket.bind(usocket.getaddrinfo(ap.ifconfig()[0], 53, 0, usocket.SOCK_DGRAM)[0][-1])
loop = uasyncio.get_event_loop()
loop.create_task(dns_handler(dns_socket, ap.ifconfig()[0]))
loop.create_task(uasyncio.start_server(_handle_request, '0.0.0.0', 80)) # type: ignore 
loop.run_forever()