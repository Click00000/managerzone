import streamlit as st
import pandas as pd

# Dosya yükleme
st.title('ManagerZone Analiz Merkezi')
st.sidebar.title("Veri Yükleme ve Filtreleme")

# Verileri yükle
players_file = st.sidebar.file_uploader("Oyuncu Verisini Yükle", type=["csv"])
teams_file = st.sidebar.file_uploader("Takım ve Lig Verisini Yükle", type=["csv"])

# Dosyalar yüklendiyse, CSV'leri pandas dataframe olarak al
if players_file is not None and teams_file is not None:
    players_df = pd.read_csv(players_file)
    teams_df = pd.read_csv(teams_file)

    st.sidebar.success("Veriler başarıyla yüklendi!")

    # Sayfa seçim
    page = st.sidebar.radio("Veri Görüntüleme", ["Takım", "Lig", "Oyuncu"])

    # 1. Takım Sayfası
    if page == "Takım":
        st.subheader("Takımların Değerleri ve Filtreleme")

        # Takım Seçimi
        team_name = st.selectbox("Takım Seç", players_df["team_name"].unique())
        team_data = players_df[players_df["team_name"] == team_name]

        # Takım bilgileri
        total_team_value = team_data["value"].sum()
        st.write(f"Toplam Kadro Değeri: {total_team_value:,} €")

        # U18, U21, U23 Kadro Değerleri
        u18_value = team_data[team_data["age"] <= 18]["value"].sum()
        u21_value = team_data[team_data["age"] <= 21]["value"].sum()
        u23_value = team_data[team_data["age"] <= 23]["value"].sum()

        st.write(f"U18 Kadro Değeri: {u18_value:,} €")
        st.write(f"U21 Kadro Değeri: {u21_value:,} €")
        st.write(f"U23 Kadro Değeri: {u23_value:,} €")

        # En değerli 11 oyuncu
        top_11 = team_data.nlargest(11, 'value')
        st.write("En Değerli 11 Oyuncu:")
        st.dataframe(top_11[["name", "age", "value"]])

    # 2. Lig Sayfası
    elif page == "Lig":
        st.subheader("Ligler ve Takım Değerleri")

        # Lig Seçimi
        league_name = st.selectbox("Lig Seç", teams_df["league_name"].unique())
        league_teams = teams_df[teams_df["league_name"] == league_name]

        # Lig verileri
        total_value = league_teams["value"].sum()
        u18_value = league_teams[league_teams["age"] <= 18]["value"].sum()
        u21_value = league_teams[league_teams["age"] <= 21]["value"].sum()
        u23_value = league_teams[league_teams["age"] <= 23]["value"].sum()

        st.write(f"Toplam Kadro Değeri: {total_value:,} €")
        st.write(f"U18 Kadro Değeri: {u18_value:,} €")
        st.write(f"U21 Kadro Değeri: {u21_value:,} €")
        st.write(f"U23 Kadro Değeri: {u23_value:,} €")

        # Takımları listele
        st.write("Ligdeki Takımlar:")
        st.dataframe(league_teams[["team_name", "value", "team_id"]])

    # 3. Oyuncu Sayfası
    elif page == "Oyuncu":
        st.subheader("Oyuncu Analizi")

        # Oyuncu Seçimi
        player_name = st.selectbox("Oyuncu Seç", players_df["name"].unique())
        player_data = players_df[players_df["name"] == player_name]

        st.write("Oyuncu Bilgileri:")
        st.write(player_data[["name", "age", "value", "salary", "countryShortname"]])

        # Oyuncunun takım bilgisi
        team_name = player_data["team_name"].iloc[0]
        team_value = players_df[players_df["team_name"] == team_name]["value"].sum()

        st.write(f"Takım: {team_name}")
        st.write(f"Takım Kadro Değeri: {team_value:,} €")

        # Oyuncunun oynadığı maç sayısı (dummy veri ekleyebilirsiniz)
        st.write(f"Oynanan Maç Sayısı: {len(player_data)}")

# Eğer dosyalar yüklenmemişse, uyarı göster
else:
    st.sidebar.warning("Lütfen CSV dosyalarını yükleyin.")
