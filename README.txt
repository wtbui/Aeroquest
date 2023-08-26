README

BEFORE USE:
Before using, use Quest-prep tool to generate a database file and OpenVSP to generate geometry(s) 
If running for slice data, write a .cuts file to specify cut locations along geometry

NOTE: File paths can only currently be specified within the source code

HOW TO USE:
In terminal use command:

"python3 Aeroquest.py <flags> <mesh number (1-3)> <-slice (IF USING SLICE)>"

Aeroquest Flags:
-h: Help Menu
-ws: Runs full Aeroquest wrapper, to run for slice data add -slice

Debug Flags:
-w: Write .VSPAero Files
-d: Delete .VSPAero Files
-s: Runs VSPAero Solver
-test: Runs test code block

TESTCASES:
Included in this folder are 4 test cases (containing 3 levels of meshes). 
Test cases labeled "Coarse" are debug meshes

KNOWN ISSUES:
- File paths can only be specified within source code at the top 
- When writing .cuts file, do not use locations that will generate duplicate points (Such as y=0 on a wing)
- When slicing thick geometries, upper edge must have negative z values
- Can not handle slice data on geometries with multiple curves