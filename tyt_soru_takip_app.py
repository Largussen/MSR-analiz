import streamlit as st
import pandas as pd
import datetime  # Burada datetime modülünü import ediyoruz
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
    "Rasyonel Sayılar",
