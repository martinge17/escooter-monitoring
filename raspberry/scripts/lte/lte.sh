#!/bin/sh

sudo systemctl stop ModemManager
sudo qmicli -d /dev/cdc-wdm0 --dms-set-operating-mode='online'

# Set interface to raw_ip

sudo ip link set wwan0 down
echo 'Y' | sudo tee /sys/class/net/wwan0/qmi/raw_ip
sudo ip link set wwan0 up

sudo qmicli -d /dev/cdc-wdm0 --wda-get-data-format
# Connect 
sudo qmicli -p -d /dev/cdc-wdm0 --device-open-net='net-raw-ip|net-no-qos-header' --wds-start-network="apn='APN HERE',ip-type=4" --client-no-release-cid

# Get IP
sudo udhcpc -q -f -i wwan0

# Set priority

sudo ifmetric wwan0 700
