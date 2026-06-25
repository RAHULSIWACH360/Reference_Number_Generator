import streamlit as st
import pandas as pd
import json
import os
import base64
import zipfile
from datetime import datetime
import io

# ── Config ──────────────────────────────────────────────────────────────────────
LOG_FILE      = "reference_log.json"
INCOMING_FILE = "incoming_log.json"
UPLOADS_DIR   = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

st.set_page_config(
    page_title="Correspondence Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CSS  — only changes vs uploaded file:
#   • Selectbox background-color #778899 → #2D5A54  (removes "slate" colour
#     that showed as dark black text on Yandex/Russian Chrome)
#   • Added -webkit-text-fill-color: #FFFFFF on every selectbox child
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background: linear-gradient(135deg, #F0FAF8 0%, #EEF6EA 45%, #FDF1EB 100%) !important; }
.block-container { padding-top: 1.8rem !important; padding-bottom: 2rem !important; }

/* ══ SIDEBAR — autofill / Yandex fix ══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3A7A72 0%, #56A097 50%, #7ECFC0 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.12) !important;
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] h2 { color:#FFFFFF !important; font-size:15px !important; font-weight:600 !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stTextInput label {
    color: rgba(255,255,255,0.80) !important; font-size:11px !important;
    text-transform: uppercase !important; letter-spacing:0.06em !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] input:hover,
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] input:active,
section[data-testid="stSidebar"] input:not(:placeholder-shown) {
    background: #2E6B64 !important; background-color: #2E6B64 !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
    border-radius: 8px !important; caret-color: #FFFFFF !important;
    box-shadow: none !important; -webkit-box-shadow: none !important; outline: none !important;
}
section[data-testid="stSidebar"] input:-webkit-autofill,
section[data-testid="stSidebar"] input:-webkit-autofill:hover,
section[data-testid="stSidebar"] input:-webkit-autofill:focus,
section[data-testid="stSidebar"] input:-webkit-autofill:active {
    -webkit-box-shadow: 0 0 0 1000px #2E6B64 inset !important;
    box-shadow: 0 0 0 1000px #2E6B64 inset !important;
    -webkit-text-fill-color: #FFFFFF !important; color: #FFFFFF !important;
    background-color: #2E6B64 !important; border: 1.5px solid rgba(255,255,255,0.35) !important;
    caret-color: #FFFFFF !important; transition: background-color 9999s ease-in-out 0s !important;
}
section[data-testid="stSidebar"] input::placeholder { color: rgba(255,255,255,0.45) !important; }
section[data-testid="stSidebar"] p { color: rgba(255,255,255,0.65) !important; font-size:11px !important; }

/* ══ METRIC CARDS ══ */
.metric-row { display:flex; gap:14px; margin-bottom:24px; }
.metric-card {
    flex:1; background:rgba(255,255,255,0.88); backdrop-filter:blur(16px);
    border-radius:18px; padding:18px 20px; border:1px solid rgba(255,255,255,.55);
    position:relative; overflow:hidden; box-shadow:0 8px 25px rgba(126,207,192,.20);
}
.metric-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; }
.metric-card.blue::before   { background:linear-gradient(90deg,#7ECFC0,#5BA897); }
.metric-card.teal::before   { background:linear-gradient(90deg,#B5D5A8,#8BBF7C); }
.metric-card.amber::before  { background:linear-gradient(90deg,#F5C9B0,#E8967A); }
.metric-card.purple::before { background:linear-gradient(90deg,#F5A09A,#F47F7F); }
.metric-num { font-size:30px; font-weight:700; color:#2D5A54; line-height:1; margin-bottom:4px; }
.metric-num.mono { font-size:12px; font-family:'JetBrains Mono',monospace; color:#3D8B80; padding-top:6px; font-weight:700; }
.metric-lbl { font-size:11px; color:#7A9E9A; font-weight:500; text-transform:uppercase; letter-spacing:0.05em; }
.metric-icon { position:absolute; top:16px; right:16px; width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:17px; }
.metric-card.blue   .metric-icon { background:#E8F7F5; }
.metric-card.teal   .metric-icon { background:#EEF6EA; }
.metric-card.amber  .metric-icon { background:#FDF1EB; }
.metric-card.purple .metric-icon { background:#FDE8E7; }

/* ══ SECTION HEADERS ══ */
.sec-hdr { font-size:12px; font-weight:700; color:#2D5A54; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
.sec-hdr::after { content:''; flex:1; height:1px; background:#7ECFC0; opacity:0.4; }

/* ══ INPUT LABELS ══ */
.stTextInput label, .stSelectbox label {
    font-size:11px !important; font-weight:600 !important; color:#4A7A74 !important;
    text-transform:uppercase !important; letter-spacing:0.07em !important;
}
.stCheckbox label span {
    font-size:13px !important; font-weight:500 !important; color:#3D8B80 !important;
    text-transform:none !important; letter-spacing:normal !important;
}
.stCheckbox { margin-top:6px !important; }

/* ══ TEXT INPUTS ══ */
.stTextInput input,
.stTextInput input:hover,
.stTextInput input:focus,
.stTextInput input:not(:placeholder-shown) {
    border-radius:9px !important; border:1.5px solid #C5E3DF !important;
    background:#F5FAFA !important; background-color:#F5FAFA !important;
    color:#2D5A54 !important; -webkit-text-fill-color:#2D5A54 !important;
    font-size:14px !important; font-family:'Inter',sans-serif !important;
    padding:10px 14px !important; transition:border-color 0.2s,box-shadow 0.2s !important;
}
.stTextInput input:focus {
    border-color:#7ECFC0 !important;
    box-shadow:0 0 0 3px rgba(126,207,192,0.22) !important;
    background:#FFFFFF !important; background-color:#FFFFFF !important;
}
.stTextInput input:-webkit-autofill,
.stTextInput input:-webkit-autofill:hover,
.stTextInput input:-webkit-autofill:focus {
    -webkit-box-shadow:0 0 0 1000px #F5FAFA inset !important;
    -webkit-text-fill-color:#2D5A54 !important;
    border:1.5px solid #C5E3DF !important;
}
.stTextInput input::placeholder { color:#A8C8C4 !important; }

/* ══ SELECTBOX — BUG FIX: removed #778899, use solid #2D5A54 everywhere ══
   Root cause: #778899 (slate-grey) has poor contrast and Yandex renders it
   as near-black background with black text. Solid dark-teal #2D5A54 is
   opaque and always renders with white text correctly. */
div[data-baseweb="select"] > div:first-child {
    border-radius:9px !important; border:1.5px solid #9CA3AF !important;
    background:#6B7280 !important; background-color:#6B7280 !important;
    cursor:pointer !important;
}
div[data-baseweb="select"] input {
    pointer-events:none !important; caret-color:transparent !important;
    cursor:pointer !important; -webkit-user-select:none !important; user-select:none !important;
    background:transparent !important; background-color:transparent !important;
    border:none !important; box-shadow:none !important;
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}
div[data-baseweb="select"] [class*="singleValue"] {
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; font-size:14px !important;
}
div[data-baseweb="select"] [class*="placeholder"] {
    color:rgba(255,255,255,0.55) !important; -webkit-text-fill-color:rgba(255,255,255,0.55) !important;
}
div[data-baseweb="select"] svg { fill:#FFFFFF !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
    background:#6B7280 !important; background-color:#6B7280 !important;
    border:1px solid #9CA3AF !important; border-radius:10px !important; overflow:hidden !important;
}
div[data-baseweb="menu"] li {
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
    font-size:14px !important; background:transparent !important; background-color:transparent !important;
}
div[data-baseweb="menu"] li:hover,
div[data-baseweb="menu"] li[aria-selected="true"] {
    background:rgba(255,255,255,0.18) !important; background-color:rgba(255,255,255,0.18) !important;
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
}

/* ══ CUSTOM PROJECT BOX ══ */
.custom-project-box {
    background:rgba(255,255,255,.65); backdrop-filter:blur(12px);
    border:1.5px dashed #7ECFC0; border-radius:12px; padding:16px; margin-top:12px;
}

/* ══ GENERATE BUTTON — dark default, RED hover ══ */
.stButton > button,
div[data-testid="stForm"] .stButton > button,
[data-testid="stFormSubmitButton"] > button,
button[kind="primaryFormSubmit"],
button[kind="primary"] {
    background:#1A2928 !important; background-image:none !important;
    border:none !important; border-radius:11px !important;
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important;
    font-size:15px !important; font-weight:600 !important;
    padding:14px !important; width:100% !important; letter-spacing:0.02em !important;
    box-shadow:0 4px 14px rgba(0,0,0,0.30) !important;
    transition:background 0.18s ease,box-shadow 0.18s ease,transform 0.12s ease !important;
    font-family:'Inter',sans-serif !important; cursor:pointer !important;
}
.stButton > button:hover,
div[data-testid="stForm"] .stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primaryFormSubmit"]:hover,
button[kind="primary"]:hover {
    background:#DC2626 !important; background-color:#DC2626 !important; background-image:none !important;
    box-shadow:0 6px 22px rgba(220,38,38,0.55) !important; transform:translateY(-1px) !important;
    color:#FFFFFF !important; -webkit-text-fill-color:#FFFFFF !important; border:none !important;
}
.stButton > button:active,
div[data-testid="stForm"] .stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active {
    background:#991B1B !important; background-image:none !important;
    transform:translateY(0) !important; color:#FFFFFF !important; border:none !important;
}
.stButton > button:focus,
div[data-testid="stForm"] .stButton > button:focus,
[data-testid="stFormSubmitButton"] > button:focus {
    background:#DC2626 !important; background-image:none !important; outline:none !important;
    box-shadow:0 0 0 3px rgba(220,38,38,0.35) !important;
    color:#FFFFFF !important; border:none !important;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,0.7) !important; border-radius:12px !important;
    padding:4px !important; gap:4px !important; border:1px solid #C5E3DF !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius:9px !important; font-size:14px !important; font-weight:600 !important;
    color:#4A7A74 !important; padding:8px 20px !important; transition:all 0.15s !important;
}
.stTabs [aria-selected="true"] { background:#2D5A54 !important; color:#FFFFFF !important; }
.stTabs [data-baseweb="tab-border"] { display:none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:16px !important; }

/* ══ RESULT CARD ══ */
.result-card {
    background:linear-gradient(135deg,#2D5A54 0%,#3D8B80 45%,#7ECFC0 100%);
    border-radius:16px; padding:24px 28px; color:white; margin-top:20px;
    position:relative; overflow:hidden; box-shadow:0 8px 28px rgba(45,90,84,0.30);
}
.result-card::after { content:''; position:absolute; top:-40px; right:-40px; width:180px; height:180px; border-radius:50%; background:rgba(255,255,255,0.06); }
.result-eyebrow { font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#B5E8E0; margin-bottom:10px; }
.result-ref { font-size:24px; font-weight:700; font-family:'JetBrains Mono',monospace; letter-spacing:3px; background:rgba(255,255,255,0.14); display:inline-block; padding:10px 20px; border-radius:10px; border:1px solid rgba(255,255,255,0.22); margin-bottom:16px; word-break:break-all; }
.result-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:14px; }
.result-field { background:rgba(255,255,255,0.10); border-radius:9px; padding:10px 14px; border:1px solid rgba(255,255,255,0.12); }
.result-field-label { font-size:10px; color:#B5E8E0; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:3px; }
.result-field-value { font-size:13px; color:#FFFFFF; font-weight:500; }
.priority-urgent { color:#F47F7F !important; }
.priority-high   { color:#F5A09A !important; }
.priority-normal { color:#B5D5A8 !important; }
.priority-low    { color:#F5C9B0 !important; }

/* ══ INCOMING CARD ══ */
.incoming-card {
    background:linear-gradient(135deg,#2A4A5A 0%,#3A6B80 50%,#7ECFC0 100%);
    border-radius:16px; padding:20px 24px; color:white; margin-top:12px;
    box-shadow:0 6px 20px rgba(42,74,90,0.28);
}
.incoming-eyebrow { font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.12em; color:#A8D8E8; margin-bottom:8px; }
.incoming-ref { font-size:20px; font-weight:700; font-family:'JetBrains Mono',monospace; letter-spacing:2px; word-break:break-all; margin-bottom:12px; }
.in-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
.in-field { background:rgba(255,255,255,0.09); border-radius:8px; padding:9px 12px; border:1px solid rgba(255,255,255,0.10); }
.in-field-label { font-size:10px; color:#A8D8E8; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:2px; }
.in-field-value { font-size:13px; color:#FFFFFF; font-weight:500; }

/* ══ UPLOAD BOX ══ */
.upload-box {
    background:rgba(255,255,255,0.75); border:1.5px dashed #7ECFC0;
    border-radius:12px; padding:14px 16px; margin-top:12px;
}
.upload-box-title { font-size:12px; font-weight:700; color:#2D5A54; text-transform:uppercase; letter-spacing:0.07em; margin-bottom:8px; }

/* ══ DATAFRAME ══ */
.stDataFrame { border-radius:12px; overflow:hidden; border:1px solid #C5E3DF !important; }

/* ══ DOWNLOAD BUTTONS ══ */
.stDownloadButton > button {
    border-radius:9px !important; border:1.5px solid #C5E3DF !important;
    background:#F5FAFA !important; color:#4A7A74 !important;
    font-size:13px !important; font-weight:500 !important; transition:all 0.15s !important;
}
.stDownloadButton > button:hover { border-color:#7ECFC0 !important; color:#2D5A54 !important; background:#E8F7F5 !important; }

hr { border-color:#C5E3DF !important; margin:18px 0 !important; }
h1 { color:#2D5A54 !important; font-weight:700 !important; font-size:24px !important; }
h2, h3 { color:#2D5A54 !important; }
.stAlert { border-radius:10px !important; }
.stCode { border-radius:10px !important; }
code { font-family:'JetBrains Mono',monospace !important; }
.footer { text-align:center; font-size:11px; color:#7A9E9A; padding:16px 0 4px; border-top:1px solid #C5E3DF; margin-top:24px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {"entries": [], "counters": {}}

def save_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_incoming():
    if os.path.exists(INCOMING_FILE):
        with open(INCOMING_FILE, "r") as f:
            return json.load(f)
    return {"entries": []}

def save_incoming(data):
    with open(INCOMING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def next_serial(data, key):
    counters = data.get("counters", {})
    current  = counters.get(key, 0) + 1
    data["counters"][key] = current
    return current

def format_ref(company, contract, year, doc_type, serial):
    return f"{company}/{contract}/{doc_type}-{year}-{str(serial).zfill(4)}"

def safe_ref_folder(ref):
    """Convert a ref number to a safe folder name."""
    return ref.replace("/", "_").replace("\\", "_")

def save_uploaded_file(ref, uploaded_file):
    """Save an uploaded file linked to a reference number. Returns saved path."""
    folder = os.path.join(UPLOADS_DIR, safe_ref_folder(ref))
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def list_uploaded_files(ref):
    """Return list of filenames uploaded for a given reference number."""
    folder = os.path.join(UPLOADS_DIR, safe_ref_folder(ref))
    if os.path.isdir(folder):
        return sorted(os.listdir(folder))
    return []

def get_file_bytes(ref, filename):
    """Read a single uploaded file and return its bytes."""
    path = os.path.join(UPLOADS_DIR, safe_ref_folder(ref), filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return None

def zip_all_uploads_for_ref(ref):
    """Return a ZIP bytes object containing all uploads for a ref."""
    folder = os.path.join(UPLOADS_DIR, safe_ref_folder(ref))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if os.path.isdir(folder):
            for fname in os.listdir(folder):
                fpath = os.path.join(folder, fname)
                zf.write(fpath, fname)
    buf.seek(0)
    return buf.getvalue()

def make_excel(df_dict):
    """
    df_dict: {"SheetName": dataframe, ...}
    Returns bytes of an xlsx workbook.
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    return buf.getvalue()

def make_pdf_bytes(title, df):
    """
    Simple PDF using only stdlib + reportlab-free approach via HTML→bytes.
    We use a pure-python approach: write an HTML table and encode as UTF-8,
    then offer it as .html download clearly labelled as PDF-ready.
    (reportlab is not always available on Streamlit Cloud free tier.)
    Falls back to a well-formatted HTML file the user can print-to-PDF.
    """
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td style='padding:6px 10px;border:1px solid #C5E3DF;font-size:11px;color:#2D5A54;'>{v}</td>" for v in row.values)
        rows_html += f"<tr>{cells}</tr>"
    headers = "".join(f"<th style='background:#2D5A54;color:white;padding:8px 10px;font-size:11px;border:1px solid #1E4A44;'>{c}</th>" for c in df.columns)
    html = f"""<!DOCTYPE html><html><head><meta charset='UTF-8'/>
<title>{title}</title>
<style>
  body{{font-family:Arial,sans-serif;margin:24px;}}
  h2{{color:#2D5A54;}} table{{border-collapse:collapse;width:100%;}}
  @media print{{body{{margin:0;}}}}
</style></head><body>
<h2>{title}</h2>
<p style='font-size:11px;color:#7A9E9A;'>Generated: {datetime.now().strftime('%d %b %Y %H:%M')} &nbsp;|&nbsp; To save as PDF: File → Print → Save as PDF</p>
<table><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table>
</body></html>"""
    return html.encode("utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**Company & Contract**")
    company  = st.text_input("Company code",    value="RFSS",       max_chars=10, key="sb_company").strip().upper()
    contract = st.text_input("Contract number", value="4224000135", key="sb_contract").strip()
    st.markdown("---")
    st.markdown('<span style="font-size:11px;opacity:0.7;">RFSS Correspondence Management System · v4.0</span>', unsafe_allow_html=True)

st.markdown("""
<script>
(function(){
    function fix(){
        document.querySelectorAll('section[data-testid="stSidebar"] input').forEach(function(el){
            el.setAttribute('autocomplete','off'); el.setAttribute('translate','no');
        });
    }
    fix(); setTimeout(fix,800); setTimeout(fix,2000);
})();
</script>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HEADER & METRICS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("# 📋 Correspondence Management System")
st.markdown('<p style="color:#5A9E98;font-size:14px;margin-top:-8px;margin-bottom:20px;">Generate, track and export outgoing & incoming document references for project correspondence.</p>', unsafe_allow_html=True)

data             = load_log()
entries          = data.get("entries", [])
incoming_data    = load_incoming()
incoming_entries = incoming_data.get("entries", [])

total   = len(entries)
today_c = sum(1 for e in entries if e.get("date","").startswith(datetime.now().strftime("%Y-%m-%d")))
in_total = len(incoming_entries)
last    = entries[-1]["ref_number"] if entries else "—"

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card blue"><div class="metric-icon">📤</div><div class="metric-num">{total}</div><div class="metric-lbl">Outgoing refs</div></div>
  <div class="metric-card teal"><div class="metric-icon">📥</div><div class="metric-num">{in_total}</div><div class="metric-lbl">Incoming logged</div></div>
  <div class="metric-card amber"><div class="metric-icon">🗓️</div><div class="metric-num">{today_c}</div><div class="metric-lbl">Generated today</div></div>
  <div class="metric-card purple"><div class="metric-icon">🔖</div><div class="metric-num mono">{last}</div><div class="metric-lbl">Last outgoing</div></div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED OPTION LISTS
# ═══════════════════════════════════════════════════════════════════════════════
doc_types = {
    "LTR":"LTR — Letter",    "RPT":"RPT — Report",
    "INV":"INV — Invoice",   "QCP":"QCP — Quality Plan",
    "TDR":"TDR — Technical Document", "NCR":"NCR — Non-Conformance Report",
    "MOM":"MOM — Minutes of Meeting", "NTC":"NTC — Notice",
    "COR":"COR — Correspondence",     "SUB":"SUB — Submittal",
}
dept_options = {
    "QC":"QC — Quality Control", "PR":"PR — Procurement",
    "PM":"PM — Project Management", "ENG":"ENG — Engineering",
    "FIN":"FIN — Finance", "LEG":"LEG — Legal",
}
project_options = {
    "ED":"ED — El Dabaa (Egypt)",    "KK":"KK — Kudankulam (India)",
    "AK":"AK — Akkuyu (Turkey)",     "BL":"BL — Bushehr (Iran)",
    "RO":"RO — Rooppur (Bangladesh)","TN":"TN — Tianwan (China)",
    "HAN":"HAN — Hanhikivi (Finland)",
}
priority_options = {
    "Normal":"🟢  Normal — Standard turnaround",
    "High":  "🟡  High — Needs prompt attention",
    "Urgent":"🔴  Urgent — Action required immediately",
    "Low":   "⚪  Low — No rush",
}


# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_out, tab_in, tab_log = st.tabs(["📤  Outgoing — Generate", "📥  Incoming — Log", "📊  Full Log & Export"])


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 1 — OUTGOING                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
with tab_out:
    col_gen, col_log_preview = st.columns([1.05, 1.95], gap="large")

    with col_gen:
        st.markdown('<div class="sec-hdr">Generate reference number</div>', unsafe_allow_html=True)

        country = st.selectbox("Select project", options=list(project_options.keys()),
            format_func=lambda x: project_options[x], key="out_project")
        project_display = project_options[country]

        use_custom = st.checkbox("✏️ Use custom project code", key="use_custom_out")
        custom_proj = ""
        custom_name = ""
        if use_custom:
            st.markdown('<div class="custom-project-box">', unsafe_allow_html=True)
            cp1, cp2 = st.columns(2)
            with cp1:
                custom_proj = st.text_input("Custom code (max 5)", max_chars=5,
                    placeholder="MYPRJ", key="cp_code").strip().upper()
            with cp2:
                custom_name = st.text_input("Project full name",
                    placeholder="My Project", key="cp_name").strip()
            st.markdown('</div>', unsafe_allow_html=True)
            country         = custom_proj if custom_proj else "PROJ"
            project_display = f"{country} — {custom_name}" if custom_name else country

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("gen_form", clear_on_submit=False):
            generated_by = st.text_input("Your full name ✱", placeholder="e.g. Rahul Siwach", key="gen_name")
            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                doc_type_sel = st.selectbox("Document type ✱", options=list(doc_types.keys()),
                    format_func=lambda x: doc_types[x], key="gen_doctype")
            with c2:
                dept = st.selectbox("Department", options=list(dept_options.keys()),
                    format_func=lambda x: dept_options[x], key="gen_dept")

            to_party = st.text_input("Addressed to — recipient ✱",
                placeholder="e.g. TPBS Engineering GmbH", key="gen_to")
            subject  = st.text_input("Subject / brief description",
                placeholder="e.g. Quality plan approval request", key="gen_subj")

            in_refs  = ["None"] + [e.get("incoming_ref","") for e in incoming_entries if e.get("incoming_ref","")]
            reply_to = st.selectbox("Reply to incoming letter (optional)", options=in_refs,
                key="gen_reply", help="Link this outgoing letter to a logged incoming letter.")

            st.divider()
            priority_key = st.selectbox("Priority level", options=list(priority_options.keys()),
                format_func=lambda x: priority_options[x], key="gen_priority")
            year = st.text_input("Reference year", value=str(datetime.now().year),
                max_chars=4, key="gen_year")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("⚡  Generate Reference Number", use_container_width=True)

        if submitted:
            errors = []
            if not generated_by.strip(): errors.append("**Your full name** is required.")
            if not to_party.strip():     errors.append("**Recipient** is required.")
            for err in errors: st.error(err)

            if not errors:
                counter_key = f"{company}_{contract}_{doc_type_sel}_{year}"
                serial_num  = next_serial(data, counter_key)
                ref         = format_ref(company, contract, year, doc_type_sel, serial_num)
                now         = datetime.now()
                p_cls       = {"Urgent":"priority-urgent","High":"priority-high",
                               "Normal":"priority-normal","Low":"priority-low"}.get(priority_key,"priority-normal")
                entry = {
                    "ref_number":    ref,
                    "generated_by":  generated_by.strip(),
                    "to_party":      to_party.strip(),
                    "subject":       subject.strip(),
                    "document_type": doc_types[doc_type_sel],
                    "department":    dept_options[dept],
                    "project":       project_display,
                    "priority":      priority_key,
                    "reply_to":      reply_to if reply_to != "None" else "",
                    "date":          now.strftime("%Y-%m-%d"),
                    "time":          now.strftime("%H:%M:%S"),
                    "datetime":      now.strftime("%Y-%m-%d %H:%M:%S"),
                    "serial":        serial_num,
                }
                data["entries"].append(entry)
                save_log(data)
                if reply_to != "None":
                    for ie in incoming_entries:
                        if ie.get("incoming_ref") == reply_to:
                            ie["replied_with"] = ref
                    save_incoming(incoming_data)

                subj_row  = f'<div class="result-field" style="grid-column:1/-1;"><div class="result-field-label">Subject</div><div class="result-field-value">{subject.strip()}</div></div>' if subject.strip() else ""
                reply_row = f'<div class="result-field" style="grid-column:1/-1;"><div class="result-field-label">Reply to incoming</div><div class="result-field-value">{reply_to}</div></div>' if reply_to != "None" else ""

                st.markdown(f"""
                <div class="result-card">
                  <div class="result-eyebrow">✓ Reference number generated successfully</div>
                  <div class="result-ref">{ref}</div>
                  <div class="result-grid">
                    <div class="result-field"><div class="result-field-label">Generated by</div><div class="result-field-value">{generated_by.strip()}</div></div>
                    <div class="result-field"><div class="result-field-label">Addressed to</div><div class="result-field-value">{to_party.strip()}</div></div>
                    <div class="result-field"><div class="result-field-label">Project</div><div class="result-field-value">{project_display}</div></div>
                    <div class="result-field"><div class="result-field-label">Document type</div><div class="result-field-value">{doc_types[doc_type_sel]}</div></div>
                    <div class="result-field"><div class="result-field-label">Department</div><div class="result-field-value">{dept_options[dept]}</div></div>
                    <div class="result-field"><div class="result-field-label">Priority</div><div class="result-field-value {p_cls}">{priority_key}</div></div>
                    <div class="result-field"><div class="result-field-label">Date & time</div><div class="result-field-value">{now.strftime("%d %b %Y, %H:%M")}</div></div>
                    <div class="result-field"><div class="result-field-label">Serial</div><div class="result-field-value">#{serial_num:04d}</div></div>
                    {subj_row}{reply_row}
                  </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Copy reference number:**")
                st.code(ref, language=None)

                # ── Upload documents for this new reference ──────────────────
                st.markdown('<div class="upload-box"><div class="upload-box-title">📎 Attach documents to this reference</div>', unsafe_allow_html=True)
                out_uploads = st.file_uploader(
                    f"Upload files for {ref}",
                    accept_multiple_files=True,
                    key=f"upload_new_{ref}",
                    label_visibility="collapsed"
                )
                if out_uploads:
                    for uf in out_uploads:
                        save_uploaded_file(ref, uf)
                    st.success(f"✅ {len(out_uploads)} file(s) attached to {ref}")
                st.markdown('</div>', unsafe_allow_html=True)
                st.rerun()

    # ── RIGHT: Outgoing log preview ──────────────────────────────────────────
    with col_log_preview:
        st.markdown('<div class="sec-hdr">Recent outgoing references</div>', unsafe_allow_html=True)

        data    = load_log()
        entries = data.get("entries", [])

        fc1, fc2, fc3 = st.columns(3)
        with fc1: search_out = st.text_input("🔍 Search", placeholder="ref, name…", key="s_out")
        with fc2:
            all_users = ["All"] + sorted(set(e.get("generated_by","") for e in entries if e.get("generated_by","")))
            fu        = st.selectbox("Filter by user", all_users, key="fu_out")
        with fc3:
            all_types = ["All"] + sorted(set(e.get("document_type","") for e in entries if e.get("document_type","")))
            ft        = st.selectbox("Filter by type", all_types, key="ft_out")

        filt = entries.copy()
        if search_out:
            s = search_out.lower()
            filt = [e for e in filt if s in e.get("ref_number","").lower()
                    or s in e.get("generated_by","").lower()
                    or s in e.get("to_party","").lower()
                    or s in e.get("subject","").lower()]
        if fu != "All": filt = [e for e in filt if e.get("generated_by","") == fu]
        if ft != "All": filt = [e for e in filt if e.get("document_type","") == ft]

        filt_rev = list(reversed(filt))
        for e in filt_rev:
            e.setdefault("project","—")
            e.setdefault("reply_to","")

        if filt_rev:
            # Add attachment count column
            for e in filt_rev:
                e["attachments"] = len(list_uploaded_files(e.get("ref_number","")))

            df_out = pd.DataFrame(filt_rev)
            cols_needed = ["ref_number","document_type","project","generated_by",
                           "to_party","subject","priority","reply_to","attachments","date","time","department"]
            for c in cols_needed:
                if c not in df_out.columns: df_out[c] = ""
            df_out = df_out[cols_needed]
            df_out.columns = ["Reference #","Doc Type","Project","Generated By",
                               "Addressed To","Subject","Priority","Reply To",
                               "📎 Files","Date","Time","Department"]
            st.dataframe(df_out, use_container_width=True, height=380,
                column_config={
                    "Reference #": st.column_config.TextColumn(width="medium"),
                    "Doc Type":    st.column_config.TextColumn(width="small"),
                    "Priority":    st.column_config.TextColumn(width="small"),
                    "📎 Files":    st.column_config.NumberColumn(width="small"),
                    "Date":        st.column_config.DateColumn(width="small", format="DD MMM YYYY"),
                    "Time":        st.column_config.TextColumn(width="small"),
                    "Subject":     st.column_config.TextColumn(width="large"),
                    "Reply To":    st.column_config.TextColumn(width="medium"),
                })

            # ── Upload files to an existing reference ────────────────────────
            st.markdown("**📎 Attach / view files for an existing reference:**")
            all_out_refs = [e.get("ref_number","") for e in filt_rev if e.get("ref_number","")]
            sel_ref = st.selectbox("Select reference", ["— choose —"] + all_out_refs, key="sel_attach_out")
            if sel_ref != "— choose —":
                up_col, dl_col = st.columns(2)
                with up_col:
                    new_files = st.file_uploader(f"Upload to {sel_ref}",
                        accept_multiple_files=True, key=f"ul_{sel_ref}")
                    if new_files:
                        for uf in new_files:
                            save_uploaded_file(sel_ref, uf)
                        st.success(f"✅ {len(new_files)} file(s) saved")
                        st.rerun()

                with dl_col:
                    existing = list_uploaded_files(sel_ref)
                    if existing:
                        st.markdown(f"**Attached files ({len(existing)}):**")
                        for fname in existing:
                            fbytes = get_file_bytes(sel_ref, fname)
                            if fbytes:
                                st.download_button(f"⬇️ {fname}", fbytes,
                                    file_name=fname, key=f"dl_{sel_ref}_{fname}")
                        # Download all as ZIP
                        zip_bytes = zip_all_uploads_for_ref(sel_ref)
                        st.download_button("📦 Download all as ZIP", zip_bytes,
                            file_name=f"{safe_ref_folder(sel_ref)}_docs.zip",
                            mime="application/zip", key=f"zip_{sel_ref}")
                    else:
                        st.info("No files attached yet.", icon="📁")

            st.markdown("<br>", unsafe_allow_html=True)
            ex1, ex2, ex3 = st.columns(3)
            df_exp = df_out.copy()
            with ex1:
                csv = df_exp.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Excel", make_excel({"Outgoing": df_exp}),
                    file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with ex2:
                pdf_bytes = make_pdf_bytes("Outgoing References", df_exp)
                st.download_button("⬇️ PDF (print-ready HTML)", pdf_bytes,
                    file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html", use_container_width=True)
            with ex3:
                st.download_button("⬇️ CSV", df_exp.to_csv(index=False).encode("utf-8"),
                    file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True)
        else:
            st.info("No outgoing entries match the current filter.", icon="ℹ️")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 2 — INCOMING                                                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
with tab_in:
    col_in_form, col_in_log = st.columns([1.05, 1.95], gap="large")

    with col_in_form:
        st.markdown('<div class="sec-hdr">Log incoming letter</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:13px;color:#5A9E98;margin-bottom:16px;">Record a letter you <strong>received</strong>. You can later link an outgoing reply to it.</p>', unsafe_allow_html=True)

        with st.form("incoming_form", clear_on_submit=True):
            in_ref  = st.text_input("Incoming reference number ✱",
                placeholder="e.g. TPBS/ED/LTR-2026-0042",
                help="The reference number printed on the received letter.")
            in_from = st.text_input("From — sender company / person ✱",
                placeholder="e.g. TPBS Engineering GmbH")
            in_subj = st.text_input("Subject ✱",
                placeholder="e.g. Request for quality plan submission")

            d1, d2 = st.columns(2)
            with d1:
                in_letter_date   = st.text_input("Letter date",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    help="Date printed on the received letter (YYYY-MM-DD).")
            with d2:
                in_received_date = st.text_input("Date received",
                    value=datetime.now().strftime("%Y-%m-%d"),
                    help="Date you actually received / registered it (YYYY-MM-DD).")

            in_proj  = st.selectbox("Project", options=list(project_options.keys()),
                format_func=lambda x: project_options[x], key="in_project")
            in_notes = st.text_input("Notes / action required",
                placeholder="e.g. Reply required by 30 Jun 2026")

            in_submitted = st.form_submit_button("📥  Log Incoming Letter", use_container_width=True)

        if in_submitted:
            in_errors = []
            if not in_ref.strip():  in_errors.append("**Incoming reference number** is required.")
            if not in_from.strip(): in_errors.append("**Sender** is required.")
            if not in_subj.strip(): in_errors.append("**Subject** is required.")
            for err in in_errors: st.error(err)

            if not in_errors:
                now = datetime.now()
                in_entry = {
                    "incoming_ref":  in_ref.strip(),
                    "from_company":  in_from.strip(),
                    "subject":       in_subj.strip(),
                    "letter_date":   in_letter_date.strip(),
                    "received_date": in_received_date.strip(),
                    "project":       project_options[in_proj],
                    "notes":         in_notes.strip(),
                    "replied_with":  "",
                    "logged_at":     now.strftime("%Y-%m-%d %H:%M:%S"),
                }
                incoming_data["entries"].append(in_entry)
                save_incoming(incoming_data)

                st.markdown(f"""
                <div class="incoming-card">
                  <div class="incoming-eyebrow">✓ Incoming letter logged</div>
                  <div class="incoming-ref">{in_ref.strip()}</div>
                  <div class="in-grid">
                    <div class="in-field"><div class="in-field-label">From</div><div class="in-field-value">{in_from.strip()}</div></div>
                    <div class="in-field"><div class="in-field-label">Project</div><div class="in-field-value">{project_options[in_proj]}</div></div>
                    <div class="in-field"><div class="in-field-label">Letter date</div><div class="in-field-value">{in_letter_date.strip()}</div></div>
                    <div class="in-field"><div class="in-field-label">Received date</div><div class="in-field-value">{in_received_date.strip()}</div></div>
                    <div class="in-field" style="grid-column:1/-1;"><div class="in-field-label">Subject</div><div class="in-field-value">{in_subj.strip()}</div></div>
                    {'<div class="in-field" style="grid-column:1/-1;"><div class="in-field-label">Notes</div><div class="in-field-value">' + in_notes.strip() + '</div></div>' if in_notes.strip() else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Upload docs right after logging ──────────────────────────
                st.markdown('<div class="upload-box"><div class="upload-box-title">📎 Attach documents to this incoming letter</div>', unsafe_allow_html=True)
                in_uploads = st.file_uploader(
                    f"Upload files for {in_ref.strip()}",
                    accept_multiple_files=True,
                    key=f"upload_in_{in_ref.strip()}",
                    label_visibility="collapsed"
                )
                if in_uploads:
                    for uf in in_uploads:
                        save_uploaded_file(in_ref.strip(), uf)
                    st.success(f"✅ {len(in_uploads)} file(s) attached")
                st.markdown('</div>', unsafe_allow_html=True)
                st.rerun()

    with col_in_log:
        st.markdown('<div class="sec-hdr">Incoming letters log</div>', unsafe_allow_html=True)

        incoming_data    = load_incoming()
        incoming_entries = incoming_data.get("entries", [])

        si1, si2 = st.columns(2)
        with si1: search_in = st.text_input("🔍 Search incoming", placeholder="ref, sender…", key="s_in")
        with si2:
            in_status = st.selectbox("Status", ["All","Awaiting reply","Replied"], key="in_status")

        in_filt = incoming_entries.copy()
        if search_in:
            s = search_in.lower()
            in_filt = [e for e in in_filt if
                       s in e.get("incoming_ref","").lower() or
                       s in e.get("from_company","").lower() or
                       s in e.get("subject","").lower()]
        if in_status == "Awaiting reply": in_filt = [e for e in in_filt if not e.get("replied_with","")]
        elif in_status == "Replied":      in_filt = [e for e in in_filt if e.get("replied_with","")]

        in_filt_rev = list(reversed(in_filt))
        for e in in_filt_rev:
            e["attachments"] = len(list_uploaded_files(e.get("incoming_ref","")))

        if in_filt_rev:
            df_in = pd.DataFrame(in_filt_rev)
            in_cols = ["incoming_ref","from_company","subject","letter_date",
                       "received_date","project","replied_with","attachments","notes"]
            for c in in_cols:
                if c not in df_in.columns: df_in[c] = ""
            df_in = df_in[in_cols]
            df_in.columns = ["Incoming Ref #","From","Subject","Letter Date",
                              "Received Date","Project","Replied With","📎 Files","Notes"]
            st.dataframe(df_in, use_container_width=True, height=340,
                column_config={
                    "Incoming Ref #": st.column_config.TextColumn(width="medium"),
                    "From":           st.column_config.TextColumn(width="medium"),
                    "Subject":        st.column_config.TextColumn(width="large"),
                    "Replied With":   st.column_config.TextColumn(width="medium"),
                    "📎 Files":       st.column_config.NumberColumn(width="small"),
                })

            # ── Attach / download for existing incoming ref ──────────────────
            st.markdown("**📎 Attach / view files for an incoming letter:**")
            all_in_refs = [e.get("incoming_ref","") for e in in_filt_rev if e.get("incoming_ref","")]
            sel_in_ref  = st.selectbox("Select incoming ref", ["— choose —"] + all_in_refs, key="sel_attach_in")
            if sel_in_ref != "— choose —":
                iu_col, id_col = st.columns(2)
                with iu_col:
                    new_in_files = st.file_uploader(f"Upload to {sel_in_ref}",
                        accept_multiple_files=True, key=f"ul_in_{sel_in_ref}")
                    if new_in_files:
                        for uf in new_in_files:
                            save_uploaded_file(sel_in_ref, uf)
                        st.success(f"✅ {len(new_in_files)} file(s) saved")
                        st.rerun()
                with id_col:
                    ex_in = list_uploaded_files(sel_in_ref)
                    if ex_in:
                        st.markdown(f"**Attached files ({len(ex_in)}):**")
                        for fname in ex_in:
                            fbytes = get_file_bytes(sel_in_ref, fname)
                            if fbytes:
                                st.download_button(f"⬇️ {fname}", fbytes,
                                    file_name=fname, key=f"dl_in_{sel_in_ref}_{fname}")
                        zip_in = zip_all_uploads_for_ref(sel_in_ref)
                        st.download_button("📦 Download all as ZIP", zip_in,
                            file_name=f"{safe_ref_folder(sel_in_ref)}_docs.zip",
                            mime="application/zip", key=f"zip_in_{sel_in_ref}")
                    else:
                        st.info("No files attached yet.", icon="📁")

            st.markdown("<br>", unsafe_allow_html=True)
            ix1, ix2, ix3 = st.columns(3)
            with ix1:
                st.download_button("⬇️ Excel", make_excel({"Incoming": df_in}),
                    file_name=f"incoming_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with ix2:
                st.download_button("⬇️ PDF (print-ready HTML)", make_pdf_bytes("Incoming Letters", df_in),
                    file_name=f"incoming_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html", use_container_width=True)
            with ix3:
                st.download_button("⬇️ CSV", df_in.to_csv(index=False).encode("utf-8"),
                    file_name=f"incoming_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True)
        else:
            st.info("No incoming letters logged yet. Use the form on the left.", icon="ℹ️")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║  TAB 3 — FULL LOG & EXPORT                                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
with tab_log:
    st.markdown('<div class="sec-hdr">Full log & export</div>', unsafe_allow_html=True)

    log_mode = st.radio("View mode", ["Outgoing","Incoming","Combined (both sheets)"],
                        horizontal=True, key="log_mode")

    if "fullscreen_log" not in st.session_state:
        st.session_state["fullscreen_log"] = False
    fs_label = "🔲 Exit fullscreen" if st.session_state["fullscreen_log"] else "⛶  Fullscreen table"
    if st.button(fs_label, key="fs_toggle"):
        st.session_state["fullscreen_log"] = not st.session_state["fullscreen_log"]

    tbl_height = 700 if st.session_state["fullscreen_log"] else 460
    if st.session_state["fullscreen_log"]:
        st.markdown("""<style>
        .block-container{max-width:100% !important;padding-left:1rem !important;padding-right:1rem !important;}
        section[data-testid="stSidebar"]{display:none !important;}
        </style>""", unsafe_allow_html=True)

    data             = load_log()
    entries          = data.get("entries", [])
    incoming_data    = load_incoming()
    incoming_entries = incoming_data.get("entries", [])

    fs1, fs2 = st.columns(2)
    with fs1: full_search = st.text_input("🔍 Search all", key="full_search")
    with fs2: full_proj   = st.selectbox("Filter by project",
        ["All"] + sorted(set(e.get("project","") for e in entries + incoming_entries if e.get("project",""))),
        key="full_proj")

    out_rows = entries.copy()
    for e in out_rows:
        e.setdefault("reply_to","")
        e["attachments"] = len(list_uploaded_files(e.get("ref_number","")))
    if full_search:
        s = full_search.lower()
        out_rows = [e for e in out_rows if s in json.dumps(e).lower()]
    if full_proj != "All":
        out_rows = [e for e in out_rows if full_proj in e.get("project","")]

    in_rows = incoming_entries.copy()
    for e in in_rows:
        e["attachments"] = len(list_uploaded_files(e.get("incoming_ref","")))
    if full_search:
        s = full_search.lower()
        in_rows = [e for e in in_rows if s in json.dumps(e).lower()]
    if full_proj != "All":
        in_rows = [e for e in in_rows if full_proj in e.get("project","")]

    o_cols2 = ["ref_number","document_type","project","generated_by",
               "to_party","subject","priority","reply_to","attachments","date","time","department"]
    i_cols2 = ["incoming_ref","from_company","subject","letter_date",
               "received_date","project","replied_with","attachments","notes"]

    df_exp_out = pd.DataFrame()
    df_exp_in  = pd.DataFrame()

    if log_mode in ["Outgoing","Combined (both sheets)"]:
        st.markdown("### 📤 Outgoing References")
        if out_rows:
            df_o = pd.DataFrame(list(reversed(out_rows)))
            for c in o_cols2:
                if c not in df_o.columns: df_o[c] = ""
            df_o = df_o[o_cols2]
            df_o.columns = ["Reference #","Doc Type","Project","Generated By",
                             "Addressed To","Subject","Priority","Reply To","📎 Files","Date","Time","Department"]
            df_exp_out = df_o.copy()
            st.dataframe(df_o, use_container_width=True, height=tbl_height,
                column_config={
                    "Reference #": st.column_config.TextColumn(width="medium"),
                    "Subject":     st.column_config.TextColumn(width="large"),
                    "📎 Files":    st.column_config.NumberColumn(width="small"),
                    "Date":        st.column_config.DateColumn(width="small", format="DD MMM YYYY"),
                })
        else:
            st.info("No outgoing entries.", icon="ℹ️")

    if log_mode in ["Incoming","Combined (both sheets)"]:
        st.markdown("### 📥 Incoming Letters")
        if in_rows:
            df_i = pd.DataFrame(list(reversed(in_rows)))
            for c in i_cols2:
                if c not in df_i.columns: df_i[c] = ""
            df_i = df_i[i_cols2]
            df_i.columns = ["Incoming Ref #","From","Subject","Letter Date",
                             "Received Date","Project","Replied With","📎 Files","Notes"]
            df_exp_in = df_i.copy()
            st.dataframe(df_i, use_container_width=True, height=tbl_height,
                column_config={
                    "Incoming Ref #": st.column_config.TextColumn(width="medium"),
                    "Subject":        st.column_config.TextColumn(width="large"),
                    "Replied With":   st.column_config.TextColumn(width="medium"),
                    "📎 Files":       st.column_config.NumberColumn(width="small"),
                })
        else:
            st.info("No incoming entries.", icon="ℹ️")

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
    '<h4 style="color:#3D8B80; margin-bottom:12px;">📥 Export options</h4>',
    unsafe_allow_html=True
    )

    ex1, ex2, ex3, ex4 = st.columns(4)

    with ex1:
        # Combined Excel — 2 sheets
        sheets = {}
        if not df_exp_out.empty: sheets["Outgoing"]  = df_exp_out
        if not df_exp_in.empty:  sheets["Incoming"]  = df_exp_in
        if sheets:
            st.download_button("⬇️ Combined Excel (2 sheets)", make_excel(sheets),
                file_name=f"full_log_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    with ex2:
        if not df_exp_out.empty:
            st.download_button("⬇️ Outgoing Excel", make_excel({"Outgoing": df_exp_out}),
                file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    with ex3:
        if not df_exp_out.empty:
            st.download_button("⬇️ Outgoing PDF (HTML)",
                make_pdf_bytes("Outgoing References", df_exp_out),
                file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html", use_container_width=True)
        if not df_exp_in.empty:
            st.download_button("⬇️ Incoming PDF (HTML)",
                make_pdf_bytes("Incoming Letters", df_exp_in),
                file_name=f"incoming_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html", use_container_width=True)

    with ex4:
        if not df_exp_out.empty:
            st.download_button("⬇️ Outgoing CSV", df_exp_out.to_csv(index=False).encode("utf-8"),
                file_name=f"outgoing_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
        if not df_exp_in.empty:
            st.download_button("⬇️ Incoming CSV", df_exp_in.to_csv(index=False).encode("utf-8"),
                file_name=f"incoming_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="footer">RFSS Correspondence Management System &nbsp;·&nbsp; Ratnamani Finow &nbsp;·&nbsp; v4.0</div>', unsafe_allow_html=True)
