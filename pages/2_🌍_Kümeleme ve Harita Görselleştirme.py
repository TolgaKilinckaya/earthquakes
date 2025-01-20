import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

st.set_page_config(page_title="Kümeleme ve Harita Görselleştirme", page_icon="🌍", layout="wide")

st.title("Kümeleme ve Harita Görselleştirme")
uploaded_file = "filtered.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    filtered_data = data[data["Magnitude"] > 4]

    k = st.sidebar.slider("Küme Sayısı (k)", min_value=2, max_value=10, value=3)
    clustering_data = filtered_data[["Latitude", "Longitude"]]
    scaler = StandardScaler()
    clustering_data_normalized = scaler.fit_transform(clustering_data)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    filtered_data["Cluster"] = kmeans.fit_predict(clustering_data_normalized)

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

        colors = ['red', 'blue', 'green', 'purple', 'orange']
        for cluster in range(k):
            cluster_data = filtered_data[filtered_data['Cluster'] == cluster]
            x, y = m(cluster_data["Longitude"].values, cluster_data["Latitude"].values)
            m.scatter(x, y, c=colors[cluster % len(colors)], s=40, alpha=0.6, edgecolor='k')

        plt.title("Haritadaki Kümeler")
        st.pyplot(plt.gcf())

    plot_clustering_map(filtered_data, k)

    cluster_stats = (
        filtered_data.groupby("Cluster")
        .agg(
            Count=("Cluster", "size"),
            Avg_Magnitude=("Magnitude", "mean"),
            Avg_Depth=("Depth", "mean"),
            Min_Magnitude=("Magnitude", "min"),
            Max_Magnitude=("Magnitude", "max"),
        )
        .reset_index()
    )

    # Renk haritası
    colors = ["red", "blue", "green", "purple", "orange", "cyan", "yellow", "pink", "brown", "gray"]
    cluster_stats["Color"] = [colors[i % len(colors)] for i in cluster_stats["Cluster"]]

    # İstatistikleri tablo olarak göster
    st.subheader("Küme İstatistikleri")
    st.table(cluster_stats)

