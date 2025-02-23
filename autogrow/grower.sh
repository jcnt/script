#!/bin/sh

wget https://dl.k8s.io/release/v1.32.0/bin/linux/amd64/kubectl -O /mnt/kubectl

while :; do 

    USED=`df |grep mnt | awk {'print $3'}`
    SIZE=`df |grep mnt | awk {'print $2'}`
    PCT=$(( USED * 100 / SIZE ))
    SEC=`date +%H%M%S`

    echo $PCT
    echo $USED
    echo $SIZE
    echo

    if [[ "$SIZE" -lt "10000000" ]]; then

        if [[ "$PCT" -lt "80" ]]; then
            cp /mnt/kubectl /mnt/kubectl.$SEC
            sync
        fi

    fi

    sleep 1

done
