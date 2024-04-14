#!/bin/bash

if [[ $# -eq 0 ]]
    then echo paramter: cluster1 or cluster2
else
    for i in `cat $1`; do ansible-playbook .poweron.yaml --extra-vars "vmname=$i"; done
fi

