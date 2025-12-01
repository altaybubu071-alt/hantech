import streamlit as st
import random
import json
import re
from datetime import datetime, timedelta
import os
import requests
import time
import google.generativeai as genai
import bcrypt
import psycopg2
from psycopg2.extras import DictCursor
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import warnings
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

LANGUAGES = {
    "🇹🇷 Türkçe": "tr", "🇬🇧 English": "en", "🇪🇸 Español": "es", "🇫🇷 Français": "fr",
    "🇩🇪 Deutsch": "de", "🇮🇹 Italiano": "it", "🇵🇹 Português": "pt", "🇷🇺 Русский": "ru",
    "🇯🇵 日本語": "ja", "🇨🇳 中文": "zh", "🇰🇷 한국어": "ko", "🇦🇷 العربية": "ar",
    "🇮🇳 हिन्दी": "hi", "🇳🇱 Nederlands": "nl", "🇸🇪 Svenska": "sv", "🇩🇰 Dansk": "da",
    "🇳🇴 Norsk": "no", "🇫🇮 Suomi": "fi", "🇵🇱 Polski": "pl", "🇬🇷 Ελληνικά": "el",
    "🇨🇿 Čeština": "cs", "🇸🇰 Slovenčina": "sk", "🇭🇺 Magyar": "hu", "🇷🇴 Română": "ro",
    "🇧🇬 Български": "bg", "🇭🇷 Hrvatski": "hr", "🇸🇮 Slovenščina": "sl", "🇪🇪 Eesti": "et",
    "🇱🇻 Latviešu": "lv", "🇱🇹 Lietuvių": "lt", "🇮🇸 Íslenska": "is", "🇺🇦 Українська": "uk",
    "🇧🇾 Беларуская": "be", "🇹🇮 ไทย": "th", "🇻🇳 Tiếng Việt": "vi", "🇵🇭 Tagalog": "tl",
    "🇮🇩 Bahasa Indonesia": "id", "🇲🇾 Bahasa Melayu": "ms", "🇸🇬 新加坡华语": "zh-sg",
    "🇲🇳 Монгол": "mn", "🇮🇷 فارسی": "fa", "🇦🇱 Shqip": "sq", "🇦🇲 Հայերեն": "hy",
    "🇦🇿 Azərbaycanca": "az", "🇰🇿 Қазақша": "kk", "🇺🇿 Ўзбекча": "uz",
    "🇧🇩 বাংলা": "bn", "🇱🇰 සිංහල": "si", "🇵🇰 اردو": "ur",
}

st.set_page_config(page_title="Han Technology Pyhton ®️", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#ffd700">
    <style>
    .stApp { background: linear-gradient(135deg, #1a1a1a 0%, #2d2416 50%, #1a1a1a 100%); color: #ffd700; }
    h1, h2, h3, label, p, div { font-family: 'Georgia', 'Arial', sans-serif !important; color: #ffd700 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select { background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%) !important; color: #ffd700 !important; border: 2px solid #b8860b !important; border-radius: 8px !important; }
    .stButton>button { background: linear-gradient(135deg, #ffd700 0%, #daa520 100%) !important; border: 2px solid #b8860b !important; color: #1a1a1a !important; width: 100% !important; padding: 12px !important; border-radius: 8px !important; font-weight: bold !important; }
    .stButton>button:hover { background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%) !important; box-shadow: 0 0 20px rgba(255, 215, 0, 0.5) !important; }
    .stSidebar { background: linear-gradient(135deg, #1a1a1a 0%, #2d2416 100%) !important; }
    .stChatMessage { background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%) !important; border: 2px solid #b8860b !important; border-radius: 12px !important; padding: 15px !important; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    @keyframes glow { 0%, 100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.5); } 50% { box-shadow: 0 0 30px rgba(255, 215, 0, 0.8); } }
    @media (max-width: 768px) { .stApp { padding: 0 10px !important; } h1, h2, h3 { font-size: 18px !important; } .stButton>button { padding: 10px !important; font-size: 14px !important; } }
    </style>
""", unsafe_allow_html=True)

def get_db_connection():
    try:
        return psycopg2.connect(os.environ.get("DATABASE_URL"))
    except Exception as e:
        st.error(f"❌ Veritabanı Hatası: {e}")
        return None

def register_user(username, email, password):
    if not username or not email or not password:
        return False, "⚠️ Tüm alanları doldurunuz!"
    if len(password) < 6:
        return False, "⚠️ Şifre en az 6 karakter olmalı!"
    conn = get_db_connection()
    if not conn:
        return False, "❌ Veritabanı hatası!"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return False, "⚠️ Bu kullanıcı adı veya email zaten kayıtlı!"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("INSERT INTO users (username, email, password_hash, password_plain) VALUES (%s, %s, %s, %s)", (username, email, password_hash, password))
        conn.commit()
        cursor.close()
        conn.close()
        return True, "✅ Kayıt başarılı! Giriş yapınız."
    except Exception as e:
        return False, f"❌ Hata: {str(e)}"

def login_user(username, password):
    if not username or not password:
        return False, "⚠️ Tüm alanları doldurunuz!"
    conn = get_db_connection()
    if not conn:
        return False, "❌ Veritabanı hatası!"
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT id, password_hash, banned FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user:
            return False, "⚠️ Kullanıcı bulunamadı!"
        if user['banned']:
            return False, "🚫 Bu Kullanıcı Banlanmış!"
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return True, username
        else:
            return False, "⚠️ Hatalı şifre!"
    except Exception as e:
        return False, f"❌ Hata: {str(e)}"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.chat_messages = []

if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center;'><h1 style='color:#ffd700;'>🔐 Han Technology Python</h1></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Giriş", "📝 Kayıt"])
    with tab1:
        username = st.text_input("👤 Kullanıcı Adı")
        password = st.text_input("🔐 Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            success, message = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = message
                st.success("✅ Hoşgeldiniz!")
                st.rerun()
            else:
                st.error(message)
    with tab2:
        new_username = st.text_input("👤 Yeni Kullanıcı Adı")
        new_email = st.text_input("📧 Email")
        new_password = st.text_input("🔐 Şifre", type="password")
        if st.button("Kayıt Ol", use_container_width=True):
            success, message = register_user(new_username, new_email, new_password)
            if success:
                st.success(message)
            else:
                st.error(message)
else:
    st.sidebar.title(f"👤 {st.session_state.username}")
    menu = st.sidebar.radio("📌 Menu", ["🏠 Ana Sayfa", "💬 AI Sohbet", "🧮 Hesap Makinesi", "🎮 Oyun", "🌐 Proxy Browser"])
    
    if menu == "🏠 Ana Sayfa":
        st.title("👋 Hoşgeldiniz!")
        st.write(f"Merhaba **{st.session_state.username}**! 🎉")
    
    elif menu == "💬 AI Sohbet":
        st.title("🤖 Yapay Zeka Sohbet")
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            st.warning("⚠️ Gemini API Anahtarı gerekli!")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            user_input = st.chat_input("💭 Mesajınızı yazınız...")
            if user_input:
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.write(user_input)
                with st.chat_message("assistant"):
                    with st.spinner("🤖 AI Yanıt Veriliyor..."):
                        try:
                            response = model.generate_content(user_input)
                            assistant_response = response.text
                            st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                            st.write(assistant_response)
                        except Exception as e:
                            st.error(f"❌ Hata: {str(e)}")
    
    elif menu == "🧮 Hesap Makinesi":
        st.title("🧮 Hesap Makinesi")
        s1 = st.number_input("🔢 Birinci Sayı", format="%.2f")
        s2 = st.number_input("🔢 İkinci Sayı", format="%.2f")
        op = st.selectbox("➕ İşlem", ["➕ Toplama", "➖ Çıkarma", "✖️ Çarpma", "➗ Bölme"])
        if st.button("= Hesapla"):
            r = 0
            if "Toplama" in op: r = s1 + s2
            elif "Çıkarma" in op: r = s1 - s2
            elif "Çarpma" in op: r = s1 * s2
            elif "Bölme" in op: r = s1 / s2 if s2 != 0 else "Hata"
            st.write(f"✅ Sonuç: **{r}**")
    
    elif menu == "🎮 Oyun":
        st.title("🎮 Tahmin Oyunu")
        if st.button("🆕 Yeni Oyun"):
            st.session_state.tahmin_sayisi = random.randint(1, 100)
            st.session_state.tahmin_hak = 5
            st.session_state.tahmin_bitti = False
            st.rerun()
        if 'tahmin_hak' not in st.session_state:
            st.session_state.tahmin_hak = 5
            st.session_state.tahmin_bitti = False
            st.session_state.tahmin_sayisi = random.randint(1, 100)
        st.write(f"⏱️ Kalan Hak: **{st.session_state.tahmin_hak}**")
        g = st.number_input("🎯 Tahmin Edin", 1, 100)
        if st.button("✓ Tahmini Gönder"):
            st.session_state.tahmin_hak -= 1
            if g == st.session_state.tahmin_sayisi:
                st.success("🎉 KAZANDIN!")
                st.balloons()
                st.session_state.tahmin_bitti = True
            elif st.session_state.tahmin_hak == 0:
                st.error(f"💀 Sayı: **{st.session_state.tahmin_sayisi}**")
                st.session_state.tahmin_bitti = True
            elif g < st.session_state.tahmin_sayisi:
                st.info("⬆️ Daha Yüksek Deneyin!")
            else:
                st.info("⬇️ Daha Düşük Deneyin!")
    
    elif menu == "🌐 Proxy Browser":
        st.title("🌐 Proxy Browser")
        url = st.text_input("🔗 URL Girin", placeholder="example.com")
        if st.button("🔍 Aç"):
            try:
                if not url.startswith("http"):
                    url = "https://" + url
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                st.success("✅ Sayfa Yüklendi!")
                soup = BeautifulSoup(response.text, 'html.parser')
                st.write(soup.get_text()[:1000])
            except Exception as e:
                st.error(f"❌ Hata: {str(e)}")
    
    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
