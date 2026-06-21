# KeepAlive_2.4G

A utility that keeps wireless headphones from auto-disconnecting.

## The Problem
Many 2.4 GHz wireless headphones with a USB dongle or Bluetooth headphones automatically turn off when there is no sound.
You have to constantly reconnect them manually, which is annoying, especially when they're OEM headphones without its own software.

## The Solution
KeepAlive sends an inaudible audio pulse every 299 seconds.
The headphones "think" there is sound playing and stay connected.

## How to Use
1. Download `KeepAlive 2.4G.zip` from the [Releases](https://github.com/...) section and unzip it.
2. Before launching, select your headphones as the output device in Windows.
3. Launch the app, click "Run".
4. Minimize to system tray by clicking "Hide" — the app runs quietly in the background.

## Build from Source
```bash
pip install -r requirements.txt
python keepalive.py

Tech Stack:

Python 3
Tkinter (UI)
Pygame (audio)
NumPy (signal generation)
Pystray (system tray icon)
