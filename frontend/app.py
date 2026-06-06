import os
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = os.environ.get("API_URL", "http://localhost:8000")

# ── Theme state (dark by default) ─────────────────────────────────────────────
if "dark" not in st.session_state:
    st.session_state.dark = True
DARK = st.session_state.dark

st.set_page_config(
    page_title="ReviewGuard — Fake Review Detection",
    page_icon="🛡️",
    layout="wide",
)

# ── CSS variables + full overrides ────────────────────────────────────────────
if DARK:
    VARS = """
    --bg:      #111113;
    --card:    #1c1c1f;
    --card2:   #232326;
    --bord:    rgba(255,255,255,0.08);
    --bord2:   rgba(255,255,255,0.05);
    --text:    #f4f4f5;
    --muted:   #a1a1aa;
    --sub:     #3f3f46;
    --brand:   #f0a565;
    --brand2:  #fbbf79;
    --red:     #f87171;
    --green:   #4ade80;
    --shadow:  rgba(0,0,0,0.5);
    --glow:    rgba(240,165,101,0.22);
    --line:    rgba(255,255,255,0.06);
    """
    PLOT_BG   = "#111113"
    PLOT_CARD = "#1c1c1f"
    TEXT_C    = "#f4f4f5"
    MUTED_C   = "#a1a1aa"
    GRID_C    = "rgba(255,255,255,0.06)"
    BRAND_C   = "#f0a565"
else:
    VARS = """
    --bg:      #f9f9f8;
    --card:    #ffffff;
    --card2:   #f4f4f3;
    --bord:    #e5e5e3;
    --bord2:   #ececea;
    --text:    #1a1917;
    --muted:   #737067;
    --sub:     #f0f0ef;
    --brand:   #e07b39;
    --brand2:  #f5a76b;
    --red:     #dc2626;
    --green:   #16a34a;
    --shadow:  rgba(0,0,0,0.04);
    --glow:    rgba(224,123,57,0.18);
    --line:    rgba(0,0,0,0.05);
    """
    PLOT_BG   = "rgba(0,0,0,0)"
    PLOT_CARD = "rgba(0,0,0,0)"
    TEXT_C    = "#1a1917"
    MUTED_C   = "#737067"
    GRID_C    = "#e5e5e3"
    BRAND_C   = "#e07b39"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root {{ {VARS} }}
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif !important; }}
#MainMenu, footer, header {{ visibility: hidden !important; }}

/* ── App background ── */
.stApp {{ background: var(--bg) !important; }}
.block-container {{ background: transparent !important; padding-top: 0 !important; padding-bottom: 4rem !important; max-width: 1280px !important; }}

/* ── Layout lines (fixed vertical dashes, exact Launch UI) ── */
.stApp::before {{
  content: '';
  position: fixed; top: 0; left: calc(50% - 640px); width: 1px; height: 100%;
  background: var(--line); border-left: 1px dashed var(--line); z-index: 0; pointer-events: none;
}}
.stApp::after {{
  content: '';
  position: fixed; top: 0; right: calc(50% - 640px); width: 1px; height: 100%;
  background: var(--line); border-right: 1px dashed var(--line); z-index: 0; pointer-events: none;
}}

/* ── Launch UI animations ── */
@keyframes appear {{
  0%   {{ opacity:0; transform:translateY(1rem); filter:blur(.5rem); }}
  50%  {{ filter:blur(0); }}
  100% {{ opacity:1; transform:translateY(0); filter:blur(0); }}
}}
@keyframes appear-zoom {{
  0%   {{ opacity:0; transform:scale(.5); }}
  100% {{ opacity:1; transform:scale(1); }}
}}
.ao   {{ animation: appear      .6s forwards ease-out; }}
.ao1  {{ animation: appear      .6s .10s forwards ease-out; opacity:0; }}
.ao2  {{ animation: appear      .6s .22s forwards ease-out; opacity:0; }}
.ao3  {{ animation: appear      .6s .35s forwards ease-out; opacity:0; }}
.ao4  {{ animation: appear      .6s .50s forwards ease-out; opacity:0; }}
.az1  {{ animation: appear-zoom .6s .70s forwards ease-out; opacity:0; }}

/* ── Navbar bar ── */
.rg-nav {{
  position: sticky; top: 0; z-index: 100;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  background: color-mix(in srgb, var(--bg) 80%, transparent);
  border-bottom: 1px solid var(--bord);
  padding: 0 2rem;
  display: flex; align-items: center; justify-content: space-between;
  height: 56px; margin-bottom: 0;
}}
.rg-nav-logo {{ font-size: 1rem; font-weight: 800; color: var(--text); display:flex; align-items:center; gap:8px; }}
.rg-nav-right {{ display:flex; align-items:center; gap:12px; }}
.rg-nav-link {{ font-size: .83rem; font-weight:500; color: var(--muted); text-decoration:none; }}
.rg-nav-link:hover {{ color: var(--text); }}
.rg-nav-btn {{
  display: inline-flex; align-items:center; gap:6px;
  padding: 6px 16px; border-radius: 8px; font-size: .83rem; font-weight:600; cursor:pointer;
  border: 1px solid var(--bord);
  background: color-mix(in srgb, var(--text) 8%, transparent);
  color: var(--text); transition: background .2s;
}}
.rg-nav-btn:hover {{ background: color-mix(in srgb, var(--text) 15%, transparent); }}

/* ── Hero ── */
.hero {{
  padding: 80px 32px 0;
  text-align: center;
  position: relative; overflow: hidden;
  border-bottom: 1px solid var(--bord);
}}
.hero-inner {{ max-width: 760px; margin: 0 auto; }}
.hero-glow {{
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 70%; height: 350px; pointer-events:none;
  background: radial-gradient(ellipse at 50% 0%, var(--glow) 0%, transparent 65%);
}}
/* Badge — outline variant from Launch UI */
.badge-outline {{
  display: inline-flex; align-items:center; gap:6px;
  border: 1px solid var(--bord); border-radius: 100px;
  padding: 5px 14px; font-size:.75rem; font-weight:600;
  color: var(--text); background: transparent;
  margin-bottom: 20px;
}}
.badge-outline .dot {{ width:6px; height:6px; border-radius:50%; background:var(--brand); }}
/* Hero title — gradient text, exact Launch UI */
.hero-title {{
  font-size: 3rem; font-weight:900; letter-spacing:-2px; line-height:1.08;
  background: linear-gradient(180deg, var(--text) 40%, var(--muted) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 40px var(--glow));
}}
.hero-sub {{
  color: var(--muted); font-size:1.05rem; font-weight:500;
  max-width:540px; margin: 0 auto 28px; line-height:1.7;
}}
/* Hero CTA buttons (Launch UI default + glow variants) */
.hero-btns {{ display:flex; justify-content:center; gap:12px; margin-bottom:48px; flex-wrap:wrap; }}
.btn-default {{
  display:inline-flex; align-items:center; gap:6px;
  padding: 9px 22px; border-radius: 8px; font-size:.9rem; font-weight:600;
  background: linear-gradient(180deg, color-mix(in srgb, var(--text) 70%,transparent), var(--text));
  color: var(--bg); border: none; cursor:pointer;
  box-shadow: 0 1px 2px var(--shadow);
  transition: opacity .2s, transform .2s;
}}
.btn-default:hover {{ opacity:.88; transform:translateY(-1px); }}
.btn-glow {{
  display:inline-flex; align-items:center; gap:6px;
  padding: 9px 22px; border-radius: 8px; font-size:.9rem; font-weight:600;
  background: color-mix(in srgb, var(--card) 100%, transparent);
  border: 1px solid var(--bord); border-bottom-color: color-mix(in srgb,var(--bord) 80%,transparent);
  color: var(--text); cursor:pointer;
  box-shadow: 0 4px 8px var(--shadow);
  transition: box-shadow .2s, transform .2s;
}}
.btn-glow:hover {{ box-shadow: 0 8px 24px var(--shadow); transform:translateY(-1px); }}

/* ── Mockup frame (MockupFrame + Mockup from Launch UI) ── */
.mockup-frame {{
  background: color-mix(in srgb, var(--bord) 50%,transparent);
  border-radius: 18px; padding: 8px;
  box-shadow: -12px 16px 48px var(--shadow);
  max-width: 820px; margin: 0 auto;
  position: relative; z-index:1;
}}
.mockup-inner {{
  background: var(--card);
  border-radius: 12px;
  border: 1px solid var(--bord);
  overflow: hidden;
  width: 100%;
}}
/* mini bar inside mockup */
.mockup-bar {{
  background: var(--card2); border-bottom:1px solid var(--bord);
  padding: 8px 14px; display:flex; align-items:center; gap:8px;
}}
.mb-dot {{ width:9px;height:9px;border-radius:50%; }}
.mb-url {{
  flex:1; background:var(--sub); border-radius:6px;
  height:18px; margin:0 10px; font-size:.62rem; color:var(--muted);
  display:flex; align-items:center; padding:0 8px; letter-spacing:.3px;
}}
.mockup-body {{ padding:20px 16px; display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.mk-card {{
  background:var(--card2); border:1px solid var(--bord); border-radius:10px;
  padding:12px 14px;
}}
.mk-label {{ font-size:.62rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px; }}
.mk-val {{ font-size:1.3rem; font-weight:800; color:var(--text); }}
.mk-val.r {{ color:var(--red); }} .mk-val.g {{ color:var(--green); }} .mk-val.o {{ color:var(--brand); }}
.mk-bar {{ background:var(--sub); border-radius:100px; height:6px; margin-top:8px; overflow:hidden; }}
.mk-fill {{ height:100%; border-radius:100px; background: linear-gradient(90deg,var(--brand),var(--brand2)); }}
.mk-row {{ grid-column:1/-1; background:var(--card2); border:1px solid var(--bord); border-radius:10px; padding:12px 14px; }}
.mk-sig {{ display:flex; align-items:center; gap:8px; margin-bottom:7px; }}
.mk-sig-dot {{ width:6px;height:6px;border-radius:50%;flex-shrink:0; }}
.mk-sig-txt {{ font-size:.72rem; color:var(--muted); }}
.mk-verdict {{
  grid-column:1/-1; text-align:center; padding:14px;
  background: color-mix(in srgb, var(--red) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--red) 30%, transparent);
  border-radius:10px; font-weight:800; font-size:.85rem; color:var(--red);
  letter-spacing:.5px;
}}

/* ── Sections ── */
.rg-section {{
  border-bottom: 1px solid var(--bord);
  padding: 48px 32px;
}}
.sec-head {{ text-align:center; margin-bottom:40px; }}
.sec-eyebrow {{
  font-size:.7rem; font-weight:700; letter-spacing:1.5px;
  text-transform:uppercase; color:var(--brand); margin-bottom:6px;
}}
.sec-title {{
  font-size:1.9rem; font-weight:800; letter-spacing:-1px; line-height:1.2;
  background: linear-gradient(180deg, var(--text) 40%, var(--muted) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.sec-sub {{ color:var(--muted); font-size:.93rem; margin-top:6px; }}

/* ── Stat bar (Launch UI stats style) ── */
.stat-row {{ display:grid; grid-template-columns:repeat(4,1fr); border:1px solid var(--bord); border-radius:14px; overflow:hidden; background:var(--card); }}
.stat-cell {{ padding:24px 20px; border-right:1px solid var(--bord); }}
.stat-cell:last-child {{ border-right:none; }}
.stat-lbl {{ font-size:.72rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.8px; margin-bottom:8px; }}
.stat-val {{
  font-size:2.4rem; font-weight:700; line-height:1;
  background: linear-gradient(180deg, var(--text) 0%, var(--brand) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  filter: drop-shadow(0 0 20px var(--glow));
}}
.stat-val.r {{ background:linear-gradient(180deg,var(--red),color-mix(in srgb,var(--red) 60%,transparent));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 14px color-mix(in srgb,var(--red) 40%,transparent)); }}
.stat-val.g {{ background:linear-gradient(180deg,var(--green),color-mix(in srgb,var(--green) 60%,transparent));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 14px color-mix(in srgb,var(--green) 30%,transparent)); }}
.stat-val.o {{ background:linear-gradient(180deg,var(--brand),var(--brand2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 20px var(--glow)); }}
.stat-desc {{ font-size:.78rem; color:var(--muted); margin-top:4px; font-weight:500; }}

/* ── Cards (glass-2 from Launch UI) ── */
.glass-card {{
  background: linear-gradient(to bottom, var(--card), color-mix(in srgb, var(--card) 85%, transparent));
  border: 1px solid var(--bord);
  border-top-color: color-mix(in srgb, var(--bord) 150%, transparent);
  border-bottom-color: color-mix(in srgb, var(--bord) 80%, transparent);
  border-radius: 14px;
  box-shadow: 0 4px 24px var(--shadow);
  padding: 24px;
  transition: transform .25s ease, box-shadow .25s ease;
}}
.glass-card:hover {{ transform:translateY(-3px); box-shadow:0 8px 32px var(--shadow); }}

/* ── Signal cards ── */
.signal-fake {{
  background: color-mix(in srgb, var(--red) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--red) 30%, transparent);
  border-left: 3px solid var(--red);
  border-radius: 10px; padding:10px 14px; margin:5px 0;
  font-size:.87rem; color:var(--text); transition:transform .15s;
}}
.signal-fake:hover {{ transform:translateX(3px); }}
.signal-genuine {{
  background: color-mix(in srgb, var(--green) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--green) 30%, transparent);
  border-left: 3px solid var(--green);
  border-radius: 10px; padding:10px 14px; margin:5px 0;
  font-size:.87rem; color:var(--text); transition:transform .15s;
}}
.signal-genuine:hover {{ transform:translateX(3px); }}
.section-label {{
  font-size:.68rem; font-weight:700; letter-spacing:1.2px;
  text-transform:uppercase; color:var(--muted); margin-bottom:6px;
}}

/* ── Items grid (exact Launch UI items section) ── */
.items-grid {{
  display: grid; grid-template-columns: repeat(3,1fr);
  border: 1px solid var(--bord); border-radius:14px; overflow:hidden;
  background: var(--card);
}}
.iitem {{
  padding: 22px 20px;
  border-right: 1px solid var(--bord);
  border-bottom: 1px solid var(--bord);
  transition: background .2s;
}}
.iitem:hover {{ background: color-mix(in srgb, var(--brand) 6%, transparent); }}
.iitem:nth-child(3n) {{ border-right:none; }}
.iitem:nth-child(n+4) {{ border-bottom:none; }}
.iicon {{
  display:inline-flex; align-items:center; gap:6px;
  font-size:.85rem; font-weight:700; color:var(--text);
  margin-bottom:8px;
}}
.iicon .ic {{
  width:30px;height:30px; background:color-mix(in srgb,var(--brand) 15%,transparent);
  border-radius:7px; display:flex; align-items:center; justify-content:center; font-size:.85rem;
}}
.idesc {{ font-size:.79rem; color:var(--muted); line-height:1.6; max-width:220px; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
  background: {"#18181b" if DARK else "var(--card)"} !important;
  border-right: 1px solid var(--bord) !important;
}}
[data-testid="stSidebar"] * {{ color: {"#d4d4d8" if DARK else "var(--text)"} !important; }}
[data-testid="stSidebar"] .stButton > button {{
  background: var(--brand) !important;
  color: {"#111113" if DARK else "#ffffff"} !important;
  border: none !important; border-radius: 8px !important;
  width: 100% !important; font-weight: 700 !important;
  box-shadow: 0 4px 14px var(--glow) !important;
  transition: opacity .2s, transform .2s !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  opacity: .88 !important; transform: translateY(-1px) !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  background: transparent !important;
  border-bottom: 1px solid var(--bord) !important;
  gap: 2px !important;
}}
.stTabs [data-baseweb="tab"] {{
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important; font-size: .87rem !important;
  color: var(--muted) !important; border-radius: 8px 8px 0 0 !important;
  padding: 10px 20px !important; background: transparent !important;
  border: none !important; transition: color .2s !important;
}}
.stTabs [aria-selected="true"] {{
  color: var(--text) !important;
  border-bottom: 2px solid var(--brand) !important;
  background: transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--text) !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.5rem !important; background: transparent !important; }}

/* ── All Streamlit text ── */
.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2,
.stMarkdown h3, .stMarkdown h4, .stMarkdown li,
.stText, .stCaption p, div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] {{ color: var(--text) !important; }}
.stCaption {{ color: var(--muted) !important; }}

/* ── Buttons ── */
.stButton > button {{
  background: linear-gradient(180deg, color-mix(in srgb, var(--text) 70%,transparent), var(--text)) !important;
  color: var(--bg) !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
  transition: opacity .2s, transform .2s, box-shadow .2s !important;
  box-shadow: 0 1px 2px var(--shadow) !important;
}}
.stButton > button:hover {{
  opacity: .88 !important; transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px var(--shadow) !important;
}}
.stFormSubmitButton > button {{
  background: var(--brand) !important;
  color: {"#111113" if DARK else "#ffffff"} !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 700 !important; font-size: .95rem !important;
  padding: 10px 32px !important;
  box-shadow: 0 4px 14px var(--glow) !important;
  transition: opacity .2s, transform .2s !important;
}}
.stFormSubmitButton > button:hover {{
  opacity: .88 !important; transform: translateY(-1px) !important;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stNumberInput > div > div > input {{
  background: {"#27272a" if DARK else "var(--card)"} !important;
  border: 1.5px solid var(--bord) !important;
  border-radius: 9px !important; color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color .2s, box-shadow .2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {{
  border-color: var(--brand) !important;
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--brand) 20%, transparent) !important;
}}
label {{ font-weight: 600 !important; font-size: .83rem !important; color: var(--muted) !important; }}

/* ── Selectbox ── */
.stSelectbox > div > div {{
  background: {"#27272a" if DARK else "var(--card)"} !important;
  border: 1.5px solid var(--bord) !important;
  border-radius: 9px !important; color: var(--text) !important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
  background: var(--card) !important;
  border: 1px solid var(--bord) !important;
  border-radius: 12px !important; padding: 16px !important;
  box-shadow: 0 2px 8px var(--shadow) !important;
  transition: transform .2s, box-shadow .2s !important;
}}
[data-testid="metric-container"]:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px var(--shadow) !important;
}}
[data-testid="stMetricValue"] {{ color: var(--text) !important; font-weight: 800 !important; }}
[data-testid="stMetricLabel"] {{ color: var(--muted) !important; }}
[data-testid="stMetricDelta"]  {{ color: var(--muted) !important; }}

/* ── DataFrames ── */
.stDataFrame {{ border: 1px solid var(--bord) !important; border-radius: 12px !important; overflow:hidden !important; }}
.stDataFrame table {{ background: var(--card) !important; color: var(--text) !important; }}
.stDataFrame th {{ background: var(--card2) !important; color: var(--muted) !important; border-color: var(--bord) !important; }}
.stDataFrame td {{ border-color: var(--bord) !important; color: var(--text) !important; }}

/* ── Alerts ── */
.stAlert {{ border-radius: 12px !important; }}
div[data-testid="stNotification"] {{ background: var(--card) !important; border-color: var(--bord) !important; }}
.stInfo  {{ background: color-mix(in srgb, var(--brand) 10%, var(--card)) !important;
  border-color: color-mix(in srgb, var(--brand) 35%, transparent) !important; }}
.stInfo p {{ color: var(--text) !important; }}
.stSuccess {{ background: color-mix(in srgb, var(--green) 10%, var(--card)) !important;
  border-color: color-mix(in srgb, var(--green) 35%, transparent) !important; }}
.stWarning {{ background: color-mix(in srgb, #f59e0b 10%, var(--card)) !important; }}
.stError   {{ background: color-mix(in srgb, var(--red) 10%, var(--card)) !important; }}

/* ── Checkbox / Slider ── */
.stCheckbox span {{ color: var(--text) !important; }}
.stSlider [data-baseweb="slider"] [role="slider"] {{
  background: var(--brand) !important; border-color: var(--brand) !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
theme_icon = "☀️" if DARK else "🌙"
st.markdown(f"""
<div class="rg-nav ao">
  <div class="rg-nav-logo">
    <span style="color:var(--brand);font-size:1.2rem;">&#9673;</span>
    ReviewGuard
  </div>
  <div class="rg-nav-right">
    <a class="rg-nav-link" href="#detect">Detect</a>
    <a class="rg-nav-link" href="#reco">Recommendations</a>
    <a class="rg-nav-link" href="#timeline">Timeline</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## &#9881; Model Controls")
if st.sidebar.button(f"{theme_icon} {'Light Mode' if DARK else 'Dark Mode'}"):
    st.session_state.dark = not DARK
    st.rerun()
st.sidebar.markdown("---")
if st.sidebar.button("Train on Real Dataset"):
    with st.spinner("Training on real data..."):
        resp = requests.post(f"{API_URL}/api/train?use_real=true")
        if resp.status_code == 200:
            data = resp.json()
            st.sidebar.success("Model trained!")
            st.sidebar.markdown(f"**Dataset:** {data.get('dataset','N/A')}")
            st.sidebar.markdown(f"**Samples:** {data.get('total_samples',0)}")
            st.sidebar.markdown(f"**ROC AUC:** {round(data['metrics']['roc_auc'],3)}")
            p = data['metrics'].get('1',{}).get('precision',0)
            r = data['metrics'].get('1',{}).get('recall',0)
            st.sidebar.markdown(f"**Precision:** {p:.1%} | **Recall:** {r:.1%}")
        else:
            st.sidebar.error(f"Error: {resp.text}")
st.sidebar.markdown("---")
st.sidebar.markdown("**How it works**")
st.sidebar.markdown("""
1. 17 features extracted from text + behaviour
2. GradientBoosting classifier scores the review
3. Feature importances explain the verdict
4. Fake reviews filtered before recommendations
""")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<section class="hero">
  <div class="hero-glow"></div>
  <div class="hero-inner">
    <div class="badge-outline ao">
      <span class="dot"></span>
      Hackathon Project &mdash; Fake Review Detection
    </div>
    <h1 class="hero-title ao1">ReviewGuard &mdash;<br>Detect Fake Reviews with AI</h1>
    <p class="hero-sub ao2">17 text + behavioural signals. Real-time verdicts. Fully explainable results. See their impact on product recommendations.</p>
    <div class="hero-btns ao3">
      <span class="btn-default">&#9654; Detect a Review</span>
      <span class="btn-glow">View Recommendations</span>
    </div>
  </div>

  <!-- Mockup frame (exact Launch UI MockupFrame style) -->
  <div class="mockup-frame az1" style="margin-bottom:-2px">
    <div class="mockup-inner">
      <div class="mockup-bar">
        <div class="mb-dot" style="background:#ff5f57"></div>
        <div class="mb-dot" style="background:#febc2e;margin:0 5px"></div>
        <div class="mb-dot" style="background:#28c840"></div>
        <div class="mb-url">reviewguard.ai/detect</div>
      </div>
      <div class="mockup-body">
        <div class="mk-card">
          <div class="mk-label">Reviews Analyzed</div>
          <div class="mk-val">2,847</div>
          <div class="mk-bar"><div class="mk-fill" style="width:100%"></div></div>
        </div>
        <div class="mk-card">
          <div class="mk-label">Fake Detected</div>
          <div class="mk-val r">312</div>
          <div class="mk-bar"><div class="mk-fill" style="width:11%;background:linear-gradient(90deg,var(--red),color-mix(in srgb,var(--red) 60%,orange))"></div></div>
        </div>
        <div class="mk-card">
          <div class="mk-label">Genuine</div>
          <div class="mk-val g">2,535</div>
          <div class="mk-bar"><div class="mk-fill" style="width:89%;background:linear-gradient(90deg,var(--green),#86efac)"></div></div>
        </div>
        <div class="mk-card">
          <div class="mk-label">Fake Rate</div>
          <div class="mk-val o">11.0%</div>
          <div class="mk-bar"><div class="mk-fill" style="width:11%"></div></div>
        </div>
        <div class="mk-row">
          <div style="font-size:.68rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">Latest Verdict</div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:var(--red)"></div><div class="mk-sig-txt">&#128681; 87% UPPERCASE text (normal &lt;5%)</div></div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:var(--red)"></div><div class="mk-sig-txt">&#128681; Account only 2 days old</div></div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:var(--red)"></div><div class="mk-sig-txt">&#128681; Not a verified purchase</div></div>
        </div>
        <div class="mk-verdict">&#128683; FAKE REVIEW DETECTED &mdash; 94% CONFIDENCE</div>
      </div>
    </div>
  </div>
</section>
""", unsafe_allow_html=True)

# ── Live stat bar ──────────────────────────────────────────────────────────────
st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
try:
    stats = requests.get(f"{API_URL}/api/stats").json()
    st.markdown(f"""
<div class="stat-row ao">
  <div class="stat-cell">
    <div class="stat-lbl">Reviews Analyzed</div>
    <div class="stat-val">{stats["total"]}</div>
    <div class="stat-desc">total processed</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Fake Detected</div>
    <div class="stat-val r">{stats["fake"]}</div>
    <div class="stat-desc">flagged by model</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Genuine</div>
    <div class="stat-val g">{stats["genuine"]}</div>
    <div class="stat-desc">passed review</div>
  </div>
  <div class="stat-cell">
    <div class="stat-lbl">Fake Rate</div>
    <div class="stat-val o">{stats["fake_rate"]:.1%}</div>
    <div class="stat-desc">of total reviews</div>
  </div>
</div>
""", unsafe_allow_html=True)
except Exception:
    st.warning("Backend not connected. Run: `uvicorn backend.api.main:app --reload --port 8000`")

st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Detect a Review",
    "Recommendations Impact",
    "Review Bombing Timeline",
    "Review History",
    "How It Works",
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
<div class="sec-head">
  <div class="sec-eyebrow">Detection Engine</div>
  <div class="sec-title">Analyze a Review</div>
  <div class="sec-sub">Paste any review and reviewer info to get an AI verdict with full explanation.</div>
</div>
""", unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns(3)
    preset = None
    if col_p1.button("Load Fake Example"):     preset = "fake"
    if col_p2.button("Load Genuine Example"):  preset = "genuine"
    if col_p3.button("Load Borderline Example"): preset = "borderline"

    defaults = {
        "fake": {
            "text": "BEST PRODUCT EVER!!! AMAZING!!! MUST BUY NOW!!! PERFECT PERFECT PERFECT!!!",
            "rating": 5.0, "verified": False, "review_count": 2, "days": 3, "helpful": 0,
        },
        "genuine": {
            "text": "Bought this three weeks ago. Battery life is solid, around 18 hours with moderate use. Build quality feels premium. Noise cancellation handles office noise well but struggles with loud environments. Worth the price for frequent travellers.",
            "rating": 4.0, "verified": True, "review_count": 47, "days": 730, "helpful": 12,
        },
        "borderline": {
            "text": "Really happy with this product! Works great and arrived fast. Would recommend to friends.",
            "rating": 5.0, "verified": False, "review_count": 8, "days": 45, "helpful": 1,
        },
    }
    d = defaults.get(preset, defaults["genuine"])

    with st.form("review_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            reviewer_id   = st.text_input("Reviewer ID", value="user_1234")
            product_id    = st.text_input("Product ID", value="prod_456")
            rating        = st.slider("Star Rating", 1.0, 5.0, d["rating"], 0.5)
            verified      = st.checkbox("Verified Purchase", value=d["verified"])
        with col_b:
            review_count  = st.number_input("Total reviews written by this person", 0, 10000, d["review_count"])
            days_joined   = st.number_input("Account age (days)", 0, 5000, d["days"])
            helpful_votes = st.number_input("Helpful votes received", 0, 10000, d["helpful"])
        review_text = st.text_area("Review Text", height=130, value=d["text"])
        submitted   = st.form_submit_button("Analyze Review")

    if submitted:
        payload = {
            "reviewer_id": reviewer_id, "product_id": product_id,
            "review_text": review_text, "rating": rating,
            "verified_purchase": verified, "review_count": review_count,
            "days_since_joined": days_joined, "helpful_votes": helpful_votes,
        }
        try:
            resp = requests.post(f"{API_URL}/api/detect", json=payload)
            if resp.status_code == 200:
                result = resp.json()
                st.markdown("---")
                prob = result["fake_probability"]
                if prob >= 0.7:
                    st.error(f"FAKE REVIEW — {prob:.0%} confidence this review is fake")
                elif prob >= 0.4:
                    st.warning(f"SUSPICIOUS — {prob:.0%} chance this is fake (needs manual review)")
                else:
                    st.success(f"LIKELY GENUINE — only {prob:.0%} chance this is fake")

                col_g, col_e = st.columns([1, 1])
                with col_g:
                    bar_color = BRAND_C if prob >= 0.7 else ("#f59e0b" if prob >= 0.4 else "#4ade80" if DARK else "#16a34a")
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number", value=prob * 100,
                        number={"suffix": "%", "font": {"size": 36, "family": "Inter", "color": TEXT_C}},
                        title={"text": "Fake Probability", "font": {"size": 13, "family": "Inter", "color": MUTED_C}},
                        gauge={
                            "axis": {"range": [0, 100], "ticksuffix": "%", "tickfont": {"color": MUTED_C}},
                            "bar": {"color": bar_color},
                            "bgcolor": PLOT_CARD,
                            "steps": [
                                {"range": [0, 40],   "color": "rgba(74,222,128,0.12)" if DARK else "#f0fdf4"},
                                {"range": [40, 70],  "color": "rgba(245,158,11,0.12)" if DARK else "#fefce8"},
                                {"range": [70, 100], "color": "rgba(248,113,113,0.12)" if DARK else "#fef2f2"},
                            ],
                            "threshold": {"line": {"color": TEXT_C, "width": 2}, "thickness": 0.75, "value": 70},
                        },
                    ))
                    fig.update_layout(
                        height=280, margin=dict(t=40, b=0, l=20, r=20),
                        paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
                        font=dict(family="Inter, sans-serif", color=TEXT_C),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Above 70% = fake. 40–70% = suspicious. Below 40% = genuine.")

                with col_e:
                    st.markdown("#### What triggered this verdict?")
                    explanation = result.get("explanation", [])
                    context_map = {
                        "uppercase_ratio":        lambda v: f"{v*100:.0f}% of text is UPPERCASE (normal: <5%)",
                        "exclamation_count":      lambda v: f"{v:.0f} exclamation marks (normal: 0–1)",
                        "sentiment_subjectivity": lambda v: f"Subjectivity score {v:.2f}/1.0 (normal: <0.6)",
                        "sentiment_polarity":     lambda v: f"Extreme positive sentiment: {v:.2f}/1.0",
                        "unique_word_ratio":      lambda v: f"Only {v*100:.0f}% unique words — repetitive text",
                        "review_count":           lambda v: f"Account has only {v:.0f} total reviews",
                        "days_since_joined":      lambda v: f"Account only {v:.0f} days old",
                        "helpful_votes":          lambda v: f"Received {v:.0f} helpful votes",
                        "verified_purchase":      lambda v: "Not a verified purchase" if v == 0 else "Verified purchase",
                        "avg_rating_given":       lambda v: f"Always gives {v:.1f}-star ratings",
                        "review_length":          lambda v: f"Review is only {v:.0f} characters",
                        "word_count":             lambda v: f"Only {v:.0f} words in review",
                    }
                    fake_sigs    = [f for f in explanation if f["score"] > 0.001][:4]
                    genuine_sigs = [f for f in explanation if f["score"] < -0.001][:2]
                    if fake_sigs:
                        st.markdown('<div class="section-label">Red flags found</div>', unsafe_allow_html=True)
                        for f in fake_sigs:
                            fn = context_map.get(f["feature"])
                            ctx = fn(f["value"]) if fn else f"{f['label']}: {f['value']:.2f}"
                            st.markdown(f'<div class="signal-fake">🚩 {ctx}</div>', unsafe_allow_html=True)
                    if genuine_sigs:
                        st.markdown('<div class="section-label" style="margin-top:12px">Genuine signals</div>', unsafe_allow_html=True)
                        for f in genuine_sigs:
                            fn = context_map.get(f["feature"])
                            ctx = fn(f["value"]) if fn else f"{f['label']}: {f['value']:.2f}"
                            st.markdown(f'<div class="signal-genuine">✅ {ctx}</div>', unsafe_allow_html=True)
                    if not fake_sigs and not genuine_sigs:
                        st.info("No strong signals — verdict based on combined weak signals.")
            else:
                st.error(f"API Error: {resp.json().get('detail', resp.text)}")
        except Exception as e:
            st.error(f"Could not connect to API: {e}")

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
<div class="sec-head">
  <div class="sec-eyebrow">Recommendation System</div>
  <div class="sec-title">How Fake Reviews Distort Rankings</div>
  <div class="sec-sub">Fake reviews inflate ratings for certain products, pushing them unfairly to the top. Filtering them restores honest rankings.</div>
</div>
""", unsafe_allow_html=True)

    try:
        data = requests.get(f"{API_URL}/api/recommendations").json()
        fc, gc, total = data["fake_count"], data["genuine_count"], data["total_reviews"]
        st.info(f"Dataset: **{total} reviews** — {gc} genuine + **{fc} fake** ({fc/total:.0%} injection rate)")

        cb, ca = st.columns(2)
        with cb:
            st.markdown("### Before Filtering")
            st.markdown("*Rankings include fake reviews*")
            df_b = pd.DataFrame(data["with_fake"])
            df_b.index = range(1, len(df_b)+1)
            df_b["avg_rating"]     = df_b["avg_rating"].map(lambda x: f"{x:.2f} ★")
            df_b["bayesian_score"] = df_b["bayesian_score"].map(lambda x: f"{x:.3f}")
            st.dataframe(df_b[["name","category","avg_rating","review_count","bayesian_score"]].rename(
                columns={"name":"Product","category":"Category","avg_rating":"Avg Rating",
                         "review_count":"Reviews","bayesian_score":"Score"}), use_container_width=True)
        with ca:
            st.markdown("### After Filtering")
            st.markdown("*Fake reviews removed*")
            df_a = pd.DataFrame(data["without_fake"])
            df_a.index = range(1, len(df_a)+1)
            def rank_arrow(c):
                if c > 0:   return f"▲ +{c}"
                elif c < 0: return f"▼ {c}"
                return "—"
            df_a["rank_change"]    = df_a["rank_change"].map(rank_arrow)
            df_a["avg_rating"]     = df_a["avg_rating"].map(lambda x: f"{x:.2f} ★")
            df_a["bayesian_score"] = df_a["bayesian_score"].map(lambda x: f"{x:.3f}")
            st.dataframe(df_a[["name","category","avg_rating","review_count","bayesian_score","rank_change"]].rename(
                columns={"name":"Product","category":"Category","avg_rating":"Avg Rating",
                         "review_count":"Reviews","bayesian_score":"Score","rank_change":"Rank Change"}), use_container_width=True)

        st.markdown("---")
        st.markdown("#### Score Comparison: Before vs After")
        nb = [r["name"].split()[0]+" "+r["name"].split()[1] for r in data["with_fake"]]
        na = [r["name"].split()[0]+" "+r["name"].split()[1] for r in data["without_fake"]]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="With Fake Reviews",    x=nb, y=[r["bayesian_score"] for r in data["with_fake"]],    marker_color=BRAND_C))
        fig2.add_trace(go.Bar(name="Fake Reviews Removed", x=na, y=[r["bayesian_score"] for r in data["without_fake"]], marker_color="#4ade80" if DARK else "#16a34a"))
        fig2.update_layout(
            barmode="group", xaxis_title="Product", yaxis_title="Bayesian Score",
            height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color=TEXT_C)),
            plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
            font=dict(family="Inter, sans-serif", color=TEXT_C),
            xaxis=dict(gridcolor=GRID_C, linecolor=GRID_C),
            yaxis=dict(gridcolor=GRID_C, linecolor=GRID_C),
            margin=dict(t=40,b=20,l=20,r=20),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Bayesian average score weights products by review volume — preventing small-sample manipulation.")
    except Exception as e:
        st.error(f"Could not load recommendations: {e}")

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
<div class="sec-head">
  <div class="sec-eyebrow">Attack Detection</div>
  <div class="sec-title">Review Bombing Timeline</div>
  <div class="sec-sub">A coordinated group posts dozens of fake 5-star reviews within hours, artificially inflating a product's rating.</div>
</div>
""", unsafe_allow_html=True)

    product_options = {
        "Sony WH-1000XM5 Headphones": "biz_001",
        "Ninja Air Fryer XL":         "biz_004",
        "Apple AirPods Pro":          "biz_009",
    }
    sel = st.selectbox("Select product to inspect:", list(product_options.keys()))
    pid = product_options[sel]

    try:
        data = requests.get(f"{API_URL}/api/timeline?product_id={pid}").json()
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Genuine Reviews", data["total_genuine"])
        c2.metric("Fake Injected",   data["total_fake"],
                  delta=f"+{data['total_fake']} in 48hrs", delta_color="inverse")
        c3.metric("Rating During Attack",  f"{data['rating_during_bomb']}★")
        c4.metric("True Rating (no fakes)", f"{data['rating_genuine_only']}★",
                  delta=f"{data['rating_genuine_only'] - data['rating_during_bomb']:.2f}",
                  delta_color="normal")
        st.markdown("---")

        daily_df   = pd.DataFrame(data["daily"])
        bomb_start = data["bomb_start"]
        bomb_end   = data["bomb_end"]

        fig3 = go.Figure()
        fig3.add_vrect(x0=bomb_start, x1=bomb_end,
            fillcolor=f"rgba(248,113,113,0.12)" if DARK else "rgba(220,50,50,0.10)",
            line_width=0, annotation_text="Attack window", annotation_position="top left",
            annotation_font_color=BRAND_C, annotation_font_size=13)
        fig3.add_trace(go.Bar(x=daily_df["date"], y=daily_df["fake_count"],
            name="Fake Reviews Posted", marker_color=BRAND_C+"66", yaxis="y2"))
        fig3.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["avg_rating"],
            name="Displayed Rating (incl. fakes)",
            line=dict(color=BRAND_C, width=2.5, dash="dot"), mode="lines"))
        fig3.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["genuine_avg"],
            name="True Rating (genuine only)",
            line=dict(color="#4ade80" if DARK else "#16a34a", width=2.5), mode="lines"))
        fig3.update_layout(
            title=dict(text=f"90-Day Review History: {sel}", font=dict(size=14, color=TEXT_C)),
            xaxis_title="Date",
            yaxis=dict(title="Average Rating", range=[1,5.5], ticksuffix="★",
                       gridcolor=GRID_C, linecolor=GRID_C),
            yaxis2=dict(title="Fake Count", overlaying="y", side="right",
                        showgrid=False, rangemode="tozero"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(color=TEXT_C, size=12)),
            height=460, hovermode="x unified",
            plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
            font=dict(family="Inter, sans-serif", color=TEXT_C),
            margin=dict(t=60,b=20,l=20,r=20),
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("#### Individual Reviews — Genuine vs Fake")
        st.caption("Each dot is one review. Notice the fake cluster during the attack window.")
        ev = pd.DataFrame(data["events"])
        ev["timestamp"] = pd.to_datetime(ev["timestamp"])
        ev["label"] = ev["is_fake"].map({True: "Fake", False: "Genuine"})
        sc = px.scatter(ev, x="timestamp", y="rating", color="label",
            color_discrete_map={"Fake": BRAND_C, "Genuine": "#4ade80" if DARK else "#16a34a"},
            opacity=0.6, labels={"timestamp": "Date", "rating": "Star Rating"}, height=320)
        sc.add_vrect(x0=bomb_start, x1=bomb_end,
            fillcolor=BRAND_C+"22", line_width=0)
        sc.update_traces(marker=dict(size=7))
        sc.update_layout(
            yaxis=dict(ticksuffix="★", range=[0.5,5.5], gridcolor=GRID_C),
            plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
            font=dict(family="Inter, sans-serif", color=TEXT_C),
            legend_title="Review type", margin=dict(t=20,b=20,l=20,r=20))
        st.plotly_chart(sc, use_container_width=True)
        st.info(
            f"The attack inflated the displayed rating by "
            f"**{data['rating_during_bomb']-data['rating_genuine_only']:.2f} stars** during 48 hours. "
            f"ReviewGuard flags these in real time, preserving the true rating.")
    except Exception as e:
        st.error(f"Could not load timeline data: {e}")

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
<div class="sec-head">
  <div class="sec-eyebrow">Audit Log</div>
  <div class="sec-title">Recently Analyzed Reviews</div>
</div>
""", unsafe_allow_html=True)
    try:
        reviews = requests.get(f"{API_URL}/api/reviews?limit=20").json()
        if reviews:
            df = pd.DataFrame(reviews)[["id","reviewer_id","product_id","rating",
                                        "fake_probability","is_fake","verified_purchase"]]
            df["is_fake"]          = df["is_fake"].map({True: "FAKE", False: "GENUINE"})
            df["fake_probability"] = df["fake_probability"].map(lambda x: f"{x:.1%}" if x is not None else "N/A")
            st.dataframe(df, use_container_width=True)
            fdf = pd.DataFrame(reviews)
            if "is_fake" in fdf.columns and len(fdf) > 0:
                counts = fdf["is_fake"].value_counts().reset_index()
                counts.columns = ["is_fake","count"]
                counts["label"] = counts["is_fake"].map({True:"Fake",False:"Genuine"})
                fp = px.pie(counts, values="count", names="label", title="Review Distribution",
                    color="label", color_discrete_map={"Fake": BRAND_C, "Genuine": "#4ade80" if DARK else "#16a34a"},
                    hole=0.45)
                fp.update_layout(
                    plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
                    font=dict(family="Inter, sans-serif", color=TEXT_C),
                    margin=dict(t=40,b=20,l=20,r=20),
                    legend=dict(font=dict(color=TEXT_C)))
                st.plotly_chart(fp, use_container_width=True)
        else:
            st.info("No reviews analyzed yet. Use the 'Detect a Review' tab.")
    except Exception:
        st.info("No reviews analyzed yet.")

# ── TAB 5: How It Works ───────────────────────────────────────────────────────
with tab5:
    bg_val     = "#111113"       if DARK else "#f9f9f8"
    card_val   = "#1c1c1f"       if DARK else "#ffffff"
    card2_val  = "#232326"       if DARK else "#f4f4f3"
    bord_val   = "rgba(255,255,255,0.08)" if DARK else "#e5e5e3"
    text_val   = "#f4f4f5"       if DARK else "#1a1917"
    muted_val  = "#a1a1aa"       if DARK else "#737067"
    brand_val  = "#f0a565"       if DARK else "#e07b39"
    red_val    = "#f87171"       if DARK else "#dc2626"
    green_val  = "#4ade80"       if DARK else "#16a34a"
    glow_val   = "rgba(240,165,101,0.22)" if DARK else "rgba(224,123,57,0.18)"
    line_val   = "rgba(255,255,255,0.06)" if DARK else "rgba(0,0,0,0.05)"

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;background:{bg_val};color:{text_val};overflow-x:hidden;}}

/* ── Layout lines ── */
body::before,body::after{{
  content:'';position:fixed;top:0;height:100%;width:1px;
  border-left:1px dashed {line_val};pointer-events:none;z-index:0;
}}
body::before{{left:10%;}} body::after{{right:10%;}}

/* ── Animations (exact Launch UI) ── */
@keyframes appear{{
  0%{{opacity:0;transform:translateY(1rem);filter:blur(.5rem);}}
  50%{{filter:blur(0);}}
  100%{{opacity:1;transform:translateY(0);filter:blur(0);}}
}}
@keyframes appear-zoom{{
  0%{{opacity:0;transform:scale(.5);}}
  100%{{opacity:1;transform:scale(1);}}
}}
.reveal{{opacity:0;transform:translateY(16px);}}
.reveal.show{{animation:appear .65s forwards ease-out;}}
.reveal.show.d1{{animation-delay:.1s;}} .reveal.show.d2{{animation-delay:.22s;}}
.reveal.show.d3{{animation-delay:.34s;}} .reveal.show.d4{{animation-delay:.46s;}}
.reveal.show.d5{{animation-delay:.58s;}} .reveal.show.d6{{animation-delay:.7s;}}
.reveal-zoom{{opacity:0;}}
.reveal-zoom.show{{animation:appear-zoom .6s forwards ease-out;}}
.reveal-zoom.show.d4{{animation-delay:.5s;}}

/* ── Navbar ── */
.nav{{
  position:sticky;top:0;z-index:100;
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
  background:color-mix(in srgb,{bg_val} 85%,transparent);
  border-bottom:1px solid {bord_val};
  padding:0 32px; height:56px;
  display:flex;align-items:center;justify-content:space-between;
}}
.nav-logo{{font-size:.95rem;font-weight:800;color:{text_val};display:flex;align-items:center;gap:8px;}}
.nav-dot{{width:8px;height:8px;border-radius:50%;background:{brand_val};}}
.nav-links{{display:flex;gap:24px;}}
.nav-link{{font-size:.82rem;font-weight:500;color:{muted_val};text-decoration:none;}}

/* ── Hero ── */
.hero{{
  padding:80px 32px 0;text-align:center;
  position:relative;overflow:hidden;
  border-bottom:1px solid {bord_val};
}}
.hero-glow{{
  position:absolute;top:0;left:50%;transform:translateX(-50%);
  width:70%;height:350px;pointer-events:none;
  background:radial-gradient(ellipse at 50% 0%,{glow_val} 0%,transparent 65%);
}}
/* Badge — outline variant */
.badge-outline{{
  display:inline-flex;align-items:center;gap:7px;
  border:1px solid {bord_val};border-radius:100px;
  padding:5px 14px;font-size:.75rem;font-weight:600;color:{text_val};
  margin-bottom:22px;
}}
.badge-dot{{width:6px;height:6px;border-radius:50%;background:{brand_val};}}
.hero-title{{
  font-size:2.8rem;font-weight:900;letter-spacing:-2px;line-height:1.08;
  background:linear-gradient(180deg,{text_val} 30%,{muted_val} 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 40px {glow_val});
  margin-bottom:16px;max-width:680px;margin-left:auto;margin-right:auto;
}}
.hero-sub{{
  color:{muted_val};font-size:1rem;font-weight:500;
  max-width:500px;margin:0 auto 32px;line-height:1.7;
}}
/* Hero buttons */
.hero-btns{{display:flex;justify-content:center;gap:12px;margin-bottom:48px;flex-wrap:wrap;}}
.btn-d{{
  display:inline-flex;align-items:center;gap:6px;padding:9px 22px;
  border-radius:8px;font-size:.88rem;font-weight:600;cursor:pointer;
  background:linear-gradient(180deg,color-mix(in srgb,{text_val} 70%,transparent),{text_val});
  color:{bg_val};border:none;box-shadow:0 1px 2px rgba(0,0,0,.3);
  transition:opacity .2s,transform .2s;
}}
.btn-d:hover{{opacity:.88;transform:translateY(-1px);}}
.btn-glow{{
  display:inline-flex;align-items:center;gap:6px;padding:9px 22px;
  border-radius:8px;font-size:.88rem;font-weight:600;cursor:pointer;
  background:{card_val};
  border:1px solid {bord_val};
  color:{text_val};
  box-shadow:0 4px 12px rgba(0,0,0,.25);
  transition:box-shadow .2s,transform .2s;
}}
.btn-glow:hover{{box-shadow:0 8px 28px rgba(0,0,0,.4);transform:translateY(-1px);}}

/* ── Mockup frame ── */
.mockup-frame{{
  background:color-mix(in srgb,{bord_val} 50%,transparent);
  border-radius:20px;padding:8px;
  box-shadow:-12px 16px 48px rgba(0,0,0,.5);
  max-width:820px;margin:0 auto;
}}
.mockup-inner{{
  background:{card_val};border-radius:14px;
  border:1px solid {bord_val};overflow:hidden;
}}
.mockup-bar{{
  background:{card2_val};border-bottom:1px solid {bord_val};
  padding:8px 14px;display:flex;align-items:center;gap:6px;
}}
.mb-dot{{width:9px;height:9px;border-radius:50%;}}
.mb-url{{
  flex:1;background:color-mix(in srgb,{muted_val} 20%,transparent);
  border-radius:6px;height:18px;margin:0 10px;font-size:.6rem;color:{muted_val};
  display:flex;align-items:center;padding:0 8px;letter-spacing:.3px;
}}
.mockup-body{{padding:20px 16px;display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
.mk-card{{
  background:{card2_val};border:1px solid {bord_val};
  border-radius:10px;padding:12px 14px;
}}
.mk-label{{font-size:.6rem;font-weight:700;color:{muted_val};text-transform:uppercase;
  letter-spacing:.8px;margin-bottom:6px;}}
.mk-val{{font-size:1.3rem;font-weight:800;color:{text_val};}}
.mk-val.r{{color:{red_val};}} .mk-val.g{{color:{green_val};}} .mk-val.o{{color:{brand_val};}}
.mk-bar{{background:color-mix(in srgb,{muted_val} 20%,transparent);
  border-radius:100px;height:5px;margin-top:8px;overflow:hidden;}}
.mk-fill{{height:100%;border-radius:100px;
  background:linear-gradient(90deg,{brand_val},{brand_val}88);}}
.mk-row{{grid-column:1/-1;background:{card2_val};border:1px solid {bord_val};
  border-radius:10px;padding:12px 14px;}}
.mk-sig{{display:flex;align-items:center;gap:8px;margin-bottom:7px;}}
.mk-sig-dot{{width:6px;height:6px;border-radius:50%;flex-shrink:0;}}
.mk-sig-txt{{font-size:.7rem;color:{muted_val};}}
.mk-verdict{{
  grid-column:1/-1;text-align:center;padding:14px;
  background:color-mix(in srgb,{red_val} 12%,transparent);
  border:1px solid color-mix(in srgb,{red_val} 30%,transparent);
  border-radius:10px;font-weight:800;font-size:.82rem;color:{red_val};letter-spacing:.5px;
}}

/* ── Section dividers ── */
.sec-div{{border:none;border-bottom:1px solid {bord_val};margin:0;}}
.section{{padding:60px 32px;position:relative;z-index:1;}}

/* ── Section header ── */
.sec-head{{text-align:center;margin-bottom:40px;}}
.sec-eyebrow{{font-size:.7rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:{brand_val};margin-bottom:6px;}}
.sec-title{{
  font-size:1.9rem;font-weight:800;letter-spacing:-1px;line-height:1.2;
  background:linear-gradient(180deg,{text_val} 40%,{muted_val} 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.sec-sub{{color:{muted_val};font-size:.92rem;margin-top:6px;}}

/* ── Demo cards ── */
.demo-card{{
  background:{card_val};border:1px solid {bord_val};border-radius:20px;
  padding:28px 24px 22px;
  box-shadow:0 4px 24px rgba(0,0,0,.{"3" if DARK else "06"});
  max-width:900px;margin:0 auto;
}}
.demo-ey{{font-size:.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:22px;}}
.demo-ey.fake{{color:{red_val};}} .demo-ey.genuine{{color:{green_val};}}

.demo-flow{{display:grid;grid-template-columns:190px 1fr 152px 1fr 152px;
  align-items:flex-start;gap:0;min-height:160px;}}

.r-card{{
  background:color-mix(in srgb,{card2_val} 100%,transparent);
  border:1.5px solid {bord_val};border-radius:14px;
  padding:15px;box-shadow:0 4px 16px rgba(0,0,0,.{"3" if DARK else "07"});
  position:relative;transition:transform .3s,box-shadow .3s;
}}
.r-card:hover{{transform:translateY(-3px);box-shadow:0 8px 28px rgba(0,0,0,.{"5" if DARK else "12"});}}
.r-stars{{font-size:.88rem;margin-bottom:7px;}}
.r-txt{{font-size:.8rem;line-height:1.5;color:{muted_val};min-height:52px;}}
.r-txt.fake{{font-weight:800;color:{red_val};text-transform:uppercase;font-size:.75rem;}}
.r-meta{{margin-top:9px;font-size:.63rem;color:{muted_val};
  border-top:1px dashed {bord_val};padding-top:7px;}}

.beam{{position:relative;height:3px;align-self:flex-start;
  margin-top:68px;margin-left:6px;margin-right:6px;}}
.beam-line{{position:absolute;top:0;left:0;right:0;height:3px;border-radius:3px;
  background:linear-gradient(90deg,{bord_val},{brand_val},{bord_val});
  transform:scaleX(0);transform-origin:left;transition:transform .7s ease .5s;}}
.beam.go .beam-line{{transform:scaleX(1);}}
.bdot{{position:absolute;top:50%;transform:translateY(-50%);
  width:8px;height:8px;border-radius:50%;
  background:{brand_val};box-shadow:0 0 10px {brand_val};opacity:0;}}
.beam.go .bdot{{animation:bflow 1.3s linear infinite .7s;}}
.beam.go .bdot.b2{{animation-delay:1.1s;}} .beam.go .bdot.b3{{animation-delay:1.5s;}}
@keyframes bflow{{0%{{left:0%;opacity:0;}}10%{{opacity:1;}}90%{{opacity:1;}}100%{{left:100%;opacity:0;}}}}

.model-box{{
  background:linear-gradient(135deg,{card2_val},{bg_val});
  border:1px solid {bord_val};
  border-radius:16px;padding:18px 14px;
  text-align:center;color:{text_val};position:relative;overflow:hidden;
  box-shadow:0 8px 28px rgba(0,0,0,.{"4" if DARK else "15"});
  opacity:0;transform:scale(.85);
  transition:opacity .5s ease .45s,transform .5s cubic-bezier(.2,.8,.3,1) .45s;
}}
.model-box.go{{opacity:1;transform:scale(1);
  animation:mpulse 2.5s ease-in-out infinite 1s;}}
@keyframes mpulse{{
  0%,100%{{box-shadow:0 8px 28px rgba(0,0,0,.3),0 0 0 0 {brand_val}00;}}
  50%{{box-shadow:0 8px 44px rgba(0,0,0,.5),0 0 40px 0 {brand_val}44;}}
}}
.mglow{{position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 110%,{brand_val}44 0%,transparent 65%);
  pointer-events:none;}}
.mscan{{position:absolute;top:0;width:45%;height:100%;
  background:linear-gradient(90deg,transparent,{brand_val}44,transparent);left:-45%;}}
.model-box.go .mscan{{animation:scan 1.9s ease-in-out infinite 1s;}}
@keyframes scan{{0%{{left:-45%}}100%{{left:115%}}}}
.micon{{font-size:1.7rem;}} .mname{{font-size:.72rem;font-weight:800;margin-top:5px;letter-spacing:1px;}}
.msub{{font-size:.58rem;color:{muted_val};margin-top:2px;letter-spacing:.4px;}}

.verdict{{border-radius:14px;padding:18px 10px;text-align:center;font-weight:900;
  opacity:0;transform:scale(2.2) rotate(-14deg);
  transition:opacity .6s ease 1.55s,transform .6s cubic-bezier(.18,1.5,.4,1) 1.55s;}}
.verdict.go{{opacity:1;transform:scale(1) rotate(-4deg);}}
.verdict:hover{{transform:scale(1.06) rotate(-2deg)!important;transition:transform .25s ease!important;}}
.vicon{{font-size:1.9rem;}} .vword{{font-size:1.3rem;letter-spacing:2px;margin-top:3px;}}
.vconf{{font-size:.65rem;font-weight:700;margin-top:5px;opacity:.8;}}
.v-fake{{
  background:color-mix(in srgb,{red_val} 12%,transparent);
  color:{red_val};border:2.5px solid {red_val};
  box-shadow:0 5px 20px color-mix(in srgb,{red_val} 30%,transparent);
}}
.v-genuine{{
  background:color-mix(in srgb,{green_val} 12%,transparent);
  color:{green_val};border:2.5px solid {green_val};
  box-shadow:0 5px 20px color-mix(in srgb,{green_val} 20%,transparent);
}}
.flabel{{text-align:center;font-size:.64rem;font-weight:700;color:{muted_val};margin-top:8px;}}

.sigs{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px;justify-content:center;}}
.sigt{{font-size:.74rem;font-weight:600;padding:5px 12px;border-radius:100px;
  opacity:0;transform:translateY(8px);transition:all .4s cubic-bezier(.2,.8,.3,1);}}
.sigt.red{{background:color-mix(in srgb,{red_val} 12%,transparent);color:{red_val};
  border:1px solid color-mix(in srgb,{red_val} 35%,transparent);}}
.sigt.grn{{background:color-mix(in srgb,{green_val} 12%,transparent);color:{green_val};
  border:1px solid color-mix(in srgb,{green_val} 30%,transparent);}}
.sigs.go .sigt{{opacity:1;transform:translateY(0);}}
.sigs.go .sigt:nth-child(1){{transition-delay:1.05s;}}
.sigs.go .sigt:nth-child(2){{transition-delay:1.25s;}}
.sigs.go .sigt:nth-child(3){{transition-delay:1.45s;}}

/* ── Items grid (exact Launch UI) ── */
.items-grid{{display:grid;grid-template-columns:repeat(3,1fr);
  border:1px solid {bord_val};border-radius:14px;overflow:hidden;background:{card_val};
  max-width:900px;margin:0 auto;}}
.iitem{{padding:22px 20px;border-right:1px solid {bord_val};
  border-bottom:1px solid {bord_val};transition:background .2s;}}
.iitem:hover{{background:color-mix(in srgb,{brand_val} 8%,transparent);}}
.iitem:nth-child(3n){{border-right:none;}}
.iitem:nth-child(n+4){{border-bottom:none;}}
.iicon-wrap{{width:32px;height:32px;background:color-mix(in srgb,{brand_val} 15%,transparent);
  border-radius:7px;display:flex;align-items:center;justify-content:center;
  font-size:.88rem;margin-bottom:10px;}}
.ititle{{font-size:.87rem;font-weight:700;color:{text_val};margin-bottom:5px;display:flex;align-items:center;gap:8px;}}
.idesc{{font-size:.77rem;color:{muted_val};line-height:1.6;max-width:220px;}}

/* ── Stats ── */
.stats-grid{{display:grid;grid-template-columns:repeat(4,1fr);
  border:1px solid {bord_val};border-radius:14px;overflow:hidden;background:{card_val};
  max-width:900px;margin:0 auto;}}
.sstat{{padding:28px 20px;border-right:1px solid {bord_val};}}
.sstat:last-child{{border-right:none;}}
.sstat-lbl{{font-size:.72rem;font-weight:600;color:{muted_val};text-transform:uppercase;letter-spacing:.8px;}}
.sstat-row{{display:flex;align-items:baseline;gap:4px;margin:10px 0 4px;}}
.sstat-val{{
  font-size:2.9rem;font-weight:700;line-height:1;
  background:linear-gradient(180deg,{text_val} 0%,{brand_val} 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 20px {glow_val});
}}
.sstat-sfx{{font-size:1.3rem;font-weight:700;color:{brand_val};}}
.sstat-desc{{font-size:.75rem;color:{muted_val};font-weight:500;}}

/* ── Tech chips ── */
.tech-row{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;}}
.tchip{{
  background:{card_val};border:1px solid {bord_val};border-radius:8px;
  padding:6px 14px;font-size:.79rem;font-weight:600;color:{muted_val};
  transition:border-color .2s,color .2s;cursor:default;
}}
.tchip:hover{{border-color:{brand_val};color:{brand_val};}}

.foot{{text-align:center;padding:24px 0 8px;font-size:.73rem;color:{muted_val};}}

/* Particle */
.fparticle{{position:fixed;font-size:.69rem;font-weight:700;
  background:{brand_val};color:{bg_val};padding:2px 8px;border-radius:6px;
  pointer-events:none;z-index:9999;white-space:nowrap;
  box-shadow:0 2px 12px {brand_val}88;}}
</style>
</head>
<body>

<!-- Navbar -->
<nav class="nav reveal show">
  <div class="nav-logo"><div class="nav-dot"></div>ReviewGuard</div>
  <div class="nav-links">
    <a class="nav-link" href="#">Detect</a>
    <a class="nav-link" href="#">Recommendations</a>
    <a class="nav-link" href="#">Timeline</a>
  </div>
</nav>

<!-- Hero -->
<div class="hero" style="padding-bottom:0">
  <div class="hero-glow"></div>
  <div class="badge-outline reveal show"><div class="badge-dot"></div>AI-Powered Fake Review Detection</div>
  <h1 class="hero-title reveal show d1">How ReviewGuard Works</h1>
  <p class="hero-sub reveal show d2">A review enters. AI scans 17 signals. Verdict in milliseconds. Every decision explained.</p>
  <div class="hero-btns reveal show d3">
    <span class="btn-d">&#9654; See Detection</span>
    <span class="btn-glow">View Source</span>
  </div>

  <!-- Mockup (Launch UI MockupFrame style) -->
  <div class="mockup-frame reveal-zoom show d4" style="margin-bottom:-2px">
    <div class="mockup-inner">
      <div class="mockup-bar">
        <div class="mb-dot" style="background:#ff5f57"></div>
        <div class="mb-dot" style="background:#febc2e;margin:0 5px"></div>
        <div class="mb-dot" style="background:#28c840"></div>
        <div class="mb-url">reviewguard.ai/detect</div>
      </div>
      <div class="mockup-body">
        <div class="mk-card"><div class="mk-label">Analyzed</div><div class="mk-val">2,847</div>
          <div class="mk-bar"><div class="mk-fill" style="width:100%"></div></div></div>
        <div class="mk-card"><div class="mk-label">Fake</div><div class="mk-val r">312</div>
          <div class="mk-bar"><div class="mk-fill" style="width:11%;background:linear-gradient(90deg,{red_val},{red_val}88)"></div></div></div>
        <div class="mk-card"><div class="mk-label">Genuine</div><div class="mk-val g">2,535</div>
          <div class="mk-bar"><div class="mk-fill" style="width:89%;background:linear-gradient(90deg,{green_val},{green_val}88)"></div></div></div>
        <div class="mk-card"><div class="mk-label">Fake Rate</div><div class="mk-val o">11.0%</div>
          <div class="mk-bar"><div class="mk-fill" style="width:11%"></div></div></div>
        <div class="mk-row">
          <div style="font-size:.65rem;font-weight:700;color:{muted_val};text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;">Latest Verdict</div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:{red_val}"></div><div class="mk-sig-txt">&#128681; 87% UPPERCASE text (normal &lt;5%)</div></div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:{red_val}"></div><div class="mk-sig-txt">&#128681; Account only 2 days old</div></div>
          <div class="mk-sig"><div class="mk-sig-dot" style="background:{red_val}"></div><div class="mk-sig-txt">&#128681; Not a verified purchase</div></div>
        </div>
        <div class="mk-verdict">&#128683; FAKE REVIEW DETECTED &mdash; 94% CONFIDENCE</div>
      </div>
    </div>
  </div>
</div>

<hr class="sec-div">

<!-- Demo 1 -->
<div class="section">
<div class="demo-card reveal" id="demo1">
  <div class="demo-ey fake">&#128681; Example &mdash; Suspicious Review</div>
  <div class="demo-flow">
    <div>
      <div class="r-card" id="rc1">
        <div class="r-stars">&#11088;&#11088;&#11088;&#11088;&#11088;</div>
        <div class="r-txt fake">BEST PRODUCT EVER!!! AMAZING!!! BUY NOW!!!</div>
        <div class="r-meta">&#128100; 2 reviews &middot; 3-day account &middot; &#10007; not verified</div>
      </div>
      <div class="flabel">&#9312; Review comes in</div>
    </div>
    <div class="beam" id="bm1a"><div class="beam-line"></div>
      <div class="bdot"></div><div class="bdot b2"></div><div class="bdot b3"></div></div>
    <div>
      <div class="model-box" id="mb1">
        <div class="mglow"></div><div class="mscan"></div>
        <div class="micon">&#129504;</div><div class="mname">AI MODEL</div>
        <div class="msub">17 SIGNALS</div>
      </div>
      <div class="flabel">&#9313; AI Analyzes</div>
    </div>
    <div class="beam" id="bm1b"><div class="beam-line"></div>
      <div class="bdot"></div><div class="bdot b2"></div><div class="bdot b3"></div></div>
    <div>
      <div class="verdict v-fake" id="vd1">
        <div class="vicon">&#128683;</div><div class="vword">FAKE</div>
        <div class="vconf">94% confidence</div>
      </div>
      <div class="flabel">&#9314; Verdict</div>
    </div>
  </div>
  <div class="sigs" id="sg1">
    <span class="sigt red">&#128681; 90% UPPERCASE text</span>
    <span class="sigt red">&#128681; brand-new 3-day account</span>
    <span class="sigt red">&#128681; not a verified purchase</span>
  </div>
</div>
</div>

<!-- Demo 2 -->
<div class="section" style="padding-top:0">
<div class="demo-card reveal" id="demo2">
  <div class="demo-ey genuine">&#10003; Example &mdash; Real Customer Review</div>
  <div class="demo-flow">
    <div>
      <div class="r-card" id="rc2">
        <div class="r-stars">&#11088;&#11088;&#11088;&#11088;</div>
        <div class="r-txt">Bought 3 weeks ago. Battery ~18h, noise cancelling handles office perfectly.</div>
        <div class="r-meta">&#128100; 47 reviews &middot; 2yr account &middot; &#10003; verified</div>
      </div>
      <div class="flabel">&#9312; Review comes in</div>
    </div>
    <div class="beam" id="bm2a"><div class="beam-line"></div>
      <div class="bdot"></div><div class="bdot b2"></div><div class="bdot b3"></div></div>
    <div>
      <div class="model-box" id="mb2">
        <div class="mglow"></div><div class="mscan"></div>
        <div class="micon">&#129504;</div><div class="mname">AI MODEL</div>
        <div class="msub">17 SIGNALS</div>
      </div>
      <div class="flabel">&#9313; AI Analyzes</div>
    </div>
    <div class="beam" id="bm2b"><div class="beam-line"></div>
      <div class="bdot"></div><div class="bdot b2"></div><div class="bdot b3"></div></div>
    <div>
      <div class="verdict v-genuine" id="vd2">
        <div class="vicon">&#10003;</div><div class="vword">GENUINE</div>
        <div class="vconf">8% fake risk</div>
      </div>
      <div class="flabel">&#9314; Verdict</div>
    </div>
  </div>
  <div class="sigs" id="sg2">
    <span class="sigt grn">&#10003; verified purchase</span>
    <span class="sigt grn">&#10003; 47 total reviews</span>
    <span class="sigt grn">&#10003; natural language</span>
  </div>
</div>
</div>

<hr class="sec-div">

<!-- Items -->
<div class="section">
  <div class="sec-head reveal">
    <div class="sec-eyebrow">System Design</div>
    <div class="sec-title">Everything that makes it work</div>
    <div class="sec-sub">Six layers of analysis working together.</div>
  </div>
  <div class="items-grid">
    <div class="iitem reveal d1">
      <div class="iicon-wrap">&#128300;</div>
      <div class="ititle">17 Extracted Signals</div>
      <div class="idesc">9 text signals + 8 behavioral signals from reviewer history, combined into one score.</div>
    </div>
    <div class="iitem reveal d2">
      <div class="iicon-wrap">&#129504;</div>
      <div class="ititle">Gradient Boosting ML</div>
      <div class="idesc">Trained on 2,000 labeled reviews. 97%+ AUC on held-out validation data.</div>
    </div>
    <div class="iitem reveal d3">
      <div class="iicon-wrap">&#128161;</div>
      <div class="ititle">Explainable Verdicts</div>
      <div class="idesc">Not a black box — every verdict shows the exact signals that triggered it.</div>
    </div>
    <div class="iitem reveal d4">
      <div class="iicon-wrap">&#128202;</div>
      <div class="ititle">Honest Recommendations</div>
      <div class="idesc">Bayesian scoring removes fake reviews before any product gets ranked.</div>
    </div>
    <div class="iitem reveal d5">
      <div class="iicon-wrap">&#128225;</div>
      <div class="ititle">Bombing Detection</div>
      <div class="idesc">Coordinated 48-hour fake spikes flagged as timeline anomalies in real time.</div>
    </div>
    <div class="iitem reveal d6">
      <div class="iicon-wrap">&#9889;</div>
      <div class="ititle">Real-Time API</div>
      <div class="idesc">FastAPI backend returns a full verdict + explanation in milliseconds.</div>
    </div>
  </div>
</div>

<hr class="sec-div">

<!-- Stats -->
<div class="section">
  <div class="stats-grid">
    <div class="sstat reveal">
      <div class="sstat-lbl">scans</div>
      <div class="sstat-row"><div class="sstat-val" data-val="17">0</div></div>
      <div class="sstat-desc">signals per review</div>
    </div>
    <div class="sstat reveal d1">
      <div class="sstat-lbl">trained on</div>
      <div class="sstat-row"><div class="sstat-val" data-val="2000">0</div></div>
      <div class="sstat-desc">labeled reviews</div>
    </div>
    <div class="sstat reveal d2">
      <div class="sstat-lbl">achieved</div>
      <div class="sstat-row"><div class="sstat-val" data-val="97">0</div><div class="sstat-sfx">%</div></div>
      <div class="sstat-desc">AUC score</div>
    </div>
    <div class="sstat reveal d3">
      <div class="sstat-lbl">across</div>
      <div class="sstat-row"><div class="sstat-val" data-val="6">0</div></div>
      <div class="sstat-desc">pipeline stages</div>
    </div>
  </div>
</div>

<!-- Tech -->
<div class="section" style="padding-top:24px;padding-bottom:40px;">
  <div class="tech-row reveal">
    <span class="tchip">Python</span><span class="tchip">FastAPI</span>
    <span class="tchip">scikit-learn</span><span class="tchip">Gradient Boosting</span>
    <span class="tchip">TextBlob</span><span class="tchip">Streamlit</span>
    <span class="tchip">Plotly</span><span class="tchip">SQLAlchemy</span>
  </div>
  <div class="foot">Based on research by Jindal &amp; Liu (2008) &middot; Lim et al. (2010) &middot; Yelp Polarity Dataset</div>
</div>

<script>
/* ── Reveal on scroll ── */
const revObs = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting) e.target.classList.add('show'); }});
}}, {{threshold:0.1}});
document.querySelectorAll('.reveal,.reveal-zoom').forEach(el => revObs.observe(el));

/* ── Demo activation ── */
function activateDemo(demo, cardId, particles) {{
  demo.querySelectorAll('.beam').forEach(b=>b.classList.add('go'));
  demo.querySelectorAll('.model-box').forEach(m=>m.classList.add('go'));
  demo.querySelectorAll('.verdict').forEach(v=>v.classList.add('go'));
  demo.querySelectorAll('.sigs').forEach(s=>s.classList.add('go'));
  setTimeout(()=>{{
    const card  = document.getElementById(cardId);
    const model = demo.querySelector('.model-box');
    if(!card||!model) return;
    particles.forEach((txt,i) => setTimeout(()=>spawnParticle(txt,card,model), i*300));
  }}, 400);
}}
function spawnParticle(text,fromEl,toEl) {{
  const fr=fromEl.getBoundingClientRect(), tr=toEl.getBoundingClientRect();
  const p=document.createElement('div'); p.className='fparticle'; p.textContent=text;
  p.style.left=(fr.left+fr.width*.4)+'px'; p.style.top=(fr.top+fr.height*.4)+'px';
  document.body.appendChild(p);
  const dx=tr.left+tr.width/2-(fr.left+fr.width*.4)-20;
  const dy=tr.top+tr.height/2-(fr.top+fr.height*.4);
  p.animate([
    {{transform:'translate(0,0) scale(1)',opacity:1}},
    {{transform:`translate(${{dx}}px,${{dy}}px) scale(0.15)`,opacity:0}}
  ],{{duration:750,easing:'ease-in',fill:'forwards'}}).onfinish=()=>p.remove();
}}
const demoObs = new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting){{
      if(e.target.id==='demo1') activateDemo(e.target,'rc1',['AMAZING!!!','BUY NOW','!!!!!']);
      if(e.target.id==='demo2') activateDemo(e.target,'rc2',['battery life','verified ✓','47 reviews']);
      demoObs.unobserve(e.target);
    }}
  }});
}},{{threshold:0.4}});
document.querySelectorAll('#demo1,#demo2').forEach(el=>demoObs.observe(el));

/* ── Counter animation ── */
function animCount(el,target,ms){{
  let v=0; const step=target/(ms/16);
  const t=setInterval(()=>{{ v=Math.min(v+step,target); el.textContent=Math.floor(v);
    if(v>=target) clearInterval(t); }},16);
}}
const cntObs=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{ if(e.isIntersecting){{
    animCount(e.target,parseInt(e.target.dataset.val),1000);
    cntObs.unobserve(e.target);
  }}}});
}},{{threshold:0.6}});
document.querySelectorAll('[data-val]').forEach(el=>cntObs.observe(el));
</script>
</body>
</html>
""", height=2400, scrolling=True)
