import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# ⛳️ Ayarlar
CSV_FILE = "soru_kayitlari.csv"
KONSOL_SIFRE = "1234"

# 🎨 Sayfa ayarları ve tema
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: white;
    }
    .stDataFrame tbody td {
        color: white !important;
    }
    .stDataFrame thead th {
        color: white !important;
    }
    div[data-testid="stMetricValue"] {
        color: white;
    }
    button:hover {
        transform: scale(1.03);
    }
    @media only screen and (max-width: 600px) {
        .stColumn {
            display: block !important;
            width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("")

konular_dict = {
    "Matematik": ["Temel Kavramlar", "Sayılar", "Bölme-Bölünebilme", "OBEB-OKEK", "Rasyonel Sayılar", "Ondalık Sayılar",
                  "Basamak Kavramı", "Faktöriyel", "Asal Çarpan", "Modüler Aritmetik", "EBOB-EKOK", "Çarpanlara Ayırma",
                  "Denklem Çözme", "Problemler", "Kümeler", "Fonksiyonlar", "Polinomlar", "Logaritma"],
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları", "Noktalama", "Dil Bilgisi"],
    "Fizik": ["Kuvvet", "Hareket", "Isı", "Optik", "Elektrik", "Manyetizma"],
    "Kimya": ["Atom", "Periyodik Sistem", "Bileşikler", "Kimyasal Tepkimeler", "Mol Hesapları", "Çözeltiler"],
    "Biyoloji": ["Hücre", "Canlıların Sınıflandırılması", "Solunum", "Üreme", "Genetik", "Ekoloji"],
    "Tarih": ["İlk Çağ", "Orta Çağ", "Osmanlı", "Kurtuluş Savaşı", "Cumhuriyet Dönemi"],
    "Coğrafya": ["İklim", "Harita Bilgisi", "Türkiye’nin Yer Şekilleri", "Nüfus", "Ekonomi"],
    "Felsefe": ["Felsefenin Alanı", "Bilgi Felsefesi", "Ahlak Felsefesi", "Sanat", "Din Felsefesi"],
    "Din Kültürü": ["İslamiyet", "İnanç", "İbadet", "Ahlak", "Din ve Hayat"]
}

menu = ["Analiz", "Konsol"]
secenek = st.sidebar.radio("Menü:", menu)

# 🔐 Konsol Şifre Kontrolü
sifre_dogru = False
if secenek == "Konsol":
    girilen = st.text_input("Konsol Girişi - Şifre:", type="password")
    if girilen == KONSOL_SIFRE:
        sifre_dogru = True
    else:
        st.warning("Konsola erişmek için doğru şifreyi girin.")

# 📊 ANALİZ SAYFASI
if secenek == "Analiz":
from PIL import Image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(Image.open("kemal.png"), width=140)

    st.header("")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        if not df.empty:
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

            st.subheader("Konu Bazlı Başarı")
            konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
            konu_grup["Toplam"] = konu_grup.sum(axis=1)
            konu_grup["Başarı %"] = (konu_grup.get("Çözüldü", 0) / konu_grup["Toplam"] * 100).round(1)
            st.dataframe(konu_grup.sort_values("Başarı %", ascending=False))

            st.subheader("Süre Analizi")
            sure_c = df[df["Durum"] == "Çözüldü"]["Süre"].mean()
            sure_y = df[df["Durum"] == "Çözülemeyen"]["Süre"].mean()
            st.write(f"✅ Çözülen Ortalama Süre: **{sure_c:.2f} dk**")
            st.write(f"❌ Çözülemeyen Ortalama Süre: **{sure_y:.2f} dk**")

            fig, ax = plt.subplots(facecolor="#121212")
            ax.bar(["Çözülen", "Çözülemeyen"], [sure_c, sure_y], color=["green", "red"])

            ax.set_ylabel("Ortalama Süre (dk)", color="white")
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')

            for spine in ax.spines.values():
                spine.set_color("white")

            ax.set_facecolor("#1E1E1E")
            fig.patch.set_facecolor("#121212")
            st.pyplot(fig)

            st.subheader("Soru Notları")
            df["Açıklama"] = df["Açıklama"].astype(str)
            aciklamalar = df[(df["Durum"] == "Çözülemeyen") & (df["Açıklama"].str.strip() != "")]
            if not aciklamalar.empty:
                for _, row in aciklamalar.iterrows():
                    st.markdown(f" **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
            else:
                st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
        else:
            st.info("Henüz kayıt yok.")
    else:
        st.warning("Veri dosyası bulunamadı.")

# 🛠 Konsol Sayfası
if secenek == "Konsol" and sifre_dogru:
    secim = st.radio("İşlem Seç:", ["Yeni Soru Ekle", "Kayıt Sil"])

    if secim == "Yeni Soru Ekle":
        st.header("➕ Yeni Soru Kaydı Ekle")
        ders = st.selectbox("Ders", list(konular_dict.keys()))
        konu = st.selectbox("Konu", konular_dict[ders])

        col1, col2 = st.columns(2)
        with col1:
            yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020", "2019", "2018"])
            soru_no = st.number_input("Soru No", min_value=1, max_value=1000, step=1)
        with col2:
            dak = st.number_input("Süre (Dakika)", min_value=0, step=1)
            sn = st.number_input("Süre (Saniye)", min_value=0, max_value=59, step=1)
            sure = round(dak + sn / 60, 2)

        durum = st.radio("Durum", ["Çözüldü", "Çözülemeyen"])
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
            st.success("Kayıt başarıyla eklendi!")

    elif secim == "Kayıt Sil":
        st.header("🗑️ Kayıt Silme")
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if df.empty:
                st.info("Hiç kayıt yok.")
            else:
                df["Görüntü"] = df.apply(lambda row: f"{row['Tarih']} | {row['Ders']} | {row['Konu']} | Soru {int(row['Soru No'])}", axis=1)
                secilen_kayit = st.selectbox("Silmek istediğin kayıt:", df["Görüntü"])
                secilen_index = df[df["Görüntü"] == secilen_kayit].index[0]

                if st.button("Sil"):
                    df = df.drop(secilen_index)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Kayıt silindi!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.warning("CSV dosyası bulunamadı.")
