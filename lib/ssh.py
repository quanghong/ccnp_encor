from netmiko import ConnectHandler
from jinja2 import FileSystemLoader, Environment

class SSH:
    def __init__(self, device_type=None, ip=None, username=None, password=None, port=None, timeout=None):
        self.device_type     = device_type
        self.ip = ip
        self.username = username
        self.password = password
        self.connection = None
        self.port = port if port else 22
        self.timeout = timeout if timeout else 20

    def connect(self):
        self.connection = ConnectHandler(device_type=self.device_type, ip=self.ip, username=self.username, password=self.password)
        return self.connection

    def disconnect(self):
        self.connection.disconnect()
