import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")

# 💡 Özelleştirilmiş stil
st.markdown("""
    <style>
    .stDataFrame thead tr th, .stDataFrame tbody tr td {
        color: white !important;
        font-weight: 500;
    }
    .stSelectbox > div > div {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

CSV_FILE = "soru_kayitlari.csv"
st.title("📊 TYT Soru Takip ve Analiz Aracı")

# Konular
konular_dict = {
    "Matematik": ["Temel Kavramlar", "Rasyonel Sayılar", "Problemler", "Permütasyon", "Kombinasyon", "Olasılık"],
    "Türkçe": ["Paragraf", "Dil Bilgisi", "Yazım Kuralları", "Noktalama"],
    "Fizik": ["Hareket", "Kuvvet", "Enerji", "Isı ve Sıcaklık"],
    "Kimya": ["Maddenin Halleri", "Asit-Baz", "Kimyasal Tepkimeler"],
    "Biyoloji": ["Hücre", "Kalıtım", "Canlıların Sınıflandırılması"],
    "Tarih": ["İlk Çağ Uygarlıkları", "Osmanlı Devleti", "Kurtuluş Savaşı"],
    "Coğrafya": ["Türkiye'nin Yer Şekilleri", "İklim", "Nüfus ve Yerleşme"],
    "Felsefe": ["Bilgi Felsefesi", "Ahlak Felsefesi", "Sanat Felsefesi"],
    "Din Kültürü": ["İslam ve İbadet", "Kur’an", "Peygamberler"]
}

# 🔐 Şifre kontrolü
st.sidebar.markdown("## 🔒 Konsol Girişi")
password = st.sidebar.text_input("Şifre:", type="password")
authorized = password == "1234"  # şifre burada belirleniyor

# Sayfa seçimi
sayfalar = ["Analiz", "Konsol"]
if authorized:
    sayfalar += ["Soru Ekle", "Kayıt Sil"]
secenek = st.sidebar.radio("Sayfa Seç:", sayfalar)

# 📊 ANALİZ SAYFASI
if secenek == "Analiz":
    st.header("📈 Çözülen Soruların Analizi")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        st.subheader("Filtreleme")
        dersler = ["Tümü"] + sorted(df["Ders"].unique())
        secilen_ders = st.selectbox("Derse göre filtrele", dersler)

        if secilen_ders != "Tümü":
            df = df[df["Ders"] == secilen_ders]

        yillar = ["Tümü"] + sorted(df["Yıl"].unique())
        secilen_yil = st.selectbox("Yıla göre filtrele", yillar)

        if secilen_yil != "Tümü":
            df = df[df["Yıl"] == secilen_yil]

        st.subheader("Genel Bilgiler")
        toplam_soru = len(df)
        cozulen = len(df[df["Durum"] == "Çözülen"])
        cozulmeyen = toplam_soru - cozulen
        ort_sure = df["Süre"].mean().round(2)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Soru", toplam_soru)
        col2.metric("Çözülen", cozulen)
        col3.metric("Çözülemeyen", cozulmeyen)
        col4.metric("Ortalama Süre", f"{ort_sure} dk")

        st.subheader("Konu Bazlı Başarı")
        konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
        konu_grup["Toplam"] = konu_grup.sum(axis=1)
        konu_grup["Başarı %"] = (konu_grup.get("Çözülen", 0) / konu_grup["Toplam"] * 100).round(1)
        st.dataframe(konu_grup.sort_values("Başarı %", ascending=False), use_container_width=True)

        st.subheader("Süre Analizi")
        sure_c = df[df["Durum"] == "Çözülen"]["Süre"].mean()
        sure_y = df[df["Durum"] == "Çözülemeyen"]["Süre"].mean()
        st.write(f"✅ Çözülen Soruların Ortalama Süresi: **{sure_c:.2f} dk**")
        st.write(f"❌ Çözülemeyen Soruların Ortalama Süresi: **{sure_y:.2f} dk**")

        st.subheader("Grafik: Süre Karşılaştırması")
        fig, ax = plt.subplots(facecolor="#0E1117")  # koyu arkaplan
        ax.set_facecolor("#0E1117")
        ax.bar(["Çözülen", "Çözülemeyen"], [sure_c, sure_y], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)", color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_edgecolor("white")
        st.pyplot(fig)

        st.subheader("Çözülemeyen Sorulardan Notlar")
        df["Açıklama"] = df["Açıklama"].astype(str)
        notlar = df[(df["Durum"] == "Çözülemeyen") & (df["Açıklama"].str.strip() != "")]
        if not notlar.empty:
            for _, row in notlar.iterrows():
                st.markdown(f"📌 **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
        else:
            st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
    else:
        st.warning("Henüz kayıt bulunmuyor.")

# 🛠️ KONSOL SAYFASI
elif secenek == "Konsol":
    if authorized:
        st.success("Konsol aktif. Sol menüden işlem seçebilirsin.")
    else:
        st.warning("Lütfen geçerli bir şifre girin.")

# ➕ SORU EKLE
elif secenek == "Soru Ekle" and authorized:
    st.header("📝 Yeni Soru Kaydı Ekle")

    ders = st.selectbox("Ders", list(konular_dict.keys()))
    konu = st.selectbox("Konu", konular_dict[ders])
    col1, col2 = st.columns(2)
    yil = col1.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020"])
    soru_no = col1.number_input("Soru No", min_value=1, max_value=50, step=1)
    sure = col2.number_input("Süre (dakika)", min_value=0.0, step=0.1, format="%.1f")
    durum = col2.radio("Durum", ["Çözülen", "Çözülemeyen"])
    aciklama = st.text_area("Açıklama (isteğe bağlı)")

    if st.button("Kaydet"):
        yeni_kayit = pd.DataFrame({
            "Tarih": [datetime.date.today()],
            "Yıl": [yil],
            "Soru No": [soru_no],
            "Ders": [ders],
            "Konu": [konu],
            "Süre": [sure],
            "Durum": [durum],
            "Açıklama": [aciklama]
        })

        if os.path.exists(CSV_FILE):
            mevcut = pd.read_csv(CSV_FILE)
            df = pd.concat([mevcut, yeni_kayit], ignore_index=True)
        else:
            df = yeni_kayit

        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Kayıt başarıyla eklendi!")

# ❌ KAYIT SİL
elif secenek == "Kayıt Sil" and authorized:
    st.header("🗑️ Kayıt Silme Paneli")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if df.empty:
            st.info("Kayıt bulunmuyor.")
        else:
            df["Görüntü"] = df.apply(lambda row: f"{row['Tarih']} | {row['Ders']} | {row['Konu']} | Soru {int(row['Soru No'])}", axis=1)
            secilen_kayit = st.selectbox("Silinecek kayıt:", df["Görüntü"])
            index = df[df["Görüntü"] == secilen_kayit].index[0]
            if st.button("Kaydı Sil"):
                df.drop(index, inplace=True)
                df.to_csv(CSV_FILE, index=False)
                st.success("Kayıt silindi.")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("Kayıt dosyası bulunamadı.")
