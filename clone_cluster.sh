#!/bin/bash

source /home/jacint/.vcps

if [[ $# -eq 0 ]]
    then echo paramter: cluster1 or cluster2
else
    for i in `cat $1`; 
        do ip=`grep $i /etc/hosts |awk '{print $1}'`;
        ansible-playbook /home/jacint/ansible/vmware/clone-vm.yaml --extra-vars "vmname=$i ipaddress=$ip password=$PS "; 
    done
fi


