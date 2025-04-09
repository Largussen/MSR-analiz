
import streamlit as st
import pandas as pd
import os
import datetime

CSV_FILE = "veriler.csv"

st.set_page_config(page_title="TYT Soru Takip", layout="wide")

st.markdown(
    "<h1 style='text-align: center; color: white;'>TYT Soru Takip ve Analiz</h1>",
    unsafe_allow_html=True
)

menu = ["Analiz", "Soru Ekle", "Kayıt Sil", "Soru Notları", "İşaretli Sorular"]
secenek = st.sidebar.selectbox("Menü", menu)

if secenek == "Soru Ekle":
    st.header("Yeni Soru Kaydı")
    col1, col2 = st.columns(2)
    with col1:
        ders = st.selectbox("Ders", ["Türkçe", "Matematik", "Fen", "Sosyal"])
        konu = st.text_input("Konu")
        dogru = st.checkbox("Doğru")
        sure_dahil = st.checkbox("Süreyi ortalamaya dahil et", value=True)
    with col2:
        soru_no = st.number_input("Soru No", min_value=1, step=1)
        dakika = st.number_input("Dakika", min_value=0, step=1)
        saniye = st.number_input("Saniye", min_value=0, max_value=59, step=1)
        zorlanma = st.slider("Zorluk (0: Çok Kolay - 4: Çok Zor)", 0, 4, 2)
        isaretli = st.checkbox("Soruyu işaretle")
    aciklama = st.text_area("Açıklama (varsa)")
    soru_notu = st.text_area("Soru Notu (varsa)")

    if st.button("Kaydet"):
        toplam_sure = dakika * 60 + saniye
        yeni_veri = pd.DataFrame([{
            "Tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Ders": ders,
            "Konu": konu,
            "Soru No": soru_no,
            "Doğru": dogru,
            "Süre": toplam_sure,
            "Zorluk": zorlanma,
            "İşaretli": isaretli,
            "Açıklama": aciklama,
            "Soru Notu": soru_notu,
            "Süre Dahil": sure_dahil
        }])
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, yeni_veri], ignore_index=True)
        else:
            df = yeni_veri
        df.to_csv(CSV_FILE, index=False)
        st.success("Kayıt başarıyla eklendi.")

elif secenek == "Analiz":
    st.header("Analiz Ekranı")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        filtre_ders = st.multiselect("Ders Seç", df["Ders"].unique())
        filtre_konu = st.multiselect("Konu Seç", df["Konu"].unique())
        filtre_zorluk = st.multiselect("Zorluk Seç (0-4)", sorted(df["Zorluk"].unique()))

        if filtre_ders:
            df = df[df["Ders"].isin(filtre_ders)]
        if filtre_konu:
            df = df[df["Konu"].isin(filtre_konu)]
        if filtre_zorluk:
            df = df[df["Zorluk"].isin(filtre_zorluk)]

        toplam_soru = len(df)
        dogru_sayi = df["Doğru"].sum()
        if "Süre Dahil" in df.columns:
            ort_sure = df[df["Süre Dahil"] == True]["Süre"].mean()
        else:
            ort_sure = df["Süre"].mean()
        ort_zorluk = df["Zorluk"].mean()

        st.metric("Toplam Soru", toplam_soru)
        st.metric("Doğru Sayısı", int(dogru_sayi))
        st.metric("Ortalama Süre (sn)", f"{ort_sure:.2f}")
        st.metric("Ortalama Zorluk", f"{ort_zorluk:.2f}")

        st.dataframe(df)
    else:
        st.warning("Henüz veri eklenmemiş.")

elif secenek == "Kayıt Sil":
    st.header("Kayıt Silme")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df.tail(10))
        sil_id = st.number_input("Silinecek Sıra No", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Sil"):
            df = df.drop(index=sil_id).reset_index(drop=True)
            df.to_csv(CSV_FILE, index=False)
            st.success("Kayıt silindi.")
    else:
        st.warning("Veri dosyası bulunamadı.")

elif secenek == "Soru Notları":
    st.header("Soru Notları")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = df[df["Soru Notu"].notna() & (df["Soru Notu"] != "")]
        filtre_ders = st.multiselect("Ders Filtrele", df["Ders"].unique())
        filtre_konu = st.multiselect("Konu Filtrele", df["Konu"].unique())

        if filtre_ders:
            df = df[df["Ders"].isin(filtre_ders)]
        if filtre_konu:
            df = df[df["Konu"].isin(filtre_konu)]

        for ders in df["Ders"].unique():
            ders_df = df[df["Ders"] == ders]
            st.subheader(f"📘 {ders}")
            for konu in ders_df["Konu"].unique():
                konu_df = ders_df[ders_df["Konu"] == konu]
                st.markdown(f"**🔹 {konu}**")
                for _, row in konu_df.iterrows():
                    st.markdown(f"- Soru {int(row['Soru No'])}: {row['Soru Notu']}")
    else:
        st.warning("Henüz not alınmış soru bulunamadı.")

elif secenek == "İşaretli Sorular":
    st.header("İşaretli Sorular")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if "İşaretli" in df.columns and True in df["İşaretli"].unique():
            for ders in df["Ders"].unique():
                alt_df = df[(df["Ders"] == ders) & (df["İşaretli"] == True)]
                if not alt_df.empty:
                    st.subheader(ders)
                    sorular = alt_df["Soru No"].tolist()
                    st.write(f"İşaretli Sorular: {', '.join(map(str, sorular))}")
    else:
        st.warning("Veri dosyası bulunamadı.")
