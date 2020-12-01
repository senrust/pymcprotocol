"""This file implements mcprotocol 3E type communication.
"""

import re
import socket
from . import mcprotocolerror
from . import mcprotocolconst as const

class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "communication type must be \"binary\" or \"ascii\""

class PLCTypeError(Exception):
    """PLC type error. PLC type must be "Q", "L" or "iQ"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "plctype must be \"Q\", \"L\" or \"iQ\""

class Type3E:
    """mcprotocol 3E binary type communication class.

    Attributes:
        sock(socket):           socket descriptor
        SOCKBUFSIZE(int):       socket buffer size
        is_connected(bool):     is instance connected to PLC
        plctype(str):           connect PLC type. "Q", "L" r "iQ"
        commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
        subheader(int):         Subheader for mc protocol
        network(int):           network No. of an access target. (0<= network <= 255)
        pc(int):                network module station No. of an access target. (0<= pc <= 255)
        dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                specify the start input/output number of a multidrop connection source module.
                                the CPU module of the multiple CPU system and redundant system.
        dest_modulesta(int):    accessing a multidrop connection station via network, 
                                specify the station No. of aaccess target module
        currentcmd(int):        cuurent communication command.

    """
    sock            = None
    SOCKBUFSIZE     = 4096
    is_connected    = False
    plctype         = const.Q_SERIES
    commtype        = const.COMMTYPE_BINARY
    subheader       = 0x50
    network         = 0
    pc              = 0xFF
    dest_moduleio   = 0X3FF
    dest_modulesta  = 0X0
    timer           = 0
    currentcmd      = None


    def __init__(self, plctype="Q"):
        """Constructor

        """
        self.set_plctype(plctype)
    
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.is_connected = True
        self.sock.settimeout(timeout)

    def close(self):
        """Close connection

        """
        self.sock.close()
        self.is_connected = False

    def send(self, send_data):
        """send mc protorocl data 

        Args: 
            send_data(bytes): mc protocol data
        
        """
        if self.is_connected:
            self.sock.send(send_data)
        else:
            raise Exception("socket is not connected")

    def recv(self):
        """recieve mc protocol data

        Returns:
            recv_data
        """
        recv_data = self.sock.recv(self.SOCKBUFSIZE)
        return recv_data

    def interpret_device(self, device):
        """Get device code and device number.

        Args:
            device(str):    device. (ex: "D1000", "Y1")

        Returns:
            devicecode(str or int): divecode if self.commtype is ascii, returns str, else, returns int
            devicenum(int):  device number
        """
        devicetype =  re.search(r"\D+", device).group(0)
        if self.commtype == const.COMMTYPE_BINARY:
            devicecode = const.DeviceConstants.get_binary_devicecode(self.plctype, devicetype)
        else:
            devicecode = const.DeviceConstants.get_ascii_devicecode(self.plctype, devicetype)
        devicenum = int(re.search(r"\d+", device).group(0))
        return devicecode, devicenum

    def set_plctype(self, plctype):
        """Check PLC type. If plctype is vaild, set self.commtype.

        Args:
            plctype(str):      plc type. "Q", "L" or "iQ". (Default: "Q") 

        """
        if plctype == "Q":
            self.plctype = const.Q_SERIES
        elif plctype == "L":
            self.plctype = const.L_SERIES
        elif plctype == "iQ":
            self.plctype = const.iQ_SERIES
        else:
            raise PLCTypeError()

    def set_commtype(self, commtype):
        """Check communication type. If commtype is vaild, set self.commtype.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """
        if commtype == "binary":
            self.commtype = const.COMMTYPE_BINARY
        elif commtype == "ascii":
            self.commtype = const.COMMTYPE_ASCII
        else:
            raise CommTypeError()

    def setaccessopt(self, commtype=None, network=None, pc=None, dest_moduleio=None, dest_modulesta=None, timer=None):
        """Set mc protocol access option.

        Args:
            commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
            network(int):           network No. of an access target. (0<= network <= 255)
            pc(int):                network module station No. of an access target. (0<= pc <= 255)
            dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                    specify the start input/output number of a multidrop connection source module.
                                    the CPU module of the multiple CPU system and redundant system.
            dest_modulesta(int):    accessing a multidrop connection station via network, 
                                    specify the station No. of aaccess target module
            timer(int):             wait time up to the completion of reading and writing processing.

        """
        if commtype:
            self.set_commtype(commtype)
        if network:
            if(0 <= network <= 255):
                self.network = network
            raise ValueError("network must be 0 <= network <= 255")
        if pc:
            if(0 <= pc <= 255):
                self.pc = pc
            raise ValueError("network must be 0 <= pc <= 255") 
        if dest_moduleio:
            if(0 <= dest_moduleio <= 65535):
                self.dest_moduleio = dest_moduleio
            raise ValueError("dest_moduleio must be 0 <= dest_moduleio <= 65535") 
        if dest_modulesta:
            if(0 <= dest_modulesta <= 255):
                self.dest_modulesta = dest_modulesta
            raise ValueError("network must be 0 <= dest_modulesta <= 255") 
        if timer:
            if(0 <= timer <= 65535):
                self.timer = timer
            raise ValueError("network must be 0 <= timer <= 65535, / 250msec") 
        return None
    
    def make_senddata(self, requestdata):
        """Makes send mc protorocl data.

        Args:
            requestdata(bytes): mc protocol request data. 
                                data must be converted according to self.commtype

        Returns:
            mc_data(bytes):     send mc protorocl data

        """
        mc_data = bytes()
        if self.commtype == const.COMMTYPE_BINARY:
            mc_data += self.subheader.to_bytes(2, "little")
            mc_data += self.network.to_bytes(1, "little")
            mc_data += self.pc.to_bytes(1, "little")
            mc_data += self.dest_moduleio.to_bytes(2, "little")
            mc_data += self.dest_modulesta.to_bytes(1, "little")
            #add data size
            # 2 is for timer size
            data_size = 2 + len(requestdata)
            mc_data += data_size.to_bytes(2, "little")
            mc_data += self.timer.to_bytes(2, "little")
            mc_data += requestdata
        else:
            mc_data += format(self.subheader, "x").ljust(4, "0").upper().encode()
            mc_data += format(self.network, "x").rjust(2, "0").upper().encode()
            mc_data += format(self.pc, "x").rjust(2, "0").upper().encode()
            mc_data += format(self.dest_moduleio, "x").rjust(4, "0").upper().encode()
            mc_data += format(self.dest_modulesta, "x").rjust(2, "0").upper().encode()
            #add data size
            # 4 is for timer size
            data_size = 4 + len(requestdata)
            mc_data += format(data_size, "x").rjust(4, "0").upper().encode()
            mc_data += format(self.timer, "x").rjust(4, "0").upper().encode()
            mc_data += requestdata
        return mc_data

    def make_commanddata(self, command, subcommand):
        """make mc protocol command and subcommand data

        Args:
            command(int):       command code
            subcommand(int):    subcommand code

        Returns:
            command_data(bytes):command data

        """
        command_data = bytes()
        if self.commtype is const.COMMTYPE_BINARY:
            command_data += command.to_bytes(2, "little")
            command_data += subcommand.to_bytes(2, "little")
        else:
            command_data += format(command, "x").rjust(4, "0").upper().encode()
            command_data += format(subcommand, "x").rjust(4, "0").upper().encode()
        return command_data
    

    def make_devicedata(self, device):
        """make mc protocol device data. (device code and device number)
        
        Args:
            device(str): device. (ex: "D1000", "Y1")

        Returns:
            device_data(bytes): device data
            
        """
        device_data = bytes()
        if self.commtype is const.COMMTYPE_BINARY:
            devicecode, devicenum = self.interpret_device(device)
            if self.plctype is const.iQ_SERIES:
                device_data += devicenum.to_bytes(4, "little")
                device_data += devicecode.to_bytes(2, "little")
            else:
                device_data += devicenum.to_bytes(3, "little")
                device_data += devicecode.to_bytes(1, "little")
        else:
            devicecode, devicenum = self.interpret_device(device)
            if self.plctype is const.iQ_SERIES:
                device_data += devicecode.encode()
                device_data += format(devicenum).rjust(8, "0").upper().encode()

            else:
                device_data += devicecode.encode()
                device_data += format(devicenum).rjust(6, "0").upper().encode()
        return device_data

    def make_valuedata(self, value):
        """make mc protocol value data.

        Args: value(int):   readsize, write value, and so on.

        Returns:
            value_data(bytes):  value data
        
        """
        value_data = bytes()
        if self.commtype == const.COMMTYPE_BINARY:
            value_data += value.to_bytes(2, "little")
        else:
            value_data += format(value, "x").rjust(4, "0").upper().encode()
        return value_data
        
    def check_cmdanswer(self, recv_data):
        """check command answer. If answer status is not 0, raise error according to answer  

        """
        if self.commtype == const.COMMTYPE_BINARY:
            answer_status = int.from_bytes(recv_data[9:11], "little")
        else:
            answer_status_str = recv_data[18:22].decode()
            answer_status = int(answer_status_str, 16)
        mcprotocolerror.check_mcprotocol_error(answer_status)

    def batchread_wordunits(self, headdevice, readsize):
        """batch read in word units.

        Args:
            headdevice(str):    Read head device. (ex: "D1000")
            readsize(int):      Number of read device points

        Returns:
            wordunits_values(list[int]):  word units value list

        """
        self.currentcmd = const.BATCHREAD_WORDUNITS
        command = 0x0401
        if self.plctype == const.iQ_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000
        
        request_data = bytes()
        request_data += self.make_commanddata(command, subcommand)
        request_data += self.make_devicedata(headdevice)
        request_data += self.make_valuedata(readsize)
        send_data = self.make_senddata(request_data)

        #send mc data
        self.send(send_data)
        self._send_data = send_data
        #reciev mc data
        recv_data = self.recv()
        self._recv_data = recv_data
        self.check_cmdanswer(recv_data)

        wordunits_values = []
        if self.commtype == const.COMMTYPE_BINARY:
            data_index = 11
            data_range = 2
            for i in range(readsize):
                wordvalue = int.from_bytes(recv_data[data_index+i*data_range:data_index+i*data_range+data_range], "little")
                wordunits_values.append(wordvalue)
        else:
            data_index = 22
            data_range = 4
            for i in range(readsize):
                wordvalue = int(recv_data[data_index+i*data_range:data_index+i*data_range+data_range].decode(), 16)
                wordunits_values.append(wordvalue)
        return wordunits_values

    def batchread_bitunits(self, headdevice, readsize):
        """batch read in bit units.

        Args:
            headdevice(str):    Read head device. (ex: "X1")
            size(int):          Number of read device points

        Returns:
            bitunits_values(list[int]):  bit units value(0 or 1) list

        """
        self.currentcmd = const.BATCHREAD_BITUNITS
        command = 0x0401
        if self.plctype == const.iQ_SERIES:
            subcommand = 0x0003
        else:
            subcommand = 0x0001
        
        request_data = bytes()
        request_data += self.make_commanddata(command, subcommand)
        request_data += self.make_devicedata(headdevice)
        request_data += self.make_valuedata(readsize)
        send_data = self.make_senddata(request_data)

        #send mc data
        self.send(send_data)
        self._send_data = send_data
        #reciev mc data
        recv_data = self.recv()
        self._recv_data = recv_data

        self.check_cmdanswer(recv_data)

        bitunits_values = []
        if self.commtype == const.COMMTYPE_BINARY:
            for i in range(readsize):
                data_index = i//2 + 11
                value = int.from_bytes(recv_data[data_index:data_index+1], "little")
                #if i//2==0, bit value is 4th bit
                if(i%2==0):
                    bitvalue = 1 if value & (1<<4) else 0
                else:
                    bitvalue = 1 if value & (1<<0) else 0
                bitunits_values.append(bitvalue)
        else:
            data_index = 22
            byte_range = 1
            for i in range(readsize):
                bitvalue = int(recv_data[data_index+i:data_index+i+byte_range].decode())
                bitunits_values.append(bitvalue)
        return bitunits_values

    def batchwrite_wordunits(self, headdevice, values):
        """batch read in word units.

        Args:
            headdevice(str):    Write head device. (ex: "D1000")
            values(list[int]):  Write values.

        """
        write_size = len(values)

        self.currentcmd = const.BATCHWRITE_WORDUNITS
        command = 0x1401
        if self.plctype == const.iQ_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000
        
        request_data = bytes()
        request_data += self.make_commanddata(command, subcommand)
        request_data += self.make_devicedata(headdevice)
        request_data += self.make_valuedata(write_size)
        for value in values:
            request_data += self.make_valuedata(value)
        send_data = self.make_senddata(request_data)

        #send mc data
        self.send(send_data)
        self._send_data = send_data
        #reciev mc data
        recv_data = self.recv()
        self._recv_data = recv_data
        self.check_cmdanswer(recv_data)

        return None

    def batchwrite_bitunits(self, headdevice, values):
        """batch read in bit units.

        Args:
            headdevice(str):    Write head device. (ex: "X10")
            values(list[int]):  Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        self.currentcmd = const.BATCHWRITE_BITUNITS
        command = 0x1401
        if self.plctype == const.iQ_SERIES:
            subcommand = 0x0003
        else:
            subcommand = 0x0001
        
        request_data = bytes()
        request_data += self.make_commanddata(command, subcommand)
        request_data += self.make_devicedata(headdevice)
        request_data += self.make_valuedata(write_size)
        if self.commtype == const.COMMTYPE_BINARY:
            #evary value is 0 or 1.
            #Even index's value turns on or off 4th bit, odd index's value turns on or off 0th bit.
            #First, create send data list. Length must be ceil of len(values).
            bit_data = [0 for _ in range((len(values) + 1)//2)]
            for index, value in enumerate(values):
                #calc which index data should be turns on.
                value_index = index//2
                #calc which bit should be turns on.
                bit_index = 4 if index%2 == 0 else 0
                #turns on or off value of 4th or 0th bit, depends on value
                bit_value = value << bit_index
                #Take or of send data
                bit_data[value_index] |= bit_value
            request_data += bytes(bit_data)
        else:
            for value in values:
                request_data += str(value).encode()
        send_data = self.make_senddata(request_data)
                    
        #send mc data
        self.send(send_data)
        self._send_data = send_data
        #reciev mc data
        recv_data = self.recv()
        self._recv_data = recv_data
        self.check_cmdanswer(recv_data)

        return None


 

            



    

    
        
