
import streamlit as st
import pandas as pd
import datetime
import os

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"

# Uygulama başlığı
st.title("📘 TYT Soru Takip ve Analiz Aracı")
st.markdown("Konu konu çözdüğün soruları takip etmek ve analiz etmek için küçük bir araç.")

# Sayfa seçimi
secenek = st.sidebar.radio("Sayfa Seç:", ["➕ Soru Girişi", "📊 Analiz"])

# Konu listesi (ilk sürüm: Matematik)
konular = [
    "Temel Kavramlar", "Sayı Basamakları", "Bölme ve Bölünebilme", "Asal Çarpanlar", "EBOB-EKOK",
    "Rasyonel Sayılar", "Ondalık Sayılar", "Sıralama - İşaret", "Mutlak Değer", "Üslü Sayılar",
    "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Problemler", "Kümeler", "Fonksiyonlar",
    "Polinomlar", "2. Dereceden Denklemler", "Çokgenler", "Çember", "Olasılık"
]

# Ders seçimi (ileride genişletmek için hazır bıraktık)
ders = "Matematik"

# Soru Girişi Sayfası
if secenek == "➕ Soru Girişi":
    st.header("➕ Yeni Soru Kaydı Ekle")

    col1, col2 = st.columns(2)
    with col1:
        yil = st.selectbox("Yıl / Kaynak", ["2024", "2023", "2022", "2021", "2020", "2019", "2018"])
        soru_no = st.number_input("Soru No", min_value=1, max_value=50, step=1)
    with col2:
        konu = st.selectbox("Konu", konular)
        sure = st.number_input("Süre (dakika)", min_value=0.0, step=0.1, format="%.1f")

    durum = st.radio("Durum", ["✅ Çözüldü", "❌ Çözemedim"])
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
        st.success("✅ Kayıt başarıyla eklendi!")

# Analiz Sayfası
elif secenek == "📊 Analiz":
    st.header("📊 Çözülen Soruların Analizi")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        st.subheader("Filtreleme")
        yillar = ["Tümü"] + sorted(df["Yıl"].unique().tolist())
        secilen_yil = st.selectbox("Yıla göre filtrele", yillar)

        if secilen_yil != "Tümü":
            df = df[df["Yıl"] == secilen_yil]

        st.subheader("📌 Genel Bilgiler")
        toplam_soru = len(df)
        cozulen = len(df[df["Durum"] == "✅ Çözüldü"])
        cozememe = toplam_soru - cozulen
        ort_sure = df["Süre"].mean().round(2)

        st.markdown(f"- Toplam Soru: **{toplam_soru}**")
        st.markdown(f"- Çözülen: **{cozulen}** ✅")
        st.markdown(f"- Çözülemeyen: **{cozememe}** ❌")
        st.markdown(f"- Ortalama Süre: **{ort_sure} dk**")

        st.subheader("📚 Konu Bazlı Performans")
        konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
        konu_grup["Toplam"] = konu_grup.sum(axis=1)
        konu_grup["Başarı %"] = (konu_grup.get("✅ Çözüldü", 0) / konu_grup["Toplam"] * 100).round(1)
        st.dataframe(konu_grup.sort_values("Başarı %", ascending=False))
    else:
        st.warning("Henüz kayıt bulunmuyor. Önce soru girişi yapmalısın.")
