import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="En Derin ve Büyük Depremler", page_icon="🔍", layout="wide")
st.title("En Derin ve Büyük Depremler")

uploaded_file = "deprem_verileri.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    n = st.sidebar.slider("Kaç deprem gösterilsin? (n)", min_value=5, max_value=40, value=10)

    # En derin ve en büyük depremleri seçme
    en_derinler = data.nlargest(n, 'Depth')
    en_buyukler = data.nlargest(n, 'Magnitude')
    ortak_depremler = pd.merge(en_derinler, en_buyukler, how='inner')

    # Harita oluştur
    st.subheader("İnteraktif Deprem Haritası")
    m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=6)

    # En derin depremler (kırmızı)
    for _, row in en_derinler.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color='red',
            fill=True,
            fill_opacity=0.6,
            popup=f"Derin Deprem:<br><b>Tarih:</b> {row['Date']}<br><b>Derinlik:</b> {row['Depth']} km<br><b>Büyüklük:</b> {row['Magnitude']}<br><b>Yer:</b> {row.get('Yer', 'N/A')}"
        ).add_to(m)

    # En büyük depremler (mavi)
    for _, row in en_buyukler.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=row['Magnitude'],
            color='blue',
            fill=True,
            fill_opacity=0.6,
            popup=f"Büyük Deprem:<br><b>Tarih:</b> {row['Date']}<br><b>Büyüklük:</b> {row['Magnitude']}<br><b>Derinlik:</b> {row['Depth']} km<br><b>Yer:</b> {row.get('Yer', 'N/A')}"
        ).add_to(m)

    # Ortak depremler (yeşil)
    for _, row in ortak_depremler.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=row['Magnitude'] + 2,
            color='green',
            fill=True,
            fill_opacity=0.8,
            popup=f"Ortak Deprem:<br><b>Tarih:</b> {row['Date']}<br><b>Derinlik:</b> {row['Depth']} km<br><b>Şiddet:</b> {row['Magnitude']}<br><b>Yer:</b> {row.get('Yer', 'N/A')}"
        ).add_to(m)

    # Ekstra: Sınır çizgisi ekle
    bounds = [[36.00, 22.50], [36.00, 30.50], [41.20, 30.50], [41.20, 22.50], [36.00, 22.50]]
    folium.PolyLine(bounds, color="black", weight=2.5, opacity=1).add_to(m)

    st_folium(m, width=1000, height=600)

    # Ek veriler
    st.subheader("İstatistiksel Bilgiler")
    st.write("En derin "+str(n)+" deprem:")
    st.write(en_derinler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
    st.write("En büyük "+str(n)+" deprem:")
    st.write(en_buyukler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
    st.write("Ortak olanlar:")
    st.write(ortak_depremler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
