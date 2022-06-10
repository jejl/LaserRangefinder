from util.encoder import Encoder

class Rotary:
    def __init__(self, config, invert = False):
        if not invert:
            self.left_pin = config.Encoder_GPIO_left_pin
            self.right_pin = config.Encoder_GPIO_right_pin
        else:
            self.left_pin = config.Encoder_GPIO_right_pin
            self.right_pin = config.Encoder_GPIO_left_pin
        self.encoder = Encoder(self.left_pin, self.right_pin, self._valueChanged)
        self.value = 0
        self.direction = "0"

    def _valueChanged(self, value, direction):
        self.value = value
        self.direction = direction

    def getValue(self):
        self.encoder.getValue()

