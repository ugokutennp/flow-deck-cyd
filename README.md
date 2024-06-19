# flow-deck-cyd
![thumbnail](primary/resources/logo.png)

## Overview
FlowDeckCYD is a system that displays VRChat join logs on a small tabletop display. It comprises two software packages:

### FlowDeckCYD Primary
This software retrieves VRChat's join logs and outputs them to a serial port.
- Outputs data to the CH340-named serial port.
- Runs in the system tray. Please add a shortcut to your Startup folder for automatic use.

### FlowDeckCYD Secondary
This software displays the information from the serial port on the screen.
- You can flash the firmware from the following page: [flow-deck-cyd Web Flasher](https://ugokutennp.github.io/flow-deck-cyd/)

## About Available CYDs
CYD stands for Cheap Yellow Display, a general term for modules featuring ESP32 and displays available at low cost from Chinese e-commerce sites. While there are several variations, the software is designed for the following specifications:
- 2.8-inch TFT display
- 240x320 pixels
- Resistive touch panel
- Using XPT2048 and ST7789
- Equipped with a USB-C port
