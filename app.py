from flask import Flask, render_template, url_for, request, Response, jsonify
from flask_restful import Resource, Api
from werkzeug.utils import redirect
import network

app = Flask(__name__, static_folder="static")
api = Api(app)

network_controller = network.NetworkController()

@app.route('/wifi', methods=['GET'])
def settings_page():
    network_controller.update()
    return render_template('wifi.html', connected_network=network_controller.connected_network,
                           available_networks=network_controller.all_available_networks)

@app.route('/wifi/reset_configuration', methods=['GET'])
def reset_configuration():
    network_controller.reset_wpa_supplicant()
    network_controller.update()
    return redirect(url_for('settings_page'))

@app.route('/wifi/scan', methods=['GET'])
def scan():
    network.scan_all()
    network_controller.update()
    return redirect(url_for('settings_page'))


@app.route('/wifi/password_request_<ssid>', methods=['GET', 'POST'])
def password_request_page(ssid):
    if request.method == 'POST':
        password = request.form.get('password')
        new_network = network.Network(ssid=ssid)
        new_network.password = password
        new_network.rewrite_wpa_supplicant(network_controller)
        network_controller.update()
        return redirect(url_for('settings_page'))
    return render_template('request_pass.html', network_ssid=ssid)


@app.route('/', methods=['GET'])
def index_page():
    network_controller.update()
    return render_template('index.html', self_ap=network_controller.ap_network, connected_network=network_controller.connected_network)

class AvailableNetworks(Resource):
    def get(self):
        network_controller.update()
        available_networks = network_controller.all_available_networks
        result = []
        for nw in available_networks:
            dc = {
                "ssid": nw.ssid, 
                "mac": nw.mac,
                "signal_quality": nw.signal_quality, 
                "encryption": nw.encryption
            }
            result.append(dc) 
        return jsonify(result) 

class SelfHotspot(Resource):
    def get(self):
        network_controller.update()
        if network_controller.ap_network is not None:
            result = {
            "ssid": network_controller.ap_network.ssid, 
            "password": network_controller.ap_network.password
            } 
            return jsonify(result)
        else:
            return None

class ConfiguredNetwork(Resource):
    def get(self):
        network_controller.update()
        if network_controller.connected_network is not None:
            result = {
                "ssid": network_controller.connected_network.ssid, 
                "mac": "none",
                "signal_quality": 0, 
                "encryption": "off"
            } 
            return jsonify(result)
        else:
            return None


api.add_resource(AvailableNetworks, '/api/available_networks')
api.add_resource(SelfHotspot, '/api/self_hotspot')
api.add_resource(ConfiguredNetwork, '/api/configured_network')

if __name__ == "__main__":
    app.run(debug=True, host="192.168.26.1")
