
import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"
SIFRE = "1234"  # Konsol erişim şifresi

# Sayfa ayarı
st.set_page_config(page_title="TYT Soru Takip", layout="wide")

# Başlık
st.title("📊 TYT Soru Takip ve Analiz Aracı")

# Şifre kontrolü
if "giris" not in st.session_state:
    st.session_state["giris"] = False

st.header("Genel Analiz")
# ANALİZ BLOĞU
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)

    toplam = len(df)
    cozulen = len(df[df["Durum"] == "Çözüldü"])
    cozememe = toplam - cozulen
    ort_sure = df["Süre"].mean().round(2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam", toplam)
    col2.metric("Çözülen", cozulen)
    col3.metric("Ortalama Süre", f"{ort_sure} dk")

    # Grafik
    fig, ax = plt.subplots(facecolor="#0e1117")
    ax.bar(["Çözülen", "Çözemedim"], [df[df["Durum"] == "Çözüldü"]["Süre"].mean(),
                                      df[df["Durum"] == "Çözemedim"]["Süre"].mean()],
           color=["green", "red"])
    ax.set_facecolor("#0e1117")
    ax.set_ylabel("Ortalama Süre (dk)")
    st.pyplot(fig)

else:
    st.info("Henüz veri girilmemiş.")

# 🔐 Konsol Giriş
st.subheader("🔐 Konsol")
if not st.session_state["giris"]:
    sifre = st.text_input("Konsola erişmek için şifre girin", type="password")
    if sifre == SIFRE:
        st.success("Giriş başarılı.")
        st.session_state["giris"] = True
    elif sifre:
        st.error("Şifre yanlış!")

# Konsol Aktifse - Soru Ekle ve Sil
if st.session_state["giris"]:
    secenek = st.radio("İşlem Seç", ["Soru Ekle", "Kayıt Sil"])

    konular_dict = {
        "Matematik": ["Temel Kavramlar", "Rasyonel Sayılar"],
        "Türkçe": ["Paragraf", "Dil Bilgisi"],
    }

    if secenek == "Soru Ekle":
        st.header("➕ Soru Ekle")

        ders = st.selectbox("Ders", list(konular_dict.keys()))
        konu = st.selectbox("Konu", konular_dict[ders])
        yil = st.selectbox("Yıl", ["2024", "2023", "2022"])
        soru_no = st.number_input("Soru No", 1, 50)
        sure = st.number_input("Süre (dk)", 0.0, step=0.1)
        durum = st.radio("Durum", ["Çözüldü", "Çözemedim"])
        aciklama = st.text_area("Açıklama")

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
            st.success("Kayıt eklendi!")

    elif secenek == "Kayıt Sil":
        st.header("🗑️ Kayıt Sil")

        df = pd.read_csv(CSV_FILE)
        df["Görüntü"] = df.apply(lambda row: f"{row['Tarih']} | {row['Ders']} | {row['Konu']} | Soru {int(row['Soru No'])}", axis=1)
        secilen = st.selectbox("Silinecek Kayıt", df["Görüntü"])

        if st.button("Sil"):
            index = df[df["Görüntü"] == secilen].index[0]
            df = df.drop(index)
            df.to_csv(CSV_FILE, index=False)
            st.success("Kayıt silindi.")
