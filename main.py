from machine import Pin, PWM, RTC, UART, I2C, ADC
import time
import random
import uos
import network
from ssd1306 import SSD1306_I2C
from secrets import secrets

# wifi_ssid = secrets['ssid']
# wifi_pass = secrets['key']
# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# wlan.connect(wifi_ssid, wifi_pass)


# pin_button = Pin(20, mode=Pin.IN, pull=Pin.PULL_DOWN)
pin_buzz = Pin(22, mode=Pin.IN, pull=Pin.PULL_UP)
pin_beep = PWM(Pin(21))

x_axis = ADC(Pin(27))
y_axis = ADC(Pin(26))

# Set up the UART for the GPS
uart = UART(0, baudrate=9600)
Pin(20, mode=Pin.IN, pull=Pin.PULL_DOWN)

i2c=I2C(0,sda=Pin(8), scl=Pin(9), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
oled.text("CaughtYa!", 0, 0)
oled.text("(c)'23 nerdymark", 0, 16)
oled.text("Binding to phone", 0, 32)
oled.show()
time.sleep(5)


buzz_ticks = 0
max_ticks = 200
all_ticks = 0
global_ticks = 0
max_global_tick = 0
widths = []
init_lat = 37.808497
init_lon = -122.410753
init_alt = 1.25
utc_offset = 8
    
    
def move_location(lat, lon, alt):
    """
    Converts time, latitude, longitude, and altitude to a mock NMEA GGA string.
    From these coords, we want to generate a string like this:
    lat = 37.808497
    lon = -122.410753
    alt = 1.25
    time = 18:19:08.00
    $GPGGA,181908.00,3404.7041778,N,07044.3966270,W,4,13,1.00,495.144,M,29.200,M,0.10,0000*40
    """
    oled.fill(0)
    oled.text("CaughtYa!", 0, 0)
    oled.text(str(lat), 0, 16)
    oled.text(str(lon), 0, 32)
    oled.show()
    
    rtc_time = RTC().datetime() 
    lat_deg = int(lat)
    lat_min = (lat - lat_deg) * 60
    lon_deg = int(lon)
    lon_min = (lon - lon_deg) * 60
    alt = int(alt)
    lat_dir = 'N' if lat > 0 else 'S'
    lon_dir = 'E' if lon > 0 else 'W'
    gps_hour = rtc_time[4] + utc_offset
    gps_time = '{:02d}{:02d}{:02d}.00'.format(gps_hour, rtc_time[5], rtc_time[6])
    gps_lat = '{:02d}{:06.3f}'.format(lat_deg, lat_min).replace('-', '')
    gps_lon = '{:03d}{:06.3f}'.format(lon_deg, lon_min).replace('-', '')
    gps_alt = '{:06.3f}'.format(alt)
    gps_str = '$GPGGA,{},{},{},{},{},{},1,12,0.9,{},M,0,M,,*40'.format(gps_time,
                                                                       gps_lat,
                                                                       lat_dir,
                                                                       gps_lon,
                                                                       lon_dir,
                                                                       1,
                                                                       gps_alt)
    return gps_str


def press_button():
    Pin(20, mode=Pin.IN, pull=Pin.PULL_UP)
    time.sleep(0.1)
    Pin(20, mode=Pin.IN, pull=Pin.PULL_DOWN)
    time.sleep(1)
    Pin(20, mode=Pin.IN, pull=Pin.PULL_UP)
    
    oled.fill(0)
    oled.text("CaughtYa!", 0, 0)
    oled.text("", 0, 16)
    oled.text("Button pressed", 0, 32)
    oled.show()
    
    return "Pressed button"


def beep():
    pin_beep.freq(900)
    pin_beep.duty_u16(1000)
    time.sleep(1)
    pin_beep.duty_u16(0)
    oled.fill(0)
    oled.text("CaughtYa!", 0, 0)
    oled.text("am i bound", 0, 16)
    oled.text("to phone?", 0, 32)
    oled.show()
    

time.sleep(5)
press_button()
time.sleep(1)

# bluetooth_init()

while True:
    # print(uart.readline())
    x_value = x_axis.read_u16()
    y_value = y_axis.read_u16()
    x_status = 'Middle'
    y_status = 'Middle'
    if x_value <= 600:
        x_status = "left"
        init_lat += 0.0001
    elif x_value >= 60000:
        x_status = "right"
        init_lat -= 0.0001
    if y_value <= 600:
        y_status = "up"
        init_lon += 0.0001
    elif y_value >= 60000:
        y_status = "down"
        init_lon -= 0.0001
    # if buttonValue == 0:
    #     buttonStatus = "pressed"
    
    # print("X: " + str(x_value) + ", Y: " + str(y_value))

    
    # pin_button.on() if pin_buzz.value() else pin_button.off()
    # Time the pin_buzz duration
    if pin_buzz.value() == 0:
        buzz_ticks += 1
        global_ticks = 0
        # print(press_button())
        press_button()
    all_ticks += 1
    global_ticks += 1
    if all_ticks >= max_ticks:
        # action = press_button()
        width = buzz_ticks / all_ticks
        if width > 0 and width < 1:
            widths.append(width)
        all_ticks = 0
        buzz_ticks = 0
        # print(width)
        
    # print(pin_buzz.value())
    if global_ticks > max_global_tick:
        max_global_tick = global_ticks
    if global_ticks > 300000:
        # print(press_button())
        press_button()
        time.sleep(0.1)
        # print('Global_ticks is higher than 3000: {}'.format(global_ticks))
    if global_ticks > 300002:
        # print('Beeping: {}'.format(global_ticks))
        press_button()
        beep()
        time.sleep(0.1)
    
    # Jiggle the location a bit
    gps_lat = random.uniform(init_lat - 0.0001, init_lat + 0.0001)
    gps_lon = random.uniform(init_lon - 0.0001, init_lon + 0.0001)
    gps_alt = random.uniform(init_alt - 0.0001, init_alt + 0.0001)
    fake_loc = move_location(gps_lat, gps_lon, gps_alt)
    # fake_loc = '{}\r\n'.format(fake_loc)
    print(fake_loc)
    uart.write(fake_loc)
    time.sleep(1)
