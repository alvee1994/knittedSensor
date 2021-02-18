#!/usr/bin/env python3

import numpy as np
import yaml
from bluepy import btle
import binascii
import os.path
from bluepy.btle import Scanner, DefaultDelegate
import os, csv, sys
import logging

# for live plotting
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time, datetime
from collections import deque

# multiprocessing
from multiprocessing import Process, Pipe

""" this section is to setup the logger """
formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(message)s',datefmt='%Y-%m-%d,%H:%M:%S')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # process everything, even if everything isn't printed
logfilename = 'kneebrace_' + datetime.datetime.now().strftime("%f") + '.log'

fh = logging.FileHandler(logfilename)
fh.setLevel(logging.DEBUG) # or any level you want
fh.setFormatter(formatter)

logger.addHandler(fh)
""" end of the logging setup """

class BLEDelegate(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)
        self.val = [0,1,2,3]

    def handleNotification(self, cHandle, data):
        decimalValue = (binascii.b2a_hex(data))
        splitted = [decimalValue[i:i+4] for i in range(0, len(decimalValue),4)]
        self.val = np.array(list(map(lambda x: int((x),16)/1000, splitted)))
        # self.val = np.insert(self.val, 0, )
        #idx = np.nonzero(self.val)
        #self.val = self.val[idx]
        BLEDevice.sensors = self.val

class BLEDevice():
    """
    the initiated peripheral itself
    """
    peripheralsInUse = []
    sensors = []
    characteristicUUID = ''
    serviceUUID = ''
    figures = []
    xs = deque(maxlen=20)
    ys = deque(maxlen=20)


    def __init__(self):
        pass


    def scanAndConnect(self):
        # initiate scanner to scan and filter bluetooth devices with the following parameters
        params = {'hci': 0,
                  'timeout': 4,
                  'sensitivity': -128,
                  'discover': True,
                  'all': True,
                  'new': True,
                  'verbose': True}

        scanner = Scanner().withDelegate(BLEDelegate(params))
        devices = scanner.scan(3)
        listOfPeripheralsAvailable = []
        devName, devAdds = self.listRelevantPeripherals()

        for dev in devices:
            for (sdid, desc, val) in dev.getScanData():
                if val == devName:
                    listOfPeripheralsAvailable.append(dev.addr)
        
        if (len(listOfPeripheralsAvailable) > 0):
            addr = self.selectDevices(devName, devAdds, listOfPeripheralsAvailable)
            for address in addr:
                self.connectOnePeripheral(address)
            return True
        else:
            print("No peripherals found.\n Exiting")
            return False

    def selectDevices(self, _devName, _devAdds, _listOfPeripheralsAvailable):
        print('Select a %s to connect to\n' %(_devName))
        for i in range(len(_listOfPeripheralsAvailable)):
            if _listOfPeripheralsAvailable[i] in _devAdds.keys():
                print('\t %i. %s' % (i, _devAdds[_listOfPeripheralsAvailable[i]]))
            else:
                print('\t %i. Unknown, addr: %s' % (i, _listOfPeripheralsAvailable[i]))

        selected = input('\nSelect sensor (e.g. 0 for 0th sensor or 02 for 0th and 2nd sensor):')
        selected = [int(a) for a in selected]
        if len(selected) <= len(_listOfPeripheralsAvailable):
            _addr = [_listOfPeripheralsAvailable[a] for a in selected]
            return _addr
        elif len(selected) > 4 or len(selected) > len(_listOfPeripheralsAvailable):
            print("\nMore devices selected than present. Try again")
            self.selectDevices(_devName, _devAdds, _listOfPeripheralsAvailable)



    def listRelevantPeripherals(self):
        # get name of known peripherals from yaml file
        knownPeripherals = open(os.getcwd() + "/knownPeripherals.yaml")
        kP = yaml.load(knownPeripherals, Loader=yaml.FullLoader)
        deviceName = list(kP.keys())[0]
        devAdds = kP[deviceName]
        self.serviceUUID = kP['Service']
        self.characteristicUUID = kP['Characteristic']
        return deviceName, devAdds

    def connectOnePeripheral(self, addr):
        p = btle.Peripheral(addr)
        p.withDelegate(BLEDelegate(p))
        self.peripheralsInUse.append(p)
        print('connected to %s ' % addr)
        self.turnOnNotifications()
        return True


    def turnOnNotifications(self):
        for peripheral in self.peripheralsInUse:
            for svc in peripheral.getServices():
                if svc.uuid == self.serviceUUID:
                    service = peripheral.getServiceByUUID(self.serviceUUID)
                    char = [c for c in service.getCharacteristics() if (c.uuid == self.characteristicUUID)]
                    handle = char[0].valHandle
                    peripheral.writeCharacteristic(handle + 1, b'\x01\x00')

    def readSensors(self):
        if len(self.peripheralsInUse) == 1:
            for p in self.peripheralsInUse:
                if p.waitForNotifications(1.0):
                    return p.addr, self.sensors
                    continue

    def readBleSensors(self, record = False):
        try:
            while(1):
                addr, data = self.readSensors();
                logger.debug(data)
                print(data)

                # if record:
                #
                #     with open('capturedData.csv', 'a') as outfile:
                #         addr, data = self.readSensors();
                #         data = np.insert(data, 0, time.process_time())
                #         print(data)
                #         writer = csv.writer(outfile)
                #         writer.writerow(data)
                # else:
                #     addr, data = self.readSensors();
                #     print(time.process_time(), data)

                ## convert for sam
                # data = self.toFloat(data)

        except KeyboardInterrupt:
            self.disconnect()
            quit()



    def toFloat(self, alldata):
        a = [np.interp(af*1000, [0, 65356], [-2, 2]) for af in alldata[:3]]
        g = [np.interp(gf*1000, [0, 4096], [-500, 500]) for gf in alldata[3:]]
        return np.append(a, g)

    def disconnect(self):
        print("\ndisconnecting all peripherals\n")
        for p in self.peripheralsInUse:
            p.disconnect()
        print("disconnected")



if __name__ == "__main__":
    # initialize smart glove
    KneeBrace = BLEDevice()
    if KneeBrace.scanAndConnect():
        try:
            if (len(sys.argv) > 1 and sys.argv[1] == 'record'):
                KneeBrace.readBleSensors(record = True)
            else:
                KneeBrace.readBleSensors()
        except KeyboardInterrupt:
            KneeBrace.disconnect()
            quit()
    else:
        quit()
    










