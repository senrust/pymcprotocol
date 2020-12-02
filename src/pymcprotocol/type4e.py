"""This file implements mcprotocol 4E type communication.
"""

import re
import socket
from . import mcprotocolerror
from . import mcprotocolconst as const
from .type3e import Type3E

class Type4E(Type3E):
    """mcprotocol 4E communication class.
    Type 4e is almost same to Type 3E. Difference is only subheader.
    So, Changed self.subhear and self._make_senddata()

    Arributes:
        subheader(int):         Subheader for mc protocol
        subheaderserial(int):   Subheader serial for mc protocol to identify client
    """
    subheader       = 0x54
    subheaderserial = 0X0000

    def set_subheaderserial(self, subheaderserial):
        """Change subheader serial

        Args:
            subheaderserial(int):   Subheader serial to change

        """
        if(0 <= subheaderserial <= 65535):
            self.subheaderserial = subheaderserial
        else:
            raise ValueError("subheaderserial must be 0 <= subheaderserial <= 65535") 
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
        if self.commtype == const.COMMTYPE_BINARY:
            mc_data += self.subheader.to_bytes(2, "little")
            mc_data += self.subheaderserial.to_bytes(2, "little")
            mc_data += self._zerovalue.to_bytes(2, "little")
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
            mc_data += format(self.subheaderserial, "x").rjust(4, "0").upper().encode()
            mc_data += format(self._zerovalue, "x").rjust(4, "0").upper().encode()
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
