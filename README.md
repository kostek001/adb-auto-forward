# ADB Auto Forward

Automatically forward/reverse TCP ports using ADB on device connection.

#### Dependencies

- Python 3.8+
- `pyudev` Python module

## Installation

- **Linux** – download and run `adb-auto-forward.py`
- **Nix (flake)** – packaged at [`kostek001/nixos-pkgs`](https://github.com/kostek001/nixos-pkgs)

## Usage

```bash
python adb-auto-forward.py idVendor:idProduct,port1,port2
```

Ports may be prefixed by `f` for forward and `r` for reverse, if neither is set it will default to forward.

Example for Quest 3:

```bash
python adb-auto-forward.py 2833:0183,9943,9944,r9757
```

Can also be set for multiple devices:

```bash
python adb-auto-forward.py 1111:2222,f8888 3333:4444,f8899,r9999,r8989
```
