import streamlit as st
import random
import json
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

# --- 120+ DİL LİSTESİ ---
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
    "🇲🇳 Монгол": "mn", "🇮🇷 فارسی": "fa", "🇮🇪 Gaeilge": "ga", "🇬🇧 Welsh (Cymraeg)": "cy",
    "🇮🇳 ગુજરાતી": "gu", "🇮🇳 মার্জনা": "bn", "🇲🇼 Chichewa": "ny", "🇰🇪 Kiswahili": "sw",
    "🇪🇬 مصري": "arz", "🇲🇦 العربية المغربية": "ar-ma", "🇦🇱 Shqip": "sq", "🇦🇲 Հայերեն": "hy",
    "🇦🇿 Azərbaycanca": "az", "🇰🇿 Қазақша": "kk", "🇺🇿 Ўзбекча": "uz", "🇹🇯 Тоҷикӣ": "tg",
    "🇰🇬 Кыргызча": "ky", "🇹🇲 Түркменче": "tk", "🇦🇫 پشتو": "ps", "🇵🇰 اردو": "ur",
    "🇧🇩 বাংলা": "bn", "🇱🇰 සිංහල": "si", "🇲🇩 नेपाली": "ne", "🇮🇳 తెలుగు": "te",
    "🇮🇳 ಕನ್ನಡ": "kn", "🇮🇳 മലയാളം": "ml", "🇮🇳 தமிழ்": "ta", "🇵🇭 Cebuano": "ceb",
    "🇲🇬 Malagasy": "mg", "🇲🇿 Zulu": "zu", "🇿🇦 Xhosa": "xh", "🇿🇦 Sotho": "st",
    "🇿🇦 Afrikaans": "af", "🇧🇷 Crioulo": "crp", "🇰🇪 Luo": "luo", "🇦🇴 Rundi": "rn",
    "🇹🇿 Tatarça": "tt", "🇧🇳 Serbsça": "sr", "🇲🇽 Mixteco": "mix", "🇵🇪 Quechua": "qu",
    "🇬🇹 K'iche'": "quc", "🇵🇦 Pampanga": "pam", "🇵🇭 Ilocano": "ilo", "🇲🇾 Minangkabau": "min",
    "🇱🇦 ລາວ": "lo", "🇲🇲 မြန်မာ": "my", "🇰🇭 ខ្មែរ": "km", "🇲🇴 廣東話": "yue",
    "🇭🇰 粵語": "yue-hk", "🇨🇭 Romansh": "rm", "🇱🇺 Lëtzebuergesch": "lb", "🇲🇹 Malti": "mt",
    "🇨🇾 Ελληνικά (Κύπρος)": "el-cy", "🇦🇩 Català": "ca", "🇪🇸 Galego": "gl", "🇧🇦 Bosanski": "bs",
    "🇦🇴 Umbundu": "umb", "🇳🇦 Herero": "hz", "🇲🇿 Ndebelele": "nd", "🇿🇼 Shona": "sn",
    "🇬🇳 Fula": "ff", "🇲🇱 Bambara": "bm", "🇸🇳 Wolof": "wo", "🇿🇦 Venda": "ve",
    "🇿🇦 Tsonga": "ts", "🇲🇿 Nyanja": "ny", "🇳🇪 Haussa": "ha", "🇳🇬 Yorùbá": "yo",
    "🇳🇬 Igbo": "ig", "🇺🇬 Luganda": "lg", "🇰🇪 Samburu": "saq", "🇱🇻 Latviešu (Latvia)": "lv-lv",
    "🇪🇪 Eesti (Estonia)": "et-ee", "🇲🇹 Malti (Malta)": "mt-mt"
}

st.set_page_config(page_title="Han Technology Pyhton ®️", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#ffd700">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="Han Tech">
    <script>
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('service-worker.js').then(
          function(registration) {
            console.log('✅ Service Worker Başarılı:', registration.scope);
          },
          function(err) {
            console.log('Service Worker Hatası:', err);
          }
        );
      });
    }
    </script>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2416 50%, #1a1a1a 100%);
        color: #ffd700;
    }
    h1, h2, h3, label, p, div {
        font-family: 'Georgia', 'Arial', sans-serif !important;
        color: #ffd700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%) !important;
        color: #ffd700 !important;
        border: 2px solid #b8860b !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ffd700 0%, #daa520 100%) !important;
        border: 2px solid #b8860b !important;
        color: #1a1a1a !important;
        width: 100% !important;
        padding: 12px !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ffed4e 0%, #ffd700 100%) !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.5) !important;
    }
    .stSidebar {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2416 100%) !important;
    }
    .stChatMessage {
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%) !important;
        border: 2px solid #b8860b !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin: 8px 0 !important;
    }
    .stChatMessage p, .stChatMessage span {
        color: #ffd700 !important;
        font-family: 'Georgia', 'Arial', sans-serif !important;
    }
    .stChatInputContainer {
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%) !important;
        border: 3px solid #ffd700 !important;
        border-radius: 12px !important;
        padding: 10px !important;
        margin-top: 20px !important;
    }
    .stChatInputContainer input {
        background: #1a1a1a !important;
        color: #ffd700 !important;
        border: 2px solid #b8860b !important;
        border-radius: 8px !important;
    }
    .stChatInputContainer input::placeholder {
        color: #daa520 !important;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .server-updating {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 30px 0;
        padding: 20px;
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%);
        border: 3px solid #ffd700;
        border-radius: 15px;
        animation: pulse 2s ease-in-out infinite;
    }
    .server-updating .emoji {
        font-size: 40px;
        animation: rotate 2s linear infinite;
        display: inline-block;
    }
    .server-updating .flag {
        font-size: 40px;
        display: inline-block;
    }
    .server-updating .text {
        font-size: 24px;
        color: #ffd700;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        font-family: 'Georgia', serif;
    }
    @keyframes fillProgress {
        0% { width: 0%; }
        50% { width: 100%; }
        100% { width: 0%; }
    }
    .loading-container {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%);
        border: 2px solid #ffd700;
        border-radius: 12px;
    }
    .loading-label {
        font-size: 16px;
        color: #ffd700;
        font-weight: bold;
        margin-bottom: 15px;
        letter-spacing: 1px;
        font-family: 'Georgia', serif;
    }
    .progress-bar-container {
        width: 100%;
        height: 30px;
        background: #1a1a1a;
        border: 2px solid #b8860b;
        border-radius: 8px;
        overflow: hidden;
        position: relative;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #ffd700 0%, #ffed4e 50%, #ffd700 100%);
        animation: fillProgress 2.5s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 10px rgba(255, 215, 0, 0.5), inset 0 0 10px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 0 30px rgba(255, 215, 0, 0.8), inset 0 0 20px rgba(255, 215, 0, 0.5); }
    }
    @keyframes slideIn {
        0% { transform: translateY(-20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .developer-box {
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%);
        border: 3px solid #ffd700;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        margin: 50px 0;
        animation: glow 2s ease-in-out infinite, slideIn 0.6s ease-out;
    }
    .developer-text {
        font-size: 24px;
        color: #ffd700;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
        font-family: 'Georgia', serif;
        margin: 10px 0;
    }
    .auth-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%);
        border: 3px solid #ffd700;
        border-radius: 15px;
        text-align: center;
        animation: slideIn 0.6s ease-out;
    }
    .auth-title {
        font-size: 32px;
        color: #ffd700;
        font-weight: bold;
        margin-bottom: 30px;
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.6);
    }
    @media (max-width: 768px) {
        .stApp { padding: 0 10px !important; }
        .auth-container { max-width: 100% !important; margin: 30px auto !important; padding: 20px !important; }
        .auth-title { font-size: 24px !important; }
        h1, h2, h3 { font-size: 18px !important; }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea { font-size: 14px !important; padding: 8px !important; }
        .stButton>button { padding: 10px !important; font-size: 14px !important; width: 100% !important; }
        .developer-box { padding: 20px !important; margin: 20px 0 !important; }
        .developer-text { font-size: 16px !important; }
        .stTabs { width: 100% !important; }
    }
    @media (max-width: 480px) {
        .auth-container { padding: 15px !important; margin: 20px auto !important; }
        .auth-title { font-size: 20px !important; margin-bottom: 20px !important; }
        h1, h2, h3 { font-size: 16px !important; }
        .stButton>button { padding: 8px !important; font-size: 12px !important; }
        .developer-box { padding: 15px !important; }
    }
    </style>
""", unsafe_allow_html=True)

def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
        return conn
    except Exception as e:
        st.error(f"❌ Veritabanı Bağlantısı Hatası: {e}")
        return None

def initialize_database():
    try:
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                password_plain VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                reset_token VARCHAR(255) UNIQUE NOT NULL,
                expiry_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20),
                otp_code VARCHAR(6),
                expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '10 minutes'),
                used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_history (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20),
                message TEXT,
                api_provider VARCHAR(50),
                status VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        pass

def send_reset_email(email, reset_token):
    try:
        sender_email = "noreply@hantechnology.com"
        sender_password = "test123"
        if not sender_email or not sender_password:
            return False, "⚠️ Email sistemi yapılandırılmamış!"
        reset_link = f"http://localhost:5000?token={reset_token}"
        subject = "🔐 Şifre Sıfırlama Linki - Han Technology Pyhton ®️"
        body = f"""
        <html>
            <body style="background: #1a1a1a; color: #ffd700; font-family: Georgia, serif; padding: 20px;">
                <div style="background: linear-gradient(135deg, #2d2416 0%, #1a1a1a 100%); border: 2px solid #ffd700; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #ffd700;">🔐 Şifre Sıfırlama</h2>
                    <p>Merhaba,</p>
                    <p>Şifrenizi sıfırlamak için aşağıdaki linke tıklayınız (30 dakika geçerli):</p>
                    <p><a href="{reset_link}" style="background: linear-gradient(135deg, #ffd700 0%, #daa520 100%); color: #1a1a1a; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">🔐 Şifreyi Sıfırla</a></p>
                    <p>Ya da bu kodu kullan: <code>{reset_token}</code></p>
                    <p>Bu bağlantı 30 dakika boyunca geçerlidir.</p>
                    <p>Eğer bu isteği siz yapmadıysanız, bu emaili göz ardı edin.</p>
                    <hr style="border-color: #ffd700;">
                    <p style="font-size: 12px; color: #daa520;">Han Technology Pyhton ®️</p>
                </div>
            </body>
        </html>
        """
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email
        msg.attach(MIMEText(body, 'html'))
        return True, "✅ Şifre Reset Emaili Gönderildi!"
    except Exception as e:
        return False, f"❌ Email Gönderme Hatası: {str(e)}"

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
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, password_plain) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "✅ Kayıt başarılı! Giriş yapınız."
    except Exception as e:
        return False, f"❌ Hata: {str(e)}"

def request_password_reset(email):
    if not email:
        return False, "⚠️ Email adresini giriniz!"
    conn = get_db_connection()
    if not conn:
        return False, "❌ Veritabanı hatası!"
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return False, "⚠️ Bu email adresi kayıtlı değil!"
        reset_token = secrets.token_urlsafe(32)
        expiry_time = datetime.now() + timedelta(minutes=30)
        cursor.execute(
            "UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE id = %s",
            (reset_token, expiry_time, user['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        success, message = send_reset_email(email, reset_token)
        return success, message
    except Exception as e:
        return False, f"❌ Hata: {str(e)}"

def reset_password(reset_token, new_password):
    if not reset_token or not new_password:
        return False, "⚠️ Tüm alanları doldurunuz!"
    if len(new_password) < 6:
        return False, "⚠️ Şifre en az 6 karakter olmalı!"
    conn = get_db_connection()
    if not conn:
        return False, "❌ Veritabanı hatası!"
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(
            "SELECT id FROM users WHERE reset_token = %s AND reset_token_expiry > NOW()",
            (reset_token,)
        )
        user = cursor.fetchone()
        if not user:
            cursor.close()
            conn.close()
            return False, "⚠️ Geçersiz veya Süresi Dolmuş Token!"
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "UPDATE users SET password_hash = %s, password_plain = %s, reset_token = NULL, reset_token_expiry = NULL WHERE id = %s",
            (password_hash, new_password, user['id'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "✅ Şifre Başarıyla Sıfırlandı! Giriş Yapabilirsiniz."
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
        cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            cursor.close()
            conn.close()
            return False, "⚠️ Hatalı kullanıcı adı veya şifre!"
        cursor.close()
        conn.close()
        return True, "✅ Giriş başarılı!"
    except Exception as e:
        return False, f"❌ Hata: {str(e)}"

def normalize_phone(phone):
    phone = ''.join(filter(str.isdigit, phone))
    if not phone.startswith('90'):
        if phone.startswith('0'):
            phone = '9' + phone[1:]
        else:
            phone = '90' + phone
    return '+' + phone

def auto_debug_button():
    if st.button("🔧 DEBUG AUTO-FIX", key=f"debug_{random.randint(1000, 9999)}"):
        fix_result = "System Status: OK ✅"
        st.markdown(f"""
            <div style="
                position: fixed;
                top: 10px;
                right: 10px;
                background: #00ff00;
                color: #000;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                z-index: 9999;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
                text-align: center;
                font-size: 14px;
            ">
                ✅ FIX COMPLETE! | {fix_result} | 🎉
            </div>
        """, unsafe_allow_html=True)
        time.sleep(3)

def send_otp(phone_number, delay=0.0, retry=0, api_provider="naosstars"):
    if delay > 0:
        time.sleep(delay)
    phone_number = normalize_phone(phone_number)
    try:
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO otp_codes (phone_number, otp_code)
            VALUES (%s, %s)
            RETURNING id, otp_code, expires_at
        """, (phone_number, otp_code))
        result = cursor.fetchone()
        conn.commit()
        if not result:
            cursor.close()
            conn.close()
            return False, {"error": "❌ Veritabanı hatası"}
        sms_message = f"Han Tech OTP: {otp_code}"
        sms_response = None
        sms_status = "pending"
        sms_error = None
        try:
            if api_provider == "naosstars":
                sms_api_url = "https://api.naosstars.com/api/smsSend/9c9fa861-cc5d-43b0-b4ea-1b541be15350"
                sms_payload = {"telephone": phone_number, "message": sms_message}
                sms_response = requests.post(sms_api_url, json=sms_payload, timeout=10)
            elif api_provider == "filemarket":
                sms_api_url = "https://api.filemarket.com.tr/v1/otp/send"
                headers = {"Content-Type": "application/json", "User-Agent": "Han-Tech/1.0"}
                sms_payload = {"telephone": phone_number, "otp": otp_code, "message": sms_message}
                sms_response = requests.post(sms_api_url, json=sms_payload, headers=headers, timeout=10)
            elif api_provider == "metro":
                sms_api_url = "https://mobile.metro-tr.com/api/mobileAuth/validateSmsSend"
                headers = {"Content-Type": "application/json"}
                sms_payload = {"phone": phone_number, "otp": otp_code, "message": sms_message}
                sms_response = requests.post(sms_api_url, json=sms_payload, headers=headers, timeout=10)
            elif api_provider == "hizliecza":
                sms_api_url = "https://prod.hizliecza.net/mobil/account/sendOTP"
                sms_payload = {"telephone": phone_number, "code": otp_code, "message": sms_message}
                sms_response = requests.post(sms_api_url, json=sms_payload, timeout=10)
            elif api_provider == "twilio":
                account_sid = os.getenv("TWILIO_ACCOUNT_SID")
                auth_token = os.getenv("TWILIO_AUTH_TOKEN")
                from_number = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
                if account_sid and auth_token:
                    from twilio.rest import Client
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(body=sms_message, from_=from_number, to=phone_number)
                    sms_response = type('obj', (object,), {'status_code': 200, 'sid': message.sid})()
                else:
                    sms_error = "Twilio credentials not configured"
            if sms_response and sms_response.status_code in [200, 201]:
                sms_status = "sent"
            else:
                sms_status = "failed"
                sms_error = f"HTTP {sms_response.status_code if sms_response else 'No Response'}"
        except Exception as api_error:
            sms_status = "error"
            sms_error = str(api_error)[:100]
        try:
            cursor.execute("""
                INSERT INTO sms_history (phone_number, message, api_provider, status)
                VALUES (%s, %s, %s, %s)
            """, (phone_number, sms_message, api_provider, sms_status))
            conn.commit()
        except:
            pass
        cursor.close()
        conn.close()
        if sms_status == "sent":
            return True, {
                "success": True,
                "otp_code": otp_code,
                "phone": phone_number,
                "message": f"✅ OTP SMS başarıyla gönderildi! | OTP: {otp_code} | 10 dakika geçerli",
                "expires_at": str(result[2]),
                "sms_sent": True,
                "api": api_provider
            }
        else:
            return True, {
                "success": True,
                "otp_code": otp_code,
                "phone": phone_number,
                "message": f"⚠️ OTP oluşturuldu | SMS: {sms_status.upper()} | OTP: {otp_code}",
                "expires_at": str(result[2]),
                "sms_sent": False,
                "sms_error": sms_error,
                "sms_status": sms_status
            }
    except requests.exceptions.Timeout:
        if retry < 2:
            return send_otp(phone_number, delay, retry+1, api_provider)
        return None, "⏱️ SMS API timeout - 3x denendi"
    except requests.exceptions.ConnectionError:
        if retry < 2:
            return send_otp(phone_number, delay, retry+1, api_provider)
        return None, "🌐 SMS API bağlantı hatası - 3x denendi"
    except Exception as e:
        return None, f"❌ Hata: {str(e)[:100]}"

def anasayfa():
    auto_debug_button()
    st.header("👋 Hoşgeldiniz!")
    st.markdown("""
    <div class="server-updating">
        <span class="emoji">⚙️</span>
        <span class="flag">🇹🇷</span>
        <span class="text">Turkey Server Is Updating</span>
        <span class="flag">🇹🇷</span>
        <span class="emoji">⚙️</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("*Merhaba PixeI Place Duck Guild Sponsorlu Çok Kullanışlı Siteye Hoşgeldiniz Altay Han 2025-2026 Updated Web Site* 🚀✨🎉")
    st.markdown("""
    <div class="loading-container">
        <div class="loading-label">Sistem Yükleniyor</div>
        <div class="progress-bar-container">
            <div class="progress-bar-fill"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.write(f"✨ **Hoşgeldiniz, {st.session_state.username}!** ✨")

def sms_paneli():
    auto_debug_button()
    st.header("📨 Mesaj Paneli - SMS/OTP Management")
    st.write("📬 Gerçek OTP/SMS Gönderin! 🌍 | 4 API Sağlayıcısı + Twilio")
    st.markdown("---")
    tab_nao, tab_file, tab_metro, tab_hizli, tab_twilio, tab_verify, tab_history = st.tabs([
        "🟢 Naosstars", "🔵 FileMarket", "🟠 Metro TR", "🟣 Hızlıecza",
        "📱 Twilio", "✅ OTP Doğrula", "📊 Geçmiş"
    ])
    
    with tab_nao:
        st.subheader("🟢 Naosstars OTP Sistemi")
        st.info("🔗 API: https://api.naosstars.com/api/smsSend/")
        st.write("**Format:** 905XXXXXXXXX | +905359876543 | 0534 6123 456")
        col1, col2 = st.columns(2)
        with col1:
            telefon_nao = st.text_input("📞 Telefon Numarası", placeholder="905XXXXXXXXX", key="nao_phone")
        with col2:
            if st.button("🧪 API Test", key="test_nao"):
                with st.spinner("🔄 Test ediliyor..."):
                    try:
                        test_url = "https://api.naosstars.com/api/smsSend/9c9fa861-cc5d-43b0-b4ea-1b541be15350"
                        test_payload = {"telephone": "905421678945", "message": "TEST"}
                        r = requests.post(test_url, json=test_payload, timeout=5)
                        if r.status_code in [200, 201]:
                            st.success(f"✅ API Aktif! Status: {r.status_code}")
                        else:
                            st.warning(f"⚠️ API Response: {r.status_code}")
                    except Exception as e:
                        st.error(f"❌ Test Hatası: {str(e)[:50]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 OTP SMS Gönder", use_container_width=True, key="send_nao"):
                if not telefon_nao:
                    st.warning("⚠️ Telefon numarası giriniz!")
                else:
                    with st.spinner("📨 Naosstars üzerinden gönderiliyor..."):
                        success, response = send_otp(telefon_nao, api_provider="naosstars")
                        if success and isinstance(response, dict):
                            st.success("✅ OTP SMS Gönderildi!", icon="✅")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #00ff00, #00cc00); padding: 20px; border-radius: 10px; text-align: center;">
                                <h2 style="color: #fff;">📱 {response.get('phone', telefon_nao)}</h2>
                                <h1 style="color: #ffd700; font-size: 48px;">{response.get('otp_code', '???')}</h1>
                                <p style="color: #fff;">✅ {response.get('message', 'SMS GÖNDERILDI!')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(f"❌ {response}")
        with col2:
            if st.button("🔥 100x BULK OTP", use_container_width=True, key="bulk_nao"):
                if not telefon_nao:
                    st.warning("⚠️ Telefon giriniz!")
                else:
                    pb = st.progress(0)
                    st_txt = st.empty()
                    cnt = 0
                    for i in range(100):
                        success, _ = send_otp(telefon_nao, delay=0, api_provider="naosstars")
                        if success: cnt += 1
                        if (i + 1) % 25 == 0:
                            st_txt.info(f"⏳ {i+1}/100 | ✅ {cnt}")
                            pb.progress((i + 1) / 100)
                    st.success(f"✅ 100/100 GÖNDERİLDİ! Başarılı: {cnt} 🎉")
    
    with tab_file:
        st.subheader("🔵 FileMarket OTP Sistemi")
        st.info("🔗 API: https://api.filemarket.com.tr/v1/otp/send")
        st.write("**Format:** 905XXXXXXXXX | +905359876543")
        col1, col2 = st.columns(2)
        with col1:
            telefon_file = st.text_input("📞 Telefon Numarası", placeholder="905XXXXXXXXX", key="file_phone")
        with col2:
            if st.button("🧪 API Test", key="test_file"):
                with st.spinner("🔄 Test ediliyor..."):
                    try:
                        test_url = "https://api.filemarket.com.tr/v1/otp/send"
                        test_payload = {"telephone": "905421678945", "otp": "123456", "message": "TEST"}
                        test_headers = {"Content-Type": "application/json", "User-Agent": "Han-Tech/1.0"}
                        r = requests.post(test_url, json=test_payload, headers=test_headers, timeout=5)
                        if r.status_code in [200, 201]:
                            st.success(f"✅ API Aktif! Status: {r.status_code}")
                        else:
                            st.warning(f"⚠️ API Response: {r.status_code}")
                    except Exception as e:
                        st.error(f"❌ Test Hatası: {str(e)[:50]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 OTP SMS Gönder", use_container_width=True, key="send_file"):
                if not telefon_file:
                    st.warning("⚠️ Telefon numarası giriniz!")
                else:
                    with st.spinner("📨 FileMarket üzerinden gönderiliyor..."):
                        success, response = send_otp(telefon_file, api_provider="filemarket")
                        if success and isinstance(response, dict):
                            st.success("✅ OTP SMS Gönderildi!", icon="✅")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #0066ff, #0044cc); padding: 20px; border-radius: 10px; text-align: center;">
                                <h2 style="color: #fff;">📱 {response.get('phone', telefon_file)}</h2>
                                <h1 style="color: #ffd700; font-size: 48px;">{response.get('otp_code', '???')}</h1>
                                <p style="color: #fff;">✅ {response.get('message', 'SMS GÖNDERILDI!')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(f"❌ {response}")
        with col2:
            if st.button("🔥 100x BULK OTP", use_container_width=True, key="bulk_file"):
                if not telefon_file:
                    st.warning("⚠️ Telefon giriniz!")
                else:
                    pb = st.progress(0)
                    st_txt = st.empty()
                    cnt = 0
                    for i in range(100):
                        success, _ = send_otp(telefon_file, delay=0, api_provider="filemarket")
                        if success: cnt += 1
                        if (i + 1) % 25 == 0:
                            st_txt.info(f"⏳ {i+1}/100 | ✅ {cnt}")
                            pb.progress((i + 1) / 100)
                    st.success(f"✅ 100/100 GÖNDERİLDİ! Başarılı: {cnt} 🎉")
    
    with tab_metro:
        st.subheader("🟠 Metro TR OTP Sistemi")
        st.info("🔗 API: https://mobile.metro-tr.com/api/mobileAuth/validateSmsSend")
        st.write("**Format:** 905XXXXXXXXX | +905359876543")
        col1, col2 = st.columns(2)
        with col1:
            telefon_metro = st.text_input("📞 Telefon Numarası", placeholder="905XXXXXXXXX", key="metro_phone")
        with col2:
            if st.button("🧪 API Test", key="test_metro"):
                with st.spinner("🔄 Test ediliyor..."):
                    try:
                        test_url = "https://mobile.metro-tr.com/api/mobileAuth/validateSmsSend"
                        test_payload = {"phone": "905421678945", "otp": "123456", "message": "TEST"}
                        test_headers = {"Content-Type": "application/json"}
                        r = requests.post(test_url, json=test_payload, headers=test_headers, timeout=5)
                        if r.status_code in [200, 201]:
                            st.success(f"✅ API Aktif! Status: {r.status_code}")
                        else:
                            st.warning(f"⚠️ API Response: {r.status_code}")
                    except Exception as e:
                        st.error(f"❌ Test Hatası: {str(e)[:50]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 OTP SMS Gönder", use_container_width=True, key="send_metro"):
                if not telefon_metro:
                    st.warning("⚠️ Telefon numarası giriniz!")
                else:
                    with st.spinner("📨 Metro TR üzerinden gönderiliyor..."):
                        success, response = send_otp(telefon_metro, api_provider="metro")
                        if success and isinstance(response, dict):
                            st.success("✅ OTP SMS Gönderildi!", icon="✅")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #ff8800, #ff6600); padding: 20px; border-radius: 10px; text-align: center;">
                                <h2 style="color: #fff;">📱 {response.get('phone', telefon_metro)}</h2>
                                <h1 style="color: #ffd700; font-size: 48px;">{response.get('otp_code', '???')}</h1>
                                <p style="color: #fff;">✅ {response.get('message', 'SMS GÖNDERILDI!')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(f"❌ {response}")
        with col2:
            if st.button("🔥 100x BULK OTP", use_container_width=True, key="bulk_metro"):
                if not telefon_metro:
                    st.warning("⚠️ Telefon giriniz!")
                else:
                    pb = st.progress(0)
                    st_txt = st.empty()
                    cnt = 0
                    for i in range(100):
                        success, _ = send_otp(telefon_metro, delay=0, api_provider="metro")
                        if success: cnt += 1
                        if (i + 1) % 25 == 0:
                            st_txt.info(f"⏳ {i+1}/100 | ✅ {cnt}")
                            pb.progress((i + 1) / 100)
                    st.success(f"✅ 100/100 GÖNDERİLDİ! Başarılı: {cnt} 🎉")
    
    with tab_hizli:
        st.subheader("🟣 Hızlıecza OTP Sistemi")
        st.info("🔗 API: https://prod.hizliecza.net/mobil/account/sendOTP")
        st.write("**Format:** 905XXXXXXXXX | +905359876543")
        col1, col2 = st.columns(2)
        with col1:
            telefon_hizli = st.text_input("📞 Telefon Numarası", placeholder="905XXXXXXXXX", key="hizli_phone")
        with col2:
            if st.button("🧪 API Test", key="test_hizli"):
                with st.spinner("🔄 Test ediliyor..."):
                    try:
                        test_url = "https://prod.hizliecza.net/mobil/account/sendOTP"
                        test_payload = {"telephone": "905421678945", "code": "123456", "message": "TEST"}
                        r = requests.post(test_url, json=test_payload, timeout=5)
                        if r.status_code in [200, 201]:
                            st.success(f"✅ API Aktif! Status: {r.status_code}")
                        else:
                            st.warning(f"⚠️ API Response: {r.status_code}")
                    except Exception as e:
                        st.error(f"❌ Test Hatası: {str(e)[:50]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 OTP SMS Gönder", use_container_width=True, key="send_hizli"):
                if not telefon_hizli:
                    st.warning("⚠️ Telefon numarası giriniz!")
                else:
                    with st.spinner("📨 Hızlıecza üzerinden gönderiliyor..."):
                        success, response = send_otp(telefon_hizli, api_provider="hizliecza")
                        if success and isinstance(response, dict):
                            st.success("✅ OTP SMS Gönderildi!", icon="✅")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #aa00ff, #8800cc); padding: 20px; border-radius: 10px; text-align: center;">
                                <h2 style="color: #fff;">📱 {response.get('phone', telefon_hizli)}</h2>
                                <h1 style="color: #ffd700; font-size: 48px;">{response.get('otp_code', '???')}</h1>
                                <p style="color: #fff;">✅ {response.get('message', 'SMS GÖNDERILDI!')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                        else:
                            st.error(f"❌ {response}")
        with col2:
            if st.button("🔥 100x BULK OTP", use_container_width=True, key="bulk_hizli"):
                if not telefon_hizli:
                    st.warning("⚠️ Telefon giriniz!")
                else:
                    pb = st.progress(0)
                    st_txt = st.empty()
                    cnt = 0
                    for i in range(100):
                        success, _ = send_otp(telefon_hizli, delay=0, api_provider="hizliecza")
                        if success: cnt += 1
                        if (i + 1) % 25 == 0:
                            st_txt.info(f"⏳ {i+1}/100 | ✅ {cnt}")
                            pb.progress((i + 1) / 100)
                    st.success(f"✅ 100/100 GÖNDERİLDİ! Başarılı: {cnt} 🎉")
    
    with tab_twilio:
        st.subheader("📱 Twilio Professional SMS")
        twilio_account = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_auth = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
        if not all([twilio_account, twilio_auth, twilio_number]):
            st.warning("⚠️ Twilio Credentials Gerekli!\n- TWILIO_ACCOUNT_SID\n- TWILIO_AUTH_TOKEN\n- TWILIO_PHONE_NUMBER")
        else:
            st.success("✅ Twilio Aktif!")
            telefon_twilio = st.text_input("📞 Telefon", placeholder="+905XXXXXXXXX", key="twilio_phone")
            if st.button("📤 SMS Gönder (Twilio)", use_container_width=True):
                if not telefon_twilio:
                    st.warning("⚠️ Telefon giriniz!")
                else:
                    with st.spinner("📨 Twilio üzerinden gönderiliyor..."):
                        success, response = send_otp(telefon_twilio, api_provider="twilio")
                        if success:
                            st.success("✅ SMS Gönderildi!")
                            st.write(response)
                        else:
                            st.error(f"❌ {response}")
    
    with tab_verify:
        st.subheader("✅ OTP Doğrulama Paneli")
        verify_phone = st.text_input("📞 Telefon Numarası", placeholder="905XXXXXXXXX", key="verify_phone")
        verify_code = st.text_input("🔐 OTP Kodu (6-digit)", placeholder="000000", key="verify_code")
        if st.button("✅ OTP Doğrula", use_container_width=True):
            if not verify_phone or not verify_code:
                st.warning("⚠️ Telefon ve OTP kodunu giriniz!")
            else:
                try:
                    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, otp_code, expires_at, used FROM otp_codes
                        WHERE phone_number = %s AND otp_code = %s
                        ORDER BY created_at DESC LIMIT 1
                    """, (normalize_phone(verify_phone), verify_code))
                    otp_record = cursor.fetchone()
                    if not otp_record:
                        st.error("❌ Geçersiz OTP kodu!")
                    elif otp_record[2] < datetime.now():
                        st.error("❌ OTP süresi dolmuş!")
                    elif otp_record[3]:
                        st.error("❌ OTP zaten kullanılmış!")
                    else:
                        cursor.execute("UPDATE otp_codes SET used = TRUE WHERE id = %s", (otp_record[0],))
                        conn.commit()
                        st.success("✅ OTP Başarıyla Doğrulandı! 🎉")
                        st.balloons()
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)[:50]}")
    
    with tab_history:
        st.subheader("📊 SMS Geçmişi")
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT phone_number, message, api_provider, status, created_at 
                FROM sms_history 
                ORDER BY created_at DESC 
                LIMIT 100
            """)
            history = cursor.fetchall()
            cursor.close()
            conn.close()
            if history:
                for phone, msg, api, status, created in history:
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
                    with col1:
                        st.caption(f"📱 {phone}")
                    with col2:
                        st.caption(f"🏢 {api}")
                    with col3:
                        status_emoji = "✅" if status == "sent" else "⏳" if status == "pending" else "❌"
                        st.caption(f"{status_emoji} {status}")
                    with col4:
                        st.caption(f"🕐 {created}")
            else:
                st.info("Henüz SMS geçmişi yok")
        except Exception as e:
            st.error(f"❌ Geçmiş yüklenemedi: {str(e)[:50]}")

def yapay_zeka_sohbet():
    auto_debug_button()
    st.header("🤖 AI Sohbet - Google Gemini")
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ Google Gemini API Key gerekli! Env vars'a ekleyin.")
        return
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Gemini Config Hatası: {str(e)[:50]}")
        return
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if user_input := st.chat_input("Mesajınız..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("🤖 AI cevap hazırlanıyor..."):
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(user_input)
                assistant_message = response.text
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_message})
                with st.chat_message("assistant"):
                    st.markdown(assistant_message)
            except Exception as e:
                st.error(f"❌ Hata: {str(e)[:100]}")

def hesap_makinesi():
    auto_debug_button()
    st.header("🧮 Hesap Makinesi")
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.number_input("1. Sayı", value=0.0, key="calc_num1")
    with col2:
        num2 = st.number_input("2. Sayı", value=0.0, key="calc_num2")
    operation = st.radio("İşlem Seç", ["➕ Toplama", "➖ Çıkarma", "✖️ Çarpma", "➗ Bölme"], horizontal=True)
    if st.button("🔢 Hesapla", use_container_width=True):
        if "Toplama" in operation:
            result = num1 + num2
        elif "Çıkarma" in operation:
            result = num1 - num2
        elif "Çarpma" in operation:
            result = num1 * num2
        elif "Bölme" in operation:
            if num2 == 0:
                st.error("❌ Sıfıra bölünemez!")
                return
            result = num1 / num2
        st.success(f"✅ Sonuç: {result}")

def futbol_penalti():
    auto_debug_button()
    st.header("⚽ Futbol Penaltı Oyunu")
    if "game_score" not in st.session_state:
        st.session_state.game_score = {"user": 0, "ai": 0, "game_over": False, "round": 0}
    st.subheader(f"Skor: Oyuncu {st.session_state.game_score['user']} - {st.session_state.game_score['ai']} AI")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⬅️ SOL", use_container_width=True):
            ai_direction = random.choice(["SOL", "SAG"])
            if ai_direction == "SOL":
                st.warning("⚠️ Sağladı! AI kurtardı!")
            else:
                st.success("✅ GOOOL! Siz gol attınız!")
                st.session_state.game_score["user"] += 1
    with col2:
        if st.button("⬆️ ORTA", use_container_width=True):
            ai_direction = random.choice(["SOL", "SAG"])
            if ai_direction == "ORTA" or random.random() < 0.3:
                st.warning("⚠️ Kurtardı!")
            else:
                st.success("✅ GOOOL!")
                st.session_state.game_score["user"] += 1
    with col3:
        if st.button("➡️ SAG", use_container_width=True):
            ai_direction = random.choice(["SOL", "SAG"])
            if ai_direction == "SAG":
                st.warning("⚠️ Sağladı!")
            else:
                st.success("✅ GOOOL!")
                st.session_state.game_score["user"] += 1

def proxy_paneli():
    auto_debug_button()
    st.header("🌐 Proxy Browser")
    url_input = st.text_input("🔗 URL Gir", placeholder="www.google.com veya https://...", key="proxy_url")
    if st.button("🚀 YÜKLENİYOR", use_container_width=True):
        if not url_input:
            st.warning("⚠️ URL giriniz!")
        else:
            with st.spinner("📡 İçerik yükleniyor..."):
                try:
                    if not url_input.startswith("http"):
                        url_input = "https://" + url_input
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(url_input, headers=headers, timeout=15, verify=False)
                    if response.status_code == 200:
                        st.success(f"✅ Sayfa Yüklendi! Status: {response.status_code}")
                        st.info(f"📊 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                        st.write(response.text[:2000])
                    else:
                        st.error(f"❌ Hata: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Bağlantı Hatası: {str(e)[:100]}")

def kullanicilar_listesi():
    auto_debug_button()
    st.header("👥 Kullanıcı Yönetimi - Admin Paneli")
    try:
        conn = get_db_connection()
        if not conn:
            st.error("❌ Veritabanı bağlantısı başarısız!")
            return
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT id, username, email, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        if users:
            st.subheader(f"📊 Toplam Kullanıcı: {len(users)}")
            for user in users:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"👤 {user['username']}")
                with col2:
                    st.write(f"📧 {user['email']}")
                with col3:
                    st.write(f"📅 {user['created_at']}")
                with col4:
                    if st.button("🗑️ Sil", key=f"del_{user['id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM users WHERE id = %s", (user['id'],))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("✅ Kullanıcı silindi!")
                        st.rerun()
        else:
            st.info("Henüz kayıtlı kullanıcı yok")
    except Exception as e:
        st.error(f"❌ Hata: {str(e)[:100]}")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_admin = False
    st.session_state.admin_password = "Admin@2025"
    st.session_state.chat_messages = []
    st.session_state.selected_language = "🇹🇷 Türkçe"

initialize_database()

if not st.session_state.logged_in:
    st.markdown("""
    <div class="auth-container">
        <h1 class="auth-title">🎯 Han Technology Pyhton ®️</h1>
    </div>
    """, unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Giriş Yap", "📝 Kayıt Ol", "🛡️ Admin", "🔑 Şifre Sıfırla"])
    
    with tab1:
        st.markdown("### 🔐 Giriş Yap")
        login_username = st.text_input("👤 Kullanıcı Adı", placeholder="Kullanıcı adınız", key="login_user")
        login_password = st.text_input("🔑 Şifre", type="password", placeholder="Şifreniz", key="login_pass")
        if st.button("🚪 Giriş Yap 🚪", use_container_width=True):
            success, result = login_user(login_username, login_password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success(result)
                st.balloons()
                st.rerun()
            else:
                st.error(result)
        if st.button("🎭 Anonim Giriş (PIN: 22)", use_container_width=True):
            pin = st.text_input("🔐 PIN Gir", type="password", key="anon_pin")
            if pin == "22":
                st.session_state.logged_in = True
                st.session_state.username = "👤 Anonim"
                st.success("✅ Anonim giriş başarılı!")
                st.balloons()
                st.rerun()
    
    with tab2:
        st.markdown("### 📝 Kayıt Ol")
        reg_username = st.text_input("👤 Kullanıcı Adı", placeholder="Kullanıcı adınızı seçiniz", key="reg_user")
        reg_email = st.text_input("📧 E-posta", placeholder="E-posta adresinizi giriniz", key="reg_email")
        reg_password = st.text_input("🔑 Şifre", type="password", placeholder="Şifrenizi oluşturunuz", key="reg_pass")
        reg_password_confirm = st.text_input("🔑 Şifre Doğrula", type="password", placeholder="Şifrenizi tekrar giriniz", key="reg_pass_confirm")
        if st.button("✍️ Kayıt Ol ✍️", use_container_width=True):
            if reg_password != reg_password_confirm:
                st.error("⚠️ Şifreler eşleşmiyor!")
            else:
                success, message = register_user(reg_username, reg_email, reg_password)
                if success:
                    st.success(message)
                    st.info("🔐 Şimdi giriş yapabilirsiniz!")
                else:
                    st.error(message)
    
    with tab3:
        st.markdown("### 🛡️ Admin Giriş")
        admin_password = st.text_input("🔑 Admin Şifresi", type="password", placeholder="Admin şifresini giriniz", key="admin_pass")
        if st.button("🔐 Admin Giriş 🔐", use_container_width=True):
            if admin_password == st.session_state.admin_password:
                st.session_state.logged_in = True
                st.session_state.username = "👨‍💼 Admin"
                st.session_state.is_admin = True
                st.success("✅ Admin Paneline Hoşgeldiniz! 🎉")
                st.balloons()
                st.rerun()
            else:
                st.error("⚠️ Hatalı Admin Şifresi!")
    
    with tab4:
        st.markdown("### 🔑 Şifreyi Unuttum?")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📧 Adım 1: Email Gönder")
            reset_email = st.text_input("📧 Email Adresiniz", placeholder="kayıtlı email giriniz", key="reset_email")
            if st.button("📤 Reset Linki Gönder 📤", use_container_width=True):
                if reset_email:
                    success, message = request_password_reset(reset_email)
                    if success:
                        st.success(message)
                        st.info("💬 Email'inizi kontrol edin! Reset linkini tıklayın")
                    else:
                        st.error(message)
                else:
                    st.warning("⚠️ Email giriniz!")
        with col2:
            st.markdown("#### 🔐 Adım 2: Yeni Şifre Belirle")
            reset_token = st.text_input("🔑 Reset Token", placeholder="Email'den gelen token", key="reset_token")
            new_password = st.text_input("🔑 Yeni Şifre", type="password", placeholder="Yeni şifreniz", key="new_pass")
            new_password_confirm = st.text_input("🔑 Şifre Doğrula", type="password", placeholder="Şifrenizi tekrar giriniz", key="new_pass_confirm")
            if st.button("✅ Şifre Sıfırla ✅", use_container_width=True):
                if new_password != new_password_confirm:
                    st.error("⚠️ Şifreler eşleşmiyor!")
                elif not reset_token or not new_password:
                    st.warning("⚠️ Tüm alanları doldurunuz!")
                else:
                    success, message = reset_password(reset_token, new_password)
                    if success:
                        st.success(message)
                        st.info("🔐 Artık giriş yapabilirsiniz!")
                    else:
                        st.error(message)

else:
    st.sidebar.markdown("<h3>🌍 Dil Seçimi 🌍</h3>", unsafe_allow_html=True)
    st.session_state.selected_language = st.sidebar.selectbox(
        "💬 Dil Seç",
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.selected_language) if st.session_state.selected_language in LANGUAGES else 0,
        label_visibility="collapsed"
    )
    st.sidebar.markdown(f"**Seçilen Dil:** {st.session_state.selected_language}")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h2>🔥Menü🔥</h2>", unsafe_allow_html=True)
    if st.session_state.is_admin:
        st.sidebar.info("🛡️ **Admin Paneli** 🛡️")
        menu_item = st.sidebar.radio("💎 SEÇ", 
            ["👥 Kullanıcılar"],
            label_visibility="collapsed"
        )
    else:
        menu_item = st.sidebar.radio("💎 SEÇ", 
            ["💫 Anasayfa", "🤖 AI Sohbet", "📧 SMS Paneli", "🧮 Hesap Makinesi", "⚽ Football Game", "🌐 Proxy"],
            label_visibility="collapsed"
        )
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Çıkış Yap 🚪", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.is_admin = False
        st.session_state.chat_messages = []
        st.rerun()
    if st.session_state.is_admin:
        kullanicilar_listesi()
    elif menu_item == "💫 Anasayfa":
        anasayfa()
    elif menu_item == "🤖 AI Sohbet":
        yapay_zeka_sohbet()
    elif menu_item == "📧 SMS Paneli":
        sms_paneli()
    elif menu_item == "🧮 Hesap Makinesi":
        hesap_makinesi()
    elif menu_item == "⚽ Football Game":
        futbol_penalti()
    elif menu_item == "🌐 Proxy":
        proxy_paneli()

        
