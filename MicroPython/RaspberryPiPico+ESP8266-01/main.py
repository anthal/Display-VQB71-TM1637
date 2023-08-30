"""

"""
import uos
import utime
#import machine
import tm1637_6dig

from machine import UART
from machine import Pin
from machine import WDT
from machine import RTC
from machine import Timer
#import micropython

# Winterzeit / Sommerzeit
#GMT_OFFSET = 1 # 1 h (Winterzeit)
GMT_OFFSET = 2 # 2 h (Sommerzeit)

# NTP-Host
#NTP_HOST = 'pool.ntp.org'
NTP_HOST = '192.168.0.1'

# Onboard-LED:
led = Pin(25, Pin.OUT)

class SERIAL():

    def init(self):
        """
        Init
        """
        #self.uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), bits=8, parity=None, stop=1, txbuf=256, flow=0)
        self.uart0 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1, txbuf=256, flow=0)
        #self.uart0 = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9), bits=8, parity=None, stop=1, txbuf=256, flow=0)
        print("Machine:     " + uos.uname()[4])
        print("MicroPython: " + uos.uname()[3])
        #print(micropython.mem_info())
        # all LEDS off
        tm1.write([0, 0, 0, 0, 0 ,0])
        tm2.write([0, 0, 0, 0, 0 ,0])
        tm3.write([0, 0, 0, 0, 0 ,0])


    def send_at_cmd(self, at_cmd, debug=False):
        """
        Sende AT Kommando an GSM-Modul
        """
        txData = b'AT{}\r\n'.format(at_cmd)
        # Sende den Puffer mit Bytes:
        self.uart0.write(txData)
        if debug:
            print("Send: 'AT{}'".format(at_cmd))


    def read_answer(self, line=True):
        """
        Hole Antwort vom GSM-Modul
        
        :line:
        * True - Use of readline from UART
        * False - Use of read one character from UART 
        """
        rx_data_dec_list = []
        rxData = bytes()
        # "any": Anzahl der Bytes im Empfangspuffer:
        #print(self.uart0.any())
        # Für anspruchsvollere Abfragen der verfügbaren Zeichen verwenden Sie select.poll
        while self.uart0.any() > 0:
            #led_blink()
            if line:
                # Hole alle Bytes einer Zeile:
                rxData = self.uart0.readline()
            else:
                # Hole ein Byte:
                rxData = self.uart0.read(1)
            # print(rxData)

            try:
                rx_data_dec = rxData.decode('utf-8')
            except:
                print("Unicode-Error in '{}'".format(rxData))
                rx_data_dec = ""
                # return None

            if line:
                rx_data_dec_list.append(rx_data_dec[:-2])
            else:
                rx_data_dec_list.append(rx_data_dec)

            # Reset Watchdog:
#            wdt.feed()

        #if line:
        #    if rx_data_dec_list:
        #        print(rx_data_dec_list)
        return rx_data_dec_list


    def wait_of_ser_line(self, wait_string, debug=False):
        """
        Warte auf Zeile wait_string vom GSM Modul

        """
        ret_list = self.read_answer()
        if ret_list:
            if debug:
                print("read_answer: " + str(ret_list))
        i = 0
        while (wait_string not in ret_list):
            ret_list = self.read_answer()
            if ret_list:
                if debug:
                    print("read_answer: " + str(ret_list))
            if ret_list and "ERROR" in ret_list:
                return("ERROR")
            #if not ret_list:
            #    return("Keine verwertbare Antwort vom GSM Modul")
            utime.sleep(0.1)
            i += 1
            # print(i)
            led_blink()

            if i > 10:
                if not ret_list:
                    return("Keine Antwort vom ESP-Modul!")
                else:
                    return("'" + wait_string + "' nicht gefunden!")

        return(ret_list)


def led_blink(on_time=0.1):
    led.value(1)
    utime.sleep(on_time)
    led.value(0)


def get_month_num(month):
    if month == "Jan":
        return 1
    if month == "Feb":
        return 2
    if month == "Mar":
        return 3
    if month == "Apr":
        return 4
    if month == "Mai":
        return 5
    if month == "Jun":
        return 6
    if month == "Jul":
        return 7
    if month == "Aug":
        return 8
    if month == "Sep":
        return 9
    if month == "Okt":
        return 10
    if month == "Nov":
        return 11
    if month == "Dec":
        return 12

####################################################################
# MAIN
####################################################################
# Add Objekte:
ser = SERIAL()
rtc = RTC()

tm1 = tm1637_6dig.TM1637(clk=Pin(0), dio=Pin(1))
tm2 = tm1637_6dig.TM1637(clk=Pin(2), dio=Pin(3))
tm3 = tm1637_6dig.TM1637(clk=Pin(4), dio=Pin(5))

ser.init()

tm1.show('000000')
tm2.show('000000')
tm3.show('unsync')

tm1.numbers(0, 0, 0)
tm2.numbers(0, 0, 0)

print("Suche ESP-Modul...")
# Warten nach Kaltstart:
#utime.sleep(6)
# Test Kommunikation zum ESP:
ser.send_at_cmd("")
ret_val = ser.wait_of_ser_line("OK", True)
#print(ret_val)
if "OK" not in ret_val:
    print("ERROR: keine Antwort vom ESP")
else:
    # Reset:
    #ser.send_at_cmd("+RST")
    #ret_val = ser.wait_of_ser_line("OK")
 
    # Versionsabfrage:
    #ser.send_at_cmd("+GMR")
    #ret_val = ser.wait_of_ser_line("OK")

    # Setzen des NTP-Servers:
    ser.send_at_cmd("+CIPSNTPCFG=1,%s,\"%s\"" % (GMT_OFFSET, NTP_HOST))
    ret_val = ser.wait_of_ser_line("OK", True)
    
    # Setzen des Client-Modes:
    ser.send_at_cmd("+CWMODE=1")
    ret_val = ser.wait_of_ser_line("OK", True)

    # Anmelden im WLAN:
    ser.send_at_cmd("+CWJAP=\"anth-0\",\"anthal-17!\"")
    #ret_val = ser.wait_of_ser_line("WIFI", True)
    ret_val = ser.wait_of_ser_line("WIFI DISCONNECT", True)
    utime.sleep(5)
    ret_val = ser.wait_of_ser_line("WIFI CONNECTED", True)

    # Abfrage der IP-Adresse:
    ser.send_at_cmd("+CIPSTA?")
    ret_val = ser.wait_of_ser_line("OK", True)
    # 'AT+CIPSTA?',
    # '+CIPSTA:ip:"192.168.0.129"',
    # '+CIPSTA:gateway:"192.168.0.1"',
    # '+CIPSTA:netmask:"255.255.255.0"',
    # '',
    # 'OK'
    ip = ret_val[1].split('"')[1]
    print()
    print("IP-Adresse: " + ip)
    ip = ip.split(".")
    #print(ip[3])
    #utime.sleep(5)
    while True:
        # Setzen des NTP-Zeitabfrage:
        ser.send_at_cmd("+CIPSNTPTIME?")
        ret_val = ser.wait_of_ser_line("OK")
        timestring = ret_val[1].split(":")
        day = int(timestring[1].split(" ")[2])
        month = timestring[1].split(" ")[1]
        year = int(timestring[3].split(" ")[1])
        hour = int(timestring[1].split(" ")[3])
        minute = int(timestring[2])
        second = int(timestring[3].split(" ")[0])
        month = int(get_month_num(month)) 
        
        print("{0:02}.{1:02}.{2:02}".format(day, month, year-2000), end=' - ')
        print("{0:02}:{1:02}:{2:02}".format(hour, minute, second))
        tm1.numbers(hour, minute, second)
        tm2.numbers(day, month, int(year) - 2000)
        tm3.show('IP ' + ip[3])
        #tm3.show('888888')
        utime.sleep(1)
      
