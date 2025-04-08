import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

CSV_FILE = "soru_kayitlari.csv"
KONSOL_SIFRE = "1234"  # Şifreni buradan ayarlayabilirsin

st.set_page_config(page_title="TYT Soru Takip", layout="wide", initial_sidebar_state="expanded")
st.title("TYT Soru Takip ve Analiz Aracı")

# Konular
konular_dict = {
    "Matematik": ["Temel Kavramlar", "Sayılar", "Problemler", "Fonksiyonlar", "Geometri"],
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Dil Bilgisi"],
    "Fizik": ["Hareket", "Kuvvet", "Enerji", "Optik"],
    "Kimya": ["Atom", "Periyodik Sistem", "Kimyasal Tepkimeler"],
    "Biyoloji": ["Hücre", "Canlıların Sınıflandırılması", "Ekosistem"],
    "Tarih": ["İnkılap Tarihi", "Orta Çağ", "Yeni Çağ"],
    "Coğrafya": ["Harita Bilgisi", "İklim", "Yer Şekilleri"],
    "Felsefe": ["Felsefenin Alanı", "Bilgi Felsefesi"],
    "Din Kültürü": ["İslam ve İbadet", "Kur’an-ı Kerim"]
}

# Oturum yönetimi
if "dogrulandi" not in st.session_state:
    st.session_state.dogrulandi = False

menu = ["Analiz", "Konsol"]
if st.session_state.dogrulandi:
    menu += ["Soru Girişi", "Kayıt Sil"]

secenek = st.sidebar.radio("Sayfa Seç:", menu)

# 🔐 Konsol Şifre Ekranı
if secenek == "Konsol":
    st.header("🔐 Konsol Girişi")
    sifre = st.text_input("Şifreyi Gir:", type="password")
    if st.button("Giriş Yap"):
        if sifre == KONSOL_SIFRE:
            st.session_state.dogrulandi = True
            st.success("Giriş başarılı! Yeni sekmeler aktif.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Hatalı şifre!")

# ➕ Soru Girişi
elif secenek == "Soru Girişi" and st.session_state.dogrulandi:
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

# 📊 Analiz
elif secenek == "Analiz":
    st.header("Çözülen Soruların Analizi")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        st.subheader("Filtreleme")
        dersler = ["Tümü"] + sorted(df["Ders"].dropna().unique())
        secilen_ders = st.selectbox("Derse göre filtrele", dersler)

        if secilen_ders != "Tümü":
            df = df[df["Ders"] == secilen_ders]

        yillar = ["Tümü"] + sorted(df["Yıl"].dropna().unique())
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
        st.write(f"✅ Çözülen Ortalama: **{sure_c:.2f} dk**")
        st.write(f"❌ Çözemedim Ortalama: **{sure_y:.2f} dk**")

        st.subheader("Grafik: Süre Karşılaştırması")
        fig, ax = plt.subplots(facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        ax.bar(["Çözülen", "Çözemedim"], [sure_c, sure_y], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)", color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)

        st.subheader("Çözülmeyen Sorulardan Notlar")
        df["Açıklama"] = df["Açıklama"].astype(str)
        aciklamalar = df[(df["Durum"] == "Çözemedim") & (df["Açıklama"].str.strip() != "")]
        if not aciklamalar.empty:
            for _, row in aciklamalar.iterrows():
                st.markdown(f"📌 **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
        else:
            st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
    else:
        st.warning("Henüz veri bulunmuyor.")

# 🗑️ Kayıt Silme
elif secenek == "Kayıt Sil" and st.session_state.dogrulandi:
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
                st.success("Kayıt silindi!")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("Kayıt dosyası bulunamadı.")
