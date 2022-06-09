from gpiozero import LED
from time import sleep

relay = LED(1, active_high=False, initial_value=False)

print("Turn on")
relay.on()
print("Relay value = {}".format(relay.value))
sleep(2)

print("Turn off")
relay.off()
print("Relay value = {}".format(relay.value))
sleep(2)

print("Turn on")
relay.on()
print("Relay value = {}".format(relay.value))
sleep(2)

