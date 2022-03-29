import re
import subprocess

cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
regexps = [
    re.compile(r"^ESSID:\"(?P<ssid>.*)\"$"),
    re.compile(r"Signal level=(?P<signal_quality>\d+)/(?P<signal_total>\d+).*$"),
]

# Detect encryption type
wpaRe = re.compile(r"IE:\ WPA\ Version\ 1$")
wpa2Re = re.compile(r"IE:\ IEEE\ 802\.11i/WPA2\ Version\ 1$")

# Runs the comnmand to scan the list of networks.
# Must run as super user.
# Does not specify a particular device, so will scan all network devices.

def scan(interface='wlan1'):
    cmd = ["iwlist", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')
    return points


# Parses the response from the command "iwlist scan"
def parse(content):
    cells = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
            continue
        wpa = wpaRe.search(line)
        if wpa is not None:
            cells[-1].update({'encryption': 'wpa'})
        wpa2 = wpa2Re.search(line)
        if wpa2 is not None:
            cells[-1].update({'encryption': 'wpa2'})
        for expression in regexps:
            result = expression.search(line)
            if result is not None:
                if 'encryption' in result.groupdict():
                    if result.groupdict()['encryption'] == 'on':
                        cells[-1].update({'encryption': 'wep'})
                    else:
                        cells[-1].update({'encryption': 'off'})
                else:
                    cells[-1].update(result.groupdict())
                continue
    return cells

# sudo required
def scan_all(interface="wlan1"):
    print("Scanning...")
    cmd = ["iw", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')

class Network:
    def __init__(self, ssid):
        super().__init__()
        self.ssid = ssid
        self.password = None
        self.mac = None
        self.encryption = None
        self.signal_quality = 0
        self.signal_pic = "images/wifi-min.png"
    
    def rewrite_wpa_supplicant(self, controller):
        with open('/etc/wpa_supplicant/wpa_supplicant-wlan1.conf', 'w') as wpa_config:
            new_config = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=RU\n"
            new_config = new_config + "\nnetwork={\n\tssid=\"" + self.ssid + "\"\n\tpsk=\"" + self.password + "\"\n}\n"
            wpa_config.write(new_config)
            print(new_config)
            wpa_config.close()
            controller.reconfigure_interface()




class NetworkController:
    def __init__(self):
        super().__init__()
        self.ap_network = None
        self.connected_network = None
        self.all_available_networks = []
        self.get_ap_network()
        self.get_connected_network() 
        self.get_available_networks()

    def update(self):
        self.get_connected_network()
        self.get_available_networks()
        
    def reset_wpa_supplicant(self):
        with open('/etc/wpa_supplicant/wpa_supplicant-wlan1.conf', 'w') as wpa_config:
            new_config = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=RU\n"
            wpa_config.write(new_config)
            print(new_config)
            wpa_config.close()
            self.reconfigure_interface()

    def reconfigure_interface(self):
        cmd = ["wpa_cli", "-i", "wlan1", "reconfigure"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        points = proc.stdout.read().decode('utf-8')

    def get_ap_network(self):
        regExNetwork = re.compile(
            r"network=\{\s*ssid=\"(?P<ssid>.*)\"\s*mode=(?P<mode>.*)\s*frequency=(?P<frequency>.*)\s*key_mgmt=(?P<key_mgmt>.*)\s*proto=(?P<proto>.*)\s*pairwise=(?P<pairwise>.*)\s*psk=(?P<psk>.*)\s\}")
        with open('/etc/wpa_supplicant/wpa_supplicant-wlan0.conf') as wpa_config:
            conf_text = wpa_config.read()
            result = regExNetwork.search(conf_text)
            wpa_config.close()
            if result is not None:
                self.ap_network = Network(ssid=result.groupdict()['ssid'])
                self.ap_network.password = result.groupdict()['psk']
          
    def get_connected_network(self):
        self.connected_network = None
        proc = subprocess.Popen(["iw", "wlan1", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        points = proc.stdout.read().decode('utf-8')
        networks = []
        ssidEx_iw_dev = re.compile(r"ssid (?P<ssid>.*)")
        macEx_iw_dev = re.compile(r"addr (?P<mac>.*)")
        lines = points.split('\n')
        for line in lines:
            line = line.strip()
            ssid = ssidEx_iw_dev.search(line)
            if ssid != None:
                self.connected_network = Network(ssid=ssid.groupdict()['ssid'])
                print("CONNECTED_NETWORK:", self.connected_network.ssid)
                continue

    def get_available_networks(self):
        self.all_available_networks = []
        content = scan(interface='wlan1')
        iw_cells = parse(content)
        for nw in iw_cells:
            new_network = Network(nw['ssid'])
            new_network.mac = nw['mac']
            new_network.signal_quality = int(nw['signal_quality'])
            if int(nw['signal_quality']) >= 66:
                new_network.signal_pic = "images/wifi-max.png"
            elif 33 < int(nw['signal_quality']) < 66:
                new_network.signal_pic = "images/wifi-50.png"
            else:
                new_network.signal_pic = "images/wifi-min.png"
            
            if self.connected_network != None:
                if new_network.ssid != self.connected_network.ssid and new_network.ssid != self.ap_network.ssid and new_network.ssid != '':
                    self.all_available_networks.append(new_network)
            elif new_network.ssid != self.ap_network.ssid and new_network.ssid != '':
                    self.all_available_networks.append(new_network)
