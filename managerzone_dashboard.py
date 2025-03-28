import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

# CSV dosyalarını yüklemek için yardımcı fonksiyon
@st.cache_data(show_spinner=False)
def load_csv(file):
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"CSV dosyası yüklenirken bir hata oluştu: {e}")
        return pd.DataFrame()

# Başlık ve ana açıklama
st.set_page_config(page_title="ManagerZone Analiz Merkezi", layout="wide")
st.title("📊 ManagerZone Analiz Merkezi")
st.markdown("### Verileri yükleyin ve analizleri görselleştirin.")

# Dosya yükleme alanları
st.sidebar.header("CSV Dosyaları Yükleyin")
players_file = st.sidebar.file_uploader("Oyuncular Verisi", type="csv")
leagues_file = st.sidebar.file_uploader("Ligi ve Takımları Verisi", type="csv")

# Dosyalar yüklendiyse veriyi al
if players_file and leagues_file:
    players_df = load_csv(players_file)
    leagues_df = load_csv(leagues_file)
    
    # Veriyi işle ve gösterecek alanlar
    st.subheader("📅 Veri Bilgisi")
    st.write(f"Toplam Oyuncu Sayısı: {len(players_df)}")
    st.write(f"Toplam Takım Sayısı: {len(leagues_df)}")
    
    # Takım ve oyuncu sayıları analizi
    st.subheader("📊 Takım ve Oyuncu Analizi")
    team_player_count = players_df.groupby("team_name").size().reset_index(name="player_count")
    st.write("Her Takımda Bulunan Oyuncu Sayıları")
    st.dataframe(team_player_count)

    # Takımların ligdeki sıralamasını ve analizini yapabiliriz
    st.subheader("🏆 Takımların Liglerdeki Dağılımı")
    team_league = leagues_df[["team_name", "league_name"]].drop_duplicates()
    st.write("Takımlar ve Ligdeki Adları")
    st.dataframe(team_league)

    # Genel oyuncu yaş ve değer analizi
    st.subheader("⚽ Oyuncu Yaş ve Değer Dağılımı")
    players_df["age"] = pd.to_numeric(players_df["age"], errors="coerce")
    players_df["value"] = pd.to_numeric(players_df["value"], errors="coerce")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=players_df["age"], y=players_df["value"], mode='markers', 
                             marker=dict(color='blue', size=8, opacity=0.6, line=dict(width=0.5, color='black'))))
    fig.update_layout(title="Oyuncu Yaş ve Değer Dağılımı",
                      xaxis_title="Yaş",
                      yaxis_title="Değer",
                      showlegend=False)
    st.plotly_chart(fig)

    # En yüksek değerli oyuncuları listeleyelim
    st.subheader("💰 En Yüksek Değerli Oyuncular")
    top_players = players_df.nlargest(10, 'value')
    st.write(top_players[["name", "team_name", "age", "value"]])

else:
    st.warning("Lütfen her iki CSV dosyasını da yükleyin.")
