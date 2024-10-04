#!/bin/bash

# Ansi color code variables
red="\e[0;91m"
blue="\e[0;94m"
expand_bg="\e[K"
blue_bg="\e[0;104m${expand_bg}"
red_bg="\e[0;101m${expand_bg}"
green_bg="\e[0;102m${expand_bg}"
green="\e[0;92m"
white="\e[0;97m"
bold="\e[1m"
uline="\e[4m"
reset="\e[0m"

echo -e "${green}Adding Debian Testing repository${reset}"
# First add Debian testing repository, at the time of writing this guide it is required for installing dependencies such as python3-paho-mqtt

sudo cp /etc/apt/sources.list /etc/apt/sources.list.back

sudo sed -i 's/bookworm/testing/g' /etc/apt/sources.list

sudo apt update && sudo apt upgrade -y

echo -e "${green}Installing required packages${reset}"

# Now install nedded dependencies
sudo apt install -y python3-paho-mqtt python3-systemd libqmi-utils udhcpc ifmetric

echo -e "${green}Adding LTE script to crontab and running it!${reset}"

# Add lte.sh script to crontab
(crontab -l 2>/dev/null; echo "@reboot $HOME/escooter-monitoring/raspberry/scripts/lte.sh") | crontab -

# Run the script
/bin/bash $HOME/escooter-monitoring/raspberry/scripts/lte.sh

echo -e "${green}Installing and enabling the monitoring and relay services${reset}"

# Move the unit files and enable the client services
sudo cp $HOME/escooter-monitoring/raspberry/relay_mqtt_client/relay.service /etc/systemd/system/
sudo cp $HOME/escooter-monitoring/raspberry/escooter-monitoring.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable --now relay.service
sudo systemctl enable --now escooter-monitoring.service

echo -e "${green}Installation complete!, rebooting...${reset}"
sudo reboot -h now



