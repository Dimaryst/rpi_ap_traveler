# RPi AP Traveler
  AP Traveler for RPi. Use this web app to configure your RPi as AP Bridge with WireGuard. 

## Setup

Update your RPi and install packages (also you need to configure 'raspi-config' wlan settings)
```
  sudo raspi-config
  sudo apt-get update
  sudo apt-get install mitmproxy
  sudo apt-get install python3-pip
  sudo pip3 install flask
  sudo pip3 install flask-restful
  sudo ./install_rtl_driver.sh
  sudo reboot now
```

Connect to Pi_Traveler Hotspot with 'raspberry' password
```
  ssh pi@192.168.26.1
```

Update rc.local
```
  sudo nano /etc/rc.local
```

Insert before "exit 0"
```
  sudo ./home/pi/rpi_ap_traveler/configure_iptables.sh
  sudo mitmweb --mode transparent --showhost &
  sudo python3 /home/pi/rpi_ap_traveler/app.py &
```  
  
Reboot RPi and connect 192.168.26.1:5000
