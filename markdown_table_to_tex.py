#!/usr/bin/env python
# convert markdown table to latex table

import os
import sys

try:
    # Take filename as first argument
    table_file = sys.argv[1]
except IndexError:
    # Clear the console
    os.system('clear')
    print("#####################################################################")
    print("#                             Markdown table to Tex                 #")
    print("####################################################################\n")
    print("[*] ERROR: Please provide a file containing the table to be uniqued \
        and sorted!\n".replace('    ', ''))
    print ("Example: ./markdown_table_to_tex.py table.txt")
    print("Example table:")
    print("| column1(url) | column2(txt) |")
    print("|https://foo.com | we owned this |")
    print("|http://leaked.online | wtf |")
    sys.exit()

# Read in all lined from user specified file
with open(table_file, 'r') as open_file:
    mylines = open_file.readlines()

# Convert to a set to remove duplicates, then convert to list
mylines_list = list(set(mylines))

mylines_list.sort()
for i in range(2,len(mylines_list)):
    mylines_list[i] = mylines_list[i].replace(" ", "")
    mylines_list[i] = mylines_list[i].replace("|", "\\url{",1)
    mylines_list[i] = mylines_list[i].replace("|", "} & ",1)
    mylines_list[i] = mylines_list[i].replace("|", "\\\\",1)
    print (mylines_list[i].strip())
    print ("\\hline")


