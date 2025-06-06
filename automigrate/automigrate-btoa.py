#!/usr/bin/python3

import os
import sys
import time

import urllib3
from pypureclient import flasharray

urllib3.disable_warnings()

tdb = {}

with open("/home/jacint/.fatoken") as token:
    lines = token.readlines()

for line in lines:
    ll = line.strip().split("=")
    tdb[ll[0]] = ll[1]

x70a = flasharray.Client("10.206.205.33", api_token=tdb["X70A"], verify_ssl=False)
x70b = flasharray.Client("10.206.205.36", api_token=tdb["X70B"], verify_ssl=False)
faa = flasharray.Client("10.206.205.23", api_token=tdb["FAA"], verify_ssl=False)
fab = flasharray.Client("10.206.205.26", api_token=tdb["FAB"], verify_ssl=False)

# if len(sys.argv) < 4:
#     print(f"Usage: {sys.argv[0]} <volume name> <source> <destination>")
#     quit()
# else:
#     SRC = sys.argv[2]
#     DST = sys.argv[3]
#     VOL = sys.argv[1]

VOL = "jj-automigrate"

# print(f"Migrating {VOL} from {SRC} to {DST}...")
print(f"Migrating jj-automigrate from FAB to FAA...")

POD = "jj-pod-" + time.strftime("%Y%m%d%H%M%S")

pod = flasharray.PodPost()
response = fab.post_pods(pod=pod, names=[POD])
print("Creating Pod...", response.status_code)

container = {"pod": {"name": POD}}
response = fab.patch_volumes(names=[VOL], volume=container)
print("Moving volume to Pod...", response.status_code)

response = fab.post_pods_arrays(member_names=["PureCZ-FA-A"], group_names=[POD])
print("Adding Pod member...", response.status_code)

podvol = POD + "::" + VOL
response = faa.get_volumes(names=[podvol])

print("waiting for pod sync", end="", flush=True)
while response.status_code == 400:
    print(".", end="", flush=True)
    time.sleep(1)
    response = faa.get_volumes(names=[podvol])


resp = 400
while resp != 200:
    print(".", end="", flush=True)
    time.sleep(1)
    response = faa.post_connections(volume_names=[podvol], host_names=["jjRHEL"])
    resp = response.status_code

print("\nConnecting Vol on second array...", resp)

print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")
time.sleep(5)

response = fab.delete_connections(volume_names=[podvol], host_names=["jjRHEL"])
print("Removing host connection on source...", response.status_code)

print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")

response = faa.delete_pods_members(pod_names=[POD], member_names=["PureCZ-FA-B"])
print("Removing source from pod...", response.status_code)

container = {"pod": {"name": ""}}
response = faa.patch_volumes(names=[podvol], volume=container)
print("Moving volume out from the Pod...", response.status_code)

# response = fab.delete_pods(names=[POD])
# print("Deleting Pod on source...", response.status_code)
