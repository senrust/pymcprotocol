.. pymcprotocol documentation master file, created by
   sphinx-quickstart on Sun Nov 29 18:32:01 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================================
Welcome to pymcprotocol's documentation!
============================================

About pymcprotocol
==================================
pymcprotocol is MC Protocol(MELSEC Communication Protocol) implementation by Python.

Installation
==================================
.. code-block:: shell

   pip install pymcprotocol


Protocol type
==================================
Now, pymcprotocol supports only mcprotocol 3E type.
In the future, support 4E type. (And if possible, 1C~4C type too...)

How to use pymcprotocol
==================================

1. Set up PLC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You need to set upopen your PLC port to communicate by mcprotocol in Gxworks2 or Gxworks3.  

- Open port you want to communicate.  
- Select "Communication Data Code". If you select ascii type, you also need to set "ascii" in setaccessopt method. (default is "bainary")
- If you would like to write in to PLC, you also have to check __Enable online change__

2. Connect by Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

   import pymcprotocol

   #If you use Q series PLC
   pymc3e = pymcprotocol.Type3E()
   #if you use L series PLC,
   pymc3e = pymcprotocol.Type3E(plctype="L")
   #if you use iQ series PLC,
   pymc3e = pymcprotocol.Type3E(plctype="iQ")

   #If you use ascii byte communication. (default is "binary")
   pymc3e.setaccessopt(commtype="ascii")
   pymc3e.connect("192.168.1.2", 1025)

3. Send command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

   #read from D100 to D110
   pymc3e.batchread_wordunits(headdevice="D100", size=10)

   #read from X10 to X20
   pymc3e.batchread_bitunits(headdevice="X10", size=10)
   
   pymc3e.close()


.. toctree::
   :maxdepth: 2

   pymcprotocol



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
