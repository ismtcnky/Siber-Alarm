import csv, time, os
import urllib.request
from datetime import datetime

# AYARLAR
SHEET_ID = "1upCcokblqOVxX0ddov-iwLxGXnF2zt0Lz2zYsfPHnvE"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Son gönderilenleri tekrar atmamak için
SEEN_FILE = "seen.txt"

def get_keywords():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        with urllib.request.urlopen(url) as r:
            text = r.read().decode('utf-8')
            reader = csv.reader(text.splitlines())
            keywords = []
            for i, row in enumerate(reader):
                if i==0: continue # başlık
                if row and row[0].strip():
                    keywords.append(row[0].strip())
            return keywords if keywords else ["#sakarya", "#adapazarı", "#cinayet", "#polis"]
    except Exception as e:
        print(f"Sheet okunamadı: {e}")
        return ["#sakarya", "#adapazarı", "#cinayet", "#polis"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = f'{{"chat_id":"{CHAT_ID}", "text":{repr(msg)}}}'.encode()
    # basit gönderim için browser benzeri istek
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(e)

def search_news(keywords):
    # Ücretsiz arama: Nitter (X) ve Google News RSS kullanıyoruz
    # Burada şimdilik demo olarak Google News'i tarıyoruz
    # İstersen sonra X API eklersin
    results = []
    for kw in keywords:
        clean = kw.replace("#","")
        rss_url = f"https://news.google.com/rss/search?q={clean}+Sakarya&hl=tr&gl=TR&ceid=TR:tr"
        try:
            with urllib.request.urlopen(rss_url) as r:
                xml = r.read().decode()
                # basit parse
                if clean.lower() in xml.lower():
                    # ilk haberi al
                    results.append(f"{kw} için yeni haber bulundu - {rss_url}")
        except:
            pass
    return results

# ANA AKIŞ
keywords = get_keywords()
print(f"Keywords: {keywords}")

# Daha önce gönderilenleri yükle
seen = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(f.read().splitlines())

new_items = search_news(keywords)

for item in new_items:
    if item not in seen:
        send_telegram(f"🚨 SAKARYA ALARM\n\n{keywords} eşleşti:\n{item}\n\n{datetime.now().strftime('%H:%M')}")
        seen.add(item)

# seen'i kaydet
with open(SEEN_FILE, "w") as f:
    f.write("\n".join(seen))
