from flask import Flask, render_template, url_for, request, Response
from werkzeug.utils import redirect
import iwlist

app = Flask(__name__, static_folder="static")


@app.route('/wifi', methods=['GET'])
def settings_page():
    content = iwlist.scan(interface='wlan1')
    iw_cells = iwlist.parse(content)
    for cell in iw_cells:
        if int(cell['signal_quality']) >= 66:
            cell["signal_picture"] = "images/wifi-max.png"
        elif 33 < int(cell['signal_quality']) < 66:
            cell["signal_picture"] = "images/wifi-50.png"
        else:
            cell["signal_picture"] = "images/wifi-min.png"            
    iwlist.remove_known_networks_from_list(iwlist.get_networks_wpa_supplicant(), iw_cells)
    print(iwlist.get_connected_network_ssid())
    return render_template('wifi.html', current_networks=iwlist.get_connected_network_ssid(),
                           configured_networks=iwlist.get_networks_wpa_supplicant(),
                           available_networks=iw_cells)


@app.route('/wifi/password_request_<ssid>', methods=['GET', 'POST'])
def password_request_page(ssid):
    if request.method == 'POST':
        password = request.form.get('password')
        print(ssid, password)
        iwlist.add_network_to_wpa_supplicant(ssid, password)
        return redirect(url_for('settings_page'))
    return render_template('request_pass.html', network_ssid=ssid)


@app.route('/wifi/remove_network_<ssid>', methods=['GET'])
def remove_network(ssid):
    print(ssid)
    iwlist.remove_network_from_wpa_supplicant(ssid)
    return redirect(url_for('settings_page'))

@app.route('/', methods=['GET'])
def index_page():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True, host="192.168.26.1")
