import network
import random
import socket
import time

class ConfigurationError(Exception):
    pass

class WebServer():
    '''Hosts a webserver using a soft access point on 192.168.4.1.'''

    def __init__(self, base_path: str) -> None:
        '''
        Initializes the class.
        
        base_path
            The directory path in which all files are contained.
        '''
        self.base_path = base_path
        self.cached_files = {}

    def config(self, **kwargs) -> None:
        '''
        Sets configuration options using keyword arguments.
        
        Required options: html_path, ssid, password.
        '''
        if 'html_path' in kwargs:
            self.html_path = kwargs['html_path']
        if 'ssid' in kwargs:
            self.ssid = kwargs['ssid']
        if 'password' in kwargs:
            self.password = kwargs['password']

    def start(self) -> None:
        '''Starts the webserver (blocking).'''
        self.enable_ap(-1)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', 80))
        server_socket.listen(5)

        try:
            while True:
                connection = server_socket.accept()[0]
                request = connection.recv(1024)
                if response := self._get_response(request):
                    connection.send(response)
                connection.close()
        finally:
            server_socket.close()
            connection.close()

    def enable_ap(self, timeout: int) -> bool:
        '''
        Activates AP mode using the SSID and password from the class.

        timeout
            maximum time to wait in ms (0 to disable and -1 to wait indefinitely).

        Returns True if successful and False if timed out.
        '''
        
        if not hasattr(self, 'ap'):
            self._check_config('ssid', 'password')
            self.ap = network.WLAN(network.AP_IF)
            self.ap.config(essid=self.ssid, password=self.password)

        if self.ap.active() or self.ap.active(True) or timeout == 0:
            return True
        
        start_time = time.ticks_ms()
        while not self.ap.active():
            if 0 < timeout and timeout < time.ticks_ms() - start_time:
                return False
        return True
    
    def _get_response(self, request: bytes) -> object:
        '''Parses the request and returns the response'''
        method, target = request.decode().split(' ')[:2]
        path = target.split('?')[0]

        print(request)

        if method == 'GET':
            if path == '/':
                self._check_config('html_path')
                path += self.html_path
            if path not in self.cached_files:
                try:
                    with open(self.base_path + path) as file:
                        self.cached_files[path] = file.read()
                except Exception:
                    self.cached_files[path] = None
            return self.cached_files[path]
        elif method == 'POST':
            if path == '/random':
                return str(random.randint(0, 99))
    
    def _check_config(self, *args: str) -> None:
        '''Checks if all the specified configuration options have been set, throws ConfigurationError otherwise.'''
        if (unset_options := [option for option in args if not hasattr(self, option)]):
            msg = f'The following configuration options are required, but have not been set: {unset_options}'
            raise ConfigurationError(msg)