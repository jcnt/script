#!/bin/bash

if [[ $# -eq 0 ]]
    then echo paramter: cluster1 or cluster2
    exit 1
fi

if [[ $1 == cluster1 ]]
    then 
        master=jjmaster
        workers="jjkw11 jjkw12 jjkw13 jjkw14"
	    podcidr=10.77.1.0/24
	    svccidr=10.78.1.0/24

elif [[ $1 == cluster2 ]]
    then 
	    master=jjmastdr
        workers="jjkw21 jjkw22 jjkw23 jjkw24"
	    podcidr=10.77.2.0/24
	    svccidr=10.78.2.0/24
fi

./template-clone.sh $1
./poweron-cluster.sh $1
echo "sleeping for 30 sec, VMs coming up, re-IP, SSH re-key"
sleep 30
./finalize_cluster.sh $1
cd ../ansible/k8slab-init/
ansible-playbook init-k8s.yaml --extra-vars "cluster=$1"
ansible-playbook init-containerd.yaml --extra-vars "cluster=$1"
ansible-playbook init-kubeadm.yaml --extra-vars "cluster=$1"
ssh $master sudo kubeadm init --pod-network-cidr $podcidr --service-cidr $svccidr
ansible-playbook jump-get-kube-config.yaml --extra-vars "master=$master"
mv /tmp/$master/etc/kubernetes/admin.conf /home/jacint/.kube/config.$1
cp /home/jacint/.kube/config.$1 /home/jacint/.kube/config
kubectl apply -f flannel-$1.yaml

TOKEN=`ssh $master sudo kubeadm token list |grep "kubeadm init" |awk '{print $1}'`
for i in `echo $workers`;do ssh $i sudo kubeadm join $master:6443 --token $TOKEN --discovery-token-unsafe-skip-ca-verification; done
ansible-playbook distribute-kube-config.yaml --extra-vars "cluster=$1"

if [[ $1 == cluster1 ]]
    then
        for i in `echo $workers`;do kubectl patch node $i -p '{"spec":{"podCIDR":"10.77.1.0/24"}}'; done
elif [[ $1 == cluster2 ]]
    then
        for i in `echo $workers`;do kubectl patch node $i -p '{"spec":{"podCIDR":"10.77.2.0/24"}}'; done
fi

