# ESP32-Controller
This repository houses all code used within my ESP32 Controller project. It consists of two Arduino-IDE based codes for ESP32, and two Python scripts written on VSCode for game mechanics.
The video showcase is in my youtube channel, linked here: https://youtu.be/ZSkPuP4Syzo 

I am still learning a lot about coding as well as hardware-based components, and so the code may be very rudimentary and barbaric compared to other complex scripts and algorithms. It's a passion of mine and any insight or advice would be greatly appreciated while I expand my knowledge!

# Arduino Code
There are two Arduino codes: One for the Controller itself, and one for the receiver ESP32 (also called the slave ESP32).

**Controller**

The Controller code is used to collect data from certain modules (Joystick, Push buttons) and send them over to the peer ESP32.
- Must be powered externally as it will function wirelessly
- Depending on orientation and pin initialization, the code can be customized to reflect that.
- Ensure Peer ESP32 Mac Address is correct or else ESP-NOW protocol will not work

**Recevier ESP32**

The receiver code (Slave code) is used to receive data, and transfer it over the serial port for the python scripts to use.
- Must be connected to the computer on a valid USB port where Serial Port works
- Install appropriate drivers if Serial Port doesn't work

# Python Scripts

The python scripts are coded uniquely to each game, as each game has different mechanics that cannot be transfered to a different game. This repository includes two scripts: one for Minecraft, and one for Sekiro: Shadows Die Twice.
The keystrokes are based upon virtual keyboard actions, simulating an actual keyboard. Mouse movement is based on Windows32 API for mouse events, and clicks are based on the Pynput library.

- Code can be modified accordingly to each game
- Integer array indexes can be swapped for different mechanics
- More statements can be added for additional events



