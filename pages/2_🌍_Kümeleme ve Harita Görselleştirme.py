import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Kümeleme ve Harita Görselleştirme", page_icon="🌍", layout="wide")
st.title("Kümeleme ve Harita Görselleştirme")

uploaded_file = "deprem_verileri.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    filtered_data = data[data["Magnitude"] > 4]

    k = st.sidebar.slider("Küme Sayısı (k)", min_value=2, max_value=10, value=3)
    clustering_data = filtered_data[["Latitude", "Longitude"]]
    scaler = StandardScaler()
    clustering_data_normalized = scaler.fit_transform(clustering_data)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    filtered_data["Cluster"] = kmeans.fit_predict(clustering_data_normalized)

    def plot_clustering_map_interactive(filtered_data, k):
        st.subheader("İnteraktif Kümeleme Haritası")
        m = folium.Map(location=[filtered_data["Latitude"].mean(), filtered_data["Longitude"].mean()], zoom_start=6)

        colors = ['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'yellow', 'pink', 'brown', 'gray']

        for cluster in range(k):
            cluster_data = filtered_data[filtered_data['Cluster'] == cluster]
            for _, row in cluster_data.iterrows():
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,
                    color=colors[cluster % len(colors)],
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"<b>Deprem</b><br><b>Tarih:</b> {row.get('Date', 'N/A')}<br><b>Derinlik:</b> {row['Depth']} km<br><b>Büyüklük:</b> {row['Magnitude']}<br><b>Küme:</b> {cluster}",
                        max_width=250
                    )
                ).add_to(m)

        # Koordinat kutusu
        box_bounds = [[36.0, 22.5], [36.0, 30.5], [41.2, 30.5], [41.2, 22.5], [36.0, 22.5]]
        folium.PolyLine(locations=box_bounds, color="black", weight=2.5).add_to(m)

        st_folium(m, width=1000, height=600)

    # Harita çiz
    plot_clustering_map_interactive(filtered_data, k)

    # Küme istatistikleri
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

    # Renk eşleme
    colors = ["red", "blue", "green", "purple", "orange", "cyan", "yellow", "pink", "brown", "gray"]
    cluster_stats["Color"] = [colors[i % len(colors)] for i in cluster_stats["Cluster"]]

    # Tablo göster
    st.subheader("Küme İstatistikleri")
    st.table(cluster_stats)

    # Derinlik-Büyüklük K-Means görselleştirme
    if 'Depth' not in data.columns or 'Magnitude' not in data.columns:
        st.error("The dataset must contain 'Depth' and 'Magnitude' columns.")
    else:
        clustering_data_depth = data[['Depth']].dropna()
        scaler = StandardScaler()
        clustering_data_normalized = scaler.fit_transform(clustering_data_depth)

        kmeans_depth = KMeans(n_clusters=k, random_state=42, n_init=10)
        data['Cluster'] = kmeans_depth.fit_predict(clustering_data_normalized)

        st.subheader("Derinliğe Göre Kümeleme")
        fig, ax = plt.subplots(figsize=(9, 6))
        for cluster in range(k):
            cluster_data = data[data['Cluster'] == cluster]
            ax.scatter(cluster_data['Magnitude'], cluster_data['Depth'], label=f'Cluster {cluster}', alpha=0.6)

        ax.invert_yaxis()
        ax.set_xlabel('Büyüklük')
        ax.set_ylabel('Derinlik (km)')
        ax.set_title('K-Means Kümeleme: Derinlik vs. Büyüklük')
        ax.legend()
        ax.grid()
        st.pyplot(fig)

        cluster_stats_depth = data.groupby('Cluster').agg(
            Average_Depth=('Depth', 'mean'),
            Average_Magnitude=('Magnitude', 'mean'),
            Earthquake_Count=('Magnitude', 'count')
        ).reset_index()

        st.subheader("Küme İstatistikleri (Derinlik)")
        st.write(cluster_stats_depth)
