# Quellen:
# NTP: https://www.elektronik-kompendium.de/sites/raspberry-pi/2708151.htm
# TM1637: https://github.com/mcauser/micropython-tm1637


# Bibliotheken laden
import machine
import network
import sys
import time
import usocket as socket
import ustruct as struct
import tm1637_6dig
from mqtt_simple import MQTTClient

# Objekte:
rtc = machine.RTC()
from machine import Pin

tm1 = tm1637_6dig.TM1637(clk=Pin(0), dio=Pin(1))
tm2 = tm1637_6dig.TM1637(clk=Pin(2), dio=Pin(3))
tm3 = tm1637_6dig.TM1637(clk=Pin(4), dio=Pin(5))

# WLAN-Konfiguration
wlanSSID = 'anth-0'
wlanPW = 'anthal-17!'
network.country('DE')

# MQTT-Konfiguration
mqttBroker = '192.168.0.144'
mqttClient = 'RasPiPico'
mqttUser = 'mqtt'
mqttPW = 'mqtt1'
mqttTopic = b"cmnd/7seg/displaytext"

# Winterzeit / Sommerzeit
#GMT_OFFSET = 3600 * 1 # 3600 = 1 h (Winterzeit)
GMT_OFFSET = 3600 * 2 # 3600 = 1 h (Sommerzeit)

# Status-LED
led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)

# NTP-Host
#NTP_HOST = 'pool.ntp.org'
NTP_HOST = '192.168.0.1'

# Funktion: WLAN-Verbindung
def wlanConnect():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('WLAN-Verbindung herstellen')
        wlan.active(True)
        wlan.connect(wlanSSID, wlanPW)
        for i in range(10):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            print('.', end='')
            tm1.number(i)
            time.sleep(1)
    if wlan.isconnected():
        print('WLAN-Verbindung hergestellt')
        tm2.show('NET OK')
        led_onboard.on()
    else:
        print('Keine WLAN-Verbindung')
        tm2.show('NO NET')
        led_onboard.off()
    print('WLAN-Status:', wlan.status())
    tm1.number(wlan.status())
    time.sleep(1)


# Funktion: Zeit per NTP holen
def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)                                                                                                                                        
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)


# Funktion: RTC-Zeit setzen
def setTimeRTC():
    # NTP-Zeit holen
    tm = getTimeNTP()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


# Funktion: RTC-Zeit holen:
def getTimeRTC():
    return rtc.datetime() # get date and time
    
    
# Callback-Funktion: Empfang einer MQTT-Nachricht
def mqttDo(topic, msg):
    # Onboard-LED-Toggle
    led_onboard.toggle()
    # MQTT-Nachricht ausgeben
    print("Topic: %s, Wert: %s" % (topic, int(msg)))
    # Anzeige des Wohnungsleistungsaufnahme über MQTT:
    tm3.number(int(msg))
    
    
# Funktion: Verbindung zum MQTT-Server herstellen
def mqttConnect():
    if mqttUser != '' and mqttPW != '':
        print("MQTT-Verbindung herstellen: %s mit %s als %s" % (mqttClient, mqttBroker, mqttUser))
        client = MQTTClient(mqttClient, mqttBroker, port=1883, user=mqttUser, password=mqttPW,  keepalive=100, ssl=False, ssl_params={})
        print(mqttTopic)
    else:
        print("MQTT-Verbindung herstellen: %s mit %s" % (mqttClient, mqttBroker))
        client = MQTTClient(mqttClient, mqttBroker)
    # Registrierung der CallBack Funktion:
    client.set_callback(mqttDo)
    client.connect()
    client.subscribe(mqttTopic)
    print('MQTT-Verbindung hergestellt')
    return client

############################################################################
# Hauptprogramm
############################################################################
# all LEDS off
tm1.write([0, 0, 0, 0, 0 ,0])
tm2.write([0, 0, 0, 0, 0 ,0])
tm3.write([0, 0, 0, 0, 0 ,0])

tm1.show('WLAN')
tm2.show('search')
tm3.show('HALLO')
#time.sleep(10)

# WLAN-Verbindung herstellen
wlanConnect()

# Zeit setzen
setTimeRTC()

# MQTT-Verbindungsaufbau
try:
    client = mqttConnect()
    # 
    client.subscribe(topic=mqttTopic)
    print("Subscribe: %s" %  mqttTopic)
    # Warten auf Nachrichten
    while True:
        client.check_msg()
        date_time = getTimeRTC()
        day = date_time[2]
        month = date_time[1]
        year = date_time[0]
        hour = date_time[4]
        minute = date_time[5]
        secound = date_time[6]
        print("{0:02}.{1:02}.{2:02}".format(day, month, year -2000), end=' - ')
        print("{0:02}:{1:02}:{2:02}".format(hour, minute, secound))
        tm1.numbers(hour, minute, secound)
        #time.sleep(3)
        tm2.numbers(day, month, year - 2000)
        time.sleep(1)            

except OSError:
    print('Fehler: Keine MQTT-Verbindung')
    



