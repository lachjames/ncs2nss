# ncs2nss

ncs2nss is an open-source Python implementation of the DeNCS decompiler for Neverwinter Nights scripts (NWN, KOTOR, etc.)

## Goals
There are a few goals underpinning this project:
 - Create a new, open-source implementation of DeNCS which can be maintained by the community
 - Provide a demonstration of a working NCS decompiler for the xoreos-tools team, so they can hook into my implementation if they want (or rewrite it in C++ if they prefer)
 - (My own goal) learn about decompilation theory, and hopefully use this tool as an example for others who might wish to implement a simple decompiler (my end goal here is to create a YouTube video series on decompilation)

## Requirements
This decompiler is implemented in Python (written for Python 3.7 and I do recommend that you use 3.7+ because I sometimes rely on newer Python features in my code). It might work fine with earlier versions, but I make no guarantees.

## Installation
Either download the repository as a zip file, or clone it onto your local machine.

## Usage
ncs2nss is still in active (and very early) development. To test it out, run the following command from the base directory of the repository:

> python test_parser.py [NCS file]

If the decompilation was a success, you will find the file "decompiled.nss", which will (hopefully) contain the decompiled files.

## Known Issues and Limitations
This project is very new and there are bound to be bugs - in all honestly, it is more likely that a given .ncs file will not decompile completely correctly, than that it will. For simple scripts ncs2nss might work perfectly, but please be aware of the following known bugs and limitations:
 - ncs2nss is currently being written to read .ncs files either from the original compiler used during game development, or by nwnnsscomp.exe _with the --optimise flag NOT set_. There is no particular reason why the program cannot be extended to work with optimized code, but this will require some changes to how the data flow analysis is done. If you are finding this to be a limitation, please file an issue so I know to make this a higher priority.
 - Nested loops seem to work fine, but loops with multiple conditions combined with && or || do not work properly (I'm working on it...). Do-while loops and infinite loops also (probably) do not work; this is a bug, not a feature, but there's a clear roadmap for fixing it.
 - Break and continue statements not yet supported; also a high priority.
 - Vector support has been added (tenatively, with possible bugs).
 - Detecting structs is maybe possible due to a compiler artifact where it allocates all the space for a struct before setting values (rather than interleaving the creation and separation operations). I could add a feature which detects multiple spaces allocated in a row, and treats the resulting region of memory as a struct. This is a low priority as it does not affect compilability (only readability, which is still important but not as important as compilability).
 - ncs2nss is being developed for KOTOR and KOTOR 2 modding; it might work for other games but I make no guarantees. Hopefully I will be able to integrate much of my work with the xoreos-tools project, where others who are well-versed in the other games using NSS scripting can make it more compatible with other games. For now, it might or might not work (given you provide your own nwscript.nss file).
 - Switch statements are decompiled into if statements; this should be a relatively easy fix but it's not high on my list of priorities - some languages (\*cough\* Python \*cough\*) don't support switches to begin with so it's not like it's a dealbreaker.
 
## Background
This project is mainly based on algorithms developed by Cristina Cifuentes for her 1994 thesis "Reverse Decompilation Techniques" (and the subsequent papers spawned from this thesis). Much of the thesis, as well as other literature in the field, focuses on difficult decompilation cases arising from things like:
 - Obfuscation, or where the assembly code is purposefully made harder to read or decompile by the original author
 - Non-structured assembly, where (for example) goto statements or compiler optimisations have been used in a way which makes the control flow graph non-structured (see https://en.wikipedia.org/wiki/Control-flow_graph for more info)
 - Register tracing, which adds another dimension to data flow analysis

With this in mind, we can see that NCS code is a relatively nice assembly language to decompile for several reasons:
 - The original NCS compiler was not obfuscated (to any degree I can see, at least), and there already exist open-source compilers for compiling to NCS assembly.
 - Both the original NCS compiler and the community-created compilers are relatively straightforward, and do not significantly optimize the code (as it is not really complex enough to require it in the majority of cases).
 - NSS has no "goto" statement and a fairly limited set of control structures, meaning that (barring compiler optimisations/bugs) 
 - NCS code does not use registers; it is a stack-only assembly language. This simplifies data flow analysis quite a bit, because we only need to trace variables on the stack.

"Relatively simple" does not mean "simple" though, and there are still significant challenges which have to be overcome to implement a complete decompiler for NCS code:
 - Different compilers have different idioms, and earlier compilers (even the original ones created by game developers) contain bugs and implementation differences which must be reconcilled within the decompiler
 - Capturing all the edge cases of decompilation is quite difficult, because even one error in a massive script can break the entire thing.
 - Similarly, one error in (e.g.) the stack analysis can propagate through the entire codebase, causing massive issues. So the decompiler has to be airtight in many difficult ways.
 
I'm doing my best to fix all the bugs and issues with the decompiler, but I'd certainly be very open to others who might be willing to contribute to the project. Feel free to file an issue or pull request if you want to contribute.
 
## Acknowledgements
I have decompiled the original (Java) DeNCS, and found the lexing/parsing information useful (though I reimplemented it myself in Python using a different library). I do not believe I have "stolen" any code from DeNCS in any way, but I want to be upfront about this to be safe.
 
## Licensing
This is currently a private repo, so while I do ask that you don't distribute copies/access to the code yet, please feel to take a look. I'll licence it properly (and fully open source) once it's made public.

This project would not be possible without the following tools, in no particular order:
 - xoreos-tools
 - nwnnsscomp.exe
 - rply (Python library for creating lexers and parsers)
 - original DeNCS
 - The NCS assembly reference at http://www.nynaeve.net/Skywing/nwn2/Documentation/ncs.html
 
 (TODO: insert appropriate open source license information for above tools where required)
