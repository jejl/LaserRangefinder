import time
from lsm303d import LSM303D
import numpy as np


class Accelerometer:
    def __init__(self, config):
        self.accelerometer = LSM303D(config.accel_addr)
        self.xyz_acc = [0, 0, 0]
        self.xyz_mag = [0, 0, 0]
        self.heading = 0
        self.norm_heading = 0
        self.pitch = 0
        self.roll = 0
        self.norm = 0
        self.GetCalcReport()

    def Update(self):
        self.getAccel()
        self.getMagnet()
        self.calcHeading()
        self.calcNormHeading()

    def GetCalcReport(self):
        self.Update()
        print(
            "Pitch: %.2f Roll: %.2f Heading: %.2f"
            % (
                np.rad2deg(self.pitch),
                np.rad2deg(self.roll),
                np.rad2deg(self.norm_heading),
            )
        )

    def getAccel(self):
        self.xyz_acc = self.accelerometer.accelerometer()

    def getMagnet(self):
        self.xyz_mag = self.accelerometer.magnetometer()

    def calcHeading(self):
        self.heading = np.arctan2(self.xyz_mag[1], self.xyz_mag[0]) % (2 * np.pi)

    def calcNormHeading(self):
        # Normalize accelerometer values.
        self.norm = np.sqrt(
            self.xyz_acc[0] * self.xyz_acc[0]
            + self.xyz_acc[1] * self.xyz_acc[1]
            + self.xyz_acc[2] * self.xyz_acc[2]
        )

        accXnorm = self.xyz_acc[0] / self.norm
        accYnorm = self.xyz_acc[1] / self.norm
        accZnorm = self.xyz_acc[2] / self.norm

        # Calculate pitch and roll
        self.pitch = np.arcsin(accXnorm)
        self.roll = -np.arcsin(accYnorm / np.cos(self.pitch))

        # Calculate the new tilt compensated values
        # The compass and accelerometer are orientated differently on the BerryIMUv1, v2 and v3.
        # needs to be taken into consideration when performing the calculations
        # X compensation

        magXcomp = self.xyz_mag[0] * np.cos(self.pitch) + self.xyz_mag[2] * np.sin(
            self.pitch
        )

        # Y compensation
        magYcomp = (
            self.xyz_mag[0] * np.sin(self.roll) * np.sin(self.pitch)
            + self.xyz_mag[1] * np.cos(self.roll)
            - self.xyz_mag[2] * np.sin(self.roll) * np.cos(self.pitch)
        )

        # Calculate heading
        self.norm_heading = np.arctan2(magYcomp, magXcomp) % (2 * np.pi)

