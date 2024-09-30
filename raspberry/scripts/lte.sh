#!/bin/sh

# I'm using QMI to connect to the modem. More on that here: https://www.jeffgeerling.com/blog/2022/using-4g-lte-wireless-modems-on-raspberry-pi
# The priority is modified, so the WIFI connection has priority over the LTE: https://superuser.com/questions/331720/how-do-i-set-the-priority-of-network-connections-in-ubuntu

sudo systemctl stop ModemManager
sudo qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'

# Set interface to raw_ip

sudo ip link set wwan0 down
echo 'Y' | sudo tee /sys/class/net/wwan0/qmi/raw_ip
sudo ip link set wwan0 up

sudo qmicli -d /dev/cdc-wdm0 --wda-get-data-format
# Connect MAKE SURE TO ADD YOUR APN HERE
sudo qmicli -p -d /dev/cdc-wdm0 --device-open-net='net-raw-ip|net-no-qos-header' --wds-start-network="apn='APN HERE',ip-type=4" --client-no-release-cid

# Get IP
sudo udhcpc -q -f -i wwan0

# Set priority

sudo ifmetric wwan0 700