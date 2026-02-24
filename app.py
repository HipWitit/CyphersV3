import streamlit as st
import re
import os
import random
import hashlib
import base64
import streamlit.components.v1 as components
from cryptography.fernet import Fernet
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
        color: #B4A7D6 !important; 
        border: 2px solid #B4A7D6 !important;
        font-family: "Courier New", Courier, monospace !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }}

    .stProgress > div > div > div > div {{ background-color: #B4A7D6 !important; }}

    [data-testid="column"], [data-testid="stVerticalBlock"] > div {{ width: 100% !important; flex: 1 1 100% !important; }}
    .stButton, .stButton > button {{ width: 100% !important; display: block !important; }}

    div.stButton > button p {{
        font-size: 38px !important; 
        font-weight: 800 !important;
        line-height: 1.1 !important;
        margin: 0 !important;
        text-align: center !important;
    }}

    div.stButton > button {{
        background-color: #B4A7D6 !important; 
        color: #FFD4E5 !important;
        border-radius: 15px !important;
        min-height: 100px !important; 
        border: none !important;
        text-transform: uppercase;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-top: 15px !important;
    }}

    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button p {{ font-size: 24px !important; }}
    div[data-testid="stVerticalBlock"] > div:last-child .stButton > button {{
        min-height: 70px !important;
        background-color: #D1C4E9 !important;
    }}

    .result-box {{
        background-color: #FEE2E9; 
        color: #B4A7D6;
        padding: 15px;
        border-radius: 10px;
        font-family: "Courier New", Courier, monospace !important;
        border: 2px solid #B4A7D6;
        word-wrap: break-word;
        margin-top: 15px;
        font-weight: bold;
    }}

    .whisper-text {{
        color: #B4A7D6;
        font-family: "Courier New", Courier, monospace !important;
        font-weight: bold;
        font-size: 26px;
        margin-top: 20px;
        border-top: 2px dashed #B4A7D6;
        padding-top: 15px;
    }}

    .custom-footer {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        margin-top: 60px;
    }}
    
    .footer-text {{
        color: #B4A7D6;
        font-family: "Courier New", Courier, monospace;
        font-size: 22px;
        font-weight: bold;
        margin-top: 15px;
        letter-spacing: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE CRYPTO LOGIC ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_fernet_sbox(kw):
    """Generates a robust key-dependent S-box using Fernet and explicit Int seeding."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"fernet_sbox_v1", iterations=100000, backend=default_backend())
    key_bytes = kdf.derive((kw + PEPPER).encode())
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    f = Fernet(fernet_key)
    
    # Deterministic hash generation
    seed_bytes = hashlib.sha256(f.encrypt(b"SBOX_SEED")).digest()
    
    # SAFE CONVERSION: Explicitly convert bytes to a large integer
    seed_int = int.from_bytes(seed_bytes, byteorder='big')
    
    rng = random.Random(seed_int)
    sbox = list(range(MOD))
    rng.shuffle(sbox)
    inv_sbox = [sbox.index(i) for i in range(MOD)]
    return sbox, inv_sbox

def get_matrix_elements(kw):
    salt = b"matrix_salt_v3" 
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=salt, iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive((kw + PEPPER).encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def apply_sweet_parity(val_str):
    def replacer(match):
        digit = match.group(2)
        return ('🍭' if int(digit) % 2 == 0 else '🍬') + digit
    return re.sub(r'(-)(\d)', replacer, val_str)

def modInverse(n, m=MOD):
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

def clear_everything():
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()

# Chemistry Meter Logic
if kw:
    has_digit = any(char.isdigit() for char in kw)
    has_special = any(not char.isalnum() for char in kw)
    base_score = len(kw) / 12.0
    bonus = (0.1 if has_digit else 0) + (0.1 if has_special else 0)
    strength = min(base_score + bonus, 1.0)
    st.write(f"🧪 **CHEMISTRY LEVEL:** {int(strength*100)}%")
    st.progress(strength)
else:
    st.write("🧪 **CHEMISTRY LEVEL:** 0%")
    st.progress(0.0)

hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

# Footer
st.markdown('<div class="custom-footer">', unsafe_allow_html=True)
if os.path.exists("LPB.png"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("LPB.png", use_container_width=True)
st.markdown('<div class="footer-text">CREATED BY</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. THE CORE FUNCTIONS ---
if kw and (kiss_btn or tell_btn):
    a, b, c, d = get_matrix_elements(kw)
    det = (a * d - b * c) % MOD
    det_inv = modInverse(det)
    sbox, inv_sbox = get_fernet_sbox(kw)
    
    if det_inv:
        if kiss_btn:
            points = []
            for char in user_input:
                x_raw, y_raw = get_char_coord(char)
                x, y = sbox[x_raw], sbox[y_raw]
                nx, ny = (a*x + b*y) % MOD, (c*x + d*y) % MOD
                points.append((nx, ny))
            
            if points:
                hx = "".join(EMOJI_MAP.get(digit, digit) for digit in apply_sweet_parity(str(points[0][0])))
                hy = "".join(EMOJI_MAP.get(digit, digit) for digit in apply_sweet_parity(str(points[0][1])))
                header = f"{hx[::-1]},{hy[::-1]}"
                
                m_list = []
                for i in range(len(points)-1):
                    dx_v, dy_v = points[i+1][0]-points[i][0], points[i+1][1]-points[i][1]
                    dx = "".join(EMOJI_MAP.get(d, d) for d in apply_sweet_parity(str(dx_v)))
                    dy = "".join(EMOJI_MAP.get(d, d) for d in apply_sweet_parity(str(dy_v)))
                    m_list.append(f"({dx[::-1]},{dy[::-1]})" if (i+1)%2==0 else f"({dx},{dy})")
                
                res = f"{header} | MOVES: {' '.join(m_list)}"
                with output_placeholder.container():
                    st.markdown(f'<div class="result-box">{res}</div>', unsafe_allow_html=True)
                    components.html(f"""<button onclick="navigator.share({{title:'Secret',text:`{res}\\n\\nHint: {hint_text}`}})" style="background-color:#B4A7D6; color:#FFD4E5; font-weight:bold; border-radius:20px; min-height:80px; width:100%; cursor:pointer; font-size: 28px; border:none; text-transform:uppercase;">SHARE ✨</button>""", height=100)

        if tell_btn:
            try:
                clean_in = user_input.split("Hint:")[0].strip()
                h_part, m_part = clean_in.split("|")
                rev_map = {v: k for k, v in EMOJI_MAP.items()}
                
                def e_to_m(s):
                    s = "".join(rev_map.get(ch, ch) for ch in s)
                    return int(s.replace('🍭', '-').replace('🍬', '-'))

                hx_e, hy_e = h_part.strip().split(",")
                curr_x, curr_y = e_to_m(hx_e[::-1]), e_to_m(hy_e[::-1])
                
                inv_a, inv_b = (d * det_inv) % MOD, (-b * det_inv) % MOD
                inv_c, inv_d = (-c * det_inv) % MOD, (a * det_inv) % MOD
                
                def resolve(cx, cy):
                    ux_s, uy_s = (inv_a * cx + inv_b * cy) % MOD, (inv_c * cx + inv_d * cy) % MOD
                    return chr(inv_sbox[ux_s])

                decoded = [resolve(curr_x, curr_y)]
                moves = re.findall(r"\(([^)]+)\)", m_part)
                for i, m in enumerate(moves):
                    dx_e, dy_e = m.split(",")
                    dx, dy = (e_to_m(dx_e[::-1]), e_to_m(dy_e[::-1])) if (i+1)%2==0 else (e_to_m(dx_e), e_to_m(dy_e))
                    curr_x, curr_y = curr_x + dx, curr_y + dy
                    decoded.append(resolve(curr_x, curr_y))
                
                output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {"".join(decoded)}</div>', unsafe_allow_html=True)
            except: st.error("Chemistry Error! The key or message is mismatched.")
    else: st.error("Key Matrix is unstable. Try a different key!")
