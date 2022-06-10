from gpiozero import LED
from time import sleep

class Relay:
    def __init__(self, config):
        self.pin_to_circuit = config.Relay_GPIO_pin
        self.relay = LED(self.pin_to_circuit, active_high=False, initial_value=False)


    def on(self):
        self.relay.on()

    def off(self):
        self.relay.off()
