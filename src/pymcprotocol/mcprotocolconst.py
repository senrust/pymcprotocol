"""This file defines mcprotocol constant.
"""
#PLC definetion
Q_SERIES    = "Q"
L_SERIES    = "L"
QnA_SERIES  = "QnA"
iQL_SERIES  = "iQ-L"
iQR_SERIES  = "iQ-R"

#command definition
BATCHREAD_WORDUNITS     = 1
BATCHREAD_BITUNITS      = 2
BATCHWRITE_WORDUNITS    = 3
BATCHWRITE_BITUNITS     = 4
RANDOMREAD              = 5
RANDOMWRITE             = 6
RANDOMWRITE_BITUNITS    = 7

#communication type
COMMTYPE_BINARY = "binary"
COMMTYPE_ASCII   = "ascii"

class DeviceCodeError(Exception):
    """devicecode error. Device is not exsist.

    Attributes:
        plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)

    """
    def __init__(self, plctype, devicename):
        self.plctype = plctype
        self.devicename = devicename

    def __str__(self):
        return "devicename: {} is not support {} series PLC".format(self.devicename, self.plctype)

class DeviceConstants:
    """This class defines mc protocol deveice constatnt.

    Attributes:
        D_DEVICE(int):  D devide code (0xA8)

    """
    #These device supports all series
    SM_DEVICE = 0x91
    SD_DEVICE = 0xA9
    X_DEVICE  = 0x9C
    Y_DEVICE  = 0x9D
    M_DEVICE  = 0x90
    L_DEVICE  = 0x92
    F_DEVICE  = 0x93
    V_DEVICE  = 0x94
    B_DEVICE  = 0xA0
    D_DEVICE  = 0xA8
    W_DEVICE  = 0xB4
    TS_DEVICE = 0xC1
    TC_DEVICE = 0xC0
    TN_DEVICE = 0xC2
    SS_DEVICE = 0xC7
    SC_DEVICE = 0xC6
    SN_DEVICE = 0xC8
    CS_DEVICE = 0xC4
    CC_DEVICE = 0xC3
    CN_DEVICE = 0xC5
    SB_DEVICE = 0xA1
    SW_DEVICE = 0xB5
    DX_DEVICE = 0xA2
    DY_DEVICE = 0xA3
    R_DEVICE  = 0xAF
    ZR_DEVICE = 0xB0

    #These device supports only "iQ-R" series
    LTS_DEVICE  = 0x51
    LTC_DEVICE  = 0x50
    LTN_DEVICE  = 0x52
    LSTS_DEVICE = 0x59
    LSTC_DEVICE = 0x58
    LSTN_DEVICE = 0x5A
    LCS_DEVICE  = 0x55
    LCC_DEVICE  = 0x54
    LCN_DEVICE  = 0x56
    LZ_DEVICE   = 0x62
    RD_DEVICE   = 0x2C

    
    def __init__(self):
        """Constructor
        """
        pass
    
    @staticmethod
    def get_binary_devicecode(plctype, devicename):
        """Static method that returns devicecode from device name.

        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")

        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → 0xA8)
        
        """
        if devicename == "SM":
            return DeviceConstants.SM_DEVICE
        elif devicename == "SD":
            return DeviceConstants.SD_DEVICE
        elif devicename == "X":
            return DeviceConstants.X_DEVICE
        elif devicename == "Y":
            return DeviceConstants.Y_DEVICE
        elif devicename == "M":
            return DeviceConstants.M_DEVICE
        elif devicename == "L":
            return DeviceConstants.L_DEVICE
        elif devicename == "F":
            return DeviceConstants.F_DEVICE
        elif devicename == "V":
            return DeviceConstants.V_DEVICE
        elif devicename == "B":
            return DeviceConstants.B_DEVICE
        elif devicename == "D":
            return DeviceConstants.D_DEVICE
        elif devicename == "W":
            return DeviceConstants.W_DEVICE
        elif devicename == "TS":
            return DeviceConstants.TS_DEVICE
        elif devicename == "TC":
            return DeviceConstants.TC_DEVICE
        elif devicename == "TN":
            return DeviceConstants.TN_DEVICE
        elif devicename == "SS":
            return DeviceConstants.SS_DEVICE
        elif devicename == "SC":
            return DeviceConstants.SC_DEVICE
        elif devicename == "SN":
            return DeviceConstants.SN_DEVICE
        elif devicename == "CS":
            return DeviceConstants.CS_DEVICE
        elif devicename == "CC":
            return DeviceConstants.CC_DEVICE
        elif devicename == "CN":
            return DeviceConstants.CN_DEVICE
        elif devicename == "SB":
            return DeviceConstants.SB_DEVICE
        elif devicename == "SW":
            return DeviceConstants.SW_DEVICE
        elif devicename == "DX":
            return DeviceConstants.DX_DEVICE
        elif devicename == "DY":
            return DeviceConstants.DY_DEVICE
        elif devicename == "R":
            return DeviceConstants.R_DEVICE
        elif devicename == "ZR":
            return DeviceConstants.ZR_DEVICE
        elif (devicename == "LTS") and (plctype == iQR_SERIES):
            return DeviceConstants.LTS_DEVICE
        elif (devicename == "LTC") and (plctype == iQR_SERIES):
            return DeviceConstants.LTC_DEVICE
        elif (devicename == "LTN") and (plctype == iQR_SERIES):
            return DeviceConstants.LTN_DEVICE
        elif (devicename == "LSTS") and (plctype == iQR_SERIES):
            return DeviceConstants.LSTS_DEVICE
        elif (devicename == "LSTN") and (plctype == iQR_SERIES):
            return DeviceConstants.LSTN_DEVICE
        elif (devicename == "LCS") and (plctype == iQR_SERIES):
            return DeviceConstants.LCS_DEVICE
        elif (devicename == "LCC") and (plctype == iQR_SERIES):
            return DeviceConstants.LCC_DEVICE
        elif (devicename == "LCN") and (plctype == iQR_SERIES):
            return DeviceConstants.LCN_DEVICE
        elif (devicename == "LZ") and (plctype == iQR_SERIES):
            return DeviceConstants.LZ_DEVICE
        elif (devicename == "RD") and (plctype == iQR_SERIES):
            return DeviceConstants.RD_DEVICE
        else:
            raise DeviceCodeError(plctype, devicename)

    @staticmethod
    def get_ascii_devicecode(plctype, devicename):
        """Static method that returns devicecode from device name.

        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")

        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → "D*")
        
        """
        if plctype == iQR_SERIES:
            padding = 4
        else:
            padding = 2
        if devicename == "SM":
            return devicename.ljust(padding, "*")
        elif devicename == "SD":
            return devicename.ljust(padding, "*")
        elif devicename == "X":
            return devicename.ljust(padding, "*")
        elif devicename == "Y":
            return devicename.ljust(padding, "*")
        elif devicename == "M":
            return devicename.ljust(padding, "*")
        elif devicename == "L":
            return devicename.ljust(padding, "*")
        elif devicename == "F":
            return devicename.ljust(padding, "*")
        elif devicename == "V":
            return devicename.ljust(padding, "*")
        elif devicename == "B":
            return devicename.ljust(padding, "*")
        elif devicename == "D":
            return devicename.ljust(padding, "*")
        elif devicename == "W":
            return devicename.ljust(padding, "*")
        elif devicename == "TS":
            return devicename.ljust(padding, "*")
        elif devicename == "TC":
            return devicename.ljust(padding, "*")
        elif devicename == "TN":
            return devicename.ljust(padding, "*")
        elif devicename == "SS":
            return devicename.ljust(padding, "*")
        elif devicename == "SC":
            return devicename.ljust(padding, "*")
        elif devicename == "SN":
            return devicename.ljust(padding, "*")
        elif devicename == "CS":
            return devicename.ljust(padding, "*")
        elif devicename == "CC":
            return devicename.ljust(padding, "*")
        elif devicename == "CN":
            return devicename.ljust(padding, "*")
        elif devicename == "SB":
            return devicename.ljust(padding, "*")
        elif devicename == "SW":
            return devicename.ljust(padding, "*")
        elif devicename == "DX":
            return devicename.ljust(padding, "*")
        elif devicename == "DY":
            return devicename.ljust(padding, "*")
        elif devicename == "R":
            return devicename.ljust(padding, "*")
        elif devicename == "ZR":
            return devicename.ljust(padding, "*")
        elif (devicename == "LTS") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LTC") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LTN") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LSTS") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LSTN") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LCS") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LCC") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LCN") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "LZ") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        elif (devicename == "RD") and (plctype == iQR_SERIES):
            return devicename.ljust(padding, "*")
        else:
            raise DeviceCodeError(plctype, devicename)