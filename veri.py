import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
import pandas as pd
from datetime import datetime
import streamlit as st

# Kaydetme klasörü, Streamlit'le uyumlu olabilmesi için geçici olarak kullanacağımız dizin
DATA_DIR = "./managerzone_data"  # Streamlit ile çalışacak dizin
os.makedirs(DATA_DIR, exist_ok=True)

# Sabit takım bilgileri
TEAMS = [
    {"teamId": "876200", "teamName": "Altan-69erc"},
    {"teamId": "895745", "teamName": "Daday"},
    {"teamId": "950074", "teamName": "Erzin Spor"},
    {"teamId": "937054", "teamName": "FC Kandıra"},
    {"teamId": "887769", "teamName": "Fainera"},
    {"teamId": "914687", "teamName": "Fırtınagücü"},
    {"teamId": "927107", "teamName": "Kovancilar"},
    {"teamId": "931205", "teamName": "Nrdlife Junior"},
    {"teamId": "950648", "teamName": "Pink Floyd"},
    {"teamId": "918800", "teamName": "TARSUSLU"},
    {"teamId": "553929", "teamName": "Yürekli TÜRK"},
    {"teamId": "926863", "teamName": "goviza"},
]

# User-Agent tanımla
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/xml"
}

session = requests.Session()

# Verileri çekme ve kaydetme fonksiyonu
def fetch_team_players(team, date_str):
    url = f"https://www.managerzone.com/xml/team_playerlist.php?sport_id=1&team_id={team['teamId']}"
    res = session.get(url, headers=HEADERS)
    root = ET.fromstring(res.content)
    team_root = root.find("TeamPlayers")

    players = []
    if team_root is not None:
        for p in team_root.findall("Player"):
            players.append({
                "date": date_str,
                "team_id": team['teamId'],
                "team_name": team['teamName'],
                "player_id": p.attrib.get("id"),
                "name": p.attrib.get("name"),
                "shirtNo": p.attrib.get("shirtNo"),
                "age": p.attrib.get("age"),
                "birthSeason": p.attrib.get("birthSeason"),
                "birthDay": p.attrib.get("birthDay"),
                "height": p.attrib.get("height"),
                "weight": p.attrib.get("weight"),
                "value": p.attrib.get("value"),
                "salary": p.attrib.get("salary"),
                "countryShortname": p.attrib.get("countryShortname"),
                "injuryType": p.attrib.get("injuryType"),
                "injuryDays": p.attrib.get("injuryDays"),
                "junior": p.attrib.get("junior")
            })
    return players

# Ana fonksiyonla veri çekme
def update_data():
    all_players = []
    all_matches = []
    all_match_details = []

    # Bugünkü tarih
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    # Sabit takımlar üzerinden veri çekimi başlıyor
    print("\n📥 Sabit takımlar üzerinden veri çekimi başlıyor...")
    for team in TEAMS:
        try:
            print(f"\n🔍 {team['teamName']} işleniyor...")
            players = fetch_team_players(team, today_str)
            all_players.extend(players)
            # Burada diğer veri çekme fonksiyonları da kullanılabilir.
        except Exception as e:
            print(f"⚠️ Hata oluştu ({team['teamName']}): {e}")

    # Verileri CSV olarak kaydet
    if all_players:
        daily_players_file = os.path.join(DATA_DIR, f"mz_players_{today_str}.csv")
        with open(daily_players_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
            writer.writeheader()
            writer.writerows(all_players)

        print("✅ Oyuncu CSV dosyaları oluşturuldu.")
    else:
        print("⚠️ Oyuncu verisi bulunamadı.")
