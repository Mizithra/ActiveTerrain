from pathlib import Path
def write_header(gen,name,data):
    with open(gen / f"{name}.h", "w") as f:
        f.write("#pragma once\n#include <Arduino.h>\nconst uint8_t " + name + "Icon[] PROGMEM={\n")
        for i, b in enumerate(data):
            if i % 12 == 0:
                f.write(" ")
            f.write(f"0x{b:02X},")
            if i % 12 == 11:
                f.write("\n")
        f.write("\n};")
            
            
def write_icons(gen,icons):
    with open(gen / "icons.h", "w") as h, open(gen / "icons.cpp", "w") as cpp:
        h.write("#pragma once\n")
        for n, _ in icons:
            h.write(f'#include "{n}.h"\n')
        h.write("\nenum class Faction{\n")
        h.write(",\n".join([n.capitalize() for n, _ in icons]))
        h.write("\n};\nconst uint8_t* getFactionBitmap(Faction);\nconst char* getFactionName(Faction);")

        cpp.write('#include "icons.h"\n')
        cpp.write("const uint8_t* getFactionBitmap(Faction f){switch(f){")
        for n, _ in icons:
            cpp.write(f"case Faction::{n.capitalize()}:return {n}Icon;")
        cpp.write("default:return nullptr;}}\n")

        cpp.write("const char* getFactionName(Faction f){switch(f){")
        for n, d in icons:
            cpp.write(f'case Faction::{n.capitalize()}:return "{d}";')
        cpp.write('default:return "";}}')
