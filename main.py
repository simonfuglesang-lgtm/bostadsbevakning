import requests
import json
from datetime import datetime

# ---------------------------------------------------------
# KONFIGURATION
# ---------------------------------------------------------

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

# DITT NTFY-TOPIC HÄR
NTFY_TOPIC = "bostadsbevakning"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


# ---------------------------------------------------------
# NTFY-NOTIFIERING
# ---------------------------------------------------------

def send_ntfy(title, message):
    try:
        requests.post(NTFY_URL, data=f"{title}\n{message}".encode("utf-8"))
    except Exception as e:
        print(f"[NTFY ERROR] {e}")


# ---------------------------------------------------------
# JSON-HANTERING
# ---------------------------------------------------------

def load_previous_ids():
    try:
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("sent_ids", []))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()


def save_results(sent_ids, new_items):
    data = {
        "last_run": datetime.utcnow().isoformat() + "Z",
        "sent_ids": list(sent_ids),
        "new_items": new_items
    }
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------
# HÄMTA & FILTRERA ANNONSER
# ---------------------------------------------------------

def fetch_listings():
    resp = requests.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.json()


def filter_listings(listings):
    matching = []

    for item in listings:
        # Typ
        if not any(item.get(t, False) for t in ALLOW_TYPES):
            continue

        # Kommun
        if item.get("Kommun") != "Stockholm":
            continue

        # Stadsdel
        if item.get("Stadsdel") not in ALLOW_STADSDELAR:
            continue

        # Yta (robust)
        yta = item.get("Yta")
        if yta is None or yta < MIN_YTA:
            continue

        # Rum (robust)
        rum = item.get("AntalRum")
        if rum is None or rum < MIN_RUM:
            continue

        matching.append(item)

    return matching


# ---------------------------------------------------------
# HUVUDLOGIK + DAGLIG STATUSNOTIS
# ---------------------------------------------------------

def main():
    previous_ids = load_previous_ids()
    listings = fetch_listings()
    matching = filter_listings(listings)

    sent_ids = set(previous_ids)
    new_items_summary = []

    new_count = 0

    for obj in matching:
        annons_id = obj.get("AnnonsId")
        if annons_id in sent_ids:
            continue

        title = f"{obj.get('Gatuadress', '')}, {obj.get('Stadsdel', '')}"
        area = obj.get("Kommun", "Okänd kommun")
        rooms = obj.get("AntalRum", "Okänt antal rum")
        size = obj.get("Yta", "Okänd yta")
        rent = obj.get("Hyra", "Okänd hyra")
        deadline = obj.get("AnnonseradTill", "Okänt datum")
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

        new_count += 1

    # ---------------------------------------------------------
    # DAGLIG STATUSNOTIS
    # ---------------------------------------------------------
    if new_count == 0:
        send_ntfy("Status", "Inga nya objekt idag")
    else:
        send_ntfy("Status", f"{new_count} nya objekt hittades idag")

    save_results(sent_ids, new_items_summary)


if __name__ == "__main__":
    main()
