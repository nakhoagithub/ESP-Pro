import neopixel
from machine import Pin, Timer
from service import tool

class Led:
    def __init__(self, conf, internet):
        self.conf = conf
        self.internet = internet
        self.led_pin = self.conf.get("led_pin", 38)
        self.num_of_led = self.conf.get("num_of_led", 10)
        self.led_mode = bool(self.conf.get("led_mode", 1))
        self.led = Pin(self.led_pin, Pin.OUT)
        
        if self.num_of_led < 1:
            self.num_of_led == 1
        self.pixels = neopixel.NeoPixel(self.led, self.num_of_led)
        self.timer = Timer(1)
        self.state_blink = True

    def led_rgb(self, r=255, g=255, b=255, index=0):
        if 0 <= index < self.num_of_led:
            self.pixels[index] = (g, r, b)
            self.pixels.write()
    
    def led_default(self, index=0):
        self.led_rgb(128, 128, 128, index)

    def led_white(self, index=0):
        self.led_rgb(255, 255, 255, index)
        
    def led_red(self, index=0):
        self.led_rgb(255, 0, 0, index)

    def led_green(self, index=0):
        self.led_rgb(0, 255, 0, index)

    def led_blue(self, index=0):
        self.led_rgb(0, 0, 255, index)
        
    def led_yellow(self, index=0):
        self.led_rgb(255, 255, 0, index)
        
    def led_cyan(self, index=0):
        self.led_rgb(0, 255, 255, index)
        
    def led_magenta(self, index=0):
        self.led_rgb(255, 0, 255, index)
        
    def led_sliver(self, index=0):
        self.led_rgb(192, 192, 192, index)

    def led_off(self, index=0):
        self.led_rgb(0, 0, 0, index)

    def _blink(self, timer):
        if self.state_blink:
            if self.internet.wlan.isconnected():
                self.led_green()
            else:
                self.led_default()
        else:
            self.led_off()
        self.state_blink = not self.state_blink

    def start(self):
        if self.led_mode:
            self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self._blink)
        else:
            self.led_off()
            
    def stop(self):
        self.timer.deinit()
        self.led_off()
