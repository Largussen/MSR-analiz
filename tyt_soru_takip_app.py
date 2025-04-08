import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="TYT Soru Takip ve Analiz Aracı", layout="wide", initial_sidebar_state="expanded")

# Dosya yolu
DATA_FILE = "veriler.csv"
PASSWORD = "1234"

# Veri dosyası yoksa oluştur
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Ders", "Konu", "Soru No", "Doğru", "Süre (dk)", "Açıklama"])
    df.to_csv(DATA_FILE, index=False)

# Veriyi oku
df = pd.read_csv(DATA_FILE)

# Tema renk ayarı (karanlık mod uyumlu)
st.markdown("""
    <style>
        .main { background-color: #111; }
        .css-1aumxhk, .css-1v3fvcr { color: white !important; }
        .stDataFrame, .stTable td { color: white !important; }
        .stRadio > div { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<h1 style='text-align: center; color: white;'>📊 TYT Soru Takip ve Analiz Aracı</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📚 Menü")

page = st.sidebar.radio("Sayfa Seç:", ["Analiz", "Konsol"])

# ---------------------- ANALİZ ---------------------
if page == "Analiz":
    st.subheader("🔍 Soru Analizi")

    dersler = df["Ders"].unique().tolist()
    secilen_ders = st.selectbox("Ders Seç:", dersler)

    if secilen_ders:
        filtreli = df[df["Ders"] == secilen_ders]
        
        konular = filtreli["Konu"].unique().tolist()
        secilen_konu = st.selectbox("Konu Seç:", konular)

        yillik = filtreli[filtreli["Konu"] == secilen_konu] if secilen_konu else filtreli

        st.dataframe(yillik.style.set_properties(**{'color': 'white'}))

        # Doğru-yanlış sayısı
        dogru_sayisi = yillik[yillik["Doğru"] == "Evet"].shape[0]
        yanlis_sayisi = yillik[yillik["Doğru"] == "Hayır"].shape[0]

        st.write(f"✅ Çözülen: {dogru_sayisi}")
        st.write(f"❌ Çözülemeyen: {yanlis_sayisi}")

        # Ortalama süre karşılaştırma
        ort_sure_dogru = yillik[yillik["Doğru"] == "Evet"]["Süre (dk)"].mean()
        ort_sure_yanlis = yillik[yillik["Doğru"] == "Hayır"]["Süre (dk)"].mean()

        fig, ax = plt.subplots()
        ax.bar(["Çözülen", "Çözülemeyen"], [ort_sure_dogru, ort_sure_yanlis], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)")
        ax.set_facecolor("#1e1e1e")
        fig.patch.set_facecolor("#1e1e1e")
        st.pyplot(fig)

# ---------------------- KONSOL ---------------------
elif page == "Konsol":
    st.subheader("🔐 Konsol Girişi")

    sifre = st.text_input("Şifre:", type="password")
    if sifre == PASSWORD:
        st.success("Konsol aktif. Sol menüden işlem seçebilirsin.")
        alt_sayfa = st.sidebar.radio("Konsol Sayfası Seç:", ["Soru Ekle", "Kayıt Sil"])
        
        # ------------- Soru Ekleme -------------
        if alt_sayfa == "Soru Ekle":
            st.subheader("➕ Yeni Soru Ekle")

            ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "Din"])
            konu = st.text_input("Konu")
            soru_no = st.number_input("Soru No", min_value=1, max_value=5000, step=1)
            dogru = st.selectbox("Bu soruyu çözdün mü?", ["Evet", "Hayır"])
            sure = st.number_input("Süre (dk)", min_value=0.1, max_value=100.0, step=0.1)
            aciklama = st.text_area("Açıklama (opsiyonel)", "")

            if st.button("Kaydet"):
                yeni_kayit = pd.DataFrame([[ders, konu, soru_no, dogru, sure, aciklama]],
                                          columns=df.columns)
                df = pd.concat([df, yeni_kayit], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("✅ Soru kaydedildi!")

        # ------------- Kayıt Silme -------------
        elif alt_sayfa == "Kayıt Sil":
            st.subheader("🗑️ Kayıt Sil")

            if df.empty:
                st.warning("Hiç kayıt yok.")
            else:
                index = st.number_input("Silinecek kayıt numarası", min_value=0, max_value=len(df)-1, step=1)
                if st.button("Kaydı Sil"):
                    df = df.drop(index)
                    df.to_csv(DATA_FILE, index=False)
                    st.success(f"{index}. kayıt silindi.")
    else:
        st.warning("Konsol işlemleri için doğru şifreyi giriniz.")
