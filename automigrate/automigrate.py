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

fullname = {
    "FAA": "PureCZ-FA-A",
    "FAB": "PureCZ-FA-B",
    "X70A": "PureCZ-X70-A",
    "X70B": "PureCZ-X70-B",
}

if len(sys.argv) < 4:
    print(f"Usage: {sys.argv[0]} <volume name> <source array> <destination array>")
    quit()

VOL = sys.argv[1]
SRC = sys.argv[2].upper()
DST = sys.argv[3].upper()
POD = "jj-pod-" + time.strftime("%Y%m%d%H%M%S")
PODVOL = POD + "::" + VOL

src = flasharray.Client(SRC, api_token=tdb[SRC], verify_ssl=False)
dst = flasharray.Client(DST, api_token=tdb[DST], verify_ssl=False)

print(f"Migrating {VOL} from {fullname[SRC]} to {fullname[DST]}...")

pod = flasharray.PodPost()
response = src.post_pods(pod=pod, names=[POD])
print("Creating Pod...", response.status_code)

container = {"pod": {"name": POD}}
response = src.patch_volumes(names=[VOL], volume=container)
print("Moving volume to Pod...", response.status_code)

response = src.post_pods_arrays(member_names=[fullname[DST]], group_names=[POD])
print("Adding Pod member...", response.status_code)

resp = 400
print("waiting for pod sync", end="", flush=True)
while resp != 200:
    print(".", end="", flush=True)
    time.sleep(1)
    response = dst.get_volumes(names=[PODVOL])
    resp = response.status_code

resp = 400
while resp != 200:
    print(".", end="", flush=True)
    time.sleep(1)
    response = dst.post_connections(volume_names=[PODVOL], host_names=["jjRHEL"])
    resp = response.status_code

print("\nConnecting Vol on second array...", resp)

print()
print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")
print()
time.sleep(5)

response = src.delete_connections(volume_names=[PODVOL], host_names=["jjRHEL"])
print("Removing host connection on source...", response.status_code)

print()
print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")
print()

response = dst.delete_pods_members(pod_names=[POD], member_names=[fullname[SRC]])
print("Removing source array from pod...", response.status_code)

container = {"pod": {"name": ""}}
response = dst.patch_volumes(names=[PODVOL], volume=container)
print("Moving volume out of the Pod...", response.status_code)

response = src.delete_pods(names=[POD + ".restretch"])
print("Eradicate restretch Pod on source...", response.status_code)

destroy = {"destroyed": True}
response = dst.patch_pods(pod=destroy, names=[POD])
print("Destroy Pod on target...", response.status_code)

response = dst.delete_pods(names=[POD])
print("Eradicate Pod on target...", response.status_code)

# todo:
# - poll the source array for host connections into variable
