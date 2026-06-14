import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io

# ── Config ─────────────────────────────────────────────────────────────────────
LOG_FILE = "reference_log.json"

st.set_page_config(
    page_title="Reference Number Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Pastel palette: teal #7ECFC0, sage #B5D5A8, peach #F5C9B0, salmon #F5A09A, rose #F47F7F ── */

/* ── Page background ── */
.stApp {
    background: linear-gradient(135deg, #F0FAF8 0%, #EEF6EA 45%, #FDF1EB 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3A7A72 0%, #56A097 50%, #7ECFC0 100%);
    border-right: 1px solid rgba(255,255,255,0.12);
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] h2 { color: #FFFFFF !important; font-size: 15px !important; font-weight: 600 !important; }
section[data-testid="stSidebar"] .stTextInput label { color: rgba(255,255,255,0.75) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.06em; }
section[data-testid="stSidebar"] input { background: rgba(255,255,255,0.18) !important; border: 1px solid rgba(255,255,255,0.25) !important; color: #FFFFFF !important; border-radius: 8px !important; caret-color: #FFFFFF !important; }
section[data-testid="stSidebar"] input:focus { background: rgba(255,255,255,0.22) !important; border: 1px solid rgba(255,255,255,0.55) !important; color: #FFFFFF !important; box-shadow: 0 0 0 2px rgba(255,255,255,0.15) !important; outline: none !important; }
section[data-testid="stSidebar"] input::placeholder { color: rgba(255,255,255,0.45) !important; }
section[data-testid="stSidebar"] input:-webkit-autofill,
section[data-testid="stSidebar"] input:-webkit-autofill:focus { -webkit-box-shadow: 0 0 0 1000px rgba(56,120,110,0.9) inset !important; -webkit-text-fill-color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stMarkdown p { color: rgba(255,255,255,0.65) !important; font-size: 11px !important; }

/* ── Metric cards ── */
.metric-row { display: flex; gap: 14px; margin-bottom: 24px; }
.metric-card {
    flex: 1; background: rgba(255,255,255,0.88); backdrop-filter: blur(16px);
    border-radius: 18px; padding: 18px 20px; border: 1px solid rgba(255,255,255,.55);
    position: relative; overflow: hidden; box-shadow: 0 8px 25px rgba(126,207,192,.20);
}
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.metric-card.blue::before   { background: linear-gradient(90deg, #7ECFC0, #5BA897); }
.metric-card.teal::before   { background: linear-gradient(90deg, #B5D5A8, #8BBF7C); }
.metric-card.amber::before  { background: linear-gradient(90deg, #F5C9B0, #E8967A); }
.metric-card.purple::before { background: linear-gradient(90deg, #F5A09A, #F47F7F); }
.metric-num { font-size: 30px; font-weight: 700; color: #2D5A54; line-height: 1; margin-bottom: 4px; }
.metric-num.mono { font-size: 13px; font-family: 'JetBrains Mono', monospace; color: #3D8B80; padding-top: 6px; }
.metric-lbl { font-size: 11px; color: #7A9E9A; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.metric-icon { position: absolute; top: 16px; right: 16px; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 17px; }
.metric-card.blue .metric-icon   { background: #E8F7F5; }
.metric-card.teal .metric-icon   { background: #EEF6EA; }
.metric-card.amber .metric-icon  { background: #FDF1EB; }
.metric-card.purple .metric-icon { background: #FDE8E7; }

/* ── Section headers ── */
.sec-hdr { font-size: 12px; font-weight: 700; color: #2D5A54; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.sec-hdr::after { content: ''; flex: 1; height: 1px; background: #7ECFC0; opacity: 0.4; }

/* ── Input labels ── */
.stTextInput label, .stSelectbox label {
    font-size: 11px !important; font-weight: 600 !important; color: #4A7A74 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important;
}

/* ── Checkbox label ── */
.stCheckbox label span {
    font-size: 13px !important; font-weight: 500 !important; color: #3D8B80 !important;
    text-transform: none !important; letter-spacing: normal !important;
}
.stCheckbox { margin-top: 6px !important; }

/* ── Text input fields ── */
.stTextInput input {
    border-radius: 9px !important; border: 1.5px solid #C5E3DF !important;
    background: #F5FAFA !important; color: #2D5A54 !important; font-size: 14px !important;
    font-family: 'Inter', sans-serif !important; padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus {
    border-color: #7ECFC0 !important;
    box-shadow: 0 0 0 3px rgba(126,207,192,0.22) !important;
    background: #FFFFFF !important;
}
.stTextInput input::placeholder { color: #A8C8C4 !important; }

/* ── FIX 2: Selectbox — dark style, NOT editable (block typing) ── */
div[data-baseweb="select"] > div:first-child {
    border-radius: 9px !important; border: 1.5px solid #C5E3DF !important;
    background: #1E2D2C !important; cursor: pointer !important;
}
/* Block typing in select — makes dropdown read-only */
div[data-baseweb="select"] input {
    pointer-events: none !important;
    caret-color: transparent !important;
    cursor: pointer !important;
    -webkit-user-select: none !important;
    user-select: none !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: rgba(0,0,0,0) !important;
    text-shadow: 0 0 0 #FFFFFF !important;
}
div[data-baseweb="select"] [class*="singleValue"] { color: #FFFFFF !important; font-size: 14px !important; }
div[data-baseweb="select"] [class*="placeholder"] { color: rgba(255,255,255,0.5) !important; }
div[data-baseweb="select"] svg { fill: #7ECFC0 !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
    background: #1E2D2C !important; border: 1px solid #3D8B80 !important;
    border-radius: 10px !important; overflow: hidden !important;
}
div[data-baseweb="menu"] li { color: #FFFFFF !important; font-size: 14px !important; background: transparent !important; }
div[data-baseweb="menu"] li:hover,
div[data-baseweb="menu"] li[aria-selected="true"] { background: rgba(126,207,192,0.25) !important; color: #FFFFFF !important; }

/* ── Custom project reveal box ── */
.custom-project-box {
    background: rgba(255,255,255,.65); backdrop-filter: blur(12px);
    border: 1.5px dashed #7ECFC0; border-radius: 12px; padding: 16px; margin-top: 12px;
}

/* ── Priority badges ── */
.priority-badge {
    display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px;
    border-radius: 20px; font-size: 13px; font-weight: 600; margin-top: 6px;
}
.priority-badge.urgent { background: #FDEAEA; color: #B02020; border: 1.5px solid #F47F7F; }
.priority-badge.high   { background: #FDE8E7; color: #A04040; border: 1.5px solid #F5A09A; }
.priority-badge.normal { background: #EEF6EA; color: #3A6E30; border: 1.5px solid #B5D5A8; }
.priority-badge.low    { background: #FDF1EB; color: #8A5A3A; border: 1.5px solid #F5C9B0; }

/* ── FIX 3: Generate button — dark default, SOLID RED on hover ── */
/* Use every possible Streamlit selector to ensure hover works */
.stButton > button,
div[data-testid="stForm"] .stButton > button,
[data-testid="stFormSubmitButton"] > button,
button[kind="primaryFormSubmit"],
button[kind="primary"] {
    background: #1A2928 !important;
    background-image: none !important;
    border: none !important;
    border-radius: 11px !important;
    color: #FFFFFF !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 14px !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.30) !important;
    transition: background 0.18s ease, background-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease !important;
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
}
.stButton > button:hover,
div[data-testid="stForm"] .stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover,
button[kind="primaryFormSubmit"]:hover,
button[kind="primary"]:hover {
    background: #DC2626 !important;
    background-image: none !important;
    background-color: #DC2626 !important;
    box-shadow: 0 6px 22px rgba(220,38,38,0.55) !important;
    transform: translateY(-1px) !important;
    color: #FFFFFF !important;
}
.stButton > button:active,
div[data-testid="stForm"] .stButton > button:active,
[data-testid="stFormSubmitButton"] > button:active,
button[kind="primaryFormSubmit"]:active,
button[kind="primary"]:active {
    background: #991B1B !important;
    background-image: none !important;
    transform: translateY(0) !important;
    color: #FFFFFF !important;
}
.stButton > button:focus,
div[data-testid="stForm"] .stButton > button:focus,
[data-testid="stFormSubmitButton"] > button:focus,
button[kind="primaryFormSubmit"]:focus,
button[kind="primary"]:focus {
    background: #DC2626 !important;
    background-image: none !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(220,38,38,0.35) !important;
    color: #FFFFFF !important;
}

/* ── Result card ── */
.result-card {
    background: linear-gradient(135deg, #2D5A54 0%, #3D8B80 45%, #7ECFC0 100%);
    border-radius: 16px; padding: 24px 28px; color: white; margin-top: 20px;
    position: relative; overflow: hidden;
}
.result-card::after {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 180px; height: 180px; border-radius: 50%; background: rgba(255,255,255,0.06);
}
.result-eyebrow { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #B5E8E0; margin-bottom: 10px; }
.result-ref {
    font-size: 26px; font-weight: 700; font-family: 'JetBrains Mono', monospace;
    letter-spacing: 3px; background: rgba(255,255,255,0.14); display: inline-block;
    padding: 10px 20px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.22);
    margin-bottom: 16px; word-break: break-all;
}
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
.result-field { background: rgba(255,255,255,0.10); border-radius: 9px; padding: 10px 14px; border: 1px solid rgba(255,255,255,0.12); }
.result-field-label { font-size: 10px; color: #B5E8E0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 3px; }
.result-field-value { font-size: 13px; color: #FFFFFF; font-weight: 500; }
.priority-urgent { color: #F47F7F !important; }
.priority-high   { color: #F5A09A !important; }
.priority-normal { color: #B5D5A8 !important; }
.priority-low    { color: #F5C9B0 !important; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid #C5E3DF !important; }
[data-testid="stDataFrame"] table { font-size: 13px; }

/* ── Export buttons ── */
.stDownloadButton > button {
    border-radius: 9px !important; border: 1.5px solid #C5E3DF !important;
    background: #F5FAFA !important; color: #4A7A74 !important; font-size: 13px !important;
    font-weight: 500 !important; transition: all 0.15s !important;
}
.stDownloadButton > button:hover { border-color: #7ECFC0 !important; color: #2D5A54 !important; background: #E8F7F5 !important; }

hr { border-color: #C5E3DF !important; margin: 20px 0 !important; }
h1 { color: #2D5A54 !important; font-weight: 700 !important; font-size: 24px !important; }
h2, h3 { color: #2D5A54 !important; }
.stAlert { border-radius: 10px !important; }
.stCode { border-radius: 10px !important; }
code { font-family: 'JetBrains Mono', monospace !important; }
.footer { text-align: center; font-size: 11px; color: #7A9E9A; padding: 16px 0 4px; border-top: 1px solid #C5E3DF; margin-top: 24px; }
</style>
""", unsafe_allow_html=True)


# ── Data helpers ───────────────────────────────────────────────────────────────
def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {"entries": [], "counters": {}}


def save_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_serial(data, key):
    counters = data.get("counters", {})
    current  = counters.get(key, 0) + 1
    data["counters"][key] = current
    return current


def format_ref(company, contract, year, doc_type, serial):
    return f"{company}/{contract}/{doc_type}-{year}-{str(serial).zfill(4)}"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**Company & Contract**")
    company  = st.text_input("Company code", value="RFSS", max_chars=10).strip().upper()
    contract = st.text_input("Contract number", value="4224000135").strip()
    st.markdown("---")
    st.markdown('<span style="font-size:11px;opacity:0.7;">RFSS Reference Management · v2.1</span>', unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# 📋 Reference Number Generator")
st.markdown(
    '<p style="color:#5A9E98;font-size:14px;margin-top:-8px;margin-bottom:20px;">'
    'Generate, track and export document reference numbers for project correspondence.'
    '</p>',
    unsafe_allow_html=True
)

data    = load_log()
entries = data.get("entries", [])

# ── Metrics ────────────────────────────────────────────────────────────────────
total   = len(entries)
today_c = sum(1 for e in entries if e.get("date", "").startswith(datetime.now().strftime("%Y-%m-%d")))
users   = len(set(e.get("generated_by", "") for e in entries if e.get("generated_by", "")))
last    = entries[-1]["ref_number"] if entries else "—"

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card blue">
    <div class="metric-icon">📄</div>
    <div class="metric-num">{total}</div>
    <div class="metric-lbl">Total references</div>
  </div>
  <div class="metric-card teal">
    <div class="metric-icon">🗓️</div>
    <div class="metric-num">{today_c}</div>
    <div class="metric-lbl">Generated today</div>
  </div>
  <div class="metric-card amber">
    <div class="metric-icon">👤</div>
    <div class="metric-num">{users}</div>
    <div class="metric-lbl">Active users</div>
  </div>
  <div class="metric-card purple">
    <div class="metric-icon">🔖</div>
    <div class="metric-num mono">{last}</div>
    <div class="metric-lbl">Last generated</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Two columns ────────────────────────────────────────────────────────────────
col_gen, col_log = st.columns([1.05, 1.95], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_gen:
    st.markdown('<div class="sec-hdr">Generate reference number</div>', unsafe_allow_html=True)

    doc_types = {
        "LTR": "LTR — Letter",
        "RPT": "RPT — Report",
        "INV": "INV — Invoice",
        "QCP": "QCP — Quality Plan",
        "TDR": "TDR — Technical Document",
        "NCR": "NCR — Non-Conformance Report",
        "MOM": "MOM — Minutes of Meeting",
        "NTC": "NTC — Notice",
        "COR": "COR — Correspondence",
        "SUB": "SUB — Submittal",
    }
    dept_options = {
        "QC":  "QC — Quality Control",
        "PR":  "PR — Procurement",
        "PM":  "PM — Project Management",
        "ENG": "ENG — Engineering",
        "FIN": "FIN — Finance",
        "LEG": "LEG — Legal",
    }
    project_options = {
        "ED":  "ED — El Dabaa (Egypt)",
        "KK":  "KK — Kudankulam (India)",
        "AK":  "AK — Akkuyu (Turkey)",
        "BL":  "BL — Bushehr (Iran)",
        "RO":  "RO — Rooppur (Bangladesh)",
        "TN":  "TN — Tianwan (China)",
        "HAN": "HAN — Hanhikivi (Finland)",
    }
    priority_options = {
        "Normal": "🟢  Normal — Standard turnaround",
        "High":   "🟡  High — Needs prompt attention",
        "Urgent": "🔴  Urgent — Action required immediately",
        "Low":    "⚪  Low — No rush",
    }

    # ── FIX 1: Checkbox is OUTSIDE the form so it reacts immediately ──────────
    st.markdown("**🏗️ Project**")

    country = st.selectbox(
        "Select project",
        options=list(project_options.keys()),
        format_func=lambda x: project_options[x],
        help="Choose the project this document belongs to."
    )
    project_display = project_options[country]

    # Checkbox outside form — triggers immediate Streamlit re-render
    use_custom = st.checkbox("✏️ Use custom project")

    custom_proj = ""
    custom_name = ""
    if use_custom:
        st.markdown('<div class="custom-project-box">', unsafe_allow_html=True)
        cp1, cp2 = st.columns(2)
        with cp1:
            custom_proj = st.text_input(
                "Custom project code",
                max_chars=5,
                placeholder="e.g. MYPRJ"
            ).strip().upper()
        with cp2:
            custom_name = st.text_input(
                "Project full name",
                placeholder="e.g. My Project Name"
            ).strip()
        st.markdown('</div>', unsafe_allow_html=True)
        country = custom_proj if custom_proj else "PROJ"
        project_display = f"{country} — {custom_name}" if custom_name else country

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Rest of form (checkbox kept outside above) ────────────────────────────
    with st.form("gen_form", clear_on_submit=False):

        # ── Who ───────────────────────────────────────────────────────────────
        st.markdown("**👤 Who is generating this?**")
        generated_by = st.text_input(
            "Your full name *",
            placeholder="e.g. Rahul Siwach",
            help="Name of the person generating this reference number."
        )

        st.divider()

        # ── Document details ──────────────────────────────────────────────────
        st.markdown("**📄 Document details**")
        c1, c2 = st.columns(2)
        with c1:
            doc_type_sel = st.selectbox(
                "Document type *",
                options=list(doc_types.keys()),
                format_func=lambda x: doc_types[x],
                help="Category of document this reference is for."
            )
        with c2:
            dept = st.selectbox(
                "Department",
                options=list(dept_options.keys()),
                format_func=lambda x: dept_options[x],
                help="Department issuing the document."
            )

        to_party = st.text_input(
            "Addressed to — recipient name or organisation *",
            placeholder="e.g. TPBS Engineering GmbH",
            help="Full name or organisation the document is addressed to."
        )
        subject = st.text_input(
            "Subject / brief description",
            placeholder="e.g. Quality plan approval request",
            help="Optional short description of what this document covers."
        )

        st.divider()

        # ── Priority & year ───────────────────────────────────────────────────
        st.markdown("**🚦 Priority & year**")

        priority_key = st.selectbox(
            "Priority level",
            options=list(priority_options.keys()),
            format_func=lambda x: priority_options[x],
            help="Set the urgency level for this document."
        )

        year = st.text_input(
            "Reference year",
            value=str(datetime.now().year),
            max_chars=4,
            help="Year embedded in the reference number. Defaults to the current year."
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "⚡  Generate Reference Number",
            use_container_width=True
        )

    # ── Handle submission ─────────────────────────────────────────────────────
    if submitted:
        errors = []
        if not generated_by.strip():
            errors.append("**Your full name** is required.")
        if not to_party.strip():
            errors.append("**Recipient / addressed-to** is required.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            counter_key = f"{company}_{contract}_{doc_type_sel}_{year}"
            serial_num  = next_serial(data, counter_key)
            ref         = format_ref(company, contract, year, doc_type_sel, serial_num)
            now         = datetime.now()

            priority_color_class = {
                "Urgent": "priority-urgent",
                "High":   "priority-high",
                "Normal": "priority-normal",
                "Low":    "priority-low",
            }.get(priority_key, "priority-normal")

            entry = {
                "ref_number":    ref,
                "generated_by":  generated_by.strip(),
                "to_party":      to_party.strip(),
                "subject":       subject.strip(),
                "document_type": doc_types[doc_type_sel],
                "department":    dept_options[dept],
                "project":       project_display,
                "priority":      priority_key,
                "date":          now.strftime("%Y-%m-%d"),
                "time":          now.strftime("%H:%M:%S"),
                "datetime":      now.strftime("%Y-%m-%d %H:%M:%S"),
                "serial":        serial_num,
            }
            data["entries"].append(entry)
            save_log(data)

            subject_row = f"""
              <div class="result-field" style="grid-column:1/-1;">
                <div class="result-field-label">Subject</div>
                <div class="result-field-value">{subject.strip()}</div>
              </div>""" if subject.strip() else ""

            st.markdown(f"""
            <div class="result-card">
              <div class="result-eyebrow">✓ Reference number generated successfully</div>
              <div class="result-ref">{ref}</div>
              <div class="result-grid">
                <div class="result-field">
                  <div class="result-field-label">Generated by</div>
                  <div class="result-field-value">{generated_by.strip()}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Addressed to</div>
                  <div class="result-field-value">{to_party.strip()}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Project</div>
                  <div class="result-field-value">{project_display}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Document type</div>
                  <div class="result-field-value">{doc_types[doc_type_sel]}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Department</div>
                  <div class="result-field-value">{dept_options[dept]}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Priority</div>
                  <div class="result-field-value {priority_color_class}">{priority_key}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Date & time</div>
                  <div class="result-field-value">{now.strftime("%d %b %Y, %H:%M")}</div>
                </div>
                <div class="result-field">
                  <div class="result-field-label">Serial number</div>
                  <div class="result-field-value">#{serial_num:04d}</div>
                </div>
                {subject_row}
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Copy reference number:**")
            st.code(ref, language=None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# LOG COLUMN
# ══════════════════════════════════════════════════════════════════════════════
with col_log:
    st.markdown('<div class="sec-hdr">Reference number log</div>', unsafe_allow_html=True)

    data    = load_log()
    entries = data.get("entries", [])

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search = st.text_input("🔍 Search", placeholder="ref, name, recipient…")
    with fc2:
        all_users   = ["All"] + sorted(set(e.get("generated_by", "") for e in entries if e.get("generated_by", "")))
        filter_user = st.selectbox("Filter by user", all_users)
    with fc3:
        all_types   = ["All"] + sorted(set(e.get("document_type", "") for e in entries if e.get("document_type", "")))
        filter_type = st.selectbox("Filter by type", all_types)

    filtered = entries.copy()
    if search:
        s = search.lower()
        filtered = [e for e in filtered if
            s in e.get("ref_number",   "").lower() or
            s in e.get("generated_by", "").lower() or
            s in e.get("to_party",     "").lower() or
            s in e.get("subject",      "").lower()]
    if filter_user != "All":
        filtered = [e for e in filtered if e.get("generated_by", "") == filter_user]
    if filter_type != "All":
        filtered = [e for e in filtered if e.get("document_type", "") == filter_type]

    filtered_rev = list(reversed(filtered))

    if filtered_rev:
        for e in filtered_rev:
            if "project" not in e:
                e["project"] = "—"

        df = pd.DataFrame(filtered_rev)[[
            "ref_number", "document_type", "project", "generated_by",
            "to_party", "subject", "priority", "date", "time", "department"
        ]]
        df.columns = [
            "Reference #", "Doc Type", "Project", "Generated By",
            "Addressed To", "Subject", "Priority", "Date", "Time", "Department"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            height=460,
            column_config={
                "Reference #": st.column_config.TextColumn(width="medium"),
                "Doc Type":    st.column_config.TextColumn(width="small"),
                "Priority":    st.column_config.TextColumn(width="small"),
                "Date":        st.column_config.DateColumn(width="small", format="DD MMM YYYY"),
                "Time":        st.column_config.TextColumn(width="small"),
                "Subject":     st.column_config.TextColumn(width="large"),
            }
        )

        st.markdown("<br>", unsafe_allow_html=True)
        ex1, ex2 = st.columns(2)
        with ex1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️  Export as CSV", csv,
                file_name=f"reference_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with ex2:
            try:
                buf = io.BytesIO()
                df.to_excel(buf, index=False, engine="openpyxl")
                st.download_button(
                    "⬇️  Export as Excel", buf.getvalue(),
                    file_name=f"reference_log_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except Exception:
                st.warning("Excel export unavailable. Use CSV export instead.", icon="⚠️")
    else:
        st.info("No entries found. Generate your first reference number using the form on the left.", icon="ℹ️")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">RFSS Reference Management System &nbsp;·&nbsp; Ratnamani Finow &nbsp;·&nbsp; v2.1</div>',
    unsafe_allow_html=True
)
