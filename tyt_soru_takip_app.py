import streamlit as st
import pandas as pd
import datetime
import os
import time

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"

# Koyu tema uyarısı (Streamlit ayarlarında config.toml ile kontrol edilebilir)
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")

# Başlık ve açıklama
st.title("TYT Soru Takip ve Analiz Aracı")
st.markdown("Konu bazlı soru çözüm ilerlemeni takip edebileceğin ve performansını analiz edebileceğin bir uygulama.")

# Sayfa seçimi
secenek = st.sidebar.radio("Sayfa Seç:", ["Soru Girişi", "Analiz"])

# Konular
konular = [
    "Temel Kavramlar", "Sayı Basamakları", "Bölme ve Bölünebilme", "Asal Çarpanlar", "EBOB-EKOK",
    "Rasyonel Sayılar", "Ondalık Sayılar", "Sıralama - İşaret", "Mutlak Değer", "Üslü Sayılar",
    "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Problemler", "Kümeler", "Fonksiyonlar",
    "Polinomlar", "2. Dereceden Denklemler", "Çokgenler", "Çember", "Olasılık"
]

ders = "Matematik"

# Soru Girişi
if secenek == "Soru Girişi":
    st.header("Yeni Soru Kaydı Ekle")

    col1, col2 = st.columns(2)
    with col1:
        yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020", "2019", "2018"])
        soru_no = st.number_input("Soru No", min_value=1, max_value=50, step=1)
    with col2:
        konu = st.selectbox("Konu", konular)
        sure = st.number_input("Süre (dakika)", min_value=0.0, step=0.1, format="%.1f")

    durum = st.radio("Durum", ["Çözüldü", "Çözemedim"])
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
        with st.spinner("Kaydediliyor..."):
            time.sleep(0.5)
        st.success("Kayıt başarıyla eklendi!")

# Analiz
elif secenek == "Analiz":
    st.header("Çözülen Soruların Analizi")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        st.subheader("Filtreleme")
        yillar = ["Tümü"] + sorted(df["Yıl"].unique().tolist())
        secilen_yil = st.selectbox("Yıla göre filtrele", yillar)

        if secilen_yil != "Tümü":
            df = df[df["Yıl"] == secilen_yil]

        st.subheader("Genel Bilgiler")
        toplam_soru = len(df)
        cozulen = len(df[df["Durum"] == "Çözüldü"])
        cozememe = toplam_soru - cozulen
        ort_sure = df["Süre"].mean().round(2)

        # Animasyonlu sayaçlar
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Soru", toplam_soru)
        with col2:
            st.metric("Çözülen", cozulen)
        with col3:
            st.metric("Çözülemeyen", cozememe)
        with col4:
            st.metric("Ortalama Süre", f"{ort_sure} dk")

        st.subheader("Konu Bazlı Performans")
        konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
        konu_grup["Toplam"] = konu_grup.sum(axis=1)
        konu_grup["Başarı %"] = (konu_grup.get("Çözüldü", 0) / konu_grup["Toplam"] * 100).round(1)

        st.dataframe(konu_grup.sort_values("Başarı %", ascending=False))

    else:
        st.warning("Henüz kayıt bulunmuyor. Önce soru girişi yapmalısın.")
