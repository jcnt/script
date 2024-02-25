#!/usr/bin/python3
#
#
#
# simple python script to kill a random K8s pod in every 10 seconds
# handy to see how deployments and replicasets working


import os
from random import choice
from time import sleep

to_kill = ""

def find_pod(): 
  global to_kill
  podlist = []
  pods = os.popen("kubectl get pods --no-headers|awk {'print $1'}").read()
  for i in pods.splitlines(): 
    podlist.append(i)
  to_kill = choice(podlist)

while True: 
  find_pod()
  print("\nKilling pod")
  os.system(f"kubectl delete pod {to_kill}")
  print("\nSleeping for 10sec...  hit ctrl+c to stop\n")
  sleep(10)


