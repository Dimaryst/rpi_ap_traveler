#!/bin/sh
cd ../..
mkdir Driver_RTL8812AU
cd Driver_RTL8812AU
apt install git dkms
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
echo 'MAKE'
make dkms_install
