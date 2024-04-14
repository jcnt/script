#!/bin/sh

# refresh dotrc
rm -rf /home/jacint/git/dotrc
/usr/bin/git clone https://github.com/jcnt/dotrc
mv dotrc /home/jacint/git/
chown -R jacint:jacint /home/jacint/git/dotrc

# get IP
IP="`grep $1 /etc/hosts |awk {'print $1'}`"

# setup interfaces
sed s/IPCOMESHERE/$IP/ /root/interfaces > /etc/network/interfaces

# setup hostname
echo $1 > /etc/hostname

# rekey sshd
rm /etc/ssh/*key*
/usr/sbin/dpkg-reconfigure openssh-server

rm tempinit.sh
rm interfaces

# reboot
/usr/sbin/reboot


