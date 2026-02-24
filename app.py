import streamlit as st
import re
import os
import random
import hashlib
import base64
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Cyfer Pro: Secret Language", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "default_fallback_spice_2026"
PEPPER = str(raw_pepper)
MOD = 127 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #DBDCFF !important; }}
    .main .block-container {{ padding-bottom: 150px !important; }}
    div[data-testid="stWidgetLabel"], label {{ display: none !important; }}

    /* TEXT INPUTS - Darker Purple Text for visibility */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    input::placeholder, textarea::placeholder {{
        background-color: #FEE2E9 !important;
        color: #7E60BF !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}

    .stProgress > div > div > div > div {{ background-color: #7E60BF !important; }}

    [data-testid="column"], [data-testid="stVerticalBlock"] > div {{ width: 100% !important; flex: 1 1 100% !important; }}
    .stButton, .stButton > button {{ width: 100% !important; display: block !important; }}

    /* ACTION BUTTONS - Deep Purple from your V4 request */
    div.stButton > button {{
        background-color: #7E60BF !important; 
        color: #FFD4E5 !important;
        border-radius: 15px !important;
        min-height: 100px !important; 
        border: none !important;
        text-transform: uppercase;
        box-shadow: 0px 6px 0px #5E448F;
        margin-top: 15px !important;
    }}

    div.stButton > button p {{
        font-size: 38px !important; 
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        text-align: center !important;
    }}

    /* DESTROY BUTTON - Stays lighter for contrast */
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button p {{ font-size: 24px !important; }}
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {{
        min-height: 70px !important;
        background-color: #B4A7D6 !important;
        box-shadow: 0px 4px 0px #8E7DB3;
    }}

    .result-box {{
        background-color: #FEE2E9; 
        color: #7E60BF;
        padding: 15px;
        border-radius: 10px;
        font-family: "Courier New", Courier, monospace !important;
        border: 2px solid #7E60BF;
        word-wrap: break-word;
        margin-top: 15px;
        font-weight: bold;
    }}

    .whisper-text {{
        color: #7E60BF;
        font-family: "Courier New", Courier, monospace !important;
        font-weight: bold;
        font-size: 26px;
        margin-top: 20px;
        border-top: 2px dashed #7E60BF;
        padding-top: 15px;
    }}

    .footer-text {{
        color: #7E60BF;
        font-family: "Courier New", Courier, monospace;
        font-size: 22px;
        font-weight: bold;
        margin-top: 15px;
        letter-spacing: 2px;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_fernet_sbox(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"stable_sbox_salt_v4", iterations=100000, backend=default_backend())
    seed = int.from_bytes(hashlib.sha256(kdf.derive((kw + PEPPER).encode())).digest(), 'big')
    rng = random.Random(seed)
    sbox = list(range(MOD)); rng.shuffle(sbox)
    return sbox, [sbox.index(i) for i in range(MOD)]

def get_matrix_elements(kw):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=b"matrix_salt_v4", iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive((kw + PEPPER).encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def apply_sweet_parity(val_str):
    return re.sub(r'(-)(\d)', lambda m: ('🍭' if int(m.group(2)) % 2 == 0 else '🍬') + m.group(2), val_str)

def modInverse(n, m=MOD):
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

def clear_everything():
    for k in ["lips", "chem", "hint"]: 
        if k in st.session_state: st.session_state[k] =
