import streamlit as st
import pandas as pd

# Kullanıcının yüklediği CSV dosyalarını yüklemek için gerekli fonksiyon
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Kullanıcıdan CSV dosyalarını yüklemesini iste
st.title("📊 ManagerZone Analiz Merkezi")

# CSV yükleme
players_file = st.file_uploader("Oyuncu Verisini Yükleyin", type=["csv"])
leagues_file = st.file_uploader("Lig ve Takım Verisini Yükleyin", type=["csv"])

if players_file and leagues_file:
    players_df = load_data(players_file)
    leagues_df = load_data(leagues_file)
    
    # Ligler ve Takımlar
    st.subheader("🏅 Takımlar ve Ligler")
    league_info = leagues_df[["team_id", "team_name", "league"]].drop_duplicates()
    st.dataframe(league_info)

    # Takım bazında oyuncu sayısı
    team_player_count = players_df.groupby("team_name").size().reset_index(name="player_count")
    st.subheader("📊 Takım Oyuncu Sayısı")
    st.dataframe(team_player_count)

    # Takım ve oyuncu detayları
    st.subheader("⚽ Takım ve Oyuncu Detayları")
    team_name = st.selectbox("Bir takım seçin", players_df["team_name"].unique())
    
    team_players = players_df[players_df["team_name"] == team_name]
    st.write(f"{team_name} Takımındaki Oyuncular:")
    st.dataframe(team_players)

    # En değerli oyuncu
    st.subheader(f"🏅 {team_name} Takımının En Değerli Oyuncusu")
    most_valuable_player = team_players.loc[team_players["value"].idxmax()]
    st.write(f"**{most_valuable_player['name']}**")
    st.write(f"Değer: {most_valuable_player['value']}")

    # Yaş ve Değer Dağılımı
    st.subheader(f"📊 {team_name} Takımının Yaş ve Değer Dağılımı")
    st.bar_chart(team_players.groupby("age")["value"].sum())

    # Takımların Ligdeki Durumu
    league_status = leagues_df.groupby("league").size().reset_index(name="team_count")
    st.subheader("📈 Lig Durumu")
    st.dataframe(league_status)

else:
    st.warning("Lütfen her iki CSV dosyasını yükleyin!")
