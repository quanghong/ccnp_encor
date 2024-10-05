import telnetlib

class TELNET:
    def __init__(self, host=None, username=None, password=None, port=None, timeout=None):
        self.host     = host
        self.username = username
        self.password = password
        self.connection = None
        self.port = port if port else 23
        self.timeout = port if port else 20

    def connect(self):
        connection = telnetlib.Telnet(self.host, self.port, self.timeout)
        # pattern, _, output = self.connection.expect([b"# ", b">", b"#", b"name", b"ogin:", b"User name", b"\>\>User name\:"b"assword", b">>User password"], 15)
        self.connection = connection
        return self.connection

    def disconnect(self):
        self.connection.close()