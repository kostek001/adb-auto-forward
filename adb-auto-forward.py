#!/usr/bin/env python3

import os
import pyudev
import argparse


parser = argparse.ArgumentParser(
    prog="ADB Auto Forward", description="Automatically forward TCP ports using ADB on device connection")
parser.add_argument('device_conf', nargs='+',
                    help='an device \'idVendor:idProduct\' + ports(one or more), divided by \',\' example: 2833:0183,9943,9944')
args = parser.parse_args()


class DeviceConf:
    def __init__(self, a):
        self.id = a[0]
        if (len(self.id.split(':')[0]) != 4) or (len(self.id.split(':')[1]) != 4):
            raise Exception("Invalid id argument, example 2833:0183,9943,9944")

        self.ports = a[1:]
        if len(self.ports) == 0:
            raise Exception("No ports set, example 2833:0183,9943,9944")
        for p in self.ports:
            if not p.isnumeric():
                raise TypeError(
                    "Ports can only be an int, example 2833:0183,9943,9944")
            if (int(p) < 1024) or (int(p) > 49151):
                raise Exception(
                    "Ports only allowed in range 1024-49151, example 2833:0183,9943,9944")


deviceConfigs = []
for a in args.device_conf:
    deviceConfigs.append(DeviceConf(a.split(",")))


def addZeros(v):
    out = ""
    for _ in range(4 - len(v)):
        out += "0"
    return out + v


def usbEvent(action, device):
    ids = device.properties["PRODUCT"].split("/")
    deviceId = addZeros(ids[0]) + ":" + addZeros(ids[1])
    if (action == "bind"):
        for d in deviceConfigs:
            if (deviceId == d.id):
                serial = device.attributes.get("serial").decode("ASCII")
                print("Device", serial, "connected")
                try:
                    if os.popen("timeout 10 adb -s " + serial + " wait-for-device && echo OK").read().rstrip() != "OK":
                        raise Exception("ADB timeout")
                    for p in d.ports:
                        if os.popen("adb -s " + serial + " forward tcp:" + p + " tcp:" + p).read().rstrip() != p:
                            raise Exception(p + " forward failed")
                    print("Device", serial, ','.join(d.ports), "forwarded")
                except Exception as e:
                    print("Device", serial, e)


context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="usb")
observer = pyudev.MonitorObserver(monitor, usbEvent)
observer.start()

os.system("adb start-server")

try:
    while True:
        pass
except KeyboardInterrupt:
    pass

exit()
