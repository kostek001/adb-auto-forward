# ADB Auto Forward

Automatically forward TCP ports using ADB on device connection

## Usage

```bash
python adb-auto-forward.py idVendor:idProduct,port1,port2
```

Example for Quest 3:

```bash
python adb-auto-forward.py 2833:0183,9943,9944
```

or multiple devices:
```bash
python adb-auto-forward.py 1111:2222,8888 3333:4444,8899,9999,8989
```