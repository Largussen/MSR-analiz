import streamlit as st
import pandas as pd
import datetime
import os
import time
import matplotlib.pyplot as plt

# Sayfa ayarları
st.set_page_config(page_title="TYT Soru Takip ve Analiz", layout="wide")

# Özel CSS
st.markdown("""
    <style>
        /* Koyu tema için varsayılan renkleri değiştir */
        .stDataFrame tbody tr td {
            color: #e0e0e0 !important;
        }
        .stDataFrame thead tr th {
            color: #f0f0f0 !important;
        }
        .st-emotion-cache-1avcm0n { color: #e0e0e0 !important; } /* metric yazıları */
        .st-emotion-cache-10trblm, .st-emotion-cache-6qob1r {
            color: #e0e0e0 !important;
        }
        /* Mor renkleri beyaz/açık gri yap */
        .css-1aumxhk, .css-1offfwp {
            color: #f0f0f0 !important;
        }
        /* Hover animasyonu */
        button:hover {
            background-color: #444 !important;
            transform: scale(1.02);
            transition: 0.3s ease;
        }
        /* Fade in animasyonları */
        .fade-in {
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        /* Slide-in efekt */
        .slide-in {
            animation: slideIn 0.8s ease-out;
        }
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# CSV dosyası
CSV_FILE = "soru_kayitlari.csv"

# Şifre
GIRIS_SIFRE = "2024"

# Konular
konular_dict = {
    "Matematik": ["Temel Kavramlar", "Sayılar", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel Sayılar", "Ondalık Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Denklem Çözme", "Problemler", "Kümeler", "Fonksiyonlar", "Grafikler", "Modüler Aritmetik", "Mantık", "Sayma ve Olasılık", "Permütasyon-Kombinasyon", "Polinomlar"],
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcük Türleri", "Cümle Bilgisi", "Anlatım Bozuklukları"],
    "Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Kuvvet ve Hareket", "Isı, Sıcaklık ve Genleşme", "Elektrik", "Optik", "Basit Makineler"],
    "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Maddenin Halleri", "Karışımlar", "Asit-Baz-Tuz", "Kimya Her Yerde"],
    "Biyoloji": ["Canlıların Ortak Özellikleri", "Hücre", "Kalıtım", "Ekosistem", "Canlılarda Enerji", "Destek ve Hareket", "Solunum", "Boşaltım", "Dolaşım"],
    "Tarih": ["Tarih Bilimi", "İlk Türk Devletleri", "İslamiyet Öncesi Türk Tarihi", "Osmanlı Kuruluş Dönemi", "İnkılap Tarihi", "Milli Mücadele", "Kurtuluş Savaşı"],
    "Coğrafya": ["Doğa ve İnsan", "Harita Bilgisi", "İklim", "Nüfus", "Yer Şekilleri", "Ekonomi", "Ulaşım", "Çevre Sorunları"],
    "Felsefe": ["Felsefenin Alanı", "Bilgi Felsefesi", "Ahlak", "Sanat", "Siyaset", "Din Felsefesi"],
    "Din Kültürü": ["İslam ve İbadet", "Hz. Muhammed'in Hayatı", "Kur’an-ı Kerim", "İslam Ahlakı", "İnanç"]
}

# Sayfa seçimi
sayfalar = ["Analiz", "Konsol"]
secili_sayfa = st.sidebar.selectbox("Sayfa Seç", sayfalar)

# Konsol içeriğini şifreli göster
konsol_aktif = False
if secili_sayfa == "Konsol":
    girilen_sifre = st.text_input("🔒 Konsol erişim şifresi:", type="password")
    if girilen_sifre == GIRIS_SIFRE:
        konsol_aktif = True
    else:
        st.warning("Konsola erişmek için geçerli şifre giriniz.")

# Analiz Sayfası
if secili_sayfa == "Analiz":
    st.title("📊 TYT Soru Analiz Ekranı")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df["Açıklama"] = df["Açıklama"].astype(str)

        dersler = ["Tümü"] + sorted(df["Ders"].unique())
        secilen_ders = st.selectbox("Derse göre filtrele", dersler)
        if secilen_ders != "Tümü":
            df = df[df["Ders"] == secilen_ders]

        yillar = ["Tümü"] + sorted(df["Yıl"].unique())
        secilen_yil = st.selectbox("Yıla göre filtrele", yillar)
        if secilen_yil != "Tümü":
            df = df[df["Yıl"] == secilen_yil]

        toplam = len(df)
        cozulmus = len(df[df["Durum"] == "Çözülen"])
        cozulmemis = toplam - cozulmus
        ort_sure = df["Süre"].mean().round(2)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Soru", toplam)
        col2.metric("Çözülen", cozulmus)
        col3.metric("Çözülemeyen", cozulmemis)
        col4.metric("Ortalama Süre", f"{ort_sure} dk")

        st.subheader("Konu Bazlı Performans")
        konu_grup = df.groupby("Konu")["Durum"].value_counts().unstack().fillna(0)
        konu_grup["Toplam"] = konu_grup.sum(axis=1)
        konu_grup["Başarı %"] = (konu_grup.get("Çözülen", 0) / konu_grup["Toplam"] * 100).round(1)
        st.dataframe(konu_grup.sort_values("Başarı %", ascending=False))

        st.subheader("Süre Karşılaştırması")
        sure_c = df[df["Durum"] == "Çözülen"]["Süre"].mean()
        sure_y = df[df["Durum"] == "Çözülemeyen"]["Süre"].mean()

        fig, ax = plt.subplots()
        ax.bar(["Çözülen", "Çözülemeyen"], [sure_c, sure_y], color=["green", "red"])
        ax.set_ylabel("Ortalama Süre (dk)")
        ax.set_facecolor("#0e1117")  # koyu arkaplan
        fig.patch.set_facecolor('#0e1117')
        st.pyplot(fig)

        st.subheader("Notlar (Çözülemeyen Sorular)")
        notlar = df[(df["Durum"] == "Çözülemeyen") & (df["Açıklama"].str.strip() != "")]
        if not notlar.empty:
            for _, row in notlar.iterrows():
                st.markdown(f"📌 **{row['Ders']} - {row['Konu']}** → {row['Açıklama']}")
        else:
            st.info("Açıklama girilmiş çözülemeyen soru bulunamadı.")
    else:
        st.warning("Henüz kayıt bulunmuyor.")

# Konsol Sayfası (şifre ile açılan)
if secili_sayfa == "Konsol" and konsol_aktif:
    st.title("⚙️ Konsol")

    secim = st.radio("İşlem seçin:", ["Soru Girişi", "Kayıt Sil"])

    if secim == "Soru Girişi":
        st.subheader("➕ Yeni Soru Kaydı Ekle")

        ders = st.selectbox("Ders", list(konular_dict.keys()))
        konu = st.selectbox("Konu", konular_dict[ders])
        yil = st.selectbox("Yıl", ["2024", "2023", "2022", "2021", "2020", "2019", "2018"])
        soru_no = st.number_input("Soru No", min_value=1, max_value=1000, step=1)
        sure = st.number_input("Süre (dk)", min_value=0.0, step=0.1)
        durum = st.radio("Durum", ["Çözülen", "Çözülemeyen"])
        aciklama = st.text_area("Açıklama (isteğe bağlı)")

        if st.button("Kaydet"):
            yeni = pd.DataFrame({
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
                df = pd.read_csv(CSV_FILE)
                df = pd.concat([df, yeni], ignore_index=True)
            else:
                df = yeni
            df.to_csv(CSV_FILE, index=False)
            st.success("Kayıt başarıyla eklendi!")

    elif secim == "Kayıt Sil":
        st.subheader("🗑️ Kayıt Sil")

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if df.empty:
                st.info("Kayıt yok.")
            else:
                df["Görüntü"] = df.apply(lambda r: f"{r['Tarih']} | {r['Ders']} | {r['Konu']} | Soru {int(r['Soru No'])}", axis=1)
                sec_kayit = st.selectbox("Silmek istediğin kayıt:", df["Görüntü"])
                sec_index = df[df["Görüntü"] == sec_kayit].index[0]
                if st.button("Kaydı Sil"):
                    df = df.drop(sec_index)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Kayıt silindi!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.warning("Kayıt dosyası yok.")
