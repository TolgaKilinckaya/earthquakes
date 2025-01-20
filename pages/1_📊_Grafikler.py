import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Grafikler", page_icon="📊", layout="wide")

st.title("Zaman Serisi Analizi")
uploaded_file = "filtered.csv"

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.subheader("Yıllara Göre")
    if "Timestamp" in data.columns and "Magnitude" in data.columns:
        data["datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
        data["year"] = data["datetime"].dt.year

        plt.figure(figsize=(12, 6))
        data.groupby('year').size().plot(kind='bar', color='coral')

        # Customize the plot for better aesthetics
        plt.title('Yıllık Deprem Sıklığı', fontsize=16)
        plt.xlabel('Yıl', fontsize=12)
        plt.ylabel('Deprem Sayısı', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
            
        st.pyplot(plt.gcf())
    else:
        st.error("Bu analiz için 'Time' ve 'Magnitude' sütunları gereklidir.")
                
    st.subheader("5 Yıllığa Göre")
    if "Timestamp" in data.columns:
        data["datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
        data["year"] = data["datetime"].dt.year

        # 5 yıllık aralıkları oluştur
        bins = range(data["year"].min(), data["year"].max() + 5, 5)
        data["5_year_bin"] = pd.cut(data["year"], bins=bins, right=False)

        # Görselleştirme
        plt.figure(figsize=(12, 6))
        data.groupby("5_year_bin").size().plot(kind="bar", color="lightseagreen")

        plt.title("5 Yıllık Aralıklara Göre Deprem Sıklığı", fontsize=16)
        plt.xlabel("5-Yıllık Küme", fontsize=12)
        plt.ylabel("Deprem Sayısı", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()

        st.pyplot(plt.gcf())
    else:
        st.error("Bu analiz için 'Timestamp' sütunu gereklidir.")