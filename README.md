# ncs2nss

ncs2nss is an open-source Python implementation of the DeNCS decompiler for Neverwinter Nights scripts (NWN, KOTOR, etc.)

## Goals
There are a few goals underpinning this project:
 - Create a new, open-source implementation of DeNCS which can be maintained by the community
 - Provide a demonstration of a working NCS decompiler for the xoreos-tools team, so they can hook into my implementation if they want (or rewrite it in C++ if they prefer)
 - (My own goal) learn about decompilation theory, and hopefully use this tool as an example for others who might wish to implement a simple decompiler (my end goal here is to create a YouTube video series on decompilation)

## Requirements
This decompiler is implemented in Python (written for Python 3.7 and I do recommend that you use 3.7+ because I sometimes rely on newer Python features in my code). It might work fine with earlier versions, but I make no guarantees. Once I make a public release of an alpha version, I'll make a .exe file to simplify installation.

## Installation
Either download the repository as a zip file, or clone it onto your local machine.

## Usage
ncs2nss is still in active development. To test it out, run the following command from the base directory of the repository:

> python ncs2nss.py [NCS file]

If the decompilation was a success, you will find the file "decompiled.nss", which will (hopefully) contain the decompiled code.

## Known Issues and Limitations
This project is very new and there are bound to be bugs. For simple files, it seems to work with no issues - but for complex files it can struggle to decompile completely correctly.

Please be aware of the following known bugs and limitations:
 
### Known Bug/Missing Features List
 - Sometimes return statements are duplicated
 - Determining switch vs if statements is non-trivial and might not always work
 - Global parsing takes longer than it should.
 - Do loops aren't currently working properly, though I'm working on it
 - I need to improve the argument detection algorithm.
 - Some blocks of code are not being written, so it seems some of the control flow logic is incorrect.
 - Break and continue statements not yet supported; also a high priority.
 - Currently, we rely on the control flow analysis by xoreos-tools's "ncsdis" tool to identify subroutine signatures. Their implementation works very well most of the time, but it does not work on recursive functions. I have some ideas about this, and plan to discuss it with them. For now, if ncsdis can't analyze the control flow, I have heuristics to try to figure the function signatures out but the computed signatures have a high chance of being incorrect. This can cause ripple effects and errors througout the rest of the decompiled code as well.
 - I am working on a side project which will scan the NCS code for library functions (functions which match a function included in the NSS files that come with a particular game) and use those functions from the library rather than decompiling them from scratch. This will make decompilation both quicker and more accurate, but it's not simple to implement. I'll have it before the official release, though.
 
### Known "Not-A-Bug" List
 - Decompilation can seem to take significantly longer than DeNCS does - however, this is because of all the debug information being written to disk (including control flow diagrams and stack diagrams). Before release, I will add some features to control debug output (defaulting to off, making the program run with speed similar to DeNCS).
 - There's no GUI yet, but I'm going to add this before release too. For now, it's command-line only.
 - ncs2nss is currently being written to read .ncs files either from the original compiler used during game development, or by nwnnsscomp.exe _with the --optimise flag NOT set_. There is no particular reason why the program cannot be extended to work with optimized code, except that it will require more edge-case detection and code complexity. If you are finding this to be a limitation, please file an issue so I know to make this a higher priority.
 - Structs are ignored (except for float vectors, which are detected and treated specially). This should not be an issue as I'm not aware of any code which takes structs as arguments (or returns them), but if I'm wrong please log an issue so I can make fixing this a priority.
 - ncs2nss is being developed for KOTOR and KOTOR 2 modding; it might work for other games but I make no guarantees. Hopefully I will be able to integrate much of my work with the xoreos-tools project, where others who are well-versed in the other games using NSS scripting can make it more compatible with other games. For now, it might or might not work (given you provide your own nwscript.nss file).
 
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

However, "relatively simple" isn't the same as "simple", and there are still significant challenges which have to be overcome to implement a complete decompiler for NCS code:
 - Different compilers have different idioms, and earlier compilers (even the original ones created by game developers) contain bugs and implementation differences which must be reconcilled within the decompiler. Of course, they fixed those bugs in the later versions (which makes our job even harder as we can't just hard-code the bugs into our decompiler).
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
