"""This file is collection of mcprotocol error.

"""

class MCProtocolError(Exception):
    """devicecode error. Device is not exsist.

    Attributes:
        plctype(str):       PLC type. "Q", "L" or "iQ"
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)

    """
    def __init__(self, errorcode):
        self.errorcode =  "0x" + format(errorcode, "x").rjust(4, "0").upper()

    def __str__(self):
        return "mc protocol error: error code {}".format(self.errorcode)

    
def check_mcprotocol_error(status):
    """Check mc protocol command error.
    If errot exist(status != 0), raise Error.

    """
    if status == 0:
        return None
    else:
        raise MCProtocolError(status)

        