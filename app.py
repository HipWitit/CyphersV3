import streamlit as st
import re
import os
import random
import hashlib  # <--- FIXED: The missing piece that caused the error!
import streamlit.components.v1 as components
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Cyfer Pro: Secret Language", layout="centered")

raw_pepper = st.secrets.get("MY_SECRET_PEPPER") or "default_fallback_spice_2026"
PEPPER = str(raw_pepper)
MOD = 127  # Prime modulus for 128x128 ASCII space

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

    /* Layout fixes for mobile button stacking */
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
        height: auto !important;     
        border: none !important;
        text-transform: uppercase;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        margin-top: 15px !important;
    }}

    /* Footer Button Styling */
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

# --- 2. THE 128x128 DYNAMIC ENGINE ---
EMOJI_MAP = {'1': '🦄', '2': '🍼', '3': '🩷', '4': '🧸', '5': '🎀', '6': '🍓', '7': '🌈', '8': '🌸', '9': '💕', '0': '🫐'}

def get_char_coord(char):
    """Maps any ASCII character to a coordinate pair (x, y)."""
    val = ord(char) % MOD
    return (val, (val * 7) % MOD)

def get_dynamic_sbox(kw):
    """Generates a key-dependent shuffle for the entire 127-character set."""
    seed_str = kw + PEPPER
    seed_hash = hashlib.sha256(seed_str.encode()).digest()
    rng = random.Random(seed_hash)
    sbox = list(range(MOD))
    rng.shuffle(sbox)
    inv_sbox = [sbox.index(i) for i in range(MOD)]
    return sbox, inv_sbox

def get_matrix_elements(key_string):
    """Derives Hill Cipher matrix values from the key."""
    salt = b"sweet_parity_salt_v3_128" 
    combined_input = key_string + PEPPER 
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=4, salt=salt, iterations=100000, backend=default_backend())
    a, b, c, d = list(kdf.derive(combined_input.encode()))
    return (a % 100 + 2, b % 100 + 1, c % 100 + 1, d % 100 + 2)

def apply_sweet_parity(val_str):
    """Adds candy/lollipop indicators for negative numbers in the moves."""
    def replacer(match):
        digit = match.group(2)
        return ('🍭' if int(digit) % 2 == 0 else '🍬') + digit
    return re.sub(r'(-)(\d)', replacer, val_str)

def modInverse(n, m=MOD):
    """Calculates the modular multiplicative inverse for decryption."""
    for x in range(1, m):
        if (((n % m) * (x % m)) % m == 1): return x
    return None

def clear_everything():
    for k in ["lips", "chem", "hint"]: st.session_state[k] = ""

# --- 3. UI LAYOUT ---
if os.path.exists("CYPHER.png"): st.image("CYPHER.png")
if os.path.exists("Lock Lips.png"): st.image("Lock Lips.png")

kw = st.text_input("Key", type="password", key="lips", placeholder="SECRET KEY").strip()
hint_text = st.text_input("Hint", key="hint", placeholder="KEY HINT (Optional)")

if os.path.exists("Kiss Chemistry.png"): st.image("Kiss Chemistry.png")
user_input = st.text_area("Message", height=120, key="chem", placeholder="YOUR MESSAGE")

output_placeholder = st.empty()
kiss_btn, tell_btn = st.button("KISS"), st.button("TELL")
st.button("DESTROY CHEMISTRY", on_click=clear_everything)

st.markdown('<div class="custom-footer">', unsafe_allow_html=True)
if os.path.exists("LPB.png"):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("LPB.png", use_container_width=True)
st.markdown('<div class="footer-text">CREATED BY</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. PROCESSING ---
if kw and (kiss_btn or tell_btn):
    a, b, c, d = get_matrix_elements(kw)
    det = (a * d - b * c) % MOD
    det_inv = modInverse(det)
    current_sbox, current_inv_sbox = get_dynamic_sbox(kw)
    
    if det_inv:
        if kiss_btn:
            points = []
            for char in user_input:
                x_raw, y_raw = get_char_coord(char)
                x, y = current_sbox[x_raw], current_sbox[y_raw]
                nx, ny = (a*x + b*y) % MOD, (c*x + d*y) % MOD
                points.append((nx, ny))
            
            if points:
                # Encode starting position
                hx = "".join(EMOJI_MAP.get(digit, digit) for digit in apply_sweet_parity(str(points[0][0])))
                hy = "".join(EMOJI_MAP.get(digit, digit) for digit in apply_sweet_parity(str(points[0][1])))
                header = f"{hx[::-1]},{hy[::-1]}"
                
                # Encode moves between letters
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
                    return chr(current_inv_sbox[ux_s])

                decoded = [resolve(curr_x, curr_y)]
                moves = re.findall(r"\(([^)]+)\)", m_part)
                for i, m in enumerate(moves):
                    dx_e, dy_e = m.split(",")
                    dx, dy = (e_to_m(dx_e[::-1]), e_to_m(dy_e[::-1])) if (i+1)%2==0 else (e_to_m(dx_e), e_to_m(dy_e))
                    curr_x, curr_y = curr_x + dx, curr_y + dy
                    decoded.append(resolve(curr_x, curr_y))
                
                output_placeholder.markdown(f'<div class="whisper-text">Cypher Whispers: {"".join(decoded)}</div>', unsafe_allow_html=True)
            except: st.error("Chemistry Error! Check your Key or Cipher string.")
    else:
        st.error("Matrix Error - This key results in a non-invertible matrix. Try a different key!")
