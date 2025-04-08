import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="TYT Soru Takip ve Analiz Aracı", layout="wide")

DATA_PATH = "veriler.csv"
PASSWORD = "1234"

# Özel tema ve animasyonlar
custom_css = """
<style>
/* Genel tema */
body, .stApp {
    background-color: #111111;
    color: #FFFFFF;
}
h1, h2, h3, h4 {
    animation: fadeIn 2s ease-in-out;
}
@keyframes fadeIn {
  0% {opacity: 0;}
  100% {opacity: 1;}
}
div[data-testid="stSidebar"] {
    background-color: #1c1c1c;
    border-right: 1px solid #333;
}
div[data-testid="stSidebar"] h2 {
    color: white;
}
div[data-testid="stMarkdownContainer"] p {
    color: white;
}
div[data-baseweb="tab"] button:hover {
    background-color: #444 !important;
}

/* Hover buton efekti */
button[kind="primary"]:hover {
    transform: scale(1.02);
    transition: 0.3s ease-in-out;
    background-color: #7f5af0 !important;
}

/* Başlık parlaması */
h1 {
    text-shadow: 0 0 20px #7f5af0;
}

/* Yüklenme animasyonu */
.stSpinner {
    animation: fadeIn 1.5s ease-in-out;
}

/* Grafik yumuşak geçiş */
.css-1y4p8pa {
    animation: fadeIn 1.5s ease-in-out;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Veri okuma
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame(columns=["Ders", "Konu", "Soru No", "Doğru", "Süre (dk)", "Açıklama"])

# Sayfa seçimi
st.sidebar.title("🔎 Sayfa Seç:")
page = st.sidebar.radio("Sayfa Seç:", ["Analiz", "Konsol", "Soru Ekle", "Kayıt Sil"])

# Konsol şifre girişi
if page == "Konsol":
    st.sidebar.subheader("🔐 Konsol Girişi")
    password = st.sidebar.text_input("Şifre:", type="password")
    access_granted = password == PASSWORD

    if access_granted:
        st.success("Konsol aktif. Sol menüden işlem seçebilirsin.")
    else:
        st.warning("Konsol devre dışı. Lütfen geçerli şifreyi girin.")

# Analiz Sayfası
if page == "Analiz":
    st.title("📊 TYT Soru Takip ve Analiz Aracı")

    st.subheader("🔎 Filtreleme")
    dersler = df["Ders"].unique()
    secilen_ders = st.selectbox("Ders seç", dersler)
    yillar = df["Konu"].str.extract(r'(\d{4})').dropna()[0].unique()
    secilen_konu = st.selectbox("Konu seç", df[df["Ders"] == secilen_ders]["Konu"].unique())

    filtreli_df = df[(df["Ders"] == secilen_ders) & (df["Konu"] == secilen_konu)]

    st.subheader("📈 Performans Analizi")

    if not filtreli_df.empty:
        dogru_sayisi = filtreli_df["Doğru"].sum()
        toplam_soru = len(filtreli_df)
        basari_yuzdesi = (dogru_sayisi / toplam_soru) * 100

        st.metric("✔️ Başarı Yüzdesi", f"%{basari_yuzdesi:.2f}")

        # Süre analizi
        cozulmus = filtreli_df[filtreli_df["Doğru"] == 1]["Süre (dk)"].mean()
        cozulemeyen = filtreli_df[filtreli_df["Doğru"] == 0]["Süre (dk)"].mean()

        fig, ax = plt.subplots()
        ax.bar(["Çözülen", "Çözülemeyen"], [cozulmus, cozulemeyen], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)")
        ax.set_facecolor('#222')
        fig.patch.set_facecolor('#222')
        ax.tick_params(colors='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        st.pyplot(fig)

        st.subheader("📝 Kayıtlar")
        st.dataframe(filtreli_df.style.set_properties(**{"color": "white"}))

    else:
        st.info("Seçilen filtrelere göre kayıt bulunamadı.")

# Soru Ekleme
if page == "Soru Ekle":
    if not st.session_state.get("password_ok") and not st.sidebar.text_input("Şifre:", type="password") == PASSWORD:
        st.warning("Ekleme sayfasına erişim için şifre gerekli.")
    else:
        st.title("➕ Yeni Soru Ekle")

        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Fizik", "Kimya", "Biyoloji", "Coğrafya", "Tarih", "Felsefe"])
        konu = st.text_input("Konu")
        soru_no = st.number_input("Soru No", min_value=1, max_value=9999)
        dogru = st.selectbox("Soru Durumu", ["Çözüldü", "Çözülemedi"])
        sure = st.number_input("Çözüm Süresi (dk)", min_value=0.0, format="%.2f")
        aciklama = st.text_area("Açıklama (zorunlu değil)", max_chars=500)

        if st.button("Kaydet"):
            yeni_kayit = {
                "Ders": ders,
                "Konu": konu,
                "Soru No": soru_no,
                "Doğru": 1 if dogru == "Çözüldü" else 0,
                "Süre (dk)": sure,
                "Açıklama": aciklama
            }
            df = pd.concat([df, pd.DataFrame([yeni_kayit])], ignore_index=True)
            df.to_csv(DATA_PATH, index=False)
            st.success("Soru başarıyla eklendi.")

# Kayıt Silme
if page == "Kayıt Sil":
    if not st.session_state.get("password_ok") and not st.sidebar.text_input("Şifre:", type="password") == PASSWORD:
        st.warning("Silme işlemi için şifre gerekli.")
    else:
        st.title("🗑️ Kayıt Sil")

        if len(df) == 0:
            st.info("Silinecek kayıt bulunamadı.")
        else:
            secilecek = st.selectbox("Silinecek kaydı seç", df.index)
            st.write(df.loc[secilecek])
            if st.button("Sil"):
                df = df.drop(secilecek)
                df.to_csv(DATA_PATH, index=False)
                st.success("Kayıt silindi.")
