# Hardware
* Leiterplatte mit 1x TM1637 und 6x VQB71

# Anwendungen
## MQTT bzw. Uhrzeit ohne Programmierung
Verwendung der [Tasmota](https://tasmota.github.io/docs/)-Firmware mit ESP8266 oder ESP32 und Anbindung an MQTT.

Tasmota Doku zum TM1637 Display-Treiber: https://tasmota.github.io/docs/TM163x/

### Anschluss bei Verwendung der **WEMOS D1** Hardware
Die 4 Pins der Display Platine können direkt 1:1 mit der **WEMOS D1** Hardware verbunden werden.
 
| WEMOS D1 mini | Display-Platine |
| ------------- | ------------- |
| 5V | VCC  |
| G | GND  | 
| D4 | DIO  | 
| D3 | CLK  | 

### Installation und Konfiguration der Firmware:
* Installation der Firmware "Tasmota Display" am einfachsten über den Chrom-Browser und https://tasmota.github.io/install/
* Configuration / Module type (Sonpoff Basic): **Generic (18)**
* D3 GPIO0: TM1637 CLK
* D4 GPIO0: TM1637 DIO

### Konfiguration der Display Parameter über die Console von Tasmota
Kommandos in der Console zu Anzeige der Uhrzeit:
```
power 1
displaymodel 15
displaywidth 6
displaytype 0
displaymode 1
displaydimmer 7
```

## Mit Programmierung
### Software
Software für Raspberry Pi Pico in MicroPython

![alt Leiterplatte Seite A](https://github.com/anthal/Display-VQB71-TM1637/blob/main/Pictures/TM1637-VQB71.png?raw=true)
![alt Leiterplatte Seite B](https://github.com/anthal/Display-VQB71-TM1637/blob/main/Pictures/TM1637-VQB71_b.png?raw=true)
![alt fertige Leiterplatte 1](https://github.com/anthal/Display-VQB71-TM1637/blob/main/Pictures/20230820_102546.jpg?raw=true)
