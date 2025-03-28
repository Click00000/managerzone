import requests
import xml.etree.ElementTree as ET
import csv
import os
import time
import pandas as pd
from datetime import datetime

# Kaydetme klasörü
DATA_DIR = "managerzone_data"
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
    print(f"Fetched {len(players)} players for team {team['teamName']}")
    return players

def fetch_team_matches(team, date_str):
    url = f"https://www.managerzone.com/xml/team_matchlist.php?sport_id=1&team_id={team['teamId']}&match_status=1&limit=50"
    res = session.get(url, headers=HEADERS)
    root = ET.fromstring(res.content)

    matches = []
    for m in root.findall("Match"):
        # Maç bilgilerini çek
        match_type = m.attrib.get("type")
        if match_type == "league":  # sadece lig maçlarını al
            matches.append({
                "date": date_str,
                "team_id": team['teamId'],
                "team_name": team['teamName'],
                "match_id": m.attrib.get("id"),
                "date_played": m.attrib.get("date"),
                "type": match_type,
                "home_team": m.attrib.get("home_team_name"),
                "home_goals": m.attrib.get("home_team_goals"),
                "away_team": m.attrib.get("away_team_name"),
                "away_goals": m.attrib.get("away_team_goals"),
            })
    print(f"Fetched {len(matches)} matches for team {team['teamName']}")
    return matches

def fetch_match_details(match_id, date_str):
    url = f"https://www.managerzone.com/xml/match_info.php?sport_id=1&match_id={match_id}"
    res = session.get(url, headers=HEADERS)
    root = ET.fromstring(res.content)

    match_players = []
    match = root.find("Match")
    if match is None:
        return []

    for team in match.findall("Team"):
        team_id = team.attrib.get("id")
        team_name = team.attrib.get("name")
        team_goals = team.attrib.get("goals")
        field = team.attrib.get("field")

        for p in team.findall("Player"):
            goals_elem = p.find("Goals")
            goals = goals_elem.attrib.get("pro") if goals_elem is not None else "0"

            match_players.append({
                "date": date_str,
                "match_id": match.attrib.get("id"),
                "team_id": team_id,
                "team_name": team_name,
                "field": field,
                "player_id": p.attrib.get("id"),
                "name": p.attrib.get("name"),
                "shirtno": p.attrib.get("shirtno"),
                "goals": goals
            })
    print(f"Fetched match details for match {match_id}")
    return match_players

def append_to_master_file(data, filename):
    path = os.path.join(DATA_DIR, filename)
    df_new = pd.DataFrame(data)
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.drop_duplicates(inplace=True)
    else:
        df_combined = df_new
    df_combined.to_csv(path, index=False, encoding="utf-8")
    print(f"Appended data to {filename}")

# Bugünkü tarih
now = datetime.now()
today_str = now.strftime("%Y-%m-%d")

# Verileri çek
all_players = []
all_matches = []
all_match_details = []

print("\n📥 Sabit takımlar üzerinden veri çekimi başlıyor...")
for team in TEAMS:
    try:
        print(f"\n🔍 {team['teamName']} işleniyor...")
        players = fetch_team_players(team, today_str)
        matches = fetch_team_matches(team, today_str)
        all_players.extend(players)
        all_matches.extend(matches)

        for match in matches:
            match_id = match['match_id']
            details = fetch_match_details(match_id, today_str)
            all_match_details.extend(details)
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Hata oluştu ({team['teamName']}): {e}")

# CSV olarak günlük ve birleşik şekilde kaydet
if all_players:
    daily_players_file = os.path.join(DATA_DIR, f"mz_players_{today_str}.csv")
    with open(daily_players_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_players[0].keys())
        writer.writeheader()
        writer.writerows(all_players)
    append_to_master_file(all_players, "players_all.csv")
    print("✅ Oyuncu CSV dosyaları oluşturuldu.")
else:
    print("⚠️ Oyuncu verisi bulunamadı.")

if all_matches:
    daily_matches_file = os.path.join(DATA_DIR, f"mz_matches_{today_str}.csv")
    with open(daily_matches_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
        writer.writeheader()
        writer.writerows(all_matches)
    append_to_master_file(all_matches, "matches_all.csv")
    print("✅ Maç CSV dosyaları oluşturuldu.")
else:
    print("⚠️ Maç verisi bulunamadı.")

if all_match_details:
    daily_match_details_file = os.path.join(DATA_DIR, f"mz_match_details_{today_str}.csv")
    with open(daily_match_details_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_match_details[0].keys())
        writer.writeheader()
        writer.writerows(all_match_details)
    append_to_master_file(all_match_details, "match_details_all.csv")
    print("✅ Maç detay CSV dosyaları oluşturuldu.")
else:
    print("⚠️ Maç detay verisi bulunamadı.")

print("\n🎉 Günlük veri çekimi tamamlandı.")
