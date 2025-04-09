import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt
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

# -------------------------- ANALİZ SAYFASI --------------------------
if secenek == "Analiz":
    st.image(Image.open("kemal.png"), width=200)
    st.header("")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        # Veri tipi düzeltmeleri
        df["Süre"] = pd.to_numeric(df["Süre"], errors="coerce")
        if "OrtalamayaDahil" in df.columns:
            df["OrtalamayaDahil"] = df["OrtalamayaDahil"].astype(bool)
            df_ort = df[df["OrtalamayaDahil"] == True]
        else:
            df["OrtalamayaDahil"] = True
            df_ort = df

        if not df.empty:
            st.subheader("Filtreleme")
            dersler = ["Tümü"] + sorted(df["Ders"].unique())
            secilen_ders = st.selectbox("Derse göre filtrele", dersler)

            if secilen_ders != "Tümü":
                df = df[df["Ders"] == secilen_ders]
                df_ort = df_ort[df_ort["Ders"] == secilen_ders]

            zorluklar = ["Tümü"] + sorted(df["Zorluk"].dropna().unique())
            secilen_zorluk = st.selectbox("Zorluk seviyesine göre filtrele", zorluklar)

            if secilen_zorluk != "Tümü":
                df = df[df["Zorluk"] == int(secilen_zorluk)]
                df_ort = df_ort[df_ort["Zorluk"] == int(secilen_zorluk)]

            st.subheader("Genel Bilgiler")
            toplam_soru = len(df)
            cozulen = len(df[df["Durum"] == "Çözüldü"])
            cozememe = toplam_soru - cozulen
            ort_sure = round(df_ort["Süre"].mean(), 2)

            ort_zorluk = round(df["Zorluk"].mean(), 2)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Toplam Soru", toplam_soru)
            col2.metric("Çözülen", cozulen)
            col3.metric("Çözülemeyen", cozememe)
            col4.metric("Ortalama Süre", f"{ort_sure} dk")
            col5.metric("Ortalama Zorluk", ort_zorluk)

            st.subheader("Konu Bazlı Başarı")
            konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
            konu_grup["Toplam"] = konu_grup.sum(axis=1)
            konu_grup["Başarı %"] = (konu_grup.get("Çözüldü", 0) / konu_grup["Toplam"] * 100).round(1)
            st.dataframe(konu_grup.sort_values("Başarı %", ascending=False))

            st.subheader("Süre Analizi")
            sure_c = df_ort[df_ort["Durum"] == "Çözüldü"]["Süre"].mean()
            sure_y = df_ort[df_ort["Durum"] == "Çözülemeyen"]["Süre"].mean()
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

# ------------------------ SORU NOTLARI ------------------------
if secenek == "Soru Notları":
    st.header("📝 Soru Notları")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df["Açıklama"] = df["Açıklama"].astype(str)
        notlu = df[df["Açıklama"].str.strip() != ""]
        if not notlu.empty:
            dersler = ["Tümü"] + sorted(notlu["Ders"].unique())
            sec_ders = st.selectbox("Ders Seç", dersler)
            if sec_ders != "Tümü":
                notlu = notlu[notlu["Ders"] == sec_ders]

            konular = ["Tümü"] + sorted(notlu["Konu"].unique())
            sec_konu = st.selectbox("Konu Seç", konular)
            if sec_konu != "Tümü":
                notlu = notlu[notlu["Konu"] == sec_konu]

            for _, row in notlu.iterrows():
                st.markdown(f"**{row['Ders']} - {row['Konu']} | Soru {int(row['Soru No'])}** → {row['Açıklama']}")
        else:
            st.info("Henüz not girilmiş soru bulunmuyor.")

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
                            st.image(img, caption=f"Soru {soru_numarasi}", use_container_width=True)
                        else:
                            st.warning(f"Soru {soru_numarasi} için görsel bulunamadı.")

                        st.markdown(f"**Soru {soru_numarasi}:** {aciklama}")
        else:
            st.info("İşaretli soru yok.")
    else:
        st.warning("Kayıt dosyası bulunamadı.")

# ------------------------ KONSOL ------------------------
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
        
        # Görsel eklemek için
        img_file = st.file_uploader("Görsel yükle", type=["png", "jpg", "jpeg"])
        
        if st.button("Kaydet"):
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
                "Açıklama": [aciklama]
            })

            if os.path.exists(CSV_FILE):
                mevcut = pd.read_csv(CSV_FILE)
                df = pd.concat([mevcut, yeni_kayit], ignore_index=True)
            else:
                df = yeni_kayit

            df.to_csv(CSV_FILE, index=False)

            # Görseli kaydetme işlemi
            if img_file:
                img_path = f"images/soru_{yil}_{soru_no}.png"
                if not os.path.exists("images"):
                    os.makedirs("images")
                with open(img_path, "wb") as f:
                    f.write(img_file.getbuffer())
            
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
                    kayit = df[df["Görüntü"] == secili_kayit]
                    if st.button("Sil"):
                        df = df[df["Görüntü"] != secili_kayit]
                        df.to_csv(CSV_FILE, index=False)
                        st.success("Kayıt başarıyla silindi!")
        else:
            st.warning("Kayıt dosyası bulunamadı.")
