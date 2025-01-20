import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

st.set_page_config(page_title="En Derin ve Büyük Depremler", page_icon="🔍", layout="wide")

st.title("En Derin ve Büyük Depremler")
uploaded_file = "filtered.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    n = st.sidebar.slider("Kaç deprem gösterilsin? (n)", min_value=5, max_value=40, value=10)

    # En derin ve en büyük depremleri seçme
    en_derinler = data.nlargest(n, 'Depth')
    en_buyukler = data.nlargest(n, 'Magnitude')
    ortak_depremler = pd.merge(en_derinler, en_buyukler, how='inner')

    # Harita çizimi
    st.subheader("Deprem Haritası")
    fig, ax = plt.subplots(figsize=(12, 8))
    m = Basemap(projection='merc', llcrnrlat=data['Latitude'].min() - 0.25, urcrnrlat=data['Latitude'].max() + 0.25,
        llcrnrlon=data['Longitude'].min() - 0.25, urcrnrlon=data['Longitude'].max() + 0.25, resolution='i', ax=ax)
    m.drawcoastlines()
    m.drawcountries()
    m.fillcontinents(color='lightgray', lake_color='aqua')
    m.drawmapboundary(fill_color='aqua')

    # En derin depremleri kırmızı göster
    x, y = m(en_derinler['Longitude'].values, en_derinler['Latitude'].values)
    m.scatter(x, y, s=en_derinler['Depth'], c='red', alpha=0.6, label='En Derin Depremler')

    # En büyük depremleri mavi göster
    x, y = m(en_buyukler['Longitude'].values, en_buyukler['Latitude'].values)
    m.scatter(x, y, s=en_buyukler['Magnitude'] * 10, c='blue', alpha=0.6, label='En Büyük Depremler')

    # Ortak olanları yeşil göster
    x, y = m(ortak_depremler['Longitude'].values, ortak_depremler['Latitude'].values)
    m.scatter(x, y, s=ortak_depremler['Magnitude'] * 10, c='green', alpha=0.8, label='Ortak Depremler')

    # Lejand ve başlık
    plt.title("En Derin ve En Büyük Depremlerin Haritası", fontsize=14)
    plt.legend(loc='lower left')
    st.pyplot(fig)

    # Ek veriler
    st.subheader("İstatistiksel Bilgiler")
    st.write("En derin "+str(n)+" deprem:")
    st.write(en_derinler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
    st.write("En büyük "+str(n)+" deprem:")
    st.write(en_buyukler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
    st.write("Ortak olanlar:")
    st.write(ortak_depremler[['Date', 'Latitude', 'Longitude', 'Depth', 'Magnitude']])
