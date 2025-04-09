import streamlit as st
import pandas as pd
import datetime
import os
import time
from PIL import Image

CSV_FILE = "soru_kayitlari.csv"
KONSOL_SIFRE = "1234"

st.set_page_config(page_title="TYT Soru Takip", layout="wide")

st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    .stDataFrame tbody td, .stDataFrame thead th, div[data-testid="stMetricValue"] {
        color: white !important;
    }
    button:hover { transform: scale(1.03); }
    </style>
""", unsafe_allow_html=True)

menu = ["Analiz", "Soru Notları", "İşaretli Sorular", "Konsol"]
secenek = st.sidebar.radio("Menü:", menu)

sifre_dogru = False
if secenek == "Konsol":
    girilen = st.text_input("Konsol Girişi - Şifre:", type="password")
    if girilen == KONSOL_SIFRE:
        sifre_dogru = True
    else:
        st.warning("Konsola erişmek için doğru şifreyi girin.")

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

# -------------------------- KONSOL --------------------------
if secenek == "Konsol" and sifre_dogru:
    secim = st.radio("İşlem Seç:", ["Yeni Soru Ekle", "Kayıt Sil"])

    if secim == "Yeni Soru Ekle":
        st.header("➕ Yeni Soru Kaydı")
        ders = st.selectbox("Ders", list(konular_dict.keys()))
        konu = st.selectbox("Konu", konular_dict[ders])

        col1, col2 = st.columns(2)
        with col1:
            yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020"])
            soru_no = st.number_input("Soru No", min_value=1, step=1)
        with col2:
            dak = st.number_input("Süre (Dakika)", min_value=0, step=1)
            sn = st.number_input("Süre (Saniye)", min_value=0, max_value=59, step=1)
            sure = round(dak + sn / 60, 2)

        durum = st.radio("Durum", ["Çözüldü", "Çözülemeyen"])
        zorluk = st.slider("Zorluk Seviyesi", 0, 4, 2)
        isaretli = st.checkbox("Soruyu işaretle")
        dahil_mi = st.checkbox("Süreyi ortalamaya dahil et", value=True)
        aciklama = st.text_area("Açıklama (İsteğe Bağlı)")

        # Görsel yükleme
        uploaded_file = st.file_uploader("Görsel Yükle (İsteğe Bağlı)", type=["png", "jpg", "jpeg"])

        if st.button("Kaydet"):
            # Görseli kaydetme işlemi
            if uploaded_file is not None:
                image_path = f"images/soru_{yil}_{soru_no}.png"
                with open(image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            # Yeni kayıt oluşturma
            yeni_kayit = pd.DataFrame({
                "Tarih": [datetime.date.today()],
                "Yıl": [yil],
                "Soru No": [soru_no],
                "Ders": [ders],
                "Konu": [konu],
                "Süre": [sure],
                "Durum": [durum],
                "Zorluk": [zorluk],
                "Yıldızlı": [isaretli],
                "OrtalamayaDahil": [dahil_mi],
                "Açıklama": [aciklama],
                "Görsel": [image_path if uploaded_file is not None else ""]
            })

            if os.path.exists(CSV_FILE):
                mevcut = pd.read_csv(CSV_FILE)
                df = pd.concat([mevcut, yeni_kayit], ignore_index=True)
            else:
                df = yeni_kayit

            df.to_csv(CSV_FILE, index=False)
            st.success("Kayıt başarıyla eklendi!")

    elif secim == "Kayıt Sil":
        st.header("🗑️ Kayıt Sil")
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if df.empty:
                st.info("Hiç kayıt yok.")
            else:
                df["Görüntü"] = df.apply(lambda row: f"{row['Tarih']} | {row['Ders']} | {row['Konu']} | Soru {int(row['Soru No'])}", axis=1)
                secili_kayit = st.selectbox("Silmek istediğiniz kaydı seçin", df["Görüntü"])

                if secili_kayit:
                    sil_kayit = df[df["Görüntü"] == secili_kayit].index[0]
                    df.drop(sil_kayit, axis=0, inplace=True)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Kayıt başarıyla silindi!")
        else:
            st.warning("Kayıt dosyası bulunamadı.")

# ------------------------ İŞARETLİ SORULAR ------------------------
if secenek == "İşaretli Sorular":
    st.header("İşaretli Sorular")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if "Yıldızlı" in df.columns and True in df["Yıldızlı"].unique():
            for ders in df["Ders"].unique():
                alt_df = df[(df["Ders"] == ders) & (df["Yıldızlı"] == True)]
                if not alt_df.empty:
                    st.subheader(ders)
                    for _, row in alt_df.iterrows():
                        soru_numarasi = row["Soru No"]
                        aciklama = row["Açıklama"]
                        img_path = f"images/soru_{row['Yıl']}_{soru_numarasi}.png"  # Görselin yolu

                        # Görseli yükleme
                        if os.path.exists(img_path):
                            img = Image.open(img_path)
                            st.image(img, caption=f"Soru {soru_numarasi}", use_column_width=True)
                        else:
                            st.warning(f"Soru {soru_numarasi} için görsel bulunamadı.")

                        st.markdown(f"**Soru {soru_numarasi}:** {aciklama}")
        else:
            st.info("İşaretli soru yok.")
    else:
        st.warning("Kayıt dosyası bulunamadı.")
