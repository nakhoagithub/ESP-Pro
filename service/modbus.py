import gc
from umodbus.serial import ModbusRTU, Serial as ModbusModule
from umodbus.tcp import ModbusTCP
from service import tool
from machine import Timer

registers = {"IREGS": {}, "HREGS": {}}

register_values = []

class Modbus:
    def __init__(self, conf, internet):
        self.conf = conf
        self.internet = internet
        self.modules = tool.modules()
        self.sensors = tool.sensors()
        self.tx_client = self.conf.get("tx_client", 18)
        self.rx_client = self.conf.get("rx_client", 17)
        self.tx_module = self.conf.get("tx_module", 16)
        self.rx_module = self.conf.get("rx_module", 15)
        self.address = self.conf.get("address", 1)
        
        self.is_modbus_server = False
        self.tcp_port = self.conf.get("tcp_port", 502)
        self.client = ModbusRTU(addr=self.address, pins=(self.tx_client, self.rx_client), uart_id=1)
        self.modbus_module = ModbusModule(pins=(self.tx_module, self.rx_module), uart_id=2)
        
        self.timer_read_sensor = Timer(0)
        
        # Tạo khi không sử dụng wifi
        if self.conf.get("wifi_mode", 0) == 0:
            self._init()
        
    def init_modbus_tcp(self, ifconfig):
        # Tạo khi sử dụng wifi
        ip, _, _, _ = ifconfig
        self.client = ModbusTCP()
        
        if not self.client.get_bound_status():
            self.client.bind(local_ip=ip, local_port=self.tcp_port)
            self._init()
            
        self.is_modbus_server = True
    
    def _get_module_from_index(self, index: int):
        total_relay = 0
        befor_relay = 0
        index_module = -1
        module = None
        for k, v in sorted(self.modules.items(), key=lambda i: i[1]["address"]):
            relay = v.get("count", None)
            if relay is not None:
                total_relay += relay
                if total_relay - relay == befor_relay and (index + 1) - befor_relay <= relay:
                    index_module = index - befor_relay
                    module = v
                    return index_module, module
            
                befor_relay += relay
        return index_module, module
    
    def _get_module(self, index: int):
        try:
            bf_relay = 0
            for k, v in sorted(self.modules.items(), key=lambda i: i[1]["address"]):
                relay = v.get("count", None)
                if relay is not None:
                    if (index + 1) - bf_relay <= relay:
                        return v, bf_relay
                    bf_relay += relay
        except Exception as e:
            print("Error _get_module", e)
    
    def _send_modbus_module(self, values_copy: list, values: list):
        modules = {}
        for i, v in enumerate(values):
            if values_copy[i] != values[i]:
                module, bf_relay = self._get_module(i)
                if module is not None:
                    func = module.get("func", "r")
                    slave = module.get("address", 1)
                    start = module.get("start", 0)
                    count = module.get("count", 1)
                    on = module.get("on", 1)
                    off = module.get("off", 0)

                    key = f"{slave}.{start}.{func}.{bf_relay}"
                    values_module = []
                    for i_m in range(count):
                        value = values[bf_relay + i_m]
                        if value == 1:
                            value = on
                        elif value == 0:
                            value = off
                            
                        values_module.append(value)
                    modules[key] = values_module
                    
        for k, values_module in modules.items():
            slave, start, func, bf_relay = k.split(".")
            try:
                if func == "c":
                    self.modbus_module.write_multiple_coils(int(slave), int(start), values_module)
                if func == "r":
                    self.modbus_module.write_multiple_registers(int(slave), int(start), values_module)
            
            except Exception as e:
                print(f"Error _send_modbus_module: {e}")
        
    def _set_cb(self, reg_type, address, val):
        if address < 1: return
        
        global register_values
        register_values_copy = register_values[:]
        
        try:
            if address > len(register_values): return

            for i, v in enumerate(register_values):
                if i + 1 >= address:
                    if (i + 1) - address < len(val):
                        register_values[i] = val[(i + 1) - address]
                        
            self._send_modbus_module(register_values_copy, register_values)
            
            print(f"set {address} {val}")
        except Exception as e:
            print(f"_set_cb Error: {e}")
             
    def _get_cb(self, reg_type, address, val):
        print(f"get {address} {val}")
        
    def _init(self):
        total_hreg = 128
#         for k, v in self.modules.items():
#             count_relay = v["count"]
#             if count_relay > 0:
#                 total_hreg += count_relay
        # Module
        for i in range(1, total_hreg + 1):
            registers["HREGS"][f"HREG_{i}"] = {
                "register": i,
                "val": 0,
                "on_set_cb": self._set_cb,
                "on_get_cb": self._get_cb,
            }
            register_values.append(0)
            
        # Sensor
        for k, v in self.sensors.items():
            address = v.get("address", 1)
            count = v.get("count", 1)
            registers["IREGS"][f"IREG_SENSOR_{address}"] = {
                "register": address,
                "val": 0,
                "len": count,
                "on_set_cb": self._set_cb,
                "on_get_cb": self._get_cb,
            }
            
        self.client.setup_registers(registers=registers)
        self._run_timer()
        
    def _read_sensor(self, timer):
        for k, v in self.sensors.items():
            address = v.get("address", 1)
            start = v.get("start", 0)
            count = v.get("count", 1)
            func = v.get("func", "h")
            
            try:
                result = None
                try:
                    if func == "h":
                        result = self.modbus_module.read_holding_registers(address, start, count)
                    elif func == "i":
                        result = self.modbus_module.read_input_registers(address, start, count)
                except:
                    pass
                if result is not None:
                    self.client.set_ireg(address, list(result))
            except Exception as e:
                print(f"Error read sensor {address}: {e}")
        
    def _run_timer(self):
        try:
            self.timer_read_sensor.init(period=2000, mode=Timer.PERIODIC, callback=self._read_sensor)
        except Exception as e:
            pass
        
    def stop(self):
        try:
            self.timer_read_sensor.deinit()
        except Exception as e:
            pass
        
    def run(self):
        try:
            if self.client is not None:
                return self.client.process()
        except Exception as e:
            print("Error modbus run:", e)
