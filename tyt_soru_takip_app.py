import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# CSV dosya yolu
CSV_FILE = "data.csv"

# Sayfa başlığı ve tema ayarı
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")

# Özel stil
st.markdown(
    """
    <style>
        body {
            color: #ffffff;
            background-color: #0e1117;
        }
        .stDataFrame div {
            color: white !important;
        }
        table {
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sayfa seçimi
secenek = st.sidebar.selectbox("Sayfa Seç", ["Analiz", "Konsol"])

# Konsol şifre kontrolü
if secenek == "Konsol":
    sifre = st.text_input("Şifre", type="password")
    if sifre == "1234":
        alt_sec = st.radio("İşlem Seç", ["Soru Girişi", "Kayıt Sil"])
        if alt_sec == "Soru Girişi":
            st.header("Soru Girişi")

            tarih = st.date_input("Tarih", value=datetime.today())
            ders = st.selectbox("Ders", ["Türkçe", "Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya", "Felsefe", "Din Kültürü"])
            konu = st.text_input("Konu")
            dogru = st.number_input("Doğru Sayısı", min_value=0, step=1)
            yanlis = st.number_input("Yanlış Sayısı", min_value=0, step=1)
            cozulmeyen = st.number_input("Çözülemeyen Sayısı", min_value=0, step=1)
            sure_dk = st.number_input("Süre (dk)", min_value=0, step=1)
            sure_sn = st.number_input("Süre (sn)", min_value=0, max_value=59, step=1)
            aciklama = st.text_area("Açıklama")

            if st.button("Kaydet"):
                yeni_kayit = {
                    "Tarih": tarih.strftime("%Y-%m-%d"),
                    "Ders": ders,
                    "Konu": konu,
                    "Doğru": dogru,
                    "Yanlış": yanlis,
                    "Çözülemeyen": cozulmeyen,
                    "Süre (dk)": sure_dk + sure_sn / 60,
                    "Açıklama": aciklama
                }

                if os.path.exists(CSV_FILE):
                    df = pd.read_csv(CSV_FILE)
                    df = df.append(yeni_kayit, ignore_index=True)
                else:
                    df = pd.DataFrame([yeni_kayit])

                df.to_csv(CSV_FILE, index=False)
                st.success("Kayıt başarıyla eklendi!")

        elif alt_sec == "Kayıt Sil":
            st.header("Kayıt Sil")

            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
                st.dataframe(df)

                secilecek_index = st.number_input("Silinecek Satır Index", min_value=0, max_value=len(df)-1, step=1)

                if st.button("Sil"):
                    df = df.drop(index=secilecek_index).reset_index(drop=True)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Kayıt silindi.")
            else:
                st.warning("Kayıt bulunamadı.")

# Analiz sayfası
elif secenek == "Analiz":
    st.header("")

    # Görsel ve başlık
    st.markdown("""
        <div style="text-align:center;">
            <img src="https://raw.githubusercontent.com/username/repo/main/kemal.png" width="150" style="border-radius: 50%;">
            <p style="color: #ccc; font-size: 18px; font-weight: bold;">TYT Soru Takip & Analiz Ekranı</p>
        </div>
    """, unsafe_allow_html=True)

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        st.subheader("Kayıtlar")
        st.dataframe(df.style.set_properties(**{'color': 'white'}))

        st.subheader("İstatistikler")
        ders_filtre = st.selectbox("Ders Seç", ["Tümü"] + sorted(df["Ders"].unique().tolist()))
        if ders_filtre != "Tümü":
            df = df[df["Ders"] == ders_filtre]

        # Başarı yüzdesi
        df["Toplam"] = df["Doğru"] + df["Yanlış"] + df["Çözülemeyen"]
        df["Başarı (%)"] = (df["Doğru"] / df["Toplam"] * 100).round(2)

        konu_grup = df.groupby("Konu").agg({
            "Doğru": "sum",
            "Yanlış": "sum",
            "Çözülemeyen": "sum",
            "Süre (dk)": "mean",
            "Başarı (%)": "mean"
        }).reset_index()

        st.dataframe(konu_grup.style.set_properties(**{'color': 'white'}))

        # Görsel grafik
        fig = px.bar(konu_grup, x="Konu", y="Süre (dk)", color_discrete_sequence=["#00cc96"])
        fig.update_layout(plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white")
        fig.update_xaxes(title="Konu")
        fig.update_yaxes(title="Ortalama Süre (dk)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Henüz veri bulunmuyor.")
