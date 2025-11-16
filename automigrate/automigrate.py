#!/usr/bin/python3
#
# based on py-pure-client
# migrates a volume online from A to B array using ActiveWorkload in FlashArray
#
#

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
    print(f"Usage: {sys.argv[0]} <volname> <source array> <destination array>")
    quit()

VOL = sys.argv[1]
SRC = sys.argv[2].upper()
DST = sys.argv[3].upper()
POD = "jj-pod-" + time.strftime("%Y%m%d%H%M%S")
PODVOL = POD + "::" + VOL

src = flasharray.Client(SRC, api_token=tdb[SRC], verify_ssl=False)
dst = flasharray.Client(DST, api_token=tdb[DST], verify_ssl=False)

resp = src.get_connections(volume_names=[VOL])
HOST = list(resp.items)[0]["host"]["name"]

print(f"Migrating {VOL} from {fullname[SRC]} to {fullname[DST]}...")

pod = flasharray.PodPost()
resp = src.post_pods(pod=pod, names=[POD])
print("Creating Pod...", resp.status_code)

container = {"pod": {"name": POD}}
resp = src.patch_volumes(names=[VOL], volume=container)
print("Moving volume to Pod...", resp.status_code)

resp = src.post_pods_arrays(member_names=[fullname[DST]], group_names=[POD])
print("Adding Pod member...", resp.status_code)

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
    response = dst.post_connections(volume_names=[PODVOL], host_names=[HOST])
    resp = response.status_code

print("\nConnecting Vol on second array...", resp)

print()
print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")
print()
time.sleep(5)

resp = src.delete_connections(volume_names=[PODVOL], host_names=[HOST])
print("Removing host connection on source...", resp.status_code)

print()
print("Running rescan on iSCSI paths")
os.system("ssh rhel sudo iscsiadm -m session --rescan")
print()

resp = dst.delete_pods_members(pod_names=[POD], member_names=[fullname[SRC]])
print("Removing source array from pod...", resp.status_code)

container = {"pod": {"name": ""}}
resp = dst.patch_volumes(names=[PODVOL], volume=container)
print("Moving volume out of the Pod...", resp.status_code)

resp = src.delete_pods(names=[POD + ".restretch"])
print("Eradicate restretch Pod on source...", resp.status_code)

destroy = {"destroyed": True}
resp = dst.patch_pods(pod=destroy, names=[POD])
print("Destroy Pod on target...", resp.status_code)

resp = dst.delete_pods(names=[POD])
print("Eradicate Pod on target...", resp.status_code)

# todo:
# - make it work with hostgroup as well
