# pymcprotocol
MC Protocol(MELSEC Communication Protocol) implementation by Python

## installation 
```console 
pip install pymcprotocol
```

## Protocol type
Now, pymcprotocol supports only mcprotocol 3E type.  
In the future, I`m going to support 4E type. (And if possible, 1C~4C type too...)

## How to use mc protocol
### 1. Set up PLC
First, you need to set upopen your PLC port to communicate by mcprotocol in Gxworks2 or Gxworks3.  
- Open port you want to communicate.  
- Select "Communication Data Code". If you select ascii type, you also need to set "ascii" in setprotocolopt method. (default is "bainary")
- If you would like to write in to PLC, you also have to check __Enable online change__

### 2. Connect by Python
```python
import pymcprotocol

pymc3e = pymcprotocol.Type3E()
```

### 3. Communicate
```python
pymc3e.connect("192.168.1.2", 1025)
#If you select ascii type communication
#pymc3e.setprotocolopt(commtype="ascii")

pymc3e.close()
```