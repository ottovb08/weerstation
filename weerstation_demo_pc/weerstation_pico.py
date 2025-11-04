import network, time, urequests
from machine import Pin, I2C, ADC
import onewire, ds18x20
from bme280 import BME280

# ====== WIFI INSTELLINGEN ======
SSID = "Wifi-209"
PASSWORD = "Ricazo-9620"
SERVER = "http://192.168.0.140:5000/update"  # IP van NAS of PC-server

# ====== WIFI CONNECTIE ======
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Verbinden met WiFi...")
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Wachten op verbinding...")
        time.sleep(1)
print("Verbonden:", wlan.ifconfig())

# ====== SENSOR SETUP ======
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
bme = BME280(i2c=i2c)

# DS18B20
ds_pin = Pin(2)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print("DS18B20 sensoren:", roms)

# Windrichting (ADC) + Anemometer (pulsen)
adc = ADC(Pin(26))
wind_pin = Pin(15, Pin.IN, Pin.PULL_UP)
wind_count = 0

def wind_callback(pin):
    global wind_count
    wind_count += 1
wind_pin.irq(trigger=Pin.IRQ_FALLING, handler=wind_callback)

def adc_to_direction(adc_val):
    if adc_val <= 6220: return "Zuiden", 180
    elif adc_val <= 11980: return "Zuidwesten", 225
    elif adc_val <= 18700: return "Westen", 270
    elif adc_val <= 29600: return "Zuidoosten", 135
    elif adc_val <= 40500: return "Noordwesten", 315
    elif adc_val <= 50300: return "Oosten", 90
    elif adc_val <= 57000: return "Noordoosten", 45
    elif adc_val <= 60500: return "Noorden", 0
    else: return "Geen richting", -1

# ====== HOOFDLUS ======
MEASURE_INTERVAL = 5  # seconden

while True:
    # Windsnelheid meten
    wind_count = 0
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < MEASURE_INTERVAL*1000:
        pass
    pulses_per_sec = wind_count / MEASURE_INTERVAL
    wind_speed_kmh = pulses_per_sec * 2.25 * 1.60934  # conversie

    # Windrichting
    samples = [adc.read_u16() for _ in range(10)]
    avg_adc = sum(samples)//len(samples)
    richting, hoek = adc_to_direction(avg_adc)

    # BME280
    temp, druk, hum = bme.values
    temp = float(temp[:-1])
    druk = float(druk[:-3])
    hum = float(hum[:-1])

    # DS18B20
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    temps = []
    for rom in roms:
        temps.append(ds_sensor.read_temp(rom))

    # JSON payload
    payload = {
        "bme_temp": temp,
        "druk": druk,
        "hum": hum,
        "wind": wind_speed_kmh,
        "richting": richting,
        "hoek": hoek,
        "ds18b20_1": temps[0] if len(temps) > 0 else None,
        "ds18b20_2": temps[1] if len(temps) > 1 else None
    }

    try:
        r = urequests.post(SERVER, json=payload)
        r.close()
        print("Verzonden:", payload)
    except Exception as e:
        print("Fout bij verzenden:", e)

    time.sleep(5)