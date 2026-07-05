---
title: "Artisan on Headless Linux"
weight: 10
---

How to set up a headless Ubuntu server as a Phidget sensor hub, so that
[Artisan](https://artisan-scope.org/) running on your Mac can read the
VINT thermocouples as if they were plugged in locally.

**Architecture**: the Ubuntu server runs the **Phidget Network Server** — a
lightweight daemon that makes all attached Phidget devices available over the
LAN via WebSockets on port 5661. The Mac's Phidget22 library discovers it
automatically, and Artisan sees the remote sensors transparently. No Artisan
instance, no virtual display, and no VNC needed on the server.

```
[Phidget VINT Hub] --USB--> [Ubuntu server]
                                  |
                          phidget22networkserver
                          (WebSocket, port 5661)
                                  |
                              LAN/WiFi
                                  |
                            [MacBook]
                          Artisan + Phidget22
                          (reads sensors as local)
```

## Hardware

- Ubuntu server (22.04 or 24.04 LTS, headless)
- [Phidget VINT Hub](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=1202) (e.g. HUB0000_0) connected via USB
- Thermocouple module(s) in VINT ports — e.g. [TMP1101](https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=726) (4-input K-type) or [TMP1100](https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=725) (single)
- Mac on the same local network

---

## 1. Install the Phidget22 Library and Network Server

Phidgets provides an apt repository for Ubuntu.

```bash
# Add the Phidget repo
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo bash

# Install the library and the network server daemon
sudo apt-get install -y libphidget22 libphidget22extra phidget22networkserver
```

If you prefer not to run the setup script, download the packages directly
from [phidgets.com/downloads](https://www.phidgets.com/downloads/phidget22/libraries/linux/).

---

## 2. USB Permissions (udev Rule)

By default, USB devices are only accessible to root. Add a udev rule so the
network server process can reach the Phidget Hub without running as root.

```bash
sudo tee /etc/udev/rules.d/99-phidgets.rules <<'EOF'
SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="06c2", MODE="0664", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules

# Add the user that will run phidget22networkserver to plugdev
sudo usermod -aG plugdev $USER
```

Log out and back in (or reboot) for the group change to take effect.

---

## 3. Confirm the Phidget Hub is Visible

Plug in the VINT Hub, then verify USB enumeration and permissions:

```bash
# Device should appear
lsusb | grep -i phidget
# Expected: Bus 00X Device 00X: ID 06c2:XXXX Phidgets Inc.

# Your user should be in plugdev
groups $USER | grep plugdev

# Quick permission check — should print the device file with group rw
ls -la /dev/bus/usb/$(lsusb | grep 06c2 | awk '{print $2,$4}' | awk '{printf "%s/%03d\n", $1, $2+0}' 2>/dev/null) 2>/dev/null || \
  echo "check dmesg | tail -20 if device not found"
```

If `lsusb` doesn't show a Phidget, try a different USB port, check
`dmesg | tail -20` immediately after plugging in, or try a different cable.

---

## 4. Run the Phidget Network Server

The `phidget22networkserver` package installs a systemd unit. Enable and start
it, open the firewall port, then verify the server is listening:

```bash
sudo systemctl enable phidget22networkserver
sudo systemctl start phidget22networkserver

sudo ufw allow 5661/tcp
sudo ufw reload

sudo systemctl status phidget22networkserver
ss -tlnp | grep 5661
# Expected: LISTEN  0  ... 0.0.0.0:5661
```

The server listens on **port 5661** and publishes all connected Phidget devices
over a WebSocket interface. It also advertises itself via mDNS/Bonjour so the
Mac's Phidget22 library can discover it without needing a static IP.

### Server IP

Note the server's LAN IP — you'll need it if mDNS discovery doesn't work on
your network:

```bash
ip addr show | grep 'inet ' | grep -v 127.0.0.1
```

---

## 5. Configure Artisan on macOS

### Install the Phidget22 drivers on your Mac

The Mac needs the Phidget22 library to talk to the network server. Download
and install the macOS package from
[phidgets.com/downloads](https://www.phidgets.com/downloads/phidget22/libraries/macos/).

You do **not** need to physically attach any Phidget to the Mac.

### Open Artisan and configure the device

1. Launch Artisan on your Mac.
2. Go to **Config > Device**.
3. In the device list, select the Phidget module that matches your
   thermocouple board — e.g. **Phidget TMP1101** for a 4-input K-type board.
4. Set the channel assignments for ET (environmental/drum temp) and BT
   (bean temperature) to match how your thermocouples are wired to the VINT ports.
5. Click **OK**.

### Auto-discovery (same LAN, mDNS)

If your Mac and the Ubuntu server are on the same subnet, the Phidget22 library
discovers the network server automatically via Bonjour. No further config
needed — just press **ON** in Artisan's toolbar and you should see live ET/BT
readings within a few seconds.

### Manual server address (if mDNS doesn't work)

If auto-discovery fails (e.g. across VLANs, or mDNS is blocked), set the
server address explicitly. Open a terminal on your Mac and add the server:

```bash
# Run once — registers the server address persistently with the Phidget22 library
/usr/local/bin/phidget22admin -a <server-ip>
```

Or set it within Artisan: **Config > Device**, look for a **Server** or
**Remote** field and enter `<server-ip>:5661`.

---

## Confirming Everything Works

**On the Ubuntu server:**

```bash
# 1. Phidget hub is enumerated
lsusb | grep 06c2

# 2. Network server is running and listening
systemctl is-active phidget22networkserver
ss -tlnp | grep 5661
```

**From the Mac:**

```bash
# 3. Port is reachable from the Mac
nc -zv <server-ip> 5661
# Expected: Connection to <server-ip> port 5661 [tcp] succeeded!
```

**In Artisan (Mac):**

4. Press **ON** — ET and BT should populate within a few seconds.
5. The status bar should show the Phidget device name without an error icon.
6. Wiggle a thermocouple gently — the temperature reading should respond.

**Troubleshooting:**

| Symptom | Check |
|---|---|
| `lsusb` shows no Phidget | `dmesg | tail -20` after plugging in; try different USB port |
| networkserver fails to start | `journalctl -u phidget22networkserver` — likely a permissions issue; verify `plugdev` group |
| Port 5661 not reachable from Mac | `sudo ufw status`; confirm server IP is correct |
| Artisan shows no readings | Confirm Phidget22 drivers installed on Mac; try `phidget22admin -a <ip>` to force address |
| ET/BT swapped | Swap channel assignments in **Config > Device** |
