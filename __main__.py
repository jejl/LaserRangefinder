"""Manage Bosch laser ranger and hardware to obtain bearing, 3D orientation, location, time,
provide a display and interface, report UPS status"""

import logging
from util.config import Args, Config
from util.logging import LaserLog
from _version import __version__
from devices.ScreenAndButtons import ScreenAndButtons
from devices.Relay import Relay
from devices.Rotary import Rotary
from devices.Accelerometer import Accelerometer
from devices.UPS import UPS
from os.path import exists
import subprocess
import datetime, os, time, signal
import numpy as np

logger = logging.getLogger(__name__)

DEBUG = True


def waitfor(command, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    start = datetime.datetime.now()
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    while process.poll() is None:
        time.sleep(0.2)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            return None
    return process.stdout.readlines()


def bosch_usb_drive_off(relay):
    path = "/media/jlovell/GLM400CL"
    if exists(path):
        command = "umount {}".format(path)
        waitfor(command, 15)
        relay.off()
    else:
        return False


def bosch_usb_drive_on(relay):
    relay.on()
    time.sleep(5)
    path = "/media/jlovell/GLM400CL"
    if not exists(path):
        print("No drive drive found wait 5 sec")
        time.sleep(5)
        if not exists(path):
            return False
    else:
        print("Drive mounted")
        return True


def wait_for_button(test: bool = False):
    if test:
        print("Test mode")
        print("1: Measurement")
        print("2: Finished measurement")
        print("3: Status")
        key = int(input("Enter key: "))
        return key


def get_rotary(rotary):
    rotary.getValue()


def get_accelerometer_orientation(accelerometer):
    accelerometer.Update()


def show_orientation_data(rotary, accelerometer):
    print("Rotary value = {} angle = {}".format(rotary.value, rotary.direction))
    print("Accelerometer heading = {}".format(np.rad2deg(accelerometer.norm_heading)))
    print("Accelerometer pitch = {}".format(np.rad2deg(accelerometer.pitch)))
    print("Accelerometer roll = {}".format(np.rad2deg(accelerometer.roll)))


def check_for_usb_drive():
    pass


def mount_usb_drive():
    pass


def get_bosch_data(debug=True):
    import csv

    with open("/media/jlovell/GLM400CL/Memory.txt") as inp:
        reader = csv.DictReader(inp)
        for row in reader:
            if debug:
                print(row)
    # row contains dict of data
    # Must be indirect height measurement to get range and angle
    if not row["Function"] == "Indirect Height Measurement":
        print(
            "Error: laser ranger should be configured for Indirect height measurement!"
        )
        return False
    # Get range and angle
    data = {}
    data["time"] = row["Date"]
    data["range"] = float(row["Value1"])
    data["angle"] = float(row["Value2"])
    data["height"] = float(row["Measurement"])
    data["image_no_str"] = row["Image No."]
    return data


def show_bosch_data(bosch_data):
    print("Bosch data")
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(bosch_data)


def show_status():
    print("Status")
    pass


def write_data_to_json(config, rotary, accelerometer, bosch_data):
    import json
    from datetime import datetime

    data = {}
    data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["rotary"] = {"value": rotary.value, "direction": rotary.direction}
    data["accelerometer"] = {
        "heading": accelerometer.norm_heading,
        "pitch": accelerometer.pitch,
        "roll": accelerometer.roll,
        "norm": accelerometer.norm,
    }
    data["bosch"] = bosch_data
    with open("{}/laser_data.json".format(config.LogDir), "a") as out:
        json.dump(data, out)
        out.write("\n")
    return


def main():
    """Initialise and start the loop"""
    # Read command-line arguments, config from the config file and env variables
    # config_in = Args()
    # --------------------------------------------------------------------------
    # Create a configuration instance and add the parameters from above
    # Config instance
    config = Config()
    # Load in the config
    # config.load(config_in)
    # check the config makes sense
    # config.check_config()
    # --------------------------------------------------------------------------
    # Set up logging
    level = logging.INFO
    if DEBUG:
        level = logging.DEBUG
    LaserLog(
        config.LogDir,
        "LaserRangefinder.log",
        level=level,
    )
    logger.info("LaserRangefinder version {}".format(__version__))
    # --------------------------------------------------------------------------
    # Initialise hardware
    # Screen, then start showing status info
    screen = ScreenAndButtons()
    # Relay
    relay = Relay(config)
    # Rotary Encoder
    rotary = Rotary(config)
    # Accelerometer
    accelerometer = Accelerometer(config)
    # UPS
    ups = UPS(config)
    # GPS (skip for now)

    # --------------------------------------------------------------------------
    # Initialise data arrays

    # --------------------------------------------------------------------------
    # Dismount Bosh USB drive and turn off 5V
    bosch_usb_drive_off(relay)

    # --------------------------------------------------------------------------
    # Start the loop
    while True:
        # wait for a button press

        # key = 1
        key = wait_for_button(test=True)
        if key == 1:
            # button 1 pressed
            # Turn off 5V to Bosch
            bosch_usb_drive_off(relay)
            input("Take a measurement with the laser then press enter to continue")
            # Measurement
            rotary_angle = get_rotary(rotary)
            accelerometer_orientation = get_accelerometer_orientation(accelerometer)
            # gps_data = get_GPS()
            # Show data on screen
            show_orientation_data(rotary,accelerometer)
        elif key == 2:
            # button 2 pressed
            # Finished. Get data
            # Turn on 5V to Bosch
            bosch_usb_drive_on(relay)
            # Mount USB drive (or check that it is mounted)
            # if not check_for_usb_drive():
            #     mount_usb_drive()
            # get data from drive
            bosch_data = get_bosch_data()
            if (bosch_data):
                # show orientation and bosch data on screen
                show_orientation_data(rotary, accelerometer)
                show_bosch_data(bosch_data)
                # write data to a json file
                write_data_to_json(config, rotary, accelerometer, bosch_data)
        else:
            # button 3 pressed
            # Show status
            show_status()


if __name__ == "__main__":
    main()
