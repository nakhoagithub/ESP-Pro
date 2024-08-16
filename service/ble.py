import machine
import neopixel
import ubluetooth
import time
import gc
from ubluetooth import BLE
from machine import Timer
from service import tool


COMMANDS = [
    {
        "command": "help",
        "name": "Show help",
        "ex": "help",
    },
    {
        "command": "show",
        "name": "Show config",
        "ex": "show",
    },
    {
        "command": "restart",
        "name": "Restart ESP32",
        "ex": "restart",
    },
    {
        "command": "ledmode",
        "name": "Led Mode",
        "ex": "ledmode <0 or 1>",
        "key": "led_mode",
        "type": int,
    },
    {
        "command": "ledpin ",
        "name": "Led pin on ESP32",
        "ex": "ledpin <pin number>",
        "key": "led_pin",
        "type": int,
    },
    {
        "command": "bn ",
        "name": "Bluetooth name",
        "ex": "bn <bluetooth name>",
        "key": "bluetooth_name",
        "type": str,
    },
    {
        "command": "wfmode ",
        "name": "Wifi Mode",
        "ex": "wfmode <0 or 1>",
        "key": "wifi_mode",
        "type": int,
    },
    {
        "command": "wf ",
        "name": "Wifi Name (SSID)",
        "ex": "wf <wifi name>",
        "key": "wifi_ssid",
        "type": str,
    },
    {
        "command": "wfp ",
        "name": "Wifi Password",
        "ex": "wfp <wifi password>",
        "key": "wifi_password",
        "type": str,
    },
    {
        "command": "wfip ",
        "name": "Wifi IP Address",
        "ex": "wfip <wifi static ip address>",
        "key": "wifi_ip",
        "type": str,
    },
    {
        "command": "wfsn ",
        "name": "Wifi Subnet mask",
        "ex": "wfsn <wifi subnet mask>",
        "key": "wifi_subnet",
        "type": str,
    },
    {
        "command": "wfg ",
        "name": "Wifi Gateway",
        "ex": "wfg <wifi gateway>",
        "key": "wifi_gateway",
        "type": str,
    },
    {
        "command": "wfdns ",
        "name": "Wifi DNS",
        "ex": "wfdns <wifi dns>",
        "key": "wifi_dns",
        "type": str,
    },
    {
        "command": "tcpport ",
        "name": "Modbus TCP Port",
        "ex": "tcpport <port number>",
        "key": "tcp_port",
        "type": int,
    },
    {
        "command": "address ",
        "name": "RS485 Address",
        "ex": "address <address>",
        "key": "address",
        "type": int,
    },
    {
        "command": "txhost ",
        "name": "TX Pin Host",
        "ex": "txhost <pin number>",
        "key": "tx_host",
        "type": int,
    },
    {
        "command": "txclient ",
        "name": "TX Pin Client",
        "ex": "txclient <pin number>",
        "key": "tx_client",
        "type": int,
    },
    {
        "command": "rxclient ",
        "name": "RX Pin Client",
        "ex": "rxclient <pin number>",
        "key": "rx_client",
        "type": int,
    },
    {
        "command": "txmodule ",
        "name": "TX Pin Module",
        "ex": "txmodule <pin number>",
        "key": "tx_module",
        "type": int,
    },
    {
        "command": "rxmodule ",
        "name": "RX Pin Module",
        "ex": "rxmodule <pin number>",
        "key": "rx_module",
        "type": int,
    },
    {
        "command": "m ",
        "name": "Config module",
        "ex": "m <address> <start> <count> <func> <value on> <value off> | func: r: Registers, c: Coils",
    },
    {
        "command": "m show",
        "name": "Show modules",
        "ex": "m show",
    },
    {
        "command": "m del ",
        "name": "Delete module",
        "ex": "m del <address>",
    },
    {
        "command": "s ",
        "name": "Config sensor",
        "ex": "s <address> <start> <count> <func> | func: h: Read Holding Register, i: Read Input Register",
    },
    {
        "command": "s show",
        "name": "Show sensors",
        "ex": "s show",
    },
    {
        "command": "s del ",
        "name": "Delete sensor",
        "ex": "s del <address>",
    },
]

class Bluetooth:
    def __init__(self, conf, led, internet):
        self.conf = conf
        self.led = led
        self.internet = internet
        self.name = self.conf.get("bluetooth_name", "ESP32")
        self.ble = BLE()
        self.ble.irq(self._irq)
        self.ble.active(True)
        self.register()
        self.advertiser()
        
    def _reload_conf(self):
        self.conf = tool.conf()
        
    def _led_connect(self):
        self.led.stop()
        self.led.led_blue()
    
    def _led_disconnect(self):
        self.led.start()
        
    def _config_module(self, message: str):
        try:
            commands = message.split()
            if len(commands) == 2:
                if commands[0] == "m" and commands[1] == "show":
                    modules = tool.modules()
                    for k, v in modules.items():
                        self.send(f"Module: {v['address']} {v['start']} {v['count']} {v['func']} {v['on']} {v['off']}")
                        gc.collect()
                        time.sleep(0.05)
                        
            if len(commands) == 3:
                if commands[0] == "m" and commands[1] == "del":
                    address = int(commands[2])
                    tool.save_module(address, delete=True)
                    self.send(f"Module {address} deleted!")
                
            elif len(commands) == 7:
                address = int(commands[1])
                start = int(commands[2])
                if start < 0:
                    return self.send("Invalid parameter start >= 0")
                count = int(commands[3])
                if count < 1:
                    return self.send("Invalid parameter count > 0")
                func = str(commands[4])
                if func not in ["r", "c"]: # r register, c coil
                    return self.send("Invalid parameter func is 'r' or 'c'")
                on = int(commands[5])
                off = int(commands[6])
                tool.save_module(address, start, count, func, on, off)
                self.send(f"Module {address} saved: {address} {start} {count} {func} {on} {off}")
                
        except Exception as e:
            print(e)
            self.send("Invalid parameters")
            
    def _config_sensor(self, message: str):
        try:
            commands = message.split()
            if len(commands) == 2:
                if commands[0] == "s" and commands[1] == "show":
                    sensors = tool.sensors()
                    for k, v in sensors.items():
                        self.send(f"Sensor: {v['address']} {v['start']} {v['count']} {v['func']}")
                        gc.collect()
                        time.sleep(0.05)
                        
            if len(commands) == 3:
                if commands[0] == "s" and commands[1] == "del":
                    address = int(commands[2])
                    tool.save_sensor(address, delete=True)
                    self.send(f"Sensor {address} deleted!")
                
            elif len(commands) == 5:
                address = int(commands[1])
                start = int(commands[2])
                if start < 0:
                    return self.send("Invalid parameter start >= 0")
                count = int(commands[3])
                if count < 1:
                    return self.send("Invalid parameter count > 0")
                func = str(commands[4])
                if func not in ["h", "i"]: # h: read holding, i: read input
                    return self.send("Invalid parameter func is 3 or 4")
                tool.save_sensor(address, start, count, func)
                self.send(f"Sensor {address} saved: {address} {start} {count} {func}")
                
        except Exception as e:
            print(e)
            self.send("Invalid parameters")
        
    def _irq(self, event, data):
        if event == 1:
            self._led_connect()
        
        elif event == 2:
            self.advertiser()
            self._led_disconnect()
        
        elif event == 3:
            try:
                buffer = self.ble.gatts_read(self.rx) 
                message = buffer.decode('utf-8').strip()
                 
                if message == "restart":
                    machine.reset()
                
                elif message == "help":
                    index = 1
                    for v in COMMANDS:
                        v_name = v.get("name")
                        v_ex = v.get("ex")
                        self.send(f"{index}. {v_name}: {v_ex}")
                        index += 1
                        gc.collect()
                        time.sleep(0.05)
                    self.send("")
                    
                elif message == "show":
                    if self.conf.get("wifi_mode", 0) == 1:
                        ifconfig = self.internet.wlan.ifconfig()
                        connected = self.internet.wlan.isconnected()
                        if len(ifconfig) != 0 and connected:
                            self.send(f"Wifi connected IP: {ifconfig[0]}")
                        else:
                            self.send("Wifi not connect")
                    
                    conf = tool.conf()
                    for k, v in conf.items():
                        c = tool.find_where(COMMANDS, key=k)
                        if len(c) == 1:
                            name = c[0]["name"]
                            self.send(f"{name}: {k}={v}")
                            gc.collect()
                            time.sleep(0.05)
                    self.send("")
                            
                elif str(message).startswith("m "):
                    self._config_module(str(message))
                    
                elif str(message).startswith("s "):
                    self._config_sensor(str(message))
                
                else:  
                    for i in COMMANDS:
                        if str(message).startswith(i["command"]):
                            commands = str(message).split()
                            if len(commands) < 2:
                                self.send("Invalid parameters")
                            else:
                                type_value = i.get("type", None)
                                if type_value is not None:
                                    try:
                                        value = type_value(commands[1])
                                        tool.save_conf("is_blink", 1)
                                        key = i.get("key", "key")
                                        tool.save_conf(key, value)
                                        self.send("Successful!")
                                    except Exception as e:
                                        self.send("Invalid parameter")
                        gc.collect()
                        time.sleep(0.01)
                                        
                self._reload_conf()
            except Exception as e:
                print("Error BLE: ", e)
                     
    def register(self):        
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        try:
            self.ble.gatts_notify(1, self.tx, data + '\n')
#             for i in range(0, len(data), 20):
#                 self.ble.gatts_notify(1, self.tx, data[i:i+20])
#                 time.sleep(0.01)
        except Exception as e:
            print("Send Error:", e)
                
                
    def advertiser(self):
        name = bytearray(self.name, 'utf-8')
        # self.ble.gap_advertise(100, bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name)
        adv_data = bytearray([0x02, 0x01, 0x06]) + bytearray([len(name) + 1, 0x09]) + name
        self.ble.gap_advertise(100, adv_data)
            
            
            
