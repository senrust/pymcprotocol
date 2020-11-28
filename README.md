# pymcprotocol
MC Protocol(MELSEC Communication Protocol) implementation by Python

## installation 
```console 
pip install pymcprotocol
```

## Protocol type
Now, pymcprotocol supports mc only mcprotocol 3E binary type.  
In the future, I`m going to support 4E type. (And if possible, 1C~4C type also.)]

## How to use mc protocol
### 1. Set up PLC
First, you need to set upopen your PLC port to communicate by mcprotocol in Gxworks2 or Gxworks3.  
- Open port you want to communicate.  
- Select communication Data Code __Binary Code__
- If you would like to write in to PLC, you also have to check __Enable online change__

### 2. Connect by Python
```python
from pymcprotocol import Type3E

pyplc = Type3E(ip="192.168.1.2", port=1025)
```

### 3. Communicate
```python

```