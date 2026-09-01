import requests
import json
from datetime import datetime

API_URL = "https://bostad.stockholm.se/AllaAnnonser/"

ALLOW_TYPES = {"Vanlig", "Hyresradhus", "Familjelagenhet"}

ALLOW_STADSDELAR = [
    "Södermalm", "Liljeholmen", "Södra Hammarbyhamnen", "Årsta",
    "Kungsholmen", "Vasastan", "Aspudden", "Midsommarkransen",
    "Gröndal", "Alvik"
]

MIN_YTA = 100
MIN_RUM = 4

RESULT_FILE = "result.json"

NTFY_TOPIC = "DITT_TOPIC_HÄR"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_ntfy(title, message):
    requests.post(NTFY_URL, data=f"{title}\n{message}".encode("utf-8"))

def load_previous_ids():
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("sent_ids", []))
    except:
        return set()

def save_results(sent_ids, new_items):
    data = {
        "last_run": datetime.utcnow().isoformat() + "Z",
        "sent_ids": list(sent_ids),
        "new_items": new_items
    }
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_listings():
    resp = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.json()

def filter_listings(listings):
    matching = []
    for item in listings:
        if not any(item.get(t, False) for t in ALLOW_TYPES):
            continue
        if item.get("Kommun") != "Stockholm":
            continue
        if item.get("Stadsdel") not in ALLOW_STADSDELAR:
            continue
        if item.get("Yta", 0) < MIN_YTA:
            continue
        if item.get("AntalRum", 0) < MIN_RUM:
            continue
        matching.append(item)
    return matching

def main():
    previous_ids = load_previous_ids()
    listings = fetch_listings()
    matching = filter_listings(listings)

    sent_ids = set(previous_ids)
    new_items_summary = []

    for obj in matching:
        annons_id = obj.get("AnnonsId")
        if annons_id in sent_ids:
            continue

        title = f"{obj.get('Gatuadress', '')}, {obj.get('Stadsdel', '')}"
        area = obj.get("Kommun")
        rooms = obj.get("AntalRum")
        size = obj.get("Yta")
        rent = obj.get("Hyra")
        deadline = obj.get("AnnonseradTill")
        link = "https://bostad.stockholm.se" + obj.get("Url", "")

        message = (
            f"{area}\n"
            f"{rooms} rum, {size} kvm\n"
            f"Hyra: {rent} kr\n"
            f"Anmälan senast: {deadline}\n"
            f"{link}"
        )

        send_ntfy(title, message)
        sent_ids.add(annons_id)

        new_items_summary.append({
            "AnnonsId": annons_id,
            "Titel": title,
            "Länk": link
        })

    save_results(sent_ids, new_items_summary)

if __name__ == "__main__":
    main()
