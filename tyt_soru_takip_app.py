import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt
from PIL import Image

# 🗂️ Ayarlar
CSV_FILE = "soru_kayitlari.csv"
KONSOL_SIFRE = "1234"

# 🎨 Tema ve stil
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    .stDataFrame tbody td { color: white !important; }
    .stDataFrame thead th { color: white !important; }
    div[data-testid="stMetricValue"] { color: white; }
    button:hover { transform: scale(1.03); }
    @media only screen and (max-width: 600px) {
        .stColumn { display: block !important; width: 100% !important; }
    }
    </style>
""", unsafe_allow_html=True)

# 📚 Konular
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

# 📋 Menü
menu = ["Analiz", "Soru Notları", "Yıldızlı Sorular", "Konsol"]
secenek = st.sidebar.radio("Menü:", menu)

# 🔐 Şifre kontrolü
sifre_dogru = False
if secenek == "Konsol":
    girilen = st.text_input("Konsol Girişi - Şifre:", type="password")
    if girilen == KONSOL_SIFRE:
        sifre_dogru = True
    else:
        st.warning("Konsola erişmek için doğru şifreyi girin.")

# 📊 ANALİZ
if secenek == "Analiz":
    st.image(Image.open("kemal.png"), width=200)
    st.header("")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        if not df.empty:
            st.subheader("Filtreleme")
            dersler = ["Tümü"] + sorted(df["Ders"].unique())
            secilen_ders = st.selectbox("Derse göre filtrele", dersler)

            if secilen_ders != "Tümü":
                df = df[df["Ders"] == secilen_ders]

            zorluklar = ["Tümü", "0", "1", "2", "3", "4"]
            sec_zorluk = st.selectbox("Zorluğa göre filtrele (0: Çok Kolay - 4: Çok Zor)", zorluklar)
            if sec_zorluk != "Tümü":
                df = df[df["Zorluk"] == int(sec_zorluk)]

            yillar = ["Tümü"] + sorted(df["Yıl"].unique())
            secilen_yil = st.selectbox("Yıla göre filtrele", yillar)
            if secilen_yil != "Tümü":
                df = df[df["Yıl"] == secilen_yil]

            st.subheader("Genel Bilgiler")
            toplam_soru = len(df)
            cozulen = len(df[df["Durum"] == "Çözüldü"])
            cozememe = toplam_soru - cozulen
            ort_sure = df["Süre"].mean().round(2)
            ort_zorluk = df["Zorluk"].mean().round(2) if "Zorluk" in df.columns else "Yok"

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
        else:
            st.info("Henüz kayıt yok.")
    else:
        st.warning("Veri dosyası bulunamadı.")

# 📘 SORU NOTLARI
elif secenek == "Soru Notları":
    st.header("📝 Soru Notları")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            df["Açıklama"] = df["Açıklama"].astype(str)
            aciklamalar = df[(df["Açıklama"].str.strip() != "")]
            for _, row in aciklamalar.iterrows():
                z = f" - Zorluk: {row['Zorluk']}" if "Zorluk" in row else ""
                st.markdown(f"**{row['Ders']} - {row['Konu']} | {row['Yıl']} | Soru {int(row['Soru No'])}**{z} → {row['Açıklama']}")
        else:
            st.info("Hiç açıklama girilmemiş.")
    else:
        st.warning("Veri dosyası bulunamadı.")


elif secenek == "İşaretli Sorular":
    st.header("İşaretli Sorular")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if "İşaretli" in df.columns or "Yıldızlı" in df.columns:
            # "Yıldızlı" olarak kaydedildiyse onu "İşaretli" olarak kabul et
            if "Yıldızlı" in df.columns and "İşaretli" not in df.columns:
                df.rename(columns={"Yıldızlı": "İşaretli"}, inplace=True)

            if True in df["İşaretli"].unique():
                for ders in sorted(df["Ders"].unique()):
                    alt_df = df[(df["Ders"] == ders) & (df["İşaretli"] == True)]
                    if not alt_df.empty:
                        st.subheader(ders)
                        sorular = alt_df["Soru No"].tolist()
                        st.write(f"İşaretli Sorular: {', '.join(map(str, sorular))}")
            else:
                st.info("Henüz işaretli soru bulunmuyor.")
        else:
            st.info("Verilerde 'İşaretli' bilgisi yer almıyor.")
    else:
        st.warning("Veri dosyası bulunamadı.")


# ⚙️ KONSOL
if secenek == "Konsol" and sifre_dogru:
    secim = st.radio("İşlem Seç:", ["Yeni Soru Ekle", "Kayıt Sil"])
    if secim == "Yeni Soru Ekle":
        st.header("➕ Yeni Soru Kaydı Ekle")
        ders = st.selectbox("Ders", list(konular_dict.keys()))
        konu = st.selectbox("Konu", konular_dict[ders])
        col1, col2 = st.columns(2)
        with col1:
            yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021"])
            soru_no = st.number_input("Soru No", min_value=1, max_value=1000, step=1)
        with col2:
            dak = st.number_input("Süre (Dakika)", min_value=0, step=1)
            sn = st.number_input("Süre (Saniye)", min_value=0, max_value=59, step=1)
            sure = round(dak + sn / 60, 2)
        durum = st.radio("Durum", ["Çözüldü", "Çözülemeyen"])
        zorluk = st.slider("Zorluk Seviyesi (0: Çok Kolay - 4: Çok Zor)", 0, 4, 2)
        yildizli = st.checkbox("⭐ Soruyu yıldızla")
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
                "Açıklama": [aciklama],
                "Zorluk": [zorluk],
                "Yıldızlı": [yildizli]
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
