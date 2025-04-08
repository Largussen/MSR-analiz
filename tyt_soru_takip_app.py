import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# Sayfa ayarı
st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")

# 🎨 Tema ve Stil
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #20232a;
        border-right: 1px solid #6c63ff;
    }

    h1, h2, h3, h4 {
        color: #6c63ff !important;
        text-align: center;
    }

    .stButton>button {
        background-color: #6c63ff;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        border: none;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }

    .stButton>button:hover {
        background-color: #4b47cc;
        transform: scale(1.05);
    }

    div[data-testid="metric-container"] {
        background-color: #1c1c1e;
        padding: 10px;
        border-radius: 10px;
        color: white;
        border: 1px solid #6c63ff;
        margin-bottom: 10px;
        text-align: center;
    }

    .stDataFrame {
        background-color: #0e1117;
        border-radius: 10px;
        border: 1px solid #6c63ff;
        padding: 10px;
        color: white;
    }

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #6c63ff;
        border-radius: 10px;
    }

    textarea {
        border-radius: 10px !important;
    }

    .stSelectbox, .stNumberInput, .stTextInput, .stRadio, .stDateInput {
        background-color: #1e1e1e !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"

# Tüm TYT dersleri ve konuları
konular_dict = {
    "Matematik": ["Temel Kavramlar", "Sayılar", "Problemler", "Fonksiyonlar", "Kümeler", "Kombinasyon", "Olasılık", "İstatistik", "Denklemler", "Geometri", "Trigonometrik Fonksiyonlar"],
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım Kuralları", "Noktalama", "Dil Bilgisi", "Anlatım Bozukluğu", "Sözcük Türleri"],
    "Fizik": ["Kuvvet ve Hareket", "Isı ve Sıcaklık", "Elektrik", "Dalgalar", "Optik", "Basınç", "Modern Fizik"],
    "Kimya": ["Atom", "Periyodik Sistem", "Kimyasal Tepkimeler", "Asit-Baz", "Mol", "Organik Kimya"],
    "Biyoloji": ["Hücre", "DNA", "Ekosistem", "Canlıların Sınıflandırılması", "Genetik", "Sistemler"],
    "Tarih": ["İslamiyet Öncesi Türk Tarihi", "Osmanlı Devleti", "Kurtuluş Savaşı", "İnkılaplar", "Çağdaş Türk ve Dünya Tarihi"],
    "Coğrafya": ["Doğa ve İnsan", "Harita Bilgisi", "İklim", "Nüfus", "Ekonomi", "Türkiye'nin Yer Şekilleri"],
    "Felsefe": ["Bilgi Felsefesi", "Varlık Felsefesi", "Ahlak", "Sanat", "Siyaset", "Din Felsefesi"],
    "Din Kültürü": ["İslamiyet", "İnanç Esasları", "Ahlak", "Peygamberler", "Kur’an Bilgisi"]
}

# Şifre kontrolü
st.sidebar.title("Sayfa Seç")
sayfa = st.sidebar.radio("Menü", ["Analiz", "Konsol"])

# Varsayılan olarak Analiz açık

if sayfa == "Konsol":
    girilen_sifre = st.sidebar.text_input("🔐 Konsola erişmek için şifre girin", type="password")
    if girilen_sifre == "1234":
        secenek = st.sidebar.radio("İşlem Seç", ["Soru Girişi", "Kayıt Sil"])

        # Soru Girişi
        if secenek == "Soru Girişi":
            st.header("Yeni Soru Kaydı Ekle")

            ders = st.selectbox("Ders", list(konular_dict.keys()))
            konu = st.selectbox("Konu", konular_dict[ders])

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

        # Kayıt Sil
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
    else:
        st.warning("Konsola erişim için doğru şifreyi girin!")

# Analiz Sayfası
elif sayfa == "Analiz":
    st.title("TYT Soru Takip ve Analiz Aracı")
    st.header("📊 Çözülen Soruların Analizi")

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
        col1.metric("Toplam Soru", toplam_soru)
        col2.metric("Çözülen", cozulen)
        col3.metric("Çözülemeyen", cozememe)
        col4.metric("Ortalama Süre", f"{ort_sure} dk")

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
        ax.set_facecolor("#0e1117")
        fig.patch.set_facecolor("#0e1117")
        st.pyplot(fig)

        st.subheader("Çözülmeyen Sorulardan Notlar")
        if "Açıklama" in df.columns:
            df["Açıklama"] = df["Açıklama"].astype(str)
            aciklamalar = df[(df["Durum"] == "Çözemedim") & (df["Açıklama"].str.strip() != "")]
            if not aciklamalar.empty:
                for _, row in aciklamalar.iterrows():
                    st.markdown(f"📌 **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
            else:
                st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
    else:
        st.warning("Henüz kayıt bulunmuyor.")
