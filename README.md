# dencs-py

dencs-py is an open-source Python implementation of the DeNCS decompiler for Neverwinter Nights scripts (NWN, KOTOR, etc.)

## Installation
Either download the repository as a zip file, or clone it onto your local machine.

## Usage
dencs-py is still in active (and very early) development. To test it out, run the following command from the base directory of the repository:

> python test_parser.py [NCS file]

If the decompilation was a success, you will find the file "decompiled.nss", which will (hopefully) contain the decompiled files.

## Licensing
This is currently a private repo, so while I do ask that you don't distribute copies/access to the code yet, please feel to take a look. I'll licence it properly (and fully open source) once it's made public.

This project would not be possible without the following tools:
 - xoreos-tools
 - nwnnsscomp.exe
 - rply (Python library for creating lexers and parsers)
 - original DeNCS
 
 (TODO: insert appropriate open source license information for above tools where required)
