import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"

# Sayfa ayarı
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")

# Başlık
st.title("TYT Soru Takip ve Analiz Aracı")

# Tüm TYT dersleri ve konuları
konular_dict = {
    "Matematik": [...],  # Listeyi uzatmamak için kısaltıldı
    "Türkçe": [...],
    "Fizik": [...],
    "Kimya": [...],
    "Biyoloji": [...],
    "Tarih": [...],
    "Coğrafya": [...],
    "Felsefe": [...],
    "Din Kültürü": [...]
}

# Sayfa seçimi
secenek = st.sidebar.radio("Sayfa Seç:", ["Soru Girişi", "Analiz", "Kayıt Sil"])

# ➕ Soru Girişi Sayfası
if secenek == "Soru Girişi":
    st.header("Yeni Soru Kaydı Ekle")

    ders = st.selectbox("Ders", list(konular_dict.keys()))

    if ders in konular_dict:
        konu = st.selectbox("Konu", konular_dict[ders])
    else:
        konu = st.selectbox("Konu", ["Önce ders seçiniz."])

    col1, col2 = st.columns(2)
    with col1:
        yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020", "2019", "2018"])
        soru_no = st.number_input("Soru No", min_value=1, max_value=50, step=1)
    with col2:
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

# 📊 Analiz Sayfası
elif secenek == "Analiz":
    st.header("Çözülen Soruların Analizi")

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
        cozulen = len(df[df["Durum"] == "Çözüldü"])
        cozememe = toplam_soru - cozulen
        ort_sure = df["Süre"].mean().round(2)

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

        st.subheader("Süre Analizi")
        sure_c = df[df["Durum"] == "Çözüldü"]["Süre"].mean()
        sure_y = df[df["Durum"] == "Çözemedim"]["Süre"].mean()
        st.write(f"✅ Çözülen Soruların Ortalama Süresi: **{sure_c:.2f} dk**")
        st.write(f"❌ Çözülemeyen Soruların Ortalama Süresi: **{sure_y:.2f} dk**")

        st.subheader("Grafik: Süre Karşılaştırması")
        fig, ax = plt.subplots()
        ax.bar(["Çözülen", "Çözemedim"], [sure_c, sure_y], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)")
        st.pyplot(fig)

        st.subheader("Çözülmeyen Sorulardan Notlar")
        if "Açıklama" in df.columns:
            df["Açıklama"] = df["Açıklama"].astype(str)  # HATA BURADAN KAYNAKLIYDI
            aciklamalar = df[(df["Durum"] == "Çözemedim") & (df["Açıklama"].str.strip() != "")]
            if not aciklamalar.empty:
                for i, row in aciklamalar.iterrows():
                    st.markdown(f"📌 **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
            else:
                st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
    else:
        st.warning("Henüz kayıt bulunmuyor.")

# 🗑️ Kayıt Sil Sayfası
elif secenek == "Kayıt Sil":
    st.header("Kayıt Silme Paneli")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        if df.empty:
            st.info("Kayıt dosyası boş.")
        else:
            df["Görüntü"] = df.apply(lambda row: f"{row['Tarih']} | {row['Ders']} | {row['Konu']} | Soru {int(row['Soru No'])}", axis=1)

            secilen_kayit = st.selectbox("Silmek istediğin kaydı seç:", df["Görüntü"])
            secilen_index = df[df["Görüntü"] == secilen_kayit].index[0]

            if st.button("Kaydı Sil"):
                df = df.drop(secilen_index)
                df.to_csv(CSV_FILE, index=False)
                st.success("Kayıt silindi! Sayfa yenileniyor...")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("Kayıt dosyası bulunamadı.")
