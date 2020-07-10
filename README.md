# ncs2nss

ncs2nss is an open-source Python implementation of the DeNCS decompiler for Neverwinter Nights scripts (NWN, KOTOR, etc.)

## Installation
Either download the repository as a zip file, or clone it onto your local machine.

## Usage
ncs2nss is still in active (and very early) development. To test it out, run the following command from the base directory of the repository:

> python test_parser.py [NCS file]

If the decompilation was a success, you will find the file "decompiled.nss", which will (hopefully) contain the decompiled files.

## Known Issues and Limitations
This project is very new and there are bound to be bugs - in all honestly, it is more likely that a given .ncs file will not decompile correctly, than that it will. For simple scripts, it might work, but please be aware of the following known bugs and limitations:
 - ncs2nss is currently being written to read .ncs files either from the original compiler used during game development, or by nwnnsscomp.exe _with the --optimise flag NOT set_. There is no particular reason why the program cannot be extended to work with optimized code, but this will require some changes to how the data flow analysis is done. If you are finding this to be a limitation, please file an issue so I know to make this a higher priority.
 - Nested loops seem to work fine, but loops with multiple conditions combined with && or || do not work properly (I'm working on it...). Do-while loops and infinite loops also (probably) do not work; this is a bug, not a feature, but there's a clear roadmap for fixing it.
 - Break and continue statements not yet supported; also a high priority.
 - Vector support has been added (tenatively, with possible bugs).
 - Detecting structs is maybe possible due to a compiler artifact where it allocates all the space for a struct before setting values (rather than interleaving the creation and separation operations). I could add a feature which detects multiple spaces allocated in a row, and treats the resulting region of memory as a struct. This is a low priority as it does not affect compilability (only readability, which is still important but not as important as compilability).
 - ncs2nss is being developed for KOTOR and KOTOR 2 modding; it might work for other games but I make no guarantees. Hopefully I will be able to integrate much of my work with the xoreos-tools project, where others who are well-versed in the other games using NSS scripting can make it more compatible with other games. For now, it might or might not work (given you provide your own nwscript.nss file).
 - Switch statements are decompiled into if statements; this should be a relatively easy fix but it's not high on my list of priorities - some languages (\*cough\* Python \*cough\*) don't support switches to begin with so it's not like it's a dealbreaker.
 
## Licensing
This is currently a private repo, so while I do ask that you don't distribute copies/access to the code yet, please feel to take a look. I'll licence it properly (and fully open source) once it's made public.

This project would not be possible without the following tools, in no particular order:
 - xoreos-tools
 - nwnnsscomp.exe
 - rply (Python library for creating lexers and parsers)
 - original DeNCS
 - The NCS assembly reference at http://www.nynaeve.net/Skywing/nwn2/Documentation/ncs.html
 
 (TODO: insert appropriate open source license information for above tools where required)
