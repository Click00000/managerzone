import streamlit as st
import pandas as pd
import subprocess
import os
from datetime import datetime
from pathlib import Path

# Klasör yolu sabit
DATA_DIR = Path.home() / "Desktop" / "managerzone_data"
VERI_SCRIPT_PATH = Path.home() / "Desktop" / "veri.py"

# CSV yükleyici
@st.cache_data(show_spinner=False)
def load_all_csv(name):
    file = DATA_DIR / f"{name}.csv"
    if file.exists():
        df = pd.read_csv(file)
        return df
    return pd.DataFrame()

# Tarih bilgisi göster
def get_last_update():
    files = sorted(DATA_DIR.glob("mz_players_*.csv"))
    if files:
        date_str = files[-1].stem.replace("mz_players_", "")
        return date_str
    return "bulunamadı"

st.set_page_config(page_title="ManagerZone Analiz Merkezi", layout="wide")
st.title("📊 ManagerZone Analiz Merkezi")

# En son güncelleme tarihi
last_update = get_last_update()
st.markdown(f"📅 **Son veri tarihi:** `{last_update}`")

# GÜNCELLE BUTONU
if st.button("🔄 Verileri Güncelle (veri.py)"):
    with st.spinner("Veriler güncelleniyor, lütfen bekleyin..."):
        result = subprocess.run(["python3", str(VERI_SCRIPT_PATH)], capture_output=True, text=True)
        st.success("Veri çekimi tamamlandı!")
        st.code(result.stdout[-1500:])

# Sol Sidebar Menüsü
st.sidebar.title("📂 Menü")
menu = st.sidebar.radio("Bir analiz seç:", [
    "Kadro Gücü ve Gençlik Analizi",
    "Transfer Takibi",
    "Aktif Oyuncular (Maçlara Çıkanlar)",
    "En Çok Maç Oynayanlar",
    "U18/U21/U23 Kadro Detayları"
])

players_all = load_all_csv("players_all")
matches_all = load_all_csv("matches_all")
match_details_all = load_all_csv("match_details_all")

# Filtreler
team_filter = st.sidebar.multiselect("Takım Seç (Opsiyonel)", options=sorted(players_all["team_name"].unique()) if not players_all.empty else [])
age_min, age_max = st.sidebar.slider("Yaş Aralığı", 15, 40, (15, 40))
value_min, value_max = st.sidebar.slider("Değer Aralığı", 0, 2_000_000, (0, 2_000_000))

def apply_filters(df):
    if not df.empty:
        df = df.copy()
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        if team_filter:
            df = df[df["team_name"].isin(team_filter)]
        df = df[(df["age"] >= age_min) & (df["age"] <= age_max)]
        df = df[(df["value"] >= value_min) & (df["value"] <= value_max)]
    return df

# Kadro Gücü ve Gençlik Analizi
if menu == "Kadro Gücü ve Gençlik Analizi":
    st.subheader("🔝 Takımların Kadro Değeri ve Gençlik Profili")
    df_filtered = apply_filters(players_all)
    if df_filtered.empty:
        st.warning("Filtreye uyan oyuncu bulunamadı.")
    else:
        top11 = (
            df_filtered.groupby("team_name")
            .agg(top11_value=("value", lambda x: x.nlargest(11).sum()))
            .reset_index()
        )
        total = df_filtered.groupby("team_name")["value"].sum().reset_index(name="total_value")
        
        def calc_group_value(df, max_age):
            return df[df["age"] <= max_age].groupby("team_name")["value"].sum().reset_index(name=f"u{max_age}_value")
        
        u23 = calc_group_value(df_filtered, 23)
        u21 = calc_group_value(df_filtered, 21)
        u18 = calc_group_value(df_filtered, 18)
        count = df_filtered.groupby("team_name")["player_id"].count().reset_index(name="total_players")

        df = total.merge(top11, on="team_name").merge(u23, on="team_name", how="left")\
                 .merge(u21, on="team_name", how="left").merge(u18, on="team_name", how="left")\
                 .merge(count, on="team_name")
        st.dataframe(df.sort_values("top11_value", ascending=False))

elif menu == "Transfer Takibi":
    st.subheader("🔁 Oyuncu Transferleri")
    if players_all.empty:
        st.warning("Transfer verisi yok.")
    else:
        transfer_df = players_all.groupby("player_id")["team_name"].nunique().reset_index()
        transfer_ids = transfer_df[transfer_df["team_name"] > 1]["player_id"]
        transfer_list = players_all[players_all["player_id"].isin(transfer_ids)]
        st.dataframe(transfer_list)

elif menu == "Aktif Oyuncular (Maçlara Çıkanlar)":
    st.subheader("⚽ Maçlara Çıkan Oyuncular")
    if match_details_all.empty:
        st.warning("Maç detayı bulunamadı.")
    else:
        df = match_details_all.copy()
        if team_filter:
            df = df[df["team_name"].isin(team_filter)]
        player_counts = df.groupby(["team_name", "player_id", "name"])["match_id"].count().reset_index(name="matches_played")
        st.dataframe(player_counts.sort_values("matches_played", ascending=False))

elif menu == "En Çok Maç Oynayanlar":
    st.subheader("🏃 En Aktif Oyuncular")
    if match_details_all.empty:
        st.warning("Maç detayı bulunamadı.")
    else:
        df = match_details_all.copy()
        if team_filter:
            df = df[df["team_name"].isin(team_filter)]
        top_players = df.groupby(["player_id", "name", "team_name"])["match_id"].count().reset_index(name="played")
        top_players = top_players.sort_values("played", ascending=False)
        st.dataframe(top_players)

elif menu == "U18/U21/U23 Kadro Detayları":
    st.subheader("👶 Genç Kadro Dağılımları")
    df_filtered = apply_filters(players_all)
    u18 = df_filtered[df_filtered["age"] <= 18]
    u21 = df_filtered[df_filtered["age"] <= 21]
    u23 = df_filtered[df_filtered["age"] <= 23]

    tabs = st.tabs(["Tüm Kadro", "U18", "U21", "U23"])
    with tabs[0]: st.dataframe(df_filtered.sort_values("value", ascending=False))
    with tabs[1]: st.dataframe(u18.sort_values("value", ascending=False))
    with tabs[2]: st.dataframe(u21.sort_values("value", ascending=False))
    with tabs[3]: st.dataframe(u23.sort_values("value", ascending=False))

# Takım ve oyuncu detayları
def display_player_details(player_id):
    player = players_all[players_all["player_id"] == player_id].iloc[0]
    st.write(f"**{player['name']}**")
    st.write(f"Yaş: {player['age']}")
    st.write(f"Değer: {player['value']}")
    matches_played = match_details_all[match_details_all["player_id"] == player_id]
    st.write(f"Oynadığı Maç Sayısı: {matches_played.shape[0]}")

def display_team_details(team_name):
    team_players = players_all[players_all["team_name"] == team_name]
    total_value = team_players["value"].sum()
    transfers = team_players.groupby("team_name")["player_id"].count().reset_index(name="transfers")
    st.write(f"**{team_name}**")
    st.write(f"Kadro Değeri: {total_value}")
    st.write(f"Yapılan Transfer Sayısı: {transfers['transfers'].iloc[0]}")
    st.write(f"**Tahmini Lig Sıralaması:** 3. (Örnek Sıralama)")  # Bu kısmı daha dinamik hale getirebiliriz
    st.write(f"**Aktif Durum:** Aktif" )  # Bu kısmı da sistemle bağlayabiliriz

# Oyuncu ve Takım Detayları
if st.button("Takım Detayları"):
    team_name = st.selectbox("Bir takım seç", players_all["team_name"].unique(), key="team_selectbox_2")
    display_team_details(team_name)

if st.button("Oyuncu Detayları"):
    player_id = st.selectbox("Bir oyuncu seç", players_all["player_id"].unique(), key="player_selectbox_1")
    display_player_details(player_id)
