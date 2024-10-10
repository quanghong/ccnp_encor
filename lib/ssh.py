import os, socket
from netmiko import ConnectHandler
from jinja2 import FileSystemLoader, Environment
from dotenv import load_dotenv

load_dotenv()
EVE_NG_IP_HOST_ONLY = os.getenv('EVE_NG_IP_HOST_ONLY')

class SSH:
    def __init__(self, device_type=None, ip=None, username=None, password=None, port=None, timeout=None, source_address=None):
        self.device_type     = device_type
        self.ip = ip
        self.username = username
        self.password = password
        self.connection = None
        self.port = port if port else 22
        self.timeout = timeout if timeout else 20
        self.source_address = source_address

    def connect(self):
        if self.source_address:
            # Create a socket object
            source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Bind the socket to the source IP and any available port (port 0 lets the OS pick the port)
            source_socket.bind((EVE_NG_IP_HOST_ONLY, 0))
            source_socket.connect((self.ip, self.port))
            self.connection = ConnectHandler(device_type=self.device_type, ip=self.ip, username=self.username, password=self.password,
                                            sock=source_socket,
                                            port=self.port,
                                            verbose=True)
        else:
            self.connection = ConnectHandler(device_type=self.device_type, ip=self.ip, username=self.username, password=self.password)
        
        return self.connection

    def disconnect(self):
        self.connection.disconnect()
