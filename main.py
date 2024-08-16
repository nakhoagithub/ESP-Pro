# Power by Anh Khoa

import time
import _thread
from machine import Pin, Timer, ADC
from service import tool
from service.ble import Bluetooth
from service.internet import Internet
from service.led import Led
from service.modbus import Modbus


class Main:
    def __init__(self):
        tool.init_default()
        self.conf = tool.conf()
        self.internet = Internet(self.conf)
        self.led = Led(self.conf, self.internet)
        self.ble = Bluetooth(self.conf, self.led, self.internet)
        self.modbus = Modbus(self.conf, self.internet)
        
    def _create_modbus_server(self):
        try:
            if self.modbus.is_modbus_server: return
            if self.internet.wlan.isconnected():
                self.modbus.init_modbus_tcp(self.internet.wlan.ifconfig())
        except:
            pass
        
    def _connect_wifi(self):
        self.internet.disconnect()
        wifi_mode = self.conf.get("wifi_mode", 0)
        if bool(wifi_mode):
            wfn = self.conf.get("wifi_ssid", None)
            wfp = self.conf.get("wifi_password", None)
            if wfn and wfp:
                self.internet.connect(wfn, wfp)
                
    def run(self):
        self._connect_wifi()
        self.led.start()
        print("ESP Running")
        while True:
            try:
                self.modbus.run()
                self._create_modbus_server()
                time.sleep(0.05)
            except KeyboardInterrupt:
                print("ESP Stopped")
                break
            except Exception as e:
                
                print(f"Error main: {type(e)} {e}")
                break
        self.led.stop()
        self.modbus.stop()

main = Main()
main.run()