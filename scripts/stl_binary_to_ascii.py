from pathlib import Path
from struct import unpack as u
from sys import argv

d = Path(argv[1]).read_bytes()  # '/tmp/Neat Wolt-Vihelmo.stl'

o = "solid "
for x in range(80):
    if d[x] != 0:
        o += chr(d[x])
o += "\n"

num_faces = u('I', d[80:84])[0]
for x in range(num_faces):
    b = 84 + x * 50
    o += f"facet normal {u('f', d[b:b + 4])[0]} {u('f', d[b + 4:b + 8])[0]} {u('f', d[b + 8:b + 12])[0]}\n"
    o += "outer loop\n"
    for y in range(1, 4):
        v = b + y * 12
        o += f"vertex {u('f', d[v:v + 4])[0]} {u('f', d[v + 4:v + 8])[0]} {u('f', d[v + 8:v + 12])[0]}\n"
    o += "endloop\n"
    o += "endfacet\n"

Path(argv[2]).write_text(o)  # '/tmp/ASCII.stl'
