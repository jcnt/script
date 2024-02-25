#!/usr/bin/python3

import os

list = []

items = os.popen("ls -l|grep -v total").read()

for i in items.splitlines():
  list.append(i.split(" ")[8])

print(list)

