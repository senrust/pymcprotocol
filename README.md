# pymcprotocol
MC Protocol(MELSEC Communication Protocol) implementation by Python

## Installation 
```console 
pip install pymcprotocol
```

## Protocol type
Now, pymcprotocol supports only mcprotocol 3E type.
In the future, support 4E type. (And if possible, 1C~4C type too...)

## How to use mc protocol
### 1. Set up PLC
First, you need to set upopen your PLC port to communicate by mcprotocol in Gxworks2 or Gxworks3.  
- Open port you want to communicate.  
- Select "Communication Data Code". If you select ascii type, you also need to set "ascii" in setaccessopt method. (default is "bainary")
- If you would like to write in to PLC, you also have to check __Enable online change__

### 2. Connect by Python
```python
import pymcprotocol

#If you use Q series PLC
pymc3e = pymcprotocol.Type3E()
#if you use L series PLC,
pymc3e = pymcprotocol.Type3E(plctype="L")
#if you use iQ series PLC,
pymc3e = pymcprotocol.Type3E(plctype="iQ")

#If you use ascii byte communication, (Default is "binary")
pymc3e.setaccessopt(commtype="ascii")
pymc3e.connect("192.168.1.2", 1025)

```

### 3. Send command
```python
#read from D100 to D110
wordunits_values = pymc3e.batchread_wordunits(headdevice="D100", readsize=10)

#read from X10 to X20
bitunits_values = pymc3e.batchread_bitunits(headdevice="X10", readsize=10)

#write from D10 to D15
pymc3e.batchread_wordunits(headdevice="D10", values=[0, 10, 20, 30, 40])

#write from Y10 to Y15
pymc3e.batchread_bitunits(headdevice="Y10", values=[0, 1, 0, 1, 0])

#read "D1000", "D2000" and  dword "D3000".
word_values, dword_values = pymc3e.randomread(word_devices=["D1000", "D2000"], dword_devices=["D3000"])

#write 1000 to "D1000", 2000 to "D2000" and 655362 todword "D3000"
pymc3e.randomwrite(word_devices=["D1000", "D1002"], word_value=[1000, 2000], 
                   dword_devices=["D1004"], dword_values=[655362])

#write 1(ON) to "X0", 0(OFF) to "X10"
pymc3e.randomwrite_bitunits(bit_devices=["X0", "X10"], values=[1, 0])

pymc3e.close()
```

### API Reference
API reference is depoloyed on here.  
https://pymcprotocol.netlify.app/