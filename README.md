Bostadsbevakning med GitHub Actions + Ntfy
🏡 Översikt
Det här projektet bevakar nya bostadsannonser från Bostadsförmedlingen i Stockholm och skickar automatiska push‑notiser till mobilen via Ntfy.
Scriptet körs en gång per dygn med hjälp av GitHub Actions, filtrerar annonser enligt dina kriterier och lagrar skickade objekt i en JSON‑fil för att undvika dubbletter.

Projektet kräver ingen server, ingen hosting och inga kostnader — allt körs gratis via GitHub.

⚙️ Funktioner
Hämtar alla annonser från Bostadsförmedlingen (offentligt API)

Filtrerar på:

bostadstyp

stadsdel

minsta yta

minsta antal rum

Skickar push‑notiser via Ntfy

Lagrar skickade annons‑ID:n i result.json

Undviker dubbletter mellan körningar

Körs automatiskt varje dag via GitHub Actions

Kan köras manuellt via Run workflow

📂 Projektstruktur
Kod
bostadsbevakning/
├─ main.py                # Huvudscriptet
├─ requirements.txt       # Python-dependencies
├─ result.json            # Lagring av skickade ID:n + historik
└─ .github/
   └─ workflows/
      └─ daily.yml        # GitHub Actions workflow
🚀 Installation & Setup
1. Klona eller skapa repo
Skapa ett nytt GitHub‑repo och lägg in filerna ovan.

2. Installera Ntfy på mobilen
Ladda ner Ntfy från App Store / Google Play

Skapa ett valfritt topic, t.ex. bostadsbevakning

Lägg in topic i main.py:

python
NTFY_TOPIC = "bostadsbevakning"
3. Skapa result.json
Lägg till filen i repo‑roten:

json
{
  "sent_ids": [],
  "new_items": [],
  "last_run": ""
}
4. GitHub Actions kör scriptet automatiskt
Workflowen i .github/workflows/daily.yml kör:

checkout

setup python

install dependencies

run script

commit result.json

Cron‑schemat:

Kod
0 5 * * *
→ kör varje dag kl. 05:00 UTC
→ ca 06–07 svensk tid beroende på sommar/vintertid

📬 Notiser via Ntfy
Scriptet skickar notiser som innehåller:

adress

stadsdel

antal rum

yta

hyra

sista ansökningsdatum

direktlänk till annonsen

Exempel:

Kod
Södermalm
4 rum, 102 kvm
Hyra: 16500 kr
Anmälan senast: 2026-09-03
https://bostad.stockholm.se/...
🧠 Hur dubblettkontrollen fungerar
Varje annons har ett unikt AnnonsId.

Scriptet:

läser result.json

hämtar alla annonser

filtrerar dem

skickar notiser för nya ID:n

sparar ID:n i result.json

På så sätt får du aldrig samma notis två gånger, även om annonsen ligger kvar flera dagar.

🛠️ Manuell körning
Du kan köra scriptet manuellt via GitHub:

Gå till Actions

Välj workflow Daily Housing Check

Klicka Run workflow

Perfekt för testning.

🧪 Testning lokalt (valfritt)
Om du vill testa lokalt:

bash
pip install -r requirements.txt
python main.py
🔒 Sekretess & API‑nycklar
Projektet använder inga API‑nycklar.
Ntfy är helt anonymt och kräver ingen registrering.

📈 Framtida förbättringar (valfritt)
Loggning till fil eller GitHub Pages

E‑postnotiser via GitHub Actions

Fler filter (hyra, kötid, byggår)

Push till Discord / Slack / Telegram

👤 Skapare
Projektet är byggt av Simon och körs helt automatiskt via GitHub Actions.
