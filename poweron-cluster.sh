#!/bin/bash

source /home/jacint/.vcps

if [[ $# -eq 0 ]]
    then echo paramter: cluster1 or cluster2
else
    for i in `cat $1`; do ansible-playbook /home/jacint/ansible/vmware/poweron.yaml --extra-vars "vmname=$i password=$PS"; done
fi

