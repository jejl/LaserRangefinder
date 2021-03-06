
#Driver for the LSM303D accelerometer and magnetometer/compass

#First follow the procedure to enable I2C on R-Pi.
#1. Add the lines "i2c-bcm2708" and "i2c-dev" to the file /etc/modules
#2. Comment out the line "blacklist ic2-bcm2708" (with a #) in the file /etc/modprobe.d/raspi-blacklist.conf
#3. Install I2C utility (including smbus) with the command "apt-get install python-smbus i2c-tools"
#4. Connect the I2C device and detect it using the command "i2cdetect -y 1".  It should show up as 1D or 1E (here the variable LSM is set to 1D).


import time
from lsm303d import LSM303D
import numpy as np


lsm = LSM303D(0x1d)  # Change to 0x1e if you have soldered the address jumper

while True:
    xyz = lsm.accelerometer()
    xyz2 = lsm.magnetometer()

    heading = (180 * np.arctan2(xyz2[1], xyz2[0]) / np.pi) % 360

    print(("{:+06.2f} : {:+06.2f} : {:+06.2f} , heading = {:7.4f}").format(*xyz2, heading))
    print(("{:+06.2f}g : {:+06.2f}g : {:+06.2f}g").format(*xyz))

    time.sleep(1.0)

# #Driver by Fayetteville Free Library Robotics Group
#
# from smbus import SMBus
# busNum = 1
# b = SMBus(busNum)
#
# # Two accelerometers
# LSM_1 = 0x1d
# LSM_2 = 0x1e
#
# LSM_WHOAMI = 0b1001001 #Device self-id
#
# def twos_comp_combine(msb, lsb):
#     twos_comp = 256*msb + lsb
#     if twos_comp >= 32768:
#         return twos_comp - 65536
#     else:
#         return twos_comp
#
# #Control register addresses -- from LSM303D datasheet
#
# CTRL_0 = 0x1F #General settings
# CTRL_1 = 0x20 #Turns on accelerometer and configures data rate
# CTRL_2 = 0x21 #Self test accelerometer, anti-aliasing accel filter
# CTRL_3 = 0x22 #Interrupts
# CTRL_4 = 0x23 #Interrupts
# CTRL_5 = 0x24 #Turns on temperature sensor
# CTRL_6 = 0x25 #Magnetic resolution selection, data rate config
# CTRL_7 = 0x26 #Turns on magnetometer and adjusts mode
#
# #Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
# MAG_X_LSB = 0x08 # x
# MAG_X_MSB = 0x09
# MAG_Y_LSB = 0x0A # y
# MAG_Y_MSB = 0x0B
# MAG_Z_LSB = 0x0C # z
# MAG_Z_MSB = 0x0D
#
# #Registers holding twos-complemented MSB and LSB of magnetometer readings -- from LSM303D datasheet
# ACC_X_LSB = 0x28 # x
# ACC_X_MSB = 0x29
# ACC_Y_LSB = 0x2A # y
# ACC_Y_MSB = 0x2B
# ACC_Z_LSB = 0x2C # z
# ACC_Z_MSB = 0x2D
#
# #Registers holding 12-bit right justified, twos-complemented temperature data -- from LSM303D datasheet
# TEMP_MSB = 0x05
# TEMP_LSB = 0x06
#
#
# if b.read_byte_data(LSM_1, 0x0f) == LSM_WHOAMI:
#     print('LSM303D #1 detected successfully.')
# else:
#     print('No LSM303D #1 detected on bus {}.'.format(str(busNum)))
#
# if b.read_byte_data(LSM_2, 0x0f) == LSM_WHOAMI:
#     print('LSM303D #2 detected successfully.')
# else:
#     print('No LSM303D #2 detected on bus {}.'.format(str(busNum)))
#
# for LSM in ([LSM_1, LSM_2]):
#     b.write_byte_data(LSM, CTRL_1, 0b1010111) # enable accelerometer, 50 hz sampling
#     b.write_byte_data(LSM, CTRL_2, 0x00) #set +/- 2g full scale
#     b.write_byte_data(LSM, CTRL_5, 0b01100100) #high resolution mode, thermometer off, 6.25hz ODR
#     b.write_byte_data(LSM, CTRL_6, 0b00100000) # set +/- 4 gauss full scale
#     b.write_byte_data(LSM, CTRL_7, 0x00) #get magnetometer out of low power mode
#
# for LSM in ([LSM_1, LSM_2]):
#
#     magx = twos_comp_combine(b.read_byte_data(LSM, MAG_X_MSB), b.read_byte_data(LSM, MAG_X_LSB))
#     magy = twos_comp_combine(b.read_byte_data(LSM, MAG_Y_MSB), b.read_byte_data(LSM, MAG_Y_LSB))
#     magz = twos_comp_combine(b.read_byte_data(LSM, MAG_Z_MSB), b.read_byte_data(LSM, MAG_Z_LSB))
#
#     print("Magnetic field (x, y, z):", magx, magy, magz)
#
#     accx = twos_comp_combine(b.read_byte_data(LSM, ACC_X_MSB), b.read_byte_data(LSM, ACC_X_LSB))
#     accy = twos_comp_combine(b.read_byte_data(LSM, ACC_Y_MSB), b.read_byte_data(LSM, ACC_Y_LSB))
#     accz = twos_comp_combine(b.read_byte_data(LSM, ACC_Z_MSB), b.read_byte_data(LSM, ACC_Z_LSB))
#
#     print("Acceleration (x, y, z):", accx, accy, accz)
