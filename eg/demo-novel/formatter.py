import sys

for line in sys.stdin:
    l = line.strip()
    l = l.replace('_', ' ')
    if l:
       sys.stdout.write("{}  ".format(l))
    else:
       sys.stdout.write("\n\n")
