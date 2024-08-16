import network
import time
from service import tool

class Internet:
    def __init__(self, conf):
        self.conf = conf
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
    def scan(self):
        networks = self.wlan.scan()
        wifi_list = []
        for network in networks:
            wifi_info = {
                "ssid": network[0].decode("utf-8"),
                "bssid": ':'.join(['%02x' % b for b in network[1]]),
                "channel": network[2],
                "rssi": network[3],
                "authmode": network[4],
                "hidden": network[5]
            }
            wifi_list.append(wifi_info)
        return wifi_list
        
    def connect(self, ssid, password):
        if not self.wlan.isconnected():
            print("Connecting to network...")
            ip = self.conf.get("wifi_ip", None)
            subnet = self.conf.get("wifi_subnet", None)
            gateway = self.conf.get("wifi_gateway", None)
            dns = self.conf.get("wifi_dns", None)
            if ip and subnet and gateway and dns:
                self.wlan.ifconfig((ip, subnet, gateway, dns))
            self.wlan.connect(ssid, password)
            
    def disconnect(self):
        self.wlan.disconnect()

