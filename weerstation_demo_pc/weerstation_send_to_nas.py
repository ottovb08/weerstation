import network
import time
import urequests
from machine import Pin, SPI, ADC
import bmp280_spi
import onewire, ds18x20

# -------------------------------
# Netwerk & serverinstellingen
# -------------------------------
SSID = "Wifi-209"
PASSWORD = "Ricazo-9620"
SERVER = "http://192.168.0.140:5000/update"  # IP van je NAS

# -------------------------------
# Verbinden met WiFi
# -------------------------------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    print("Verbinden met WiFi...")
    time.sleep(1)
print("Verbonden met netwerk:", wlan.ifconfig())

# -------------------------------
# Sensorconfiguratie
# -------------------------------
# BMP280 via SPI (druk + temp)
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs_bmp = Pin(17, Pin.OUT)
bmp = bmp280_spi.BMP280(spi, cs_bmp)

# Windrichting (ADC)
adc = ADC(Pin(26))
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

# Windsnelheid (anemometer)
wind_pin = Pin(15, Pin.IN, Pin.PULL_UP)
wind_count = 0
def wind_callback(pin):
    global wind_count
    wind_count += 1
wind_pin.irq(trigger=Pin.IRQ_FALLING, handler=wind_callback)

# DS18B20 (digitale temperatuur)
ow = onewire.OneWire(Pin(14))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
print("Gevonden DS18B20-sensoren:", roms)

# -------------------------------
# Hoofdloop
# -------------------------------
while True:
    try:
        # Windsnelheid meten gedurende 2 seconden
        wind_count = 0
        start = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start) < 2000:
            pass
        pulses_per_sec = wind_count / 2
        wind_speed_mph = pulses_per_sec * 2.25
        wind_speed = wind_speed_mph * 1.60934  # km/u

        # BMP280 uitlezen
        temp = bmp.temperature
        druk = bmp.pressure / 100  # hPa

        # Windrichting uitlezen
        samples = [adc.read_u16() for _ in range(10)]
        avg_adc = sum(samples) // len(samples)
        richting, hoek = adc_to_direction(avg_adc)

        # DS18B20 uitlezen
        ds.convert_temp()
        time.sleep_ms(750)
        ds_values = []
        for rom in roms:
            ds_values.append(ds.read_temp(rom))

        # Waarden koppelen aan namen
        groene_temp = ds_values[0] if len(ds_values) > 0 else None
        gewone_temp = ds_values[1] if len(ds_values) > 1 else None

        # JSON-pakket maken
        payload = {
            "temp": round(temp, 2),
            "druk": round(druk, 2),
            "wind": round(wind_speed, 2),
            "richting": richting,
            "hoek": hoek,

            # nieuwe namen
            "groene_dakbedekking": round(groene_temp, 2) if groene_temp is not None else None,
            "gewone_dakbedekking": round(gewone_temp, 2) if gewone_temp is not None else None
        }
        
        # Versturen naar NAS
        try:
            r = urequests.post(SERVER, json=payload)
            r.close()
            print("Verzonden:", payload)
        except Exception as e:
            print("Fout bij verzenden:", e)

        time.sleep(2)  # Verzendsnelheid
    except Exception as e:
        print("Algemene fout:", e)
        time.sleep(5) 