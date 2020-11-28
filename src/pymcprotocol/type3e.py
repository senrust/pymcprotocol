import socket

class Type3E:
    """mcprotocol 3E binary type communication class.

    Attributes:
        sock(socket):   socket descriptor
        
    """
    sock = None
    
    def __init__(self, timeout=3):
        """Constructor

        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, ip, port, timeout=None):
        """Connect to PLC

        Args:
            ip (str):       ip address(IPV4) to connect PLC
            port (int):     port number of connect PLC   
            timeout (float):  timeout second in communication

        """
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self.sock.connect(ip, port)
        self.sock.settimeout(timeout)

    def close(self):
        """Close connection

        """
        self.sock.close()