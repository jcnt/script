#!/bin/sh

wget https://dl.k8s.io/release/v1.32.0/bin/linux/amd64/kubectl -O /mnt/kubectl

while :; do 

    USED=`df |grep mnt | awk {'print $(NF-3)'}`
    SIZE=`df |grep mnt | awk {'print $(NF-4)'}`
    PCT=$(( USED * 100 / SIZE ))
    SEC=`date +%H%M%S`

    if [[ "$DEBUG" == "yes" ]]; then
        echo -n "Percentage:   "
        echo $PCT
        echo -n "Used:         "
        echo $USED
        echo -n "Size:         "
        echo $SIZE
        echo
    fi


    if [[ "$SIZE" -lt "10000000" ]]; then

        if [[ "$PCT" -lt "80" ]]; then
            cp /mnt/kubectl /mnt/kubectl.$SEC
            sync
        fi

    fi

    sync
    sleep 1

done
