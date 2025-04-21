import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from obspy.clients.fdsn import Client
from obspy import UTCDateTime
import io
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Deprem Dalgaları", page_icon="🌌", layout="wide")
st.title("KOERI'den Dalga Formu Verisi 🌌")

client = Client("KOERI")

# İstasyonları çek
with st.spinner("İstasyonlar yükleniyor..."):
    try:
        inventory = client.get_stations(network="*", station="*", minlatitude=36, maxlatitude=41.2,
                                        minlongitude=22.5, maxlongitude=30.5, level="station")
        stations = []
        for net in inventory:
            for sta in net:
                stations.append({
                    "Network": net.code,
                    "Station": sta.code,
                    "Latitude": sta.latitude,
                    "Longitude": sta.longitude,
                    "Elevation": sta.elevation,
                    "SiteName": sta.site.name
                })
        stations_df = pd.DataFrame(stations)

        st.subheader("İstanbul Civarındaki İstasyonlar (40.5°-41.5°, 28°-30.5°)")
        st.dataframe(stations_df)

        # Harita göster
        st.subheader("İstasyonların Harita Üzerinde Gösterimi")
        map_center = [stations_df["Latitude"].mean(), stations_df["Longitude"].mean()]
        fmap = folium.Map(location=map_center, zoom_start=8)
        for _, row in stations_df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"{row['Network']}.{row['Station']}\n{row['SiteName']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(fmap)

        st_folium(fmap, height=500, width=1000)

    except Exception as e:
        st.error(f"İstasyon bilgileri alınamadı: {e}")

# Kullanıcıdan tarih girişi
st.sidebar.subheader("Veri Çekme Ayarları")
tarih = st.sidebar.date_input("Başlangıç Tarihi", value=pd.to_datetime("2023-02-04"))
saat = st.sidebar.time_input("Saat", value=pd.to_datetime("00:00:00").time())
sure_saat = st.sidebar.number_input("Veri Süresi (saat)", min_value=0.5, max_value=24.0, value=1.0, step=0.5)

network = st.sidebar.text_input("Network", "KO")
station = st.sidebar.text_input("İstasyon", "KHMN")
location = st.sidebar.text_input("Location", "*")
channel = st.sidebar.text_input("Kanal", "*")

if st.sidebar.button("Veriyi Getir"):
    try:
        t1 = UTCDateTime(pd.Timestamp.combine(tarih, saat))
        t2 = t1 + int(sure_saat * 3600)

        with st.spinner("Veri çekiliyor..."):
            st_wave = client.get_waveforms(network, station, location, channel, t1, t2)

        st.success("Veri başarıyla çekildi!")

        # Dalgayı çizim için matplotlib figürüne aktar
        fig = st_wave.plot(equal_scale=False, show=False, method="full")
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        st.image(buf)

    except Exception as e:
        st.error(f"Veri alınırken bir hata oluştu: {e}")
