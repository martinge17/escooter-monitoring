# Setup Scripts

This folder contains scripts designed to automate the setup of the Raspberry Pi as the client for the e-scooter monitoring system, including LTE connectivity and system services configuration. These scripts are compatible with Raspberry Pi OS.

## ⚙️ Install.sh 

The [install.sh](install.sh) script:
- **Adds the Debian testing repositories:** Needed for installing the latest version of the Python MQTT library (>2.0). It is neccesary at the moment of writing the guide while Raspberry Pi OS based on Debian 12.6.

- **Installs the required packages:**
    - `python3-paho-mqtt`:  A Python MQTT library for communication with the MQTT broker.
    - `python3-systemd:` A library to interact with systemd services from Python (used to manage the logs of the relay service).
    - `ibqmi-utils`: Utilities for handling Qualcomm LTE modems.
    - `udhcpc`: A lightweight DHCP client required to assign the default IP address and route.
    - `ifmetric`: A tool to set interface priorities (Wi-Fi over LTE).

- **Configures cron:** Adds the [LTE connection script](lte.sh) to the Raspberry Pi’s crontab, ensuring the LTE connection script is executed on boot.

- **Sets up systemd services:** The script installs and enables the required systemd services for the client and relay.

- **Reboots the Raspberry Pi:** After setup, the script reboots the Pi to apply all configurations and ensure the installed services are operational.

## 📶 lte.sh

The [lte.sh](lte.sh) script enables the 4G connection using a Qualcomm modem and sets network interface priorities:

- **Connects the 4G modem:** Using QMI to enable and establish a connection to the mobile network.

- **Prioritizes WIFI interface:** Ensures Wi-Fi is prioritized over 4G to minimize mobile data usage, this is especially useful for downloading updates when Wi-Fi is available (e.g. at home).


⚠️ **Note:** Make sure to properly configure the `lte.sh` script with your service provider APN settings before running the install script.

> **Why QMI?**
  It was the only method that worked for me to use both 4G internet and GPS location simultaneously.  

## 🚀 Installation guide

### Prerequisites

- You should have the Raspberry Pi set up with basic configuration (usernames and Wi-Fi), and ensure SSH access is available.

- ⚠️ The guide assumes you're using the `scooter` username. If you're using a different username, update the installation scripts and service files accordingly (names and paths).

- Ensure the Waveshare LTE modem is connected to the Raspberry Pi and powered on (at least one red LED should be on).


### Step-by-Step Installation

1. **Copy or clone the repository**: Copy or clone the repository to your Raspberry Pi. You can use Rsync or clone the repository directly in the `scooter` user’s home directory.

    Example of cloning:
    ```bash
    git clone https://github.com/martinge17/escooter-monitoring
    ```

2. **Download or copy the `m365` executable**: Either download the pre-compiled `m365` client or copy your own compiled version.

    ```bash
    wget https://github.com/martinge17/escooter-monitoring/releases/download/v1.0/m365_arm64_release -O $HOME/escooter-monitoring/raspberry/m365
    ```

3. **Set execution permissions** for the `m365` client and scripts (just in case):
    ```bash
    chmod +x $HOME/escooter-monitoring/raspberry/m365
    chmod +x $HOME/escooter-monitoring/raspberry/scripts/install.sh
    chmod +x $HOME/escooter-monitoring/raspberry/scripts/lte.sh
    ```

4. **(Optional) ⚠️ Modify the scripts and services:** In case you are using a user different than `scooter`.

5. **⚠️ Copy the configuration files:** Inside the `raspberry` folder (the same that contains the `m365` executable), copy the following configuration files:
    - `.mi-token` obtained [here](../../client/README.md#generating-the-mi-token-file)
    - [martinete.toml](../../client/README.md) config file filled out with all the parameters.

6. **Run the installation script**:
    ```bash
    sudo ./install.sh
    ```
    This will install the required packages, configure system services, and reboot the Raspberry Pi when finished.


### Verify Setup

Once the Raspberry Pi has rebooted, verify that everything is set up correctly:


- **Check if the services are running:**
```bash
sudo systemctl status scooter-client
sudo systemctl status scooter-relay
```

- **Confirm the 4G connection is working:**
```bash
# Check both Wi-Fi and 4G interfaces (wwan0) are active
ifconfig

# Verify the connection priority: wlan0 should have higher priority than wwan0
route -n

# Ensure you have an active internet connection through 4G:
curl --interface wwan0 https://ipinfo.io/ip
```

If everything is configured correctly, the Raspberry Pi will automatically connect to the scooter when powered on.


## 📚 Reference 

The LTE setup is based on [Jeff Geerling's blog post](https://www.jeffgeerling.com/blog/2022/using-4g-lte-wireless-modems-on-raspberry-pi), which details the process of setting up the 4G modem on a Raspberry Pi.