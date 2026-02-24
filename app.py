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

    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button p {{ font-size: 24px !important; }}
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {{
        min-height: 70px !important;
        background-color: #B4A7D6 !important;
        box-shadow: 0px 4px 0px #8E7DB3;
    }}

    .result-box {{
        background-color: #FEE2E9; color: #7E60BF; padding: 15px;
        border-radius: 10px; font-family: "Courier New", Courier, monospace !important;
        border: 2px solid #7E60BF; word-wrap: break-word;
        margin-top: 15px; font-weight: bold; text-align: center;
    }}

    .whisper-text {{
        color: #7E60BF; font-family: "Courier New", Courier, monospace !important;
        font-weight: bold; font-size: 26px; margin-top: 20px;
        border-top: 2px dashed #7E60BF; padding-top: 15px; text-align: center;
    }}

    .footer-text {{
        color: #7E60BF; font-family: "Courier New", Courier, monospace;
        font-size: 22px; font-weight: bold; margin-top: 15px;
        letter-spacing: 2px; text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENGINE (V3 Logic) ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}
REV_MAP = {v: k for k, v in EMOJI_MAP.items()}

def to_emoji(val):
    return "".join(EMOJI_MAP.get(d, d) for d in str(val))

def from_emoji(s):
    res = "".join(REV_MAP[char] for char in s if char in REV_MAP)
    return int(res) if res else 0

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
        if k in st.session_state: 
            st.session_state[k] = ""

# --- 3. UI LAYOUT (Sacred Order) ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()

# Chemistry Level Progress
if kw:
    lvl = min(len(kw)/12.0, 1.0)
    st.write(f"🧪 **CHEMISTRY LEVEL:** {int(lvl*100)}%")
    st.progress(lvl)
else:
    st.write("🧪 **CHEMISTRY LEVEL:** 0%")
    st.progress(0.0)

hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

if os.path.exists("LPB.png"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("LPB.png")

st.markdown('<div class="footer-text">CREATED BY</div>', unsafe_allow_html=True)

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    sbox, inv_sbox = get_fernet_sbox(kw)
    ma, mb, mc, md = get_matrix_elements(kw)
    det = (ma*md - mb*mc)
    
    if kiss_btn:
        res = []
        for char in user_input:
            val = sbox[ord(char) % MOD]
            # V3 Coordinate logic
            x, y = (val, (val * 7) % MOD)
            x_new, y_new = (ma*x + mb*y), (mc*x + md*y)
            res.append(f"{apply_sweet_parity(to_emoji(x_new))}.{apply_sweet_parity(to_emoji(y_new))}")
        
        output_str = "  ".join(res)
        with output_placeholder.container():
            st.markdown(f'<div class="result-box">{output_str}</div>', unsafe_allow_html=True)
            components.html(f"""<button onclick="navigator.share({{title:'Secret',text:`{output_str}\\n\\nHint: {hint_text}`}})" style="background-color:#7E60BF; color:#FFD4E5; font-weight:bold; border-radius:15px; min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; text-transform:uppercase;">SHARE ✨</button>""", height=100)

    if tell_btn:
        try:
            inv_det = modInverse(det % MOD, MOD)
            if inv_det is None: 
                st.error("Matrix Determinant not invertible! Try a different key.")
                st.stop()
            
            # Inverse Matrix elements
            da, db, dc, dd = (md * inv_det) % MOD, (-mb * inv_det) % MOD, (-mc * inv_det) % MOD, (ma * inv_det) % MOD
            
            decoded = []
            for pair in user_input.split("  "):
                parts = pair.split(".")
                # Strip parity and convert back from emojis
                x_enc = from_emoji(re.sub(r'[🍭🍬]', '-', parts[0]))
                y_enc = from_emoji(re.sub(r'[🍭🍬]', '-', parts[1]))
                
                # Reverse matrix: X = (da*x' + db*y') mod MOD
                x_orig = (da * x_enc + db * y_enc) % MOD
                decoded.append(chr(inv_sbox[int(x_orig)]))
            
            final_msg = "".join(decoded)
            output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {final_msg}</div>', unsafe_allow_html=True)
        except:
            st.error("Chemistry Error! Key or Message mismatch.")
