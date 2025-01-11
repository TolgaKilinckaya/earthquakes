!pip install streamlit==1.26.0
!pip install pandas==1.5.3
!pip install matplotlib==3.7.1
!pip install scikit-learn==1.3.0
!pip install numpy==1.23.5

import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Streamlit sayfa ayarları
st.set_page_config(page_title="Deprem Analiz ve Clustering Uygulaması", layout="wide")

# Başlık ve Açıklama
st.title("Deprem Analiz ve Clustering Uygulaması")
st.sidebar.header("Parametreler")

# Veri yükleme
uploaded_file = st.sidebar.file_uploader("Deprem Verilerini Yükle (CSV)", type=["csv"])

if uploaded_file:
    # Veriyi oku
    data = pd.read_csv(uploaded_file)

    # Sekmeleri tanımla
    tab1, tab2, tab3 = st.tabs(["Zaman Serisi Analizi", "Clustering ve Harita", "En Derin ve Büyük Depremler"])

    # 1. Sekme: Zaman Serisi Analizi
    with tab1:
        st.subheader("Zaman Serisi Analizi")
        if "Timestamp" in data.columns and "Magnitude" in data.columns:
            data["datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
            data["year"] = data["datetime"].dt.year

            plt.figure(figsize=(12, 6))
            data.groupby('year').size().plot(kind='bar', color='coral')

            # Customize the plot for better aesthetics
            plt.title('Yearly Frequency of Earthquakes', fontsize=16)
            plt.xlabel('Year', fontsize=12)
            plt.ylabel('Number of Earthquakes', fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            st.pyplot(plt.gcf())
        else:
            st.error("Bu analiz için 'Time' ve 'Magnitude' sütunları gereklidir.")
                
        st.subheader("5 Yıllık Deprem Analizi")
        if "Timestamp" in data.columns:
            data["datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
            data["year"] = data["datetime"].dt.year

            # 5 yıllık aralıkları oluştur
            bins = range(data["year"].min(), data["year"].max() + 5, 5)
            data["5_year_bin"] = pd.cut(data["year"], bins=bins, right=False)

            # Görselleştirme
            plt.figure(figsize=(12, 6))
            data.groupby("5_year_bin").size().plot(kind="bar", color="lightseagreen")

            plt.title("Earthquake Frequency in 5-Year Intervals", fontsize=16)
            plt.xlabel("5-Year Interval", fontsize=12)
            plt.ylabel("Number of Earthquakes", fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()

            st.pyplot(plt.gcf())
        else:
            st.error("Bu analiz için 'Timestamp' sütunu gereklidir.")

    # 2. Sekme: Clustering ve Harita
    with tab2:
        st.subheader("Clustering ve Harita Görselleştirme")

        # Magnitude > 4 olan depremleri filtreleme
        filtered_data = data[data["Magnitude"] > 4]

        # Kullanıcıdan K-Means parametrelerini alma
        k = st.sidebar.slider("Küme Sayısı (k)", min_value=2, max_value=10, value=3)

        # Clustering için Latitude ve Longitude sütunlarını seçin
        clustering_data = filtered_data[["Latitude", "Longitude"]]
        scaler = StandardScaler()
        clustering_data_normalized = scaler.fit_transform(clustering_data)

        # K-Means uygulama
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        filtered_data["Cluster"] = kmeans.fit_predict(clustering_data_normalized)

        # Basemap haritasını çizme işlevi
        def plot_clustering_map(filtered_data, k):
            plt.figure(figsize=(12, 8))
            m = Basemap(projection="merc",
                        llcrnrlat=filtered_data["Latitude"].min() - 0.25,
                        urcrnrlat=filtered_data["Latitude"].max() + 0.25,
                        llcrnrlon=filtered_data["Longitude"].min() - 0.25,
                        urcrnrlon=filtered_data["Longitude"].max() + 0.25,
                        resolution="i")
            m.drawcoastlines()
            m.drawcountries()
            m.drawmapboundary(fill_color="lightblue")
            m.fillcontinents(color="lightgray", lake_color="lightblue")
            m.drawparallels(range(-90, 91, 10), labels=[1, 0, 0, 0])
            m.drawmeridians(range(-180, 181, 10), labels=[0, 0, 0, 1])

            # Cluster noktalarını çiz
            colors = ['red', 'blue', 'green', 'purple', 'orange']
            for cluster in range(k):
                cluster_data = filtered_data[filtered_data['Cluster'] == cluster]
                for _, row in cluster_data.iterrows():
                    x, y = m(row["Longitude"], row["Latitude"])
                    # Nokta büyüklüğünü büyüklüğe göre ayarla
                    if 4 <= row['Magnitude'] < 5:
                        size = 40  # Küçük noktalar
                    elif 5 <= row['Magnitude'] < 6:
                        size = 80  # Orta büyüklükte noktalar
                    else:
                        size = 160  # Büyük noktalar
                    m.scatter(x, y, c=colors[cluster % len(colors)], s=size, alpha=0.6, edgecolor='k')

            plt.title("Magnitude-based Clustering (4+ Earthquakes) on Map")
            st.pyplot(plt.gcf())

        # Harita çizimi
        plot_clustering_map(filtered_data, k)
    
    # 3. Sekme: En Derin ve Büyük Depremler
    with tab3:
        st.subheader("En Derin ve Büyük Depremler")

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

else:
    st.write("Lütfen bir CSV dosyası yükleyin.")
