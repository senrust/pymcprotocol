# pymcprotocol
MC protocol(MELSEC Communication Protocol) implementation by Python.  
MC protocol enables you to operate PLC from computer.

## Installation 
```console 
pip install pymcprotocol
```

## Protocol type
pymcprotocol supports only mcprotocol 3E type and test by QPLC.  
4E type is implemented. But not tested.  
1C~4C type is not suuported.  

## Support PLC series
- Q Series
- L Series
- QnA Series
- iQ-L Series
- iQ-R Series

A and FX series are not supportted because they does not support 3E or 4E type.

## How to use mc protocol 
### 1. Set up PLC
You need to open PLC's port for mcprotocol by GxWorks2 or GxWorks3 software.  
1. Set IP address for PLC
2. Open TCP port of PLC
3. Set the port for mcprotocol.
4. Restart PLC

This page will help you.  
English: https://www.faweb.net/en/product/opc/plc/melsec/plc  
Japanese: https://qiita.com/satosisotas/items/38f64c872d161b612071  

#### Note: 
- If you select ascii type communiation,  
you also need to set "ascii" mode in setaccessopt method. (default is "bainary" mode)  
- If you would like to write data in PLC, you have to enable online change  

### 2. Connect by Python
```python
import pymcprotocol

#If you use Q series PLC
pymc3e = pymcprotocol.Type3E()
#if you use L series PLC,
pymc3e = pymcprotocol.Type3E(plctype="L")
#if you use QnA series PLC,
pymc3e = pymcprotocol.Type3E(plctype="QnA")
#if you use iQ-L series PLC,
pymc3e = pymcprotocol.Type3E(plctype="iQ-L")
#if you use iQ-R series PLC,
pymc3e = pymcprotocol.Type3E(plctype="iQ-R")

#If you use 4E type
pymc4e = pymcprotocol.Type4E()

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
pymc3e.batchwrite_wordunits(headdevice="D10", values=[0, 10, 20, 30, 40])

#write from Y10 to Y15
pymc3e.batchwrite_bitunits(headdevice="Y10", values=[0, 1, 0, 1, 0])

#read "D1000", "D2000" and  dword "D3000".
word_values, dword_values = pymc3e.randomread(word_devices=["D1000", "D2000"], dword_devices=["D3000"])

#write 1000 to "D1000", 2000 to "D2000" and 655362 todword "D3000"
pymc3e.randomwrite(word_devices=["D1000", "D1002"], word_values=[1000, 2000], 
                   dword_devices=["D1004"], dword_values=[655362])

#write 1(ON) to "X0", 0(OFF) to "X10"
pymc3e.randomwrite_bitunits(bit_devices=["X0", "X10"], values=[1, 0])

```

### 4.  Unlock and lock PLC
```python

#Unlock PLC,
#If you set PLC to locked, you need to unlkock to remote operation
#Except iQ-R, password is 4 character.
pymc3e.remote_unlock(password="1234")
#If you want to hide password from program
#You can enter passwrod directly
pymc3e.remote_unlock(request_input=True)

#Lock PLC
pymc3e.remote_lock(password="1234")
pymc3e.remote_lock(request_input=True)
```

### 5. Remote Operation
If you connect to your system by E71 module, Ethernet communication module,  
These commands are available.  

If you connect to PLC directly, C059 error returns.

```python

#remote run, clear all device
pymc3e.remote_run(clear_mode=2, force_exec=True)

#remote stop
pymc3e.remote_stop()

#remote latch clear. (have to PLC be stopped)
pymc3e.remote_latchclear()

#remote pause
pymc3e.remote_pause(force_exec=False)

#remote reset
pymc3e.remote_reset()

#read PLC type
cpu_type, cpu_code = pymc3e.read_cputype()

```

### API Reference
API manual is here.  
https://pymcprotocol.netlify.app/

### Lisence 
pymcprotocol is Released under the MIT license.

### Caution
pymcprotocol does not support entire MC protocol since it is very complicated and troublesome.  
If you would like to use unsupported function, please make Github issue.  
