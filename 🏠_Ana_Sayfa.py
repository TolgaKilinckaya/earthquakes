import streamlit as st

st.set_page_config(page_title="Ana Sayfa", page_icon="🏠", layout="wide")

st.title("🏠 Ana Sayfa")

st.write("""
Bu uygulama, deprem verilerini analiz etmek, görselleştirmek ve anlamlı kümeler oluşturmak için tasarlanmıştır. 
Aşağıdaki açıklamalar, her sayfanın ne sunduğunu göstermektedir. 
İlgili sayfaya gitmek için butonlara tıklayın.
""")

st.subheader("📊 Grafikler")
st.write("""
Deprem verilerini yıllık ve 5 yıllık aralıklarla analiz eder, görselleştirir. 
Depremlerin zaman içindeki sıklığını anlamanıza yardımcı olur.
""")
if st.button("Grafikler Sayfasına Git"):
    st.switch_page("pages/1_📊_Grafikler.py")

st.subheader("🌍 Kümeleme ve Harita Görselleştirme")
st.write("""
Depremleri büyüklüğe ve konuma göre kümeler. Harita üzerinde farklı renklerle görselleştirir. 
Ayrıca kümelerin istatistiklerini sunar.
""")
if st.button("Kümeleme ve Harita Görselleştirme Sayfasına Git"):
    st.switch_page("pages/2_🌍_Kümeleme ve Harita Görselleştirme.py")

st.subheader("🔍 En Derin ve Büyük Depremler")
st.write("""
En derin ve en büyük depremleri görselleştirir. Ortak olanları harita üzerinde gösterir ve detaylı tablo sunar.
""")
if st.button("En Derin ve Büyük Depremler Sayfasına Git"):
    st.switch_page("pages/3_🔍_En_Derin_ve_En_Büyük_Depremler.py")
