#!/bin/sh
# install drivers for wlan1 usb 
apt-get update
apt-get full-upgrade
cd ../..
mkdir Driver_RTL8812AU
cd Driver_RTL8812AU
apt install git dkms
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
echo 'MAKE'
make dkms_install


# deinstall classic networking
systemctl daemon-reload
systemctl disable --now ifupdown dhcpcd dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
apt --autoremove purge ifupdown dhcpcd dhcpcd5 isc-dhcp-client isc-dhcp-common rsyslog
rm -r /etc/network /etc/dhcp

# setup/enable systemd-resolved and systemd-networkd
systemctl disable --now avahi-daemon libnss-mdns
apt --autoremove purge avahi-daemon
apt install libnss-resolve -y
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
apt-mark hold avahi-daemon dhcpcd dhcpcd5 ifupdown isc-dhcp-client isc-dhcp-common libnss-mdns openresolv raspberrypi-net-mods rsyslog
systemctl enable systemd-networkd.service systemd-resolved.service

# configure wpa_supplicant-wlan0.conf
cat > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf <<EOF
country=RU
ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
update_config=1
p2p_disabled=1

network={
    ssid="Pi_Traveler"
    mode=2
    frequency=2412
    key_mgmt=WPA-PSK
    proto=RSN
    pairwise=CCMP
    psk="raspberry"
}
EOF

chmod 777 /etc/wpa_supplicant/wpa_supplicant-wlan0.conf
systemctl disable wpa_supplicant.service
systemctl enable wpa_supplicant@wlan0.service
rfkill unblock wlan

# configure wpa_supplicant for wlan1 as client
cat > /etc/wpa_supplicant/wpa_supplicant-wlan1.conf <<EOF
country=DE
ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev
update_config=1
p2p_disabled=1


EOF

chmod 777 /etc/wpa_supplicant/wpa_supplicant-wlan1.conf
systemctl disable wpa_supplicant.service
systemctl enable wpa_supplicant@wlan1.service

# configure interfaces
cat > /etc/systemd/network/08-wlan0.network <<EOF
[Match]
Name=wlan0
[Network]
Address=192.168.26.1/24
LLMNR=no
DNSSEC=no
MulticastDNS=yes
# IPMasquerade is doing NAT
IPMasquerade=yes
IPForward=yes
DHCPServer=yes
[DHCPServer]
DNS=84.200.69.80 1.1.1.1
EOF

# Because we don't have a bridge,
# we need two different subnets. 
# Be aware that the static ip address for the access point wlan0 belongs to another subnet than that from wlan1. 
# For the connection to the internet router we use network address translation (NAT).

cat > /etc/systemd/network/12-wlan1.network <<EOF
[Match]
Name=wlan1
[Network]
LLMNR=no
DNSSEC=no
MulticastDNS=yes
DHCP=yes
EOF

# reboot