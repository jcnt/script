#!/usr/bin/python3
#
#
#
# simple python script to kill a random K8s pod in every 10 seconds
# handy to see how deployments and replicasets working

import os
import random
import time


def find_pod():
    podlist = []
    pods = os.popen("kubectl get pods --no-headers").read()
    for i in pods.splitlines():
        podlist.append(i.split(" ")[0])
    return random.choice(podlist)


while True:
    to_kill = find_pod()
    print("\nKilling pod")
    os.system(f"kubectl delete pod {to_kill}")
    print("\nSleeping for 10sec...  hit ctrl+c to stop\n")
    time.sleep(10)
