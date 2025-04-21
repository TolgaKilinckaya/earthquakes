import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Grafikler", page_icon="📊", layout="wide")
st.title("Zaman Serisi Analizi")

uploaded_file = "deprem_verileri.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)

    # Timestamp kontrol ve datetime'a çevirme
    if "Timestamp" in data.columns:
        data["datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f", errors='coerce')
        data = data.dropna(subset=['datetime'])
        data["year"] = data["datetime"].dt.year
        data["month"] = data["datetime"].dt.month
        data["date_only"] = data["datetime"].dt.date
    else:
        st.error("Veri setinde 'Timestamp' sütunu bulunamadı.")

    # 1. Yıllara Göre Deprem Sayısı
    st.subheader("Yıllara Göre Deprem Sayısı")
    plt.figure(figsize=(12, 6))
    data.groupby('year').size().plot(kind='bar', color='coral')
    plt.title('Yıllık Deprem Sıklığı', fontsize=16)
    plt.xlabel('Yıl')
    plt.ylabel('Deprem Sayısı')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 2. Ortalama Büyüklük
    st.subheader("Yıllara Göre Ortalama Büyüklük")
    plt.figure(figsize=(12, 6))
    data.groupby("year")["Magnitude"].mean().plot(kind='line', marker='o', color='darkblue')
    plt.title("Yıllık Ortalama Deprem Büyüklüğü", fontsize=16)
    plt.xlabel("Yıl")
    plt.ylabel("Ortalama Mw")
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 3. 5 Yıllık Aralıklar
    st.subheader("5 Yıllık Aralıklara Göre Deprem Sıklığı")
    bins = range(data["year"].min(), data["year"].max() + 5, 5)
    data["5_year_bin"] = pd.cut(data["year"], bins=bins, right=False)
    plt.figure(figsize=(12, 6))
    data.groupby("5_year_bin").size().plot(kind="bar", color="lightseagreen")
    plt.title("5 Yıllık Aralıklara Göre Deprem Sıklığı", fontsize=16)
    plt.xlabel("5-Yıllık Küme")
    plt.ylabel("Deprem Sayısı")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 4. Yıl-Ay Isı Haritası
    st.subheader("Ay ve Yıla Göre Isı Haritası")
    heatmap_data = data.groupby(["year", "month"]).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(heatmap_data.T, aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(heatmap_data.index)))
    ax.set_xticklabels(heatmap_data.index, rotation=90)
    ax.set_yticks(range(1, 13))
    ax.set_yticklabels(["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"])
    plt.title("Yıl-Ay Bazlı Deprem Sıklığı")
    plt.colorbar(im, label="Deprem Sayısı")
    plt.tight_layout()
    st.pyplot(fig)

    # 5. Küme Sayımı (Kümülâtif)
    st.subheader("Kümülâtif Deprem Sayısı")
    data_sorted = data.sort_values("datetime")
    data_sorted["Cumulative"] = np.arange(1, len(data_sorted) + 1)
    plt.figure(figsize=(12,6))
    plt.plot(data_sorted["datetime"], data_sorted["Cumulative"], color="teal")
    plt.xlabel("Zaman")
    plt.ylabel("Toplam Deprem Sayısı")
    plt.title("Kümülâtif Deprem Grafiği")
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt.gcf())

    # 6. En Yoğun Gün
    st.subheader("En Yoğun Deprem Günü")
    top_day = data["date_only"].value_counts().idxmax()
    count = data["date_only"].value_counts().max()
    st.metric(label="En Yoğun Gün", value=str(top_day), delta=f"{count} deprem")
