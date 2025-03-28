import streamlit as st
import pandas as pd

# CSV dosyasını yükle
@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# CSV dosyalarını yükle
players_file = st.file_uploader("Oyuncu Verisini Yükleyin", type=["csv"])
leagues_file = st.file_uploader("Lig ve Takım Verisini Yükleyin", type=["csv"])

# Veriler yüklenmişse
if players_file is not None and leagues_file is not None:
    players_df = load_csv(players_file)
    leagues_df = load_csv(leagues_file)
    
    # Takım ve oyuncu sayıları analizi
    st.subheader("📊 Takım ve Oyuncu Analizi")
    team_player_count = players_df.groupby("teamName").size().reset_index(name="player_count")
    st.write("Her Takımda Bulunan Oyuncu Sayıları")
    st.dataframe(team_player_count)

    # Lig ve takım bilgisi
    st.subheader("🏅 Takımlar ve Ligler")
    league_info = leagues_df[["teamId", "teamName", "league_name"]].drop_duplicates()
    st.dataframe(league_info)

    # Kadro Değerleri
    st.subheader("💰 Kadro Değerleri")
    team_value = players_df.groupby("teamName").agg({
        "value": "sum",
        "salary": "sum",
        "age": "mean"
    }).reset_index()

    team_value = team_value.rename(columns={"value": "total_value", "salary": "total_salary", "age": "average_age"})

    st.write(f"Toplam Kadro Değeri, Toplam Maaş ve Ortalama Yaş")
    st.dataframe(team_value)

    # U18, U21, U23 kadro dağılımı
    st.subheader("👶 Genç Kadro Dağılımları")
    u18 = players_df[players_df["age"] <= 18].groupby("teamName").agg({
        "value": "sum",
        "salary": "sum"
    }).reset_index().rename(columns={"value": "u18_value", "salary": "u18_salary"})

    u21 = players_df[players_df["age"] <= 21].groupby("teamName").agg({
        "value": "sum",
        "salary": "sum"
    }).reset_index().rename(columns={"value": "u21_value", "salary": "u21_salary"})

    u23 = players_df[players_df["age"] <= 23].groupby("teamName").agg({
        "value": "sum",
        "salary": "sum"
    }).reset_index().rename(columns={"value": "u23_value", "salary": "u23_salary"})

    # En değerli 11 oyuncu
    st.subheader("⚽ En Değerli 11 Oyuncu")
    top_11 = players_df.nlargest(11, "value")[["name", "value", "teamName"]]
    st.dataframe(top_11)

    # Takıma göre oyuncu listesi
    team_name = st.selectbox("Bir takım seç", players_df["teamName"].unique())
    team_players = players_df[players_df["teamName"] == team_name].sort_values(by="value", ascending=False)

    st.subheader(f"{team_name} Oyuncu Listesi")
    st.dataframe(team_players[["name", "age", "value", "salary"]])
    
    # Kadro Değerleri Sonuçları
    team_summary = team_value[team_value["teamName"] == team_name]
    if not team_summary.empty:
        st.write(f"{team_name} Kadro Değerleri:")
        st.write(f"Toplam Kadro Değeri: {team_summary['total_value'].values[0]} €")
        st.write(f"Toplam Maaş: {team_summary['total_salary'].values[0]} €")
        st.write(f"Ortalama Yaş: {team_summary['average_age'].values[0]}")
    else:
        st.write("Seçilen takımın kadro değerleri bulunamadı.")
