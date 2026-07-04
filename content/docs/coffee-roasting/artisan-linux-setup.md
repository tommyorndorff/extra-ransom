---
title: "Artisan on Headless Linux"
weight: 10
---

How to install and run [Artisan](https://artisan-scope.org/) on a headless Ubuntu server with a Phidget VINT Hub connected over USB, and control it remotely from a Mac on the same LAN.

## Hardware

- Ubuntu server (22.04 or 24.04 LTS, headless — no monitor attached)
- [Phidget VINT Hub](https://www.phidgets.com/?tier=3&catid=2&pcid=1&prodid=1202) (e.g. HUB0000_0) connected via USB
- Thermocouple module(s) plugged into VINT ports, e.g. [TMP1101](https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=726) (4-input K-type) or [TMP1100](https://www.phidgets.com/?tier=3&catid=14&pcid=12&prodid=725) (single)
- Mac on the same local network

---

## 1. Install the Phidget22 Library

Phidgets provides an apt repository for Ubuntu.

```bash
# Add the Phidget repo and install the library
curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo bash
sudo apt-get install -y libphidget22 libphidget22-dev libphidget22extra
```

If you prefer not to run the setup script, download the `.deb` directly from [phidgets.com/downloads](https://www.phidgets.com/downloads/phidget22/libraries/linux/).

---

## 2. USB Permissions (udev Rule)

By default, USB devices are only accessible to root. Add a udev rule so your user account can reach the Phidget Hub without sudo.

```bash
sudo tee /etc/udev/rules.d/99-phidgets.rules <<'EOF'
SUBSYSTEM=="usb", ACTION=="add", ATTR{idVendor}=="06c2", MODE="0664", GROUP="plugdev"
EOF

sudo udevadm control --reload-rules
sudo usermod -aG plugdev $USER
```

Log out and back in (or reboot) for the group change to take effect.

---

## 3. Confirm the Phidget Hub is Visible

Plug in the VINT Hub via USB, then:

```bash
# Check USB device is enumerated
lsusb | grep -i phidget
# Expected: Bus 00X Device 00X: ID 06c2:XXXX Phidgets Inc. ...

# Check permissions — should NOT require sudo
ls -la /dev/bus/usb/$(lsusb | grep 06c2 | awk '{print $2}')/ 2>/dev/null | grep $(lsusb | grep 06c2 | awk '{print $4}' | tr -d :)
# Look for rw- for group plugdev, and that your user is in that group:
groups $USER | grep plugdev
```

If `lsusb` doesn't show a Phidget device, try a different USB port or cable, or check `dmesg | tail -20` after plugging in.

---

## 4. Install a Virtual Display

Artisan is a Qt GUI app — it needs a display even on a headless server. `Xvfb` provides a virtual framebuffer that satisfies this requirement without any physical screen.

```bash
sudo apt-get install -y xvfb
```

---

## 5. Install Artisan

Download the latest `.deb` package from the [Artisan releases page](https://github.com/artisan-roaster-scope/artisan/releases). Look for the file ending in `_amd64.deb` (or `_arm64.deb` for ARM servers like a Raspberry Pi).

```bash
# Example — replace with the actual latest version number
ARTISAN_VERSION=2.10.5
wget "https://github.com/artisan-roaster-scope/artisan/releases/download/v${ARTISAN_VERSION}/artisan-linux-${ARTISAN_VERSION}_amd64.deb"
sudo apt-get install -y "./artisan-linux-${ARTISAN_VERSION}_amd64.deb"
```

Artisan installs to `/usr/bin/artisan`.

---

## 6. First Launch and Phidget Configuration

Start Artisan with a virtual display:

```bash
Xvfb :1 -screen 0 1280x800x24 &
export DISPLAY=:1
artisan
```

Artisan's window is now running on the virtual display. To interact with it from your Mac, see [Remote Access from macOS](#remote-access-from-macos) below.

Once you can see the UI (via VNC or the web interface):

1. Go to **Config > Device** and set the device to **Phidget**.
2. Select the appropriate module type for your thermocouple board (e.g. TMP1101).
3. Assign channels to ET (environmental temperature) and BT (bean temperature).
4. Click **OK** and then **ON** in the main toolbar — you should see live temperature readings.

---

## 7. Confirm Artisan Sees the Phidget

If Artisan connects successfully, the main toolbar will show live ET and BT readings and the status bar will show "PHIDGET" without error.

If it fails:
- Check `dmesg | grep -i phidget` for USB errors
- Verify `groups $USER` includes `plugdev`
- Try running `artisan` with `sudo` temporarily to confirm it's a permissions issue, not a hardware one
- Check Artisan's log: **Help > Errors**

---

## 8. Run as a Systemd Service

To have Artisan start automatically at boot:

```bash
sudo tee /etc/systemd/system/artisan.service <<'EOF'
[Unit]
Description=Artisan Roaster Scope
After=network.target

[Service]
User=YOUR_USERNAME
Environment=DISPLAY=:1
ExecStartPre=/usr/bin/Xvfb :1 -screen 0 1280x800x24
ExecStart=/usr/bin/artisan
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable artisan
sudo systemctl start artisan
```

Replace `YOUR_USERNAME` with the account that has `plugdev` access.

Check status:
```bash
sudo systemctl status artisan
journalctl -u artisan -f
```

---

## Remote Access from macOS

### Option A: Artisan WebServer (browser-based, recommended)

Artisan has a built-in HTTP server that serves a live roast view.

1. In Artisan, go to **Config > WebServer**.
2. Enable the web server and note the port (default: **8080**).
3. From your Mac, open a browser and navigate to:

```
http://<server-ip>:8080
```

You'll see a live roast graph and temperature readings. This is read-only — you can monitor but not control the roast from the browser.

To find your server's IP:
```bash
ip addr show | grep 'inet ' | grep -v 127.0.0.1
```

### Option B: VNC (full remote desktop control)

Install a VNC server on the Ubuntu machine to get full control of Artisan's UI.

```bash
sudo apt-get install -y tigervnc-standalone-server

# Start VNC on display :1 (same display Artisan is running on)
vncserver :1 -geometry 1280x800 -depth 24
```

Connect from your Mac using **Screen Sharing** (built-in) or [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/):

- Host: `<server-ip>:5901`

### Option C: SSH X11 Forwarding

If you have XQuartz installed on your Mac:

```bash
ssh -X user@server-ip artisan
```

Artisan's window will appear on your Mac. Useful for occasional config changes, but VNC is more practical for active roasting.

---

## Confirming Everything Works End-to-End

1. **Phidget visible**: `lsusb | grep 06c2` shows the hub
2. **Group permissions**: `groups $USER` includes `plugdev`
3. **Artisan running**: `systemctl status artisan` shows active, or `ps aux | grep artisan`
4. **Live data**: Xvfb display shows ET/BT readings in Artisan toolbar (check via VNC)
5. **WebServer**: `curl http://localhost:8080` returns HTML from the server machine itself
6. **Remote access**: From Mac, browser opens `http://<server-ip>:8080` and shows a live roast display
