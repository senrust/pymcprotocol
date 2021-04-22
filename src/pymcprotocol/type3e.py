"""This file implements mcprotocol 3E type communication.
"""

import re
import socket
from . import mcprotocolerror
from . import mcprotocolconst as const


def twos_comp(val:int, mode:str="short"):
    """compute the 2's complement of int value val
    """
    if mode =="byte":
        bit = 8
    elif mode =="short":
        bit = 16
    elif mode== "long":
        bit = 32
    else:
        raise ValueError("cannnot calculate 2's complement")
    if (val & (1 << (bit - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bit)        # compute negative value
    return val  

class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "communication type must be \"binary\" or \"ascii\""

class PLCTypeError(Exception):
    """PLC type error. PLC type must be"Q", "L", "QnA", "iQ-L", "iQ-R"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "plctype must be \"Q\", \"L\", \"QnA\" \"iQ-L\" or \"iQ-R\""

class Type3E:
    """mcprotocol 3E communication class.

    Attributes:
        plctype(str):           connect PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
        commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
        subheader(int):         Subheader for mc protocol
        network(int):           network No. of an access target. (0<= network <= 255)
        pc(int):                network module station No. of an access target. (0<= pc <= 255)
        dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                specify the start input/output number of a multidrop connection source module.
                                the CPU module of the multiple CPU system and redundant system.
        dest_modulesta(int):    accessing a multidrop connection station via network, 
                                specify the station No. of aaccess target module
        timer(int):             time to raise Timeout error(/250msec). default=4(1sec)
                                If PLC elapsed this time, PLC returns Timeout answer.
                                Note: python socket timeout is always set timer+1sec. To recieve Timeout answer.
    """
    plctype         = const.Q_SERIES
    commtype        = const.COMMTYPE_BINARY
    subheader       = 0x5000
    network         = 0
    pc              = 0xFF
    dest_moduleio   = 0X3FF
    dest_modulesta  = 0X0
    timer           = 4
    _sock           = None
    _is_connected   = False
    _SOCKBUFSIZE    = 4096
    _currentcmd     = None
    _wordsize       = 2 #how many byte is required to describe word value 
                        #binary: 2, ascii:4.
    _DEBUG          = False



    def __init__(self, plctype="Q"):
        """Constructor

        """
        self._set_plctype(plctype)
    
    def _set_debug(self, debug=False):
        """Turn on debug mode
        """
        self._DEBUG = debug
    
    def connect(self, ip, port):
        """Connect to PLC

        Args:
            ip (str):       ip address(IPV4) to connect PLC
            port (int):     port number of connect PLC   
            timeout (float):  timeout second in communication

        """
        self._ip = ip
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((ip, port))
        self._is_connected = True

    def close(self):
        """Close connection

        """
        self._sock.close()
        self._is_connected = False

    def _send(self, send_data):
        """send mc protorocl data 

        Args: 
            send_data(bytes): mc protocol data
        
        """
        if self._is_connected:
            self._sock.settimeout(self.timer+1)
            self._sock.send(send_data)
        else:
            raise Exception("socket is not connected")

    def _recv(self):
        """recieve mc protocol data

        Returns:
            recv_data
        """
        recv_data = self._sock.recv(self._SOCKBUFSIZE)
        return recv_data

    def _interpret_device(self, device):
        """Get device code and device number.
        device number is converted to base number for each device.

        Args:
            device(str):    device. (ex: "D1000", "Y1")

        Returns:
            devicecode(str or int): if self.commtype is ascii, returns str devicode, else, returns int devicode
            devicenum(str or int):  if self.commtype is ascii, returns str devicenum, else, returns int devicenum
        """
        devicetype =  re.search(r"\D+", device).group(0)
        if self.commtype == const.COMMTYPE_BINARY:
            devicecode, devicebase = const.DeviceConstants.get_binary_devicecode(self.plctype, devicetype)
            devicenum = int(re.search(r"\d.*", device).group(0), devicebase)
        else:
            devicecode, _ = const.DeviceConstants.get_ascii_devicecode(self.plctype, devicetype)
            devicenum = re.search(r"\d.*", device).group(0)
        return devicecode, devicenum

    def _set_plctype(self, plctype):
        """Check PLC type. If plctype is vaild, set self.commtype.

        Args:
            plctype(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 

        """
        if plctype == "Q":
            self.plctype = const.Q_SERIES
        elif plctype == "L":
            self.plctype = const.L_SERIES
        elif plctype == "QnA":
            self.plctype = const.QnA_SERIES
        elif plctype == "iQ-L":
            self.plctype = const.iQL_SERIES
        elif plctype == "iQ-R":
            self.plctype = const.iQR_SERIES
        else:
            raise PLCTypeError()

    def _set_commtype(self, commtype):
        """Check communication type. If commtype is vaild, set self.commtype.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """
        if commtype == "binary":
            self.commtype = const.COMMTYPE_BINARY
            self._wordsize = 2
        elif commtype == "ascii":
            self.commtype = const.COMMTYPE_ASCII
            self._wordsize = 4
        else:
            raise CommTypeError()

    def _get_answerdata_index(self):
        """Get answer data index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 11
        else:
            return 22

    def _get_answerstatus_index(self):
        """Get command status index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 9
        else:
            return 18

    def setaccessopt(self, commtype=None, network=None, pc=None, dest_moduleio=None, dest_modulesta=None, timer_sec=None):
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
            timer_sec(int):         Time out to return Timeout Error from PLC. 
                                    MC protocol time is per 250msec, but for ease, setaccessopt requires per sec.
                                    Socket time out is set timer_sec + 1 sec.

        """
        if commtype:
            self._set_commtype(commtype)
        if network:
            try:
                network.to_bytes(1, "little")
                self.network = network
            except:
                raise ValueError("network must be 0 <= network <= 255")
        if pc:
            try:
                pc.to_bytes(1, "little")
                self.pc = pc
            except:
                raise ValueError("pc must be 0 <= pc <= 255") 
        if dest_moduleio:
            try:
                dest_moduleio.to_bytes(2, "little")
                self.dest_moduleio = dest_moduleio
            except:
                raise ValueError("dest_moduleio must be 0 <= dest_moduleio <= 65535") 
        if dest_modulesta:
            try:
                dest_modulesta.to_bytes(1, "little")
                self.dest_modulesta = dest_modulesta
            except:
                raise ValueError("dest_modulesta must be 0 <= dest_modulesta <= 255") 
        if timer_sec:
            try:
                timer_250msec = 4 * timer_sec
                timer_250msec.to_bytes(2, "little")
                self.timer = timer_250msec
            except:
                raise ValueError("timer_sec must be 0 <= timer_sec <= 16383, / sec") 
        return None
    
    def _make_senddata(self, requestdata):
        """Makes send mc protorocl data.

        Args:
            requestdata(bytes): mc protocol request data. 
                                data must be converted according to self.commtype

        Returns:
            mc_data(bytes):     send mc protorocl data

        """
        mc_data = bytes()
        # subheader is big endian
        if self.commtype == const.COMMTYPE_BINARY:
             mc_data += self.subheader.to_bytes(2, "big")
        else:
            mc_data += format(self.subheader, "x").ljust(4, "0").upper().encode()
        mc_data += self._encode_value(self.network, "byte")
        mc_data += self._encode_value(self.pc, "byte")
        mc_data += self._encode_value(self.dest_moduleio, "short")
        mc_data += self._encode_value(self.dest_modulesta, "byte")
        #add self.timer size
        mc_data += self._encode_value(self._wordsize + len(requestdata), "short")
        mc_data += self._encode_value(self.timer, "short")
        mc_data += requestdata
        return mc_data

    def _make_commanddata(self, command, subcommand):
        """make mc protocol command and subcommand data

        Args:
            command(int):       command code
            subcommand(int):    subcommand code

        Returns:
            command_data(bytes):command data

        """
        command_data = bytes()
        command_data += self._encode_value(command, "short")
        command_data += self._encode_value(subcommand, "short")
        return command_data
    
    def _make_devicedata(self, device):
        """make mc protocol device data. (device code and device number)
        
        Args:
            device(str): device. (ex: "D1000", "Y1")

        Returns:
            device_data(bytes): device data
            
        """
        device_data = bytes()
        devicecode, devicenum = self._interpret_device(device)
        if self.commtype is const.COMMTYPE_BINARY:
            if self.plctype is const.iQR_SERIES:
                device_data += devicenum.to_bytes(4, "little")
                device_data += devicecode.to_bytes(2, "little")
            else:
                device_data += devicenum.to_bytes(3, "little")
                device_data += devicecode.to_bytes(1, "little")
        else:
            if self.plctype is const.iQR_SERIES:
                device_data += devicecode.encode()
                device_data += devicenum.rjust(8, "0").upper().encode()
            else:
                device_data += devicecode.encode()
                device_data += devicenum.rjust(6, "0").upper().encode()
        return device_data

    def _encode_value(self, value, mode="short", isSigned=False):
        """encode mc protocol value data to byte.

        Args: 
            value(int):   readsize, write value, and so on.
            mode(str):    value type.
            isSigned(bool): convert as sigend value

        Returns:
            value_byte(bytes):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if mode == "byte":
                    value_byte = value.to_bytes(1, "little", signed=isSigned)
                elif mode == "short":
                    value_byte = value.to_bytes(2, "little", signed=isSigned)
                elif mode == "long":
                    value_byte = value.to_bytes(4, "little", signed=isSigned)
                else: 
                    raise ValueError("Please input value type")
            else:
                #check value range by to_bytes
                #convert to unsigned value
                if mode == "byte":
                    value.to_bytes(1, "little", signed=isSigned)
                    value = value & 0xff
                    value_byte = format(value, "x").rjust(2, "0").upper().encode()
                elif mode == "short":
                    value.to_bytes(2, "little", signed=isSigned)
                    value = value & 0xffff
                    value_byte = format(value, "x").rjust(4, "0").upper().encode()
                elif mode == "long":
                    value.to_bytes(4, "little", signed=isSigned)
                    value = value & 0xffffffff
                    value_byte = format(value, "x").rjust(8, "0").upper().encode()
                else: 
                    raise ValueError("Please input value type")
        except:
            raise ValueError("Exceeeded Device value range")
        return value_byte

    def _encode_devicevalue(self, value, device, mode="short"):
        """encode mc protocol device value data to bytes.

        Args: 
            value(int):   readsize, write value, and so on.
            device(str):  device
            mode(str):    value type.

        Returns:
            value_byte(bytes):  value data
        
        """
        devicename =  re.search(r"\D+", device).group(0)
        devicetype = const.DeviceConstants.get_devicetype(self.plctype, devicename)
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if mode == "byte":
                    value_byte = value.to_bytes(1, "little", signed=True)
                elif mode == "short":
                    value_byte = value.to_bytes(2, "little", signed=True)
                elif mode == "long":
                    value_byte = value.to_bytes(4, "little", signed=True)
                else: 
                    raise ValueError("Please input value type")
            else:
                #check value range by to_bytes
                #convert to unsigned value
                if mode == "byte":
                    value.to_bytes(1, "little", signed=True)
                    value = value & 0xff
                    value_byte = format(value, "x").rjust(2, "0").upper().encode()
                elif mode == "short":
                    value.to_bytes(2, "little", signed=True)
                    value = value & 0xffff
                    value_byte = format(value, "x").rjust(4, "0").upper().encode()
                elif mode == "long":
                    value.to_bytes(4, "little", signed=True)
                    value = value & 0xffffffff
                    value_byte = format(value, "x").rjust(8, "0").upper().encode()
                else: 
                    raise ValueError("Please input value type")
        except:
            raise ValueError("Exceeeded Device value range")
        return value_byte

    def _decode_value(self, byte, mode="short", isSigned=False):
        """decode byte to value

        Args: 
            value(int):   readsize, write value, and so on.
            mode(str):    value type.
            isSigned(bool): convert as sigend value  

        Returns:
            value_data(int):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                value =int.from_bytes(byte, "little", signed = isSigned)
            else:
                value = int(byte.decode(), 16)
                if isSigned:
                    value = twos_comp(value, mode)
        except:
            raise ValueError("Could not decode byte to value")
        return value

    def _decode_devicevalue(self, byte, device, mode="short"):
        """decode device data byte to value

        Args: 
            value(int):   readsize, write value, and so on.
            device(str):  device name
            mode(str):    value type.

        Returns:
            value_data(int):  value data
        
        """
        devicename =  re.search(r"\D+", device).group(0)
        devicetype = const.DeviceConstants.get_devicetype(self.plctype, devicename)
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if devicetype == const.DeviceConstants.BIT_DEVICE:
                    if mode == "byte":
                        value =int.from_bytes(byte, "big", signed = True)
                    elif mode == "short":
                        value_byte = bytes()
                        value_byte += byte[1:2]
                        value_byte += byte[0:1]
                        value =int.from_bytes(value_byte, "big", signed = True)
                    elif mode == "long":
                        value_byte = bytes()
                        value_byte += byte[3:4]
                        value_byte += byte[2:3]
                        value_byte += byte[1:2]
                        value_byte += byte[0:1]
                        value =int.from_bytes(value_byte, "big", signed = True)
                    else: 
                        raise ValueError("Please input value type")
                else:
                    value =int.from_bytes(byte, "little", signed = True)
            else:
                value = int(byte.decode(), 16)
                value = twos_comp(value, mode)

        except:
            raise ValueError("Could not decode byte to value")
        return value
        
    def _check_cmdanswer(self, recv_data):
        """check command answer. If answer status is not 0, raise error according to answer  

        """
        answerstatus_index = self._get_answerstatus_index()
        answerstatus = self._decode_value(recv_data[answerstatus_index:answerstatus_index+self._wordsize], "short")
        mcprotocolerror.check_mcprotocol_error(answerstatus)
        return None

    def batchread_wordunits(self, headdevice, readsize):
        """batch read in word units.

        Args:
            headdevice(str):    Read head device. (ex: "D1000")
            readsize(int):      Number of read device points

        Returns:
            wordunits_values(list[int]):  word units value list

        """
        self._currentcmd = const.BATCHREAD_WORDUNITS
        command = 0x0401
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(readsize)
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data    
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        word_values = []
        data_index = self._get_answerdata_index()
        for _ in range(readsize):
            wordvalue = self._decode_devicevalue(recv_data[data_index:data_index+self._wordsize], headdevice, mode="short")
            word_values.append(wordvalue)
            data_index += self._wordsize
        return word_values

    def batchread_bitunits(self, headdevice, readsize):
        """batch read in bit units.

        Args:
            headdevice(str):    Read head device. (ex: "X1")
            size(int):          Number of read device points

        Returns:
            bitunits_values(list[int]):  bit units value(0 or 1) list

        """
        self._currentcmd = const.BATCHREAD_BITUNITS
        command = 0x0401
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0003
        else:
            subcommand = 0x0001
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(readsize)
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        bit_values = []
        if self.commtype == const.COMMTYPE_BINARY:
            for i in range(readsize):
                data_index = i//2 + self._get_answerdata_index()
                value = int.from_bytes(recv_data[data_index:data_index+1], "little")
                #if i//2==0, bit value is 4th bit
                if(i%2==0):
                    bitvalue = 1 if value & (1<<4) else 0
                else:
                    bitvalue = 1 if value & (1<<0) else 0
                bit_values.append(bitvalue)
        else:
            data_index = self._get_answerdata_index()
            byte_range = 1
            for i in range(readsize):
                bitvalue = int(recv_data[data_index:data_index+byte_range].decode())
                bit_values.append(bitvalue)
                data_index += byte_range
        return bit_values

    def batchwrite_wordunits(self, headdevice, values):
        """batch write in word units.

        Args:
            headdevice(str):    Write head device. (ex: "D1000")
            values(list[int]):  Write values.

        """
        write_size = len(values)

        self._currentcmd = const.BATCHWRITE_WORDUNITS
        command = 0x1401
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(write_size)
        for value in values:
            request_data += self._encode_devicevalue(value, headdevice)
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

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

        self._currentcmd = const.BATCHWRITE_BITUNITS
        command = 0x1401
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0003
        else:
            subcommand = 0x0001
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._make_devicedata(headdevice)
        request_data += self._encode_value(write_size)
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
        send_data = self._make_senddata(request_data)
                    
        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None

    def randomread(self, word_devices, dword_devices):
        """read word units and dword units randomly.
        Moniter condition does not support.

        Args:
            word_devices(list[str]):    Read device word units. (ex: ["D1000", "D1010"])
            dword_devices(list[str]):   Read device dword units. (ex: ["D1000", "D1012"])

        Returns:
            word_values(list[int]):     word units value list
            dword_values(list[int]):    dword units value list

        """
        self._currentcmd = const.RANDOMREAD
        command = 0x0403
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000

        word_size = len(word_devices)
        dword_size = len(dword_devices)
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(word_size, mode="byte")
        request_data += self._encode_value(dword_size, mode="byte")
        for word_device in word_devices:
            request_data += self._make_devicedata(word_device)
        for dword_device in dword_devices:
            request_data += self._make_devicedata(dword_device)        
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        data_index = self._get_answerdata_index()
        word_values = []
        dword_values = []
        for word_device in word_devices:
            wordvalue = self._decode_devicevalue(recv_data[data_index:data_index+self._wordsize], word_device, mode="short")
            word_values.append(wordvalue)
            data_index += self._wordsize
        for dword_device in dword_devices:
            dwordvalue = self._decode_devicevalue(recv_data[data_index:data_index+self._wordsize*2], dword_device, mode="long")
            dword_values.append(dwordvalue)
            data_index += self._wordsize*2
        return word_values, dword_values

    def randomwrite(self, word_devices, word_values, dword_devices, dword_values):
        """write word units and dword units randomly.

        Args:
            word_devices(list[str]):    Write word devices. (ex: ["D1000", "D1020"])
            word_values(list[int]):     Values for each word devices. (ex: [100, 200])
            dword_devices(list[str]):   Write dword devices. (ex: ["D1000", "D1020"])
            dword_values(list[int]):    Values for each dword devices. (ex: [100, 200])

        """
        if len(word_devices) != len(word_values):
            raise ValueError("word_devices and word_values must be same length")
        if len(dword_devices) != len(dword_values):
            raise ValueError("dword_devices and dword_values must be same length")
            
        word_size = len(word_devices)
        dword_size = len(dword_devices)

        self._currentcmd = const.RANDOMWRITE
        command = 0x1402
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0002
        else:
            subcommand = 0x0000
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(word_size, mode="byte")
        request_data += self._encode_value(dword_size, mode="byte")
        for word_device, word_value in zip(word_devices, word_values):
            request_data += self._make_devicedata(word_device)
            request_data += self._encode_devicevalue(word_value, word_device, mode="short")
        for dword_device, dword_value in zip(dword_devices, dword_values):
            request_data += self._make_devicedata(dword_device)   
            request_data += self._encode_devicevalue(dword_value, dword_device, mode="long")     
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def randomwrite_bitunits(self, bit_devices, values):
        """write bit units randomly.

        Args:
            bit_devices(list[str]):    Write bit devices. (ex: ["X10", "X20"])
            values(list[int]):         Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        if len(bit_devices) != len(values):
            raise ValueError("bit_devices and values must be same length")
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        self._currentcmd = const.RANDOMWRITE_BITUNITS
        command = 0x1402
        if self.plctype == const.iQR_SERIES:
            subcommand = 0x0003
        else:
            subcommand = 0x0001
        
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(write_size, mode="byte")
        for bit_device, value in zip(bit_devices, values):
            request_data += self._make_devicedata(bit_device)
            #byte value for iQ-R requires 2 byte data
            if self.plctype == const.iQR_SERIES:
                request_data += self._encode_devicevalue(value, bit_device, mode="short")
            else:
                request_data += self._encode_devicevalue(value, bit_device, mode="byte")
        send_data = self._make_senddata(request_data)
                    
        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None

    def remote_run(self, clear_mode, force_exec=False):
        """Run PLC

        Args:
            clear_mode(int):     Clear mode. 0: does not clear. 1: clear except latch device. 2: clear all.
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        if not (clear_mode == 0 or  clear_mode == 1 or clear_mode == 2):
            raise ValueError("clear_device must be 0, 1 or 2. 0: does not clear. 1: clear except latch device. 2: clear all.")
        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        command = 0x1001
        subcommand = 0x0000

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(mode, mode="short")
        request_data += self._encode_value(clear_mode, mode="byte")
        request_data += self._encode_value(0, mode="byte")
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def remote_stop(self):
        """ Stop remotely.

        """
        command = 0x1002
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(0x0001, mode="short") #fixed value
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def remote_pause(self, force_exec=False):
        """pause PLC remotely.

        Args:
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        command = 0x1003
        subcommand = 0x0000

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(mode, mode="short")
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def remote_latchclear(self):
        """Clear latch remotely.
        PLC must be stop when use this command.
        """

        command = 0x1005
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(0x0001, mode="short") #fixed value 
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        return None

    def remote_reset(self):
        """Reset remotely.
        PLC must be stop when use this command.
        
        """

        command = 0x1006
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(0x0001, mode="short") #fixed value
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        #set time out 1 seconds. Because remote reset may not return data
        try:
            recv_data = self._recv()
            self._check_cmdanswer(recv_data)
        except:
            pass
        return None

    def read_cputype(self):
        """Read CPU type

        Returns:
            CPU type(str):      CPU type
            CPU code(str):      CPU code (4 length number)

        """

        command = 0x0101
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        data_index = self._get_answerdata_index()
        cpu_name_length = 16
        if self.commtype == const.COMMTYPE_BINARY:
            cpu_type = recv_data[data_index:data_index+cpu_name_length].decode()
            cpu_type = cpu_type.replace("\x20", "")
            cpu_code = int.from_bytes(recv_data[data_index+cpu_name_length:], "little")
            cpu_code = format(cpu_code, "x").rjust(4, "0")
        else:
            cpu_type = recv_data[data_index:data_index+cpu_name_length].decode()
            cpu_type = cpu_type.replace("\x20", "")
            cpu_code = recv_data[data_index+cpu_name_length:].decode()
        return cpu_type, cpu_code

    def remote_unlock(self, password="", request_input=False):
        """Unlock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        if request_input:
            password = input("Please enter password\n")
        if password.isascii() is False:
            raise ValueError("password must be only ascii code")
        if self.plctype is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")


        command = 0x1630
        subcommand = 0x0000
        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(len(password), mode="short") 
        request_data += password.encode()

        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def remote_lock(self, password="", request_input=False):
        """Lock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        if request_input:
            password = input("Please enter password\n")
        if password.isascii() is False:
            raise ValueError("password must be only ascii code")
        if self.plctype is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")

        command = 0x1631
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(len(password), mode="short") 
        request_data += password.encode()

        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)
        return None

    def echo_test(self, send_data):
        """Do echo test.
        Send data and answer data should be same.

        Args:
            send_data(str):     send data to PLC

        Returns:
            answer_len(int):    answer data length from PLC
            answer_data(str):   answer data from PLC

        """
        if send_data.isascii() is False:
            raise ValueError("send_data must be only ascii code")
        if not ( 1 <= len(send_data) <= 960):
            raise ValueError("send_data length must be from 1 to 960")

        command = 0x0619
        subcommand = 0x0000

        request_data = bytes()
        request_data += self._make_commanddata(command, subcommand)
        request_data += self._encode_value(len(send_data), mode="short") 
        request_data += send_data.encode()

        send_data = self._make_senddata(request_data)

        #send mc data
        if self._DEBUG:
            return send_data   
        else:
            self._send(send_data)
        #reciev mc data
        recv_data = self._recv()
        self._check_cmdanswer(recv_data)

        data_index = self._get_answerdata_index()

        answer_len = self._decode_value(recv_data[data_index:data_index+self._wordsize], mode="short") 
        answer = recv_data[data_index+self._wordsize:].decode()
        return answer_len, answer