"""This file implements mcprotocol 3E type communication.
"""

import socket
from . import mcprotocolerror

class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "communication type must be \"binary\" or \"ascii\""

class Type3E:
    """mcprotocol 3E binary type communication class.

    Attributes:
        sock(socket):   socket descriptor
        commtype(str):  communication type. "binary" or "ascii". (Default: "binary") 

    """
    sock = None
    commtype = "binary"
    

    def __init__(self):
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

    def set_commtype(self, commtype):
        """Check communication type. If commtype is vaild, set self.commtype.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """
        if commtype is "binary":
            self.commtype = commtype
        elif commtype is "ascii":
            self.commtype = commtype
        else:
            raise CommTypeError()
            

    def setprotocolopt(self, commtype="binary"):
        """Set mc protocol network option.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """
        self.set_commtype(commtype)