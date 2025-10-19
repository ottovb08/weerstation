import requests
import csv
import os

# Vul in met je gegevens
CHANNEL_ID = "3082076"
READ_API_KEY = "Y21QDZ80D0SXWKNO"
RESULTS = 100  # aantal records

URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results={RESULTS}"
FILENAME = "thingspeak_data.csv"

def fetch_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()["feeds"]
    else:
        print("Fout bij ophalen:", response.status_code)
        return []

def load_existing_timestamps(filename):
    """Lees bestaande tijdstempels uit CSV (om dubbele te voorkomen)."""
    if not os.path.exists(filename):
        return set()
    
    timestamps = set()
    with open(filename, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.add(row["created_at"])
    return timestamps

def save_to_csv(data, filename=FILENAME):
    if not data:
        print("Geen data om op te slaan.")
        return
    
    # Velden uit ThingSpeak (pas aan indien meer fields nodig zijn)
    fields = ["created_at", "field1", "field2"]

    # Laad bestaande tijdstempels
    existing = load_existing_timestamps(filename)

    new_rows = []
    for entry in data:
        ts = entry["created_at"]
        if ts not in existing:  # alleen nieuwe records
            row = {
                "created_at": ts,
                "field1": entry.get("field1"),
                "field2": entry.get("field2"),
            }
            new_rows.append(row)

    if not new_rows:
        print("Geen nieuwe data gevonden.")
        return

    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if f.tell() == 0:  # schrijf header als bestand leeg is
            writer.writeheader()
        writer.writerows(new_rows)

    print(f"{len(new_rows)} nieuwe records toegevoegd.")

if __name__ == "__main__":
    data = fetch_data()
    save_to_csv(data)
