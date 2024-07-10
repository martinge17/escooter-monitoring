# LTE Connection Setup

COMPLETE DOCS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

I use QMI to connect to the modem

https://www.jeffgeerling.com/blog/2022/using-4g-lte-wireless-modems-on-raspberry-pi

https://superuser.com/questions/331720/how-do-i-set-the-priority-of-network-connections-in-ubuntu

Setup script for connecting to LTE at boot:

```bash
chmod +x lte.sh
crontab -e
@reboot /home/admin/lte.sh
```
