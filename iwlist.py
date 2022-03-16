import re
import subprocess


def get_connected_network_ssid():
    proc = subprocess.Popen(["iw", "wlan1", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')
    networks = []
    ssidEx_iw_dev = re.compile(r"ssid (?P<ssid>.*)")
    lines = points.split('\n')
    for line in lines:
        line = line.strip()
        ssid = ssidEx_iw_dev.search(line)
        if ssid is not None:
            networks.append(ssid.groupdict())
            continue
    return networks


def reconfigure_interface(interface="wlan1"):
    # # # wpa_cli -i wlan1 reconfigure
    cmd = ["wpa_cli", "-i", interface, "reconfigure"]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')
    print(points)

# sudo required
def scan_all(interface="wlan1"):
    cmd = ["iw", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')
    print(points)


def get_networks_wpa_supplicant():
    regExNetwork = re.compile(r"network=\{\s*ssid=\"(?P<ssid>.*)\"\s*psk=\"(?P<psk>.*)\"\s*\}")
    with open('/etc/wpa_supplicant/wpa_supplicant-wlan1.conf') as wpa_config:
        conf_text = wpa_config.read()
        result = [item.groupdict() for item in regExNetwork.finditer(conf_text)]
        wpa_config.close()
        return result


# get current ap info
def get_ap_network_wpa_supplicant():
    regExNetwork = re.compile(
        r"network=\{\s*ssid=\"(?P<ssid>.*)\"\s*psk=\"(?P<psk>.*)\s*key_mgmt=(?P<key_mgmt>.*)\s*mode=(?P<mode>.*)\s*frequency=(?P<frequency>.*)\s\}")
    
    with open('/etc/wpa_supplicant/wpa_supplicant-wlan0.conf') as wpa_config:
        conf_text = wpa_config.read()
        result = regExNetwork.search(conf_text)
        wpa_config.close()
        if result is not None:
            return result.groupdict()


def remove_known_networks_from_list(known_networks, networks_list):
    self_ap = get_ap_network_wpa_supplicant()
    print(self_ap)
    known_networks.append(self_ap)
    print(known_networks)
    for known_network in known_networks:
        for network in networks_list:
            try:
                if known_network['ssid'] == network['ssid']:
                    networks_list.remove(network)
            except:
                print('Error')        


def remove_network_from_wpa_supplicant(network_ssid_to_remove):
    # wpa_supplicant_template = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=RU\n"
    wpa_networks = get_networks_wpa_supplicant()
    print(wpa_networks)
    for network in wpa_networks:
        if network['ssid'] == network_ssid_to_remove:
            wpa_networks.remove(network)

    with open('/etc/wpa_supplicant/wpa_supplicant-wlan1.conf', 'w') as wpa_config:
        new_config = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=RU\n"
        for network in wpa_networks:
            new_config = new_config + "\nnetwork={\n\tssid=\"" + network['ssid'] + "\"\n\tpsk=\"" + network[
                'psk'] + "\"\n}\n"
        print(new_config)

        wpa_config.write(new_config)
        # wpa_config.truncate()
        wpa_config.close()
        reconfigure_interface()


def add_network_to_wpa_supplicant(network_ssid, network_psk):
    new_network = {'ssid': network_ssid, 'psk': network_psk}
    wpa_networks = get_networks_wpa_supplicant()
    print(wpa_networks)
    wpa_networks.append(new_network)
    print(wpa_networks)
    with open('/etc/wpa_supplicant/wpa_supplicant-wlan1.conf', 'w') as wpa_config:
        new_config = "ctrl_interface=DIR=/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=RU\n"
        for network in wpa_networks:
            new_config = new_config + "\nnetwork={\n\tssid=\"" + network['ssid'] + "\"\n\tpsk=\"" + network[
                'psk'] + "\"\n}\n"
        wpa_config.write(new_config)
        wpa_config.close()
        reconfigure_interface()


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
