#
import network
import secrets
import utime
import tm1637_6dig

from machine import Pin
from machine import RTC

import uasyncio as asyncio

# Load login data from different file for safety reasons
ssid = secrets.secrets['ssid']
key = secrets.secrets['key']

led0 = machine.Pin(25, machine.Pin.OUT)


def get_month(month_str):
    if month_str == "Jan":
        return "01"
    if month_str == "Feb":
        return "02"
    if month_str == "Mar":
        return "03"
    if month_str == "Apr":
        return "04"    
    if month_str == "May":
        return "05"
    if month_str == "Jun":
        return "06"
    if month_str == "Jul":
        return "07"
    if month_str == "Aug":
        return "08"    
    if month_str == "Sep":
        return "09"
    if month_str == "Oct":
        return "10"
    if month_str == "Nov":
        return "11"
    if month_str == "Dec":
        return "12"    


####################################################################
# MAIN
####################################################################
# Add Objekte:
rtc = RTC()

tm1 = tm1637_6dig.TM1637(clk=Pin(0), dio=Pin(1))
tm2 = tm1637_6dig.TM1637(clk=Pin(2), dio=Pin(3))
tm3 = tm1637_6dig.TM1637(clk=Pin(12), dio=Pin(13))
tm4 = tm1637_6dig.TM1637(clk=Pin(10), dio=Pin(11))
tm5 = tm1637_6dig.TM1637(clk=Pin(8), dio=Pin(9))

#tm1.show('Unsync')
#tm2.show('Unsync')
#tm3.show('unsync')
#tm4.show('unsync')
#tm5.show('unsync')
tm1.show('111111')
tm2.show('222222')
tm3.show('333333')
tm4.show('444444')
tm5.show('555555')

led0.value(0)

wlan = network.WLAN(network.STA)
wlan.active(True)
retval = wlan.connect(ssid, key)
print(retval)

if wlan.isconnected():
    print("WLAN Connected")
    print(wlan.ifconfig())
    cmd = 'CIPSNTPCFG=1,2,'+ secrets.network['ntp-server']
    print(cmd)
    ret_val = wlan.sendATcmd_waitResp(cmd)
    print(ret_val)
    # Warten auf OK:
    while "ERROR" in ret_val:
        ret_val = wlan.sendATcmd_waitResp(cmd)
        print(ret_val)
        utime.sleep(1)

    # Abfrage der aktuellen Zeit per  NTP:
    cmd = 'CIPSNTPTIME?'
    second_old = "0"
    while True: 
        ret_val = wlan.sendATcmd_waitResp(cmd, debug=False)
        time_list1 = str(ret_val).split(" ")
        month = get_month(time_list1[1])
        day = time_list1[2]
        year = time_list1[4][0:4]
        timestr = time_list1[3]
        time_list2 = timestr.split(":")
        hour = time_list2[0]
        minute = time_list2[1]
        second = time_list2[2]
        
        if second != second_old and int(year) > 2022:
        #if second != second_old:
            print("{}.{}.{} {}:{}:{}".format(day, month, year, hour, minute, second))
            second_old = second
            tm1.numbers(int(hour), int(minute), int(second))
            tm2.numbers(int(day), int(month), int(year[2:4]))
            tm3.numbers(int(hour), int(minute), int(second))
            tm4.numbers(int(day), int(month), int(year[2:4]))
            tm5.numbers(int(hour), int(minute), int(second))

            if int(second) % 2 == 0:
                led0.value(1)
            else:
                led0.value(0)
        
        utime.sleep(0.5)

else:
    print("No WLAN Connection!")

