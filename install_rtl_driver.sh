# install drivers for wlan1 usb 
apt-get update
apt-get full-upgrade
cd ../
mkdir rtl_driver
cd rtl_driver
apt install git dkms
git clone https://github.com/aircrack-ng/rtl8812au.git
cd rtl8812au
echo 'MAKE'
make dkms_install
