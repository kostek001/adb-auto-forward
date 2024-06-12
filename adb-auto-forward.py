#!/usr/bin/env python3

import os
import pyudev
import argparse
import signal


parser = argparse.ArgumentParser(
    prog="ADB Auto Forward", description="Automatically forward/reverse TCP ports using ADB on device connection")
parser.add_argument('device_conf', nargs='+',
                    help='an device \'idVendor:idProduct\' + ports(one or more, prefixed by \'f\' for forward and \'r\' for reverse, if neither is set it will default to forward), divided by \',\' example: 2833:0183,9943,9944,r9757')
args = parser.parse_args()


class Port:
  def __init__(self, i):
    self.type = "reverse" if (i[0] == 'r') else "forward"
    self.port = i[1:] if ((i[0] == 'r') or (i[0] == 'f')) else i

    if not self.port.isdecimal():
      raise Exception(
          "Port must be decimal value, example: 2833:0183,9943,9944")
    elif int(self.port) < 1 or int(self.port) > 65535:
      raise Exception("Port must be in 1-65535 range")


def Id(i):
  id = i.split(':')
  if len(id) != 2:
    raise Exception("Invalid id argument, example: 2833:0183,9943,9944")
  # Check if hex + remove zeros

  def getHex(i):
    if (len(i) > 4):
      raise Exception("Invalid id argument, example: 2833:0183,9943,9944")
    return hex(int(i, 16))[2:]

  return list(map(getHex, id))


class DeviceConf:
  def __init__(self, i):
    self.id = Id(i[0])

    if len(i[1:]) == 0:
      raise Exception("No ports set, example: 2833:0183,9943,9944")
    self.ports = list(map(Port, i[1:]))


deviceConfigs = []
for a in args.device_conf:
  deviceConfigs.append(DeviceConf(a.split(",")))


def usbEvent(action, device):
  ids = device.properties["PRODUCT"].split("/")
  deviceId = ids[:2]
  if (action == "bind"):
    for d in deviceConfigs:
      if (deviceId == d.id):
        serial = device.attributes.get("serial").decode("ASCII")
        print("Device", serial, "connected")
        try:
          # Check if ADB works
          if os.popen(f"timeout 10 adb -s {serial} wait-for-device && echo OK").read().rstrip() != "OK":
            raise Exception("ADB timeout")

          # Forward/reverse ports
          for p in d.ports:
            if os.popen(f"adb -s {serial} {p.type} tcp:{p.port} tcp:{p.port}").read().rstrip() != p.port:
              raise Exception(f"{p.port} {p.type} failed")

          print("Device", serial, ','.join(
              map(lambda i: i.port, d.ports)), "forwarded")
        except Exception as e:
          print("Device", serial, e)


context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="usb")
observer = pyudev.MonitorObserver(monitor, usbEvent)
observer.start()

os.system("adb start-server")

signal.pause()

exit()
