import streamlit as st
import pandas as pd

# CSV dosyalarını yüklemek
def load_csv(file):
    df = pd.read_csv(file)
    return df

st.title("ManagerZone Analiz Merkezi")

# CSV Yükleme
players_file = st.file_uploader("Oyuncu Verisini Yükleyin", type=["csv"])
teams_file = st.file_uploader("Takım Verisini Yükleyin", type=["csv"])

# Eğer dosyalar yüklenirse işlemi başlat
if players_file is not None and teams_file is not None:
    players_df = load_csv(players_file)
    teams_df = load_csv(teams_file)

    # 2. Lig Dropdown Menüsü
    leagues = teams_df["league_name"].unique()
    selected_league = st.selectbox("Ligi Seç", leagues)

    # Ligdeki Takımlar
    league_teams = teams_df[teams_df["league_name"] == selected_league]
    st.write("Ligdeki Takımlar ve Değerleri", league_teams)

    # U18, U21, U23 Değer, Maaş, Kadro Değeri
    u18_df = players_df[players_df["age"] <= 18]
    u21_df = players_df[players_df["age"] <= 21]
    u23_df = players_df[players_df["age"] <= 23]
    
    st.write("U18 Kadro Değeri:", u18_df["value"].sum())
    st.write("U21 Kadro Değeri:", u21_df["value"].sum())
    st.write("U23 Kadro Değeri:", u23_df["value"].sum())
    
    # 3. Oyuncu Filtreleme
    player_name = st.selectbox("Oyuncu Seç", players_df["name"].unique())
    selected_player = players_df[players_df["name"] == player_name].iloc[0]
    
    st.write(f"**{selected_player['name']}**")
    st.write(f"Yaş: {selected_player['age']}")
    st.write(f"Değer: {selected_player['value']}")
    st.write(f"Maaş: {selected_player['salary']}")
    st.write(f"Ülke: {selected_player['countryShortname']}")
    
    # 4. Takım Verisi
    team_name = st.selectbox("Takım Seç", league_teams["teamName"].unique())
    team_players = players_df[players_df["teamName"] == team_name]

    # U18, U21, U23 oyuncularını ayrı ayrı gösterelim
    u18_team = team_players[team_players["age"] <= 18]
    u21_team = team_players[team_players["age"] <= 21]
    u23_team = team_players[team_players["age"] <= 23]
    
    st.write(f"**{team_name}** Takımının U18 Oyuncuları", u18_team)
    st.write(f"**{team_name}** Takımının U21 Oyuncuları", u21_team)
    st.write(f"**{team_name}** Takımının U23 Oyuncuları", u23_team)

    # En değerli 11 oyuncu
    top11_players = team_players.nlargest(11, "value")[["name", "age", "value", "salary"]]
    st.write(f"**{team_name}** Takımının En Değerli 11 Oyuncusu", top11_players)
    
    # Tüm takımları ve oyuncularını görmek için:
    st.write("Takımın Bütün Oyuncuları", team_players)

else:
    st.warning("Lütfen her iki CSV dosyasını yükleyin.")
