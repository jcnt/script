#!/bin/bash

if [[ $# -eq 0 ]]
    then echo usage: ./upgrade-k8s.sh [cluster] [version, e.g 1.29.8]
    exit 1
fi

if [[ $1 == cluster1 ]]
    then 
        master=master1
        workers=workers1

elif [[ $1 == cluster2 ]]
    then 
        master=master2
        workers=workers2
fi

debver=`echo $2 | awk -F"." '{ print $1"."$2 }'`
cd ../ansible/k8s-upgrade/
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v$debver/deb/ /" > kubernetes-sources.list
echo "Updating sources.list"
ansible-playbook sources-copy.yaml -e "cluster=$1"
echo "Upgrading master."
ansible-playbook k8s-master.yaml -e "master=$master" -e "version=$2"
echo "Waiting for kube-system pods"
sleep 240
echo "Upgrading workers."
ansible-playbook k8s-workers.yaml -e "workers=$workers" -e "version=$2"
echo "Upgrade finished."
