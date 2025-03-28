import streamlit as st
import pandas as pd
import plotly.express as px

# Veri Yükleme Fonksiyonu
def load_data(file):
    return pd.read_csv(file)

# Takımlar ve Oyuncular İçin Filtreleme Fonksiyonu
def filter_leagues_data(df, filters):
    if filters['team_name']:
        df = df[df['teamName'].str.contains(filters['team_name'], case=False)]
    if filters['league_name']:
        df = df[df['league_name'].str.contains(filters['league_name'], case=False)]
    if filters['min_points'] is not None:
        df = df[df['points'] >= filters['min_points']]
    if filters['max_points'] is not None:
        df = df[df['points'] <= filters['max_points']]
    if filters['min_value'] is not None:
        df = df[df['toplam_kadro_degeri'] >= filters['min_value']]
    if filters['max_value'] is not None:
        df = df[df['toplam_kadro_degeri'] <= filters['max_value']]
    if filters['min_rank'] is not None:
        df = df[df['guc_siralamasi'] >= filters['min_rank']]
    if filters['max_rank'] is not None:
        df = df[df['guc_siralamasi'] <= filters['max_rank']]
    return df

def filter_players_data(df, filters):
    if filters['player_name']:
        df = df[df['name'].str.contains(filters['player_name'], case=False)]
    if filters['team_name']:
        df = df[df['teamName'].str.contains(filters['team_name'], case=False)]
    if filters['league_name']:
        df = df[df['league_name'].str.contains(filters['league_name'], case=False)]
    if filters['min_age']:
        df = df[df['age'] >= filters['min_age']]
    if filters['max_age']:
        df = df[df['age'] <= filters['max_age']]
    if filters['min_value']:
        df = df[df['value'] >= filters['min_value']]
    if filters['max_value']:
        df = df[df['value'] <= filters['max_value']]
    if filters['min_height']:
        df = df[df['height'] >= filters['min_height']]
    if filters['max_height']:
        df = df[df['height'] <= filters['max_height']]
    if filters['min_weight']:
        df = df[df['weight'] >= filters['min_weight']]
    if filters['max_weight']:
        df = df[df['weight'] <= filters['max_weight']]
    if filters['country']:
        df = df[df['countryShortname'].str.contains(filters['country'], case=False)]
    if filters['junior'] != "Hepsi":
        df = df[df['junior'] == filters['junior']]
    return df

# Render Filtreleme ve Takım Görüntüleme
def render_team_search_section(leagues_df):
    st.header("Takım Arama ve Filtreleme")
    
    filtered_df = leagues_df.copy()
    
    with st.form(key="team_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            team_name = st.text_input("Takım Adı")
            min_points = st.slider("Minimum Puan", 0, 100, 0)
            min_value = st.number_input("Minimum Kadro Değeri", 0, value=0, step=100000, format="%d")
        
        with col2:
            league_name = st.text_input("Lig Adı")
            max_points = st.slider("Maksimum Puan", 0, 100, 100)
            max_value = st.number_input("Maksimum Kadro Değeri", 0, value=20000000, step=100000, format="%d")
        
        col3, col4 = st.columns(2)
        with col3:
            min_rank = st.slider("Minimum Sıralama", 1, 20, 1)
        with col4:
            max_rank = st.slider("Maksimum Sıralama", 1, 20, 20)
        
        search_button = st.form_submit_button(label="Ara")
    
    if search_button:
        filters = {
            'team_name': team_name,
            'league_name': league_name,
            'min_points': min_points,
            'max_points': max_points,
            'min_value': min_value,
            'max_value': max_value,
            'min_rank': min_rank,
            'max_rank': max_rank
        }
        filtered_df = filter_leagues_data(leagues_df, filters)
        st.subheader(f"Sonuçlar ({len(filtered_df)} takım bulundu)")
    else:
        st.subheader(f"Tüm Takımlar ({len(filtered_df)})")
        st.info("Filtre uygulamak için yukarıdaki değerleri ayarlayın ve 'Ara' düğmesine basın.")
    
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        
        currency_columns = ['toplam_kadro_degeri', 'u23_kadro_degeri', 'u21_kadro_degeri', 'u18_kadro_degeri', 'en_degerli_11']
        for col in currency_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f} €" if not pd.isna(x) else "N/A")
        
        base_columns = ['teamName', 'league_name', 'played', 'won', 'drawn', 'lost', 'points']
        value_columns = [col for col in ['toplam_kadro_degeri', 'en_degerli_11', 'guc_siralamasi'] if col in display_df.columns]
        columns_to_show = base_columns + value_columns
        st.dataframe(display_df[columns_to_show].set_index('teamName'), use_container_width=True)

# Render Oyuncu Arama ve Filtreleme
def render_player_search_section(players_df):
    st.header("Oyuncu Arama ve Filtreleme")
    
    filtered_df = players_df.copy()
    
    with st.form(key="player_search_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            player_name = st.text_input("Oyuncu Adı")
            min_age = st.slider("Minimum Yaş", 16, 40, 16)
            min_value = st.number_input("Minimum Değer", 0, value=0, step=100000, format="%d")
            min_height = st.slider("Minimum Boy (cm)", 150, 210, 150)
        
        with col2:
            team_name = st.text_input("Takım Adı")
            max_age = st.slider("Maksimum Yaş", 16, 40, 40)
            max_value = st.number_input("Maksimum Değer", 0, value=20000000, step=100000, format="%d")
            max_height = st.slider("Maksimum Boy (cm)", 150, 210, 210)
        
        with col3:
            league_name = st.text_input("Lig Adı")
            country = st.text_input("Ülke Kodu")
            junior = st.selectbox("Altyapı Oyuncusu", ["Hepsi", "Evet", "Hayır"])
            min_weight = st.slider("Minimum Kilo (kg)", 50, 110, 50)
            max_weight = st.slider("Maksimum Kilo (kg)", 50, 110, 110)
        
        search_button = st.form_submit_button(label="Ara")
    
    if search_button:
        filters = {
            'player_name': player_name,
            'team_name': team_name,
            'league_name': league_name,
            'min_age': min_age,
            'max_age': max_age,
            'min_value': min_value,
            'max_value': max_value,
            'min_height': min_height,
            'max_height': max_height,
            'min_weight': min_weight,
            'max_weight': max_weight,
            'country': country,
            'junior': junior if junior != "Hepsi" else None
        }
        filtered_df = filter_players_data(players_df, filters)
        st.subheader(f"Sonuçlar ({len(filtered_df)} oyuncu bulundu)")
    else:
        st.subheader(f"Tüm Oyuncular ({len(filtered_df)})")
        st.info("Filtre uygulamak için yukarıdaki değerleri ayarlayın ve 'Ara' düğmesine basın.")
    
    if not filtered_df.empty:
        display_df = filtered_df.copy()
        display_df['value'] = display_df['value'].apply(lambda x: f"{x:,.0f} €")
        display_df['salary'] = display_df['salary'].apply(lambda x: f"{x:,.0f} €")
        
        columns_to_show = ['name', 'age', 'value', 'teamName', 'league_name', 'countryShortname', 'height', 'weight', 'shirtNo', 'junior']
        st.dataframe(display_df[columns_to_show].set_index('name'), use_container_width=True)
    else:
        st.warning("Filtrelere uygun oyuncu bulunamadı.")

# Main Render
def main():
    st.title("ManagerZone Takım ve Oyuncu Analiz Dashboard")
    
    uploaded_league_file = st.file_uploader("Lig ve Takım Verisini Yükleyin", type=["csv"])
    uploaded_player_file = st.file_uploader("Oyuncu Verisini Yükleyin", type=["csv"])
    
    if uploaded_league_file and uploaded_player_file:
        leagues_df = load_data(uploaded_league_file)
        players_df = load_data(uploaded_player_file)
        
        render_team_search_section(leagues_df)
        render_player_search_section(players_df)

# Run the app
if __name__ == "__main__":
    main()
