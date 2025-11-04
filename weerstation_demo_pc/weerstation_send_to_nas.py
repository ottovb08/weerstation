import network, time, urequests
from machine import Pin, SPI, ADC
import bmp280_spi, onewire, ds18x20

# ---------- WiFi ----------
SSID = "Wifi-209"
PASSWORD = "Ricazo-9620"
SERVER = "http://192.168.0.140:5000/update"  # jouw NAS-IP + Flask-poort

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Verbinden met WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            print("Wachten op verbinding...")
            time.sleep(1)
    print("Verbonden:", wlan.ifconfig())
    return wlan

connect_wifi()

# ---------- BMP280 (SPI) ----------
spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs_bmp = Pin(17, Pin.OUT)
bmp = bmp280_spi.BMP280(spi, cs_bmp)

# ---------- Windrichting (ADC) ----------
adc = ADC(Pin(26))

def adc_to_direction(adc_val):
    if adc_val <= 6220:
        return "Zuiden", 180
    elif adc_val <= 11980:
        return "Zuidwesten", 225
    elif adc_val <= 18700:
        return "Westen", 270
    elif adc_val <= 29600:
        return "Zuidoosten", 135
    elif adc_val <= 40500:
        return "Noordwesten", 315
    elif adc_val <= 50300:
        return "Oosten", 90
    elif adc_val <= 57000:
        return "Noordoosten", 45
    elif adc_val <= 60500:
        return "Noorden", 0
    else:
        return "Geen richting", -1

# ---------- Windsnelheid (anemometer) ----------
wind_pin = Pin(15, Pin.IN, Pin.PULL_UP)
wind_count = 0
def wind_callback(pin):
    global wind_count
    wind_count += 1
wind_pin.irq(trigger=Pin.IRQ_FALLING, handler=wind_callback)

# ---------- DS18B20 temperatuursensoren ----------
ow = onewire.OneWire(Pin(14))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()
print("Gevonden DS18B20 sensoren:", roms)

# ---------- Hoofdloop ----------
while True:
    # Windsnelheid meten over 2s
    wind_count = 0
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < 2000:
        pass
    pulses_per_sec = wind_count / 2
    wind_speed_mph = pulses_per_sec * 2.25
    wind_speed = wind_speed_mph * 1.60934  # km/u

    # BMP280-metingen
    temp_bmp = bmp.temperature
    druk = bmp.pressure / 100  # hPa

    # Windrichting
    samples = [adc.read_u16() for _ in range(10)]
    avg_adc = sum(samples) // len(samples)
    richting, hoek = adc_to_direction(avg_adc)

    # DS18B20-metingen
    ds.convert_temp()
    time.sleep_ms(750)
    temps = [ds.read_temp(r) for r in roms]
    temp1 = temps[0] if len(temps) > 0 else None
    temp2 = temps[1] if len(temps) > 1 else None

    payload = {
        "temp_bmp": temp_bmp,
        "temp1": temp1,
        "temp2": temp2,
        "druk": druk,
        "wind": wind_speed,
        "richting": richting,
        "hoek": hoek
    }

    try:
        r = urequests.post(SERVER, json=payload)
        print("Verzonden →", payload)
        r.close()
    except Exception as e:
        print("Fout bij verzenden:", e)

    time.sleep(5)