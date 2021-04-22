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
    subheader       = 0x5400
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

    def _get_answerdata_index(self):
        """Get answer data index from return data byte.
        4e type's data index is defferent from 3e type's.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 15
        else:
            return 30

    def _get_answerstatus_index(self):
        """Get command status index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 13
        else:
            return 26

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
        mc_data += self._encode_value(self.subheaderserial, "short")
        mc_data += self._encode_value(0, "short")
        mc_data += self._encode_value(self.network, "byte")
        mc_data += self._encode_value(self.pc, "byte")
        mc_data += self._encode_value(self.dest_moduleio, "short")
        mc_data += self._encode_value(self.dest_modulesta, "byte")
        #add self.timer size
        mc_data += self._encode_value(self._wordsize + len(requestdata), "short")
        mc_data += self._encode_value(self.timer, "short")
        mc_data += requestdata
        return mc_data

