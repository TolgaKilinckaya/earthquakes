import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from obspy import read

st.set_page_config(page_title="Tremor Kümeleme", page_icon="🤖", layout="wide")
st.title("Tremor Benzeri Sinyallerin Kümeleme Analizi 🤖")

st.markdown("""
Bu sayfa, önceki sayfada çekilen sismik sinyal verisini kullanarak
**spektrogram çıkartır**, ardından **K-Means kümeleme** uygular.
""")

# ⛔ Kontrol: Session'da waveform var mı?
if "waveform_file" not in st.session_state:
    st.warning("Lütfen önce 'Dalga Formu' sayfasından bir sinyal verisi çekin.")
    st.stop()

# ✅ Veriyi oku (MSEED formatı)
try:
    stream = read(st.session_state["waveform_file"])
    trace = stream[0]
    data = trace.data.astype(np.float32)
    sr = int(trace.stats.sampling_rate)
    st.success(f"{trace.id} istasyonundan {len(data)} örnek yüklendi ({sr} Hz)")
except Exception as e:
    st.error(f"Veri okunamadı: {e}")
    st.stop()

# 🎼 Spektrogram (STFT)
S = np.abs(librosa.stft(data, n_fft=1024, hop_length=512))
S_dB = librosa.amplitude_to_db(S, ref=np.max)

st.subheader("Log-Frekans Spektrogram")
fig, ax = plt.subplots(figsize=(10, 4))
img = librosa.display.specshow(S_dB, sr=sr, hop_length=512, x_axis='time', y_axis='log', ax=ax)
fig.colorbar(img, ax=ax, format="%+2.0f dB")
plt.title("Spektrogram (log-frekans)")
st.pyplot(fig)

# 🔍 Özellik çıkarımı
spec_features = np.vstack([S.mean(axis=1), S.std(axis=1)]).T
scaler = StandardScaler()
X_scaled = scaler.fit_transform(spec_features)

# 🎯 PCA ile 2D'ye indir
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# 🧠 K-Means
k = st.slider("Küme Sayısı (k)", 2, 10, 3)
kmeans = KMeans(n_clusters=k, random_state=0, n_init='auto').fit(X_pca)

# 📊 Görselleştirme
st.subheader("K-Means Kümeleme Sonucu (PCA alanında)")
fig2, ax2 = plt.subplots()
for label in np.unique(kmeans.labels_):
    ax2.scatter(X_pca[kmeans.labels_ == label, 0], X_pca[kmeans.labels_ == label, 1], label=f"Küme {label}")
ax2.set_xlabel("PCA 1")
ax2.set_ylabel("PCA 2")
ax2.set_title("Küme Dağılımı")
ax2.legend()
st.pyplot(fig2)

# ✅ Senkronizasyon
st.session_state["last_clusters"] = kmeans.labels_.tolist()
st.session_state["last_k"] = k
