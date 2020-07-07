# dencs-py

dencs-py is an open-source Python implementation of the DeNCS decompiler for Neverwinter Nights scripts (NWN, KOTOR, etc.)

## Installation
Either download the repository as a zip file, or clone it onto your local machine.

## Usage
dencs-py is still in active (and very early) development. To test it out, run the following command from the base directory of the repository:

> python test_parser.py [NCS file]

If the decompilation was a success, you will find the file "decompiled.nss", which will (hopefully) contain the decompiled files.

## Known Issues and Limitations
This project is very new and there are bound to be bugs - in all honestly, it is more likely that a given .ncs file will not decompile correctly, than that it will. For simple scripts, it might work, but please be aware of the following known bugs and limitations:
 - dencs-py is currently being written to read .ncs files either from the original compiler used during game development, or by nwnnsscomp.exe _with the --optimise flag NOT set_. There is no particular reason why the program cannot be extended to work with optimized code, but this will require some changes to how the data flow analysis is done. If you are finding this to be a limitation, please file an issue so I know to make this a higher priority.
 - Nested loops currently don't work properly. Do-while loops and infinite loops also (probably) do not work; this is a bug, not a feature, and fixing this is a high priority.
 - Scripts which use structs are not guaranteed to work (dencs-py is blind to structs for now).
 - Vectors, structs, and any other NCS structure which requires more than one slot on the stack are not currently supported, but this is very high on my priority list.
 - Regarding structs in particular, it might be possible in some cases (due to compilers leaving artifacts indicating a variable belongs to a struct) to recover struct information but (I believe) it is not possible to recognize structs all the time because under the hood NCS has no notion of structs - it's all flattened out into variables.
 - dencs-py is being developed for KOTOR and KOTOR 2 modding; it might work for other games but I make no guarantees. Hopefully I will be able to integrate much of my work with the xoreos-tools project, where others who are well-versed in the other games using NSS scripting can make it more compatible with other games. For now, it might or might not work (given you provide your own nwscript.nss file).
 - Switch statements are decompiled into if statements; this should be a relatively easy fix but it's not high on my list of priorities because the original NSS compiler did not properly implement short circuiting anyway, so switch statements were basically if statements under the hood.

## Licensing
This is currently a private repo, so while I do ask that you don't distribute copies/access to the code yet, please feel to take a look. I'll licence it properly (and fully open source) once it's made public.

This project would not be possible without the following tools, in no particular order:
 - xoreos-tools
 - nwnnsscomp.exe
 - rply (Python library for creating lexers and parsers)
 - original DeNCS
 - The NCS assembly reference at http://www.nynaeve.net/Skywing/nwn2/Documentation/ncs.html
 
 (TODO: insert appropriate open source license information for above tools where required)
