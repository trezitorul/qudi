from datetime import datetime
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
from TLPM import TLPM
import time

class PowerMeter:
    def __init__(self):
        # Find and print connected power meter devices.
        #Initialize deviceCount
        
        self.tlPM = TLPM()
        self.deviceCount = c_uint32()
        self.tlPM.findRsrc(byref(self.deviceCount))

        print("Number of found devices: " + str(self.deviceCount.value))
        print("")

        self.resourceName = create_string_buffer(1024)

        for i in range(0, self.deviceCount.value):
            self.tlPM.getRsrcName(c_int(i), self.resourceName)
            print("Resource name of device", i, ":", c_char_p(self.resourceName.raw).value)
        print("")
        self.tlPM.close()

    def open(self, i, IDQuery = True, resetDevice = True):
        #i is an integer between 0 and self.deviceCount - 1 representing the device index to open
        #IDQuery (c_bool):This parameter specifies whether an identification query is performed during the initialization process.
		#resetDevice (c_bool):This parameter specifies whether the instrument is reset during the initialization process.
        if i not in range(0, self.deviceCount.value):
            print(f"Device index {i} out of range [0,{self.deviceCount.value}]")
        else:
            self.tlPM.getRsrcName(c_int(i), self.resourceName)
            self.tlPM = TLPM()
            self.tlPM.open(self.resourceName, c_bool(IDQuery), c_bool(resetDevice))

            message = create_string_buffer(1024)
            self.tlPM.getCalibrationMsg(message)
            print("Connected to device", i)
            print("Last calibration date: ",c_char_p(message.raw).value)
            print("")

            time.sleep(0.1) #minimize?

    def setMeterWavelength(self, desiredWavelength):
        # Set wavelength to wavelength in nm.
        #self.wavelength = c_double(desiredWavelength)
        self.tlPM.setWavelength(c_double(desiredWavelength))

    def setMeterPowerAutoRange(self, powerAutoRange):
        # Enables or disenables auto-range mode
        # 0 -> auto-range disabled
        # 1 -> auto-range enabled
        self.tlPM.setPowerAutoRange(c_int16(powerAutoRange))

    def setMeterPowerUnit(self, powerUnit):
        # Set power unit to Watts or dBm
        # 0 -> Watt
        # 1 -> dBm
        self.tlPM.setPowerUnit(c_int16(powerUnit))
    
    def getMeasurement(self):
        #Returns current power measurement
        power =  c_double()
        self.tlPM.measPower(byref(power))
        power_measurement = power.value
        time = datetime.now()
        #print(time, ":", power_measurement, "W")
        #print("")
        return power_measurement

    def getMeasurements(self, measurementCount, sleepTime):
        # Gets a specified number of elements every specified unit of time and outputs an array of measurements
        # measurementCount (int) is the number of measurements to collect
        # sleepTime is the time between each measurement in seconds. 
        # Take power measurements and save results to arrays.
        power_measurements = []
        times = []
        count = 0
        while count < measurementCount:
            power =  c_double()
            self.tlPM.measPower(byref(power))
            power_measurements.append(power.value)
            times.append(datetime.now())
            #print(times[count], ":", power_measurements[count], "W,", count+1, "out of", measurementCount, "measurements complete")
            count+=1
            time.sleep(sleepTime)
        #print("")
        return times, power_measurements

    def close(self):
        # Close power meter connection.
        self.tlPM.close()
        print("Meter succesfully closed")