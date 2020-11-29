"""This file is collection of mcprotocol error.
First, define error constant. 
Next, define Exception classes for each error.
At last, define exception raiser.
"""

RAT_ERROR = 10

class CommEroor(Exception):
    pass
    
class MCProtocolError():
    
    @staticmethod
    def RaiseMCProtocolError(error_code):
        if error_code is RAT_ERROR:
            raise CommEroor()

        