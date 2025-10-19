import requests
import csv
from datetime import datetime

# Vul in met je gegevens
CHANNEL_ID = "3082076"
READ_API_KEY = "Y21QDZ80D0SXWKNO"
RESULTS = 100  # aantal records

URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results={RESULTS}"

def fetch_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()["feeds"]
    else:
        print("Fout bij ophalen:", response.status_code)
        return []

def save_to_csv(data, filename="thingspeak_data.csv"):
    if not data:
        print("Geen data om op te slaan.")
        return
    
    # velden (hieruit kun je kiezen welke je wilt bewaren)
    fields = ["created_at", "field1", "field2"]
    
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        
        # schrijf header alleen als bestand leeg is
        if f.tell() == 0:
            writer.writeheader()
        
        for entry in data:
            row = {
                "created_at": entry["created_at"],
                "field1": entry.get("field1"),
                "field2": entry.get("field2"),
            }
            writer.writerow(row)

if __name__ == "__main__":
    data = fetch_data()
    save_to_csv(data)
    print(f"{len(data)} records opgeslagen.")
