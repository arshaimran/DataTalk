import streamlit as st
import pandas as pd
from google import genai
from dotenv import load_dotenv
import os, json, io, re, base64, html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
st.set_page_config(page_title="DataTalk", page_icon="🟢", layout="wide", initial_sidebar_state="collapsed")

# ── SVG doodle pattern (bar/line chart icons, WhatsApp-style) ─────────────────
DOODLE_SVG = """<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'>
  <!-- bar chart doodle -->
  <rect x='8' y='28' width='5' height='12' rx='1' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <rect x='15' y='22' width='5' height='18' rx='1' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <rect x='22' y='18' width='5' height='22' rx='1' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <rect x='29' y='25' width='5' height='15' rx='1' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <line x1='7' y1='41' x2='35' y2='41' stroke='%23C8CCC3' stroke-width='1' stroke-linecap='round'/>
  <!-- line chart doodle -->
  <polyline points='65,38 72,30 79,34 86,20 93,26 100,16' fill='none' stroke='%23C8CCC3' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/>
  <circle cx='65' cy='38' r='2' fill='%23C8CCC3'/>
  <circle cx='86' cy='20' r='2' fill='%23C8CCC3'/>
  <circle cx='100' cy='16' r='2' fill='%23C8CCC3'/>
  <!-- pie doodle -->
  <circle cx='20' cy='85' r='14' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <path d='M20,85 L20,71 A14,14 0 0,1 31,92 Z' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <path d='M20,85 L31,92 A14,14 0 0,1 6,92 Z' fill='none' stroke='%23C8CCC3' stroke-width='1.2'/>
  <!-- scatter doodle -->
  <circle cx='72' cy='80' r='2' fill='%23C8CCC3'/>
  <circle cx='78' cy='72' r='2' fill='%23C8CCC3'/>
  <circle cx='85' cy='75' r='2' fill='%23C8CCC3'/>
  <circle cx='80' cy='85' r='2' fill='%23C8CCC3'/>
  <circle cx='90' cy='68' r='2' fill='%23C8CCC3'/>
  <circle cx='95' cy='78' r='2' fill='%23C8CCC3'/>
  <circle cx='68' cy='88' r='2' fill='%23C8CCC3'/>
</svg>"""

DOODLE_B64 = base64.b64encode(DOODLE_SVG.encode()).decode()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

:root{{
  --bg:#EDEEE9; --surf:#FFFFFF; --surf2:#F5F6F2;
  --bdr:#D8DCD3; --bdr2:#C4C8BF;
  --g:#1A6B45; --gl:#EAF3EE; --gm:#BFDECE;
  --ink:#0C0E0C; --ink2:#343730; --sub:#585B54; --dim:#9A9E95;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html,body,[class*="css"]{{
  font-family:'IBM Plex Sans',sans-serif !important;
  background:var(--bg) !important; color:var(--ink) !important;
}}
[data-testid="collapsedControl"],[data-testid="stSidebar"],
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"]
{{display:none !important;visibility:hidden !important}}
.block-container{{padding:0 !important;max-width:100% !important}}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{{background:var(--bg) !important}}

/* TOPBAR */
.tb{{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  height:50px;background:var(--surf);border-bottom:1px solid var(--bdr);
  display:flex;align-items:center;justify-content:space-between;padding:0 20px;
}}
.tb-logo{{
  font-family:'Syne',sans-serif;font-weight:800;font-size:1.05rem;
  color:var(--ink);display:flex;align-items:center;gap:8px;letter-spacing:-.02em;
}}
.tb-icon{{
  width:26px;height:26px;background:var(--g);border-radius:6px;
  display:flex;align-items:center;justify-content:center;
}}
.tb-logo em{{color:var(--g);font-style:normal}}
.tb-r{{display:flex;align-items:center;gap:8px}}
.tb-file{{
  background:var(--bg);border:1px solid var(--bdr);border-radius:20px;
  padding:3px 11px;font-size:.72rem;color:var(--sub);
  display:flex;align-items:center;gap:5px;
}}
.tb-file b{{color:var(--ink2);font-weight:600}}
.tb-chip{{
  background:var(--gl);border:1px solid var(--gm);color:var(--g);
  font-size:.62rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  padding:2px 8px;border-radius:20px;
}}

/* DOODLE BG — applied directly to the right Streamlit column */
[data-testid="stMain"] > div > div > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child,
section.main > div > div > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child{{
  background-color:var(--bg) !important;
  background-image:url("data:image/svg+xml;base64,{DOODLE_B64}") !important;
  background-size:120px 120px !important;
  background-repeat:repeat !important;
  min-height:calc(100vh - 50px) !important;
  padding-bottom:80px !important;
}}
/* keep the .chat-bg class for the wrapper div (no-op now, harmless) */
.chat-bg{{ background:transparent; }}

/* Empty state — centre it properly */
.empty{{
  display:flex;flex-direction:column;align-items:center;
  justify-content:center;padding-top:25vh;
  gap:10px;text-align:center;
}}

/* LEFT PANEL — style the actual Streamlit column, not a fake wrapper div */
[data-testid="stMain"] > div > div > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child,
section.main > div > div > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child{{
  background:var(--surf) !important;
  border-right:1px solid var(--bdr) !important;
  min-height:calc(100vh - 50px) !important;
  overflow-y:auto !important;
  padding:14px 14px 20px !important;
}}
.lp-section{{padding:14px 14px 0}}
.lp-label{{
  font-size:.62rem;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:var(--dim);margin-bottom:7px;
  display:block;
}}
.lp-file{{margin-bottom:12px}}
.lp-filename{{
  font-size:.82rem;font-weight:600;color:var(--ink);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  margin-bottom:2px;
}}
.lp-filemeta{{font-size:.7rem;color:var(--sub)}}
.sc-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-bottom:12px}}
.sc{{background:var(--surf2);border:1px solid var(--bdr);border-radius:7px;padding:7px 9px}}
.sc-v{{font-family:'Syne',sans-serif;font-size:1.05rem;font-weight:700;color:var(--ink)}}
.sc-l{{font-size:.6rem;color:var(--dim);text-transform:uppercase;letter-spacing:.05em;margin-top:1px}}
.div{{height:1px;background:var(--bdr);margin:10px 0}}
.ctags{{display:flex;flex-direction:column;gap:3px;max-height:200px;overflow-y:auto}}
.ct{{
  padding:4px 8px;border-radius:5px;font-size:.7rem;
  font-family:'IBM Plex Mono',monospace;font-weight:500;
  background:var(--surf2);border:1px solid var(--bdr);color:var(--sub);
  display:flex;align-items:center;justify-content:space-between;
}}
.ct.n{{background:var(--gl);border-color:var(--gm);color:var(--g)}}
.ct-type{{font-size:.58rem;opacity:.6}}

/* FIX: hint buttons — deep selector beats global .stButton>button */
div[data-testid="stVerticalBlock"] .hint-btn div[data-testid="stButton"] button,
.hint-btn div[data-testid="stButton"] button,
.hint-btn button{{
  background:var(--surf2) !important;border:1px solid var(--bdr) !important;
  border-radius:6px !important;padding:6px 9px !important;
  font-size:.74rem !important;color:var(--ink2) !important;
  line-height:1.35 !important;text-align:left !important;
  width:100% !important;height:auto !important;min-height:32px !important;
  font-family:'IBM Plex Sans',sans-serif !important;
  white-space:normal !important;opacity:1 !important;
  transition:border-color .14s,background .14s !important;
}}
div[data-testid="stVerticalBlock"] .hint-btn div[data-testid="stButton"] button:hover,
.hint-btn div[data-testid="stButton"] button:hover,
.hint-btn button:hover{{
  border-color:var(--g) !important;background:var(--gl) !important;
  color:var(--g) !important;opacity:1 !important;
}}

/* FIX: ghost style for Clear / New file buttons */
div[data-testid="stVerticalBlock"] .ghost-btn div[data-testid="stButton"] button,
.ghost-btn div[data-testid="stButton"] button,
.ghost-btn button{{
  background:transparent !important;color:var(--sub) !important;
  border:1px solid var(--bdr) !important;font-size:.74rem !important;
  padding:.3rem .8rem !important;height:28px !important;width:100% !important;
  font-family:'IBM Plex Sans',sans-serif !important;opacity:1 !important;
}}
div[data-testid="stVerticalBlock"] .ghost-btn div[data-testid="stButton"] button:hover,
.ghost-btn div[data-testid="stButton"] button:hover,
.ghost-btn button:hover{{
  color:var(--ink) !important;border-color:var(--ink2) !important;
  background:transparent !important;opacity:1 !important;
}}

/* MESSAGES */
.msgs{{display:flex;flex-direction:column;gap:12px;padding:20px 20px 100px}}
.mrow{{display:flex;gap:9px;align-items:flex-start;animation:fu .22s ease}}
.mrow.u{{flex-direction:row-reverse}}
@keyframes fu{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:none}}}}
.av{{
  width:28px;height:28px;border-radius:50%;flex-shrink:0;margin-top:2px;
  display:flex;align-items:center;justify-content:center;
}}
.av.bot{{background:var(--g)}}
.av.usr{{background:var(--ink);font-size:.62rem;font-weight:700;color:#fff;font-family:'IBM Plex Sans',sans-serif}}
.bub{{
  max-width:70%;padding:.72rem 1rem;
  border-radius:14px;font-size:.84rem;line-height:1.62;
}}
.bub.bot{{
  background:var(--surf);border:1px solid var(--bdr);
  border-bottom-left-radius:3px;color:var(--ink);
  box-shadow:0 1px 5px rgba(0,0,0,.06);
}}
.bub.usr{{background:var(--ink);color:#F2F3EF;border-bottom-right-radius:3px}}
.bub b,.bub strong{{color:var(--g);font-weight:600}}

/* Typing */
.tyd{{display:inline-block;width:5px;height:5px;border-radius:50%;background:var(--g);margin:0 2px;animation:td .8s infinite}}
.tyd:nth-child(2){{animation-delay:.13s}}.tyd:nth-child(3){{animation-delay:.26s}}
@keyframes td{{0%,60%,100%{{transform:translateY(0);opacity:.3}}30%{{transform:translateY(-4px);opacity:1}}}}

/* Chart card */
.cc{{
  background:var(--surf);border:1px solid var(--bdr);border-radius:11px;
  overflow:hidden;margin:.5rem 0 0 37px;max-width:580px;
  box-shadow:0 1px 7px rgba(0,0,0,.07);
}}
.cc-hd{{
  display:flex;align-items:center;justify-content:space-between;
  padding:9px 12px;border-bottom:1px solid var(--bdr);background:var(--surf2);
}}
.cc-title{{font-size:.75rem;font-weight:600;color:var(--ink2);display:flex;align-items:center;gap:4px}}
.cc-dl{{
  font-size:.68rem;color:var(--g);font-weight:600;
  background:var(--gl);border:1px solid var(--gm);
  padding:2px 8px;border-radius:5px;text-decoration:none;
}}
.cc-dl:hover{{background:var(--gm)}}
.cc-img{{padding:10px 12px 8px}}

.empty-icon{{
  width:48px;height:48px;background:var(--surf);border:1px solid var(--bdr);
  border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;
}}
.empty-h{{font-family:'Syne',sans-serif;font-weight:700;font-size:.96rem;color:var(--ink)}}
.empty-s{{font-size:.78rem;color:var(--sub);max-width:280px;line-height:1.5}}

/* INPUT BAR */
.ibar-wrap{{
  position:sticky;bottom:0;z-index:100;
  background:linear-gradient(to top,var(--bg) 70%,transparent);
  padding:10px 16px 14px;
}}
.ibar{{
  background:var(--surf);border:1.5px solid var(--bdr);
  border-radius:10px;padding:5px 5px 5px 12px;
  display:flex;align-items:center;gap:6px;
  box-shadow:0 2px 12px rgba(0,0,0,.09);
  transition:border-color .14s;
}}
.ibar:focus-within{{border-color:var(--g);box-shadow:0 0 0 3px rgba(26,107,69,.08)}}
.stTextInput{{flex:1}}
.stTextInput>div{{margin:0 !important}}
.stTextInput>div>div>input{{
  border:none !important;outline:none !important;box-shadow:none !important;
  background:transparent !important;font-family:'IBM Plex Sans',sans-serif !important;
  font-size:.85rem !important;color:var(--ink) !important;padding:.32rem 0 !important;
}}
.stTextInput>div>div>input::placeholder{{color:var(--dim) !important;opacity:1 !important}}
.stTextInput>div>div{{background:transparent !important;border:none !important;padding:0 !important}}
.stButton>button{{
  background:var(--g) !important;color:#fff !important;border:none !important;
  border-radius:7px !important;padding:.38rem 1rem !important;
  font-family:'IBM Plex Sans',sans-serif !important;
  font-weight:600 !important;font-size:.81rem !important;white-space:nowrap !important;
  height:34px !important;transition:opacity .12s !important;
}}
.stButton>button:hover{{opacity:.84 !important}}

/* Streamlit col gap fix */
[data-testid="stHorizontalBlock"]{{gap:0 !important}}
[data-testid="stColumn"]:first-child{{padding-right:0 !important}}
[data-testid="stColumn"]:last-child{{padding-left:0 !important}}

/* Expander */
[data-testid="stExpander"]{{
  background:var(--surf2) !important;border:1px solid var(--bdr) !important;
  border-radius:8px !important;overflow:hidden;
}}
[data-testid="stExpander"] summary{{font-size:.76rem !important;color:var(--sub) !important;padding:8px 12px !important}}
[data-testid="stExpander"] p,[data-testid="stExpander"] span{{color:var(--ink) !important;font-size:.78rem !important}}

/* Scrollbar */
::-webkit-scrollbar{{width:3px}}
::-webkit-scrollbar-thumb{{background:var(--bdr2);border-radius:4px}}
.stSpinner>div{{border-top-color:var(--g) !important}}

/* LANDING — background on the main app container, card in normal flow */
.land-page [data-testid="stAppViewContainer"],
.land-page [data-testid="stMain"]{{
  background-color:var(--bg) !important;
  background-image:url("data:image/svg+xml;base64,{DOODLE_B64}") !important;
  background-size:120px 120px !important;
}}
.land-wrap{{
  display:flex;align-items:center;justify-content:center;
  min-height:calc(100vh - 90px);padding:20px;
}}
.land-inner{{
  background:var(--surf);border:1px solid var(--bdr);border-radius:20px;
  padding:36px 36px 24px;max-width:420px;width:100%;
  box-shadow:0 4px 24px rgba(0,0,0,.08);text-align:center;
}}
.land-logo{{
  width:44px;height:44px;background:var(--g);border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 16px;
}}
.land-h{{
  font-family:'Syne',sans-serif;font-weight:800;font-size:1.8rem;
  color:var(--ink);letter-spacing:-.03em;line-height:1.08;margin-bottom:8px;
}}
.land-h em{{color:var(--g);font-style:normal}}
.land-s{{font-size:.84rem;color:var(--sub);line-height:1.6;margin-bottom:20px}}

/* LANDING uploader card */
.styled-uploader{{
  margin-top:0;
}}
.styled-uploader [data-testid="stFileUploader"] label{{
  display:none !important;
}}
.styled-uploader [data-testid="stFileUploader"] section,
.styled-uploader [data-testid="stFileUploaderDropzone"]{{
  background:var(--surf2) !important;
  border:1.5px dashed var(--gm) !important;
  border-radius:12px !important;
  padding:24px 16px !important;
  cursor:pointer !important;
  transition:border-color .2s,background .2s !important;
}}
.styled-uploader [data-testid="stFileUploaderDropzone"]:hover,
.styled-uploader [data-testid="stFileUploader"] section:hover{{
  border-color:var(--g) !important;
  background:var(--gl) !important;
}}
/* Hide Streamlit's own instructions text and browse button */
.styled-uploader [data-testid="stFileUploaderDropzoneInstructions"]{{
  display:none !important;
}}
.styled-uploader small{{display:none !important}}
.styled-uploader [data-testid="stBaseButton-secondary"]{{display:none !important}}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
LOGO = """<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
  <rect x="1.5" y="8" width="3" height="6.5" rx="1" fill="white" opacity="0.5"/>
  <rect x="6.5" y="5" width="3" height="9.5" rx="1" fill="white" opacity="0.75"/>
  <rect x="11.5" y="1.5" width="3" height="13" rx="1" fill="white"/>
</svg>"""
LOGO_LG = """<svg width="22" height="22" viewBox="0 0 22 22" fill="none">
  <rect x="2" y="11" width="4" height="9" rx="1.5" fill="white" opacity="0.5"/>
  <rect x="9" y="7" width="4" height="13" rx="1.5" fill="white" opacity="0.75"/>
  <rect x="16" y="2" width="4" height="18" rx="1.5" fill="white"/>
</svg>"""
HINTS = [
    "Top 10 categories by value?",
    "Show salary distribution",
    "Trend over time",
    "Compare averages across groups",
    "Any outliers in this data?",
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def get_summary(df):
    return f"""DATASET: {len(df)} rows, {len(df.columns)} columns
Columns: {', '.join(df.columns)}
Types:\n{df.dtypes.to_string()}
Sample (first 5):\n{df.head(5).to_string()}
Stats:\n{df.describe().to_string()}"""

def ask_ai(q, summary, history):
    hist = "".join(f"{'User' if m['role']=='user' else 'AI'}: {m['content']}\n" for m in history[-6:])
    prompt = f"""You are DataTalk, a professional data analyst AI. You have the user's CSV.

{summary}

Recent chat:
{hist}
User: {q}

Rules:
1. Be specific with real numbers. Surface genuinely interesting insights.
2. Mark key numbers/terms with **double asterisks** ONLY — no HTML tags, no other formatting.
3. Keep the answer to 2-4 sentences max. Concise wins.
4. Suggest a chart only if it clearly adds value.

Reply ONLY as valid JSON (no code fences):
{{"answer":"Concise answer with **bold** key stats. Max 4 sentences.","chart":{{"type":"bar|line|scatter|pie|hist|none","x":"column_or_null","y":"column_or_null","title":"Descriptive chart title"}}}}"""
    r = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    # FIX: strip code fences safely — only from the first and last line,
    # not from every line (avoids corrupting JSON values that contain backticks)
    text = r.text.strip()
    lines = text.split('\n')
    if lines[0].startswith('```'):
        lines = lines[1:]
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
    text = '\n'.join(lines).strip()

    try:
        return json.loads(text)
    except Exception:
        return {"answer": r.text.strip(), "chart": {"type": "none"}}

def render_bold(text):
    """Safely convert **text** to <b> — no HTML injection."""
    safe = html.escape(str(text))
    safe = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', safe)
    safe = safe.replace('\n', '<br>')
    return safe

def make_chart(df, spec):
    ct = spec.get("type", "none")
    if ct == "none":
        return None
    cols = df.columns.tolist()
    x = spec.get("x") if spec.get("x") in cols else None
    y = spec.get("y") if spec.get("y") in cols else None
    title = spec.get("title", "")
    C1, C2 = '#1A6B45', '#5BB88A'
    BG, GRID, INK, SUB = '#FFFFFF', '#EAEBE6', '#0C0E0C', '#585B54'
    plt.rcParams.update({
        'font.family': 'sans-serif', 'font.size': 9,
        'axes.facecolor': BG, 'figure.facecolor': BG,
        'grid.color': GRID, 'grid.linewidth': .8, 'axes.axisbelow': True,
        'axes.labelcolor': SUB, 'xtick.color': INK, 'ytick.color': INK, 'text.color': INK,
    })
    fig, ax = plt.subplots(figsize=(7.8, 3.6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    try:
        if ct == "bar" and x and y:
            d = df.groupby(x)[y].mean().reset_index().sort_values(y, ascending=False)
            if len(d) > 14:
                d = d.head(14)
            cs = [C1 if i == 0 else C2 for i in range(len(d))]
            bars = ax.bar(d[x].astype(str), d[y], color=cs, width=.6, zorder=2, edgecolor=BG, linewidth=.6)
            for bar in bars:
                h = bar.get_height()
                lbl = f'${h/1000:.0f}K' if h >= 1000 else f'{h:.1f}'
                ax.text(bar.get_x() + bar.get_width() / 2., h * 1.01, lbl,
                        ha='center', va='bottom', fontsize=7.8, color=INK, fontweight='600')
            plt.xticks(rotation=35, ha='right', fontsize=8.5, color=INK)
            ax.set_xlabel(x, fontsize=9, color=SUB, labelpad=5)
            ax.set_ylabel(y, fontsize=9, color=SUB, labelpad=5)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, p: f'${v/1000:.0f}K' if v >= 1000 else f'{v:.0f}'))

        elif ct == "line" and x and y:
            d = df[[x, y]].dropna().sort_values(x)
            xs = range(len(d))
            vals = d[y].values
            ax.fill_between(xs, vals, alpha=.08, color=C1)
            ax.plot(xs, vals, color=C1, linewidth=2.3, zorder=3, solid_capstyle='round')
            ax.scatter([0, len(d) - 1], [vals[0], vals[-1]], color=C1, s=45, zorder=4, edgecolors=BG, linewidth=1.5)
            step = max(1, len(d) // 7)
            ax.set_xticks(list(xs)[::step])
            ax.set_xticklabels(d[x].astype(str).iloc[::step], rotation=35, ha='right', fontsize=8.5, color=INK)
            ax.set_ylabel(y, fontsize=9, color=SUB)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda v, p: f'${v/1000:.0f}K' if v >= 1000 else f'{v:.0f}'))

        elif ct == "scatter" and x and y:
            ax.scatter(df[x], df[y], color=C1, alpha=.4, s=26, edgecolors='none', zorder=2)
            try:
                z = np.polyfit(df[x].dropna(), df[y].dropna(), 1)
                p = np.poly1d(z)
                xl = np.linspace(df[x].min(), df[x].max(), 100)
                ax.plot(xl, p(xl), color=C2, linewidth=1.4, linestyle='--', alpha=.7)
            except Exception:
                pass
            ax.set_xlabel(x, fontsize=9, color=SUB)
            ax.set_ylabel(y, fontsize=9, color=SUB)

        elif ct == "pie" and x:
            d = df.groupby(x)[y].sum() if y else df[x].value_counts()
            if len(d) > 7:
                d = d.nlargest(7)
            pal = ['#1A6B45', '#2E8A5A', '#4AAE7C', '#72C99B', '#A3DEC0', '#C5EDD8', '#E4F0EB']
            w, t, a = ax.pie(d.values, labels=d.index.astype(str), autopct='%1.1f%%',
                             colors=pal[:len(d)], startangle=130,
                             textprops={'fontsize': 8.5, 'color': INK},
                             pctdistance=.8, wedgeprops={'linewidth': 2, 'edgecolor': BG})
            for ai in a:
                ai.set_color(BG)
                ai.set_fontweight('600')

        elif ct == "hist" and x:
            vals = df[x].dropna()
            n, bins, patches = ax.hist(vals, bins=28, edgecolor=BG, linewidth=.4, zorder=2)
            norm = plt.Normalize(n.min(), n.max())
            for pb, val in zip(patches, n):
                pb.set_facecolor(plt.cm.Greens(.3 + norm(val) * .6))
            ax.axvline(vals.mean(), color=C1, lw=1.4, ls='--', alpha=.85, label=f'Mean {vals.mean():.1f}')
            ax.axvline(vals.median(), color='#B8860B', lw=1.4, ls=':', alpha=.85, label=f'Median {vals.median():.1f}')
            ax.legend(fontsize=7.5, frameon=False)
            ax.set_xlabel(x, fontsize=9, color=SUB)
            ax.set_ylabel('Count', fontsize=9, color=SUB)
        else:
            plt.close()
            return None

        ax.set_title(title, fontsize=11, fontweight='700', color=INK, pad=13, loc='left')
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(colors=INK, length=0, labelsize=8.5)
        if ct not in ('pie',):
            ax.grid(True, axis='y', zorder=0, alpha=.7)
        plt.tight_layout(pad=1.2)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=165, bbox_inches='tight', facecolor=BG)
        buf.seek(0)
        plt.close()
        # FIX: store as base64 string immediately — avoids BytesIO seek-position
        # issues when the object is accessed again after st.rerun()
        return base64.b64encode(buf.read()).decode()

    except Exception:
        plt.close()
        return None

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("msgs", []), ("df", None), ("summary", None), ("fname", None),
             ("pending_hint", None), ("clear_input", False)]:
    if k not in st.session_state:
        st.session_state[k] = v
df = st.session_state.df

# ── TOPBAR ────────────────────────────────────────────────────────────────────
fb = (f'<div class="tb-file">📄 <b>{st.session_state.fname}</b> &nbsp;·&nbsp; {len(df):,} rows</div>'
      if df is not None else "")
st.markdown(f"""
<div class="tb">
  <div class="tb-logo"><div class="tb-icon">{LOGO}</div>Data<em>Talk</em></div>
  <div class="tb-r">{fb}<div class="tb-chip">Beta</div></div>
</div>
<div style="height:50px"></div>""", unsafe_allow_html=True)

# ── LANDING ───────────────────────────────────────────────────────────────────
if df is None:
    _, cc, _ = st.columns([1, 1.2, 1])
    with cc:
        # Wrap everything in a centered flex container
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:center;
                    min-height:calc(100vh - 90px)">
          <div class="land-inner">
            <div class="land-logo">{LOGO_LG}</div>
            <div class="land-h">Chat with your<br><em>CSV data.</em></div>
            <div class="land-s">Ask questions in plain English.<br>Get instant answers and charts.</div>
            <div style="font-size:1.3rem;margin-bottom:5px">📊</div>
            <div style="font-family:Syne,sans-serif;font-weight:700;font-size:.88rem;
                        color:var(--ink);margin-bottom:2px">Drop your CSV here</div>
            <div style="font-size:.75rem;color:var(--sub);margin-bottom:12px">
              drag & drop or click &nbsp;·&nbsp;
              <span style="color:var(--g);font-weight:600">any size</span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Uploader rendered right after — CSS pulls it inside the card visually
        st.markdown('<div class="styled-uploader">', unsafe_allow_html=True)
        up = st.file_uploader("u", type=["csv"], label_visibility="collapsed", key="up")
        st.markdown('</div>', unsafe_allow_html=True)

        if up:
            with st.spinner("Loading…"):
                try:
                    _df = pd.read_csv(up)
                    st.session_state.df = _df
                    st.session_state.summary = get_summary(_df)
                    st.session_state.fname = up.name
                    st.session_state.msgs = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ── WORKSPACE ─────────────────────────────────────────────────────────────────
else:
    num_cols = df.select_dtypes(include='number').columns.tolist()
    txt_cols = [c for c in df.columns if c not in num_cols]
    null_pct = round(df.isnull().mean().mean() * 100, 1)
    dupes = int(df.duplicated().sum())

    left_col, right_col = st.columns([0.24, 0.76])

    # ── LEFT PANEL ────────────────────────────────────────────────────────
    with left_col:
        # File info
        fname_safe = html.escape(str(st.session_state.fname))
        st.markdown(f"""
        <div class="lp-file">
          <span class="lp-label">Dataset</span>
          <div class="lp-filename">{fname_safe}</div>
          <div class="lp-filemeta">{len(df):,} rows &nbsp;·&nbsp; {len(df.columns)} columns</div>
        </div>
        <div class="div"></div>
        <span class="lp-label" style="margin-top:10px;display:block">Overview</span>
        <div class="sc-grid">
          <div class="sc"><div class="sc-v">{len(num_cols)}</div><div class="sc-l">Numeric</div></div>
          <div class="sc"><div class="sc-v">{len(txt_cols)}</div><div class="sc-l">Text</div></div>
          <div class="sc"><div class="sc-v">{null_pct}%</div><div class="sc-l">Nulls</div></div>
          <div class="sc"><div class="sc-v">{dupes}</div><div class="sc-l">Dupes</div></div>
        </div>
        <div class="div"></div>
        """, unsafe_allow_html=True)

        # Data preview
        with st.expander("📋  Preview data", expanded=False):
            st.dataframe(df.head(15), use_container_width=True, height=180)

        # Columns
        tags = "".join(
            f'<div class="ct {"n" if c in num_cols else ""}"><span>{html.escape(c)}</span>'
            f'<span class="ct-type">{"num" if c in num_cols else "cat"}</span></div>'
            for c in df.columns
        )
        st.markdown(f"""
        <span class="lp-label">Columns</span>
        <div class="ctags">{tags}</div>
        <div class="div" style="margin:10px 0"></div>
        <span class="lp-label">Try asking</span>
        """, unsafe_allow_html=True)

        # FIX: hints are now real st.button() elements so clicking them works.
        # Each button sets pending_hint in session_state and triggers a rerun.
        for hint in HINTS:
            st.markdown('<div class="hint-btn">', unsafe_allow_html=True)
            if st.button(f'"{hint}"', key=f"hint_{hint}"):
                st.session_state.pending_hint = hint
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="div" style="margin:10px 0"></div>', unsafe_allow_html=True)

        # FIX: ghost button styling via wrapper div with class
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("🗑 Clear", key="clr", use_container_width=True):
                st.session_state.msgs = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
            if st.button("↩ New file", key="newf", use_container_width=True):
                st.session_state.df = None
                st.session_state.msgs = []
                st.session_state.fname = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT PANEL ───────────────────────────────────────────────────────
    with right_col:
        if not st.session_state.msgs:
            st.markdown("""
            <div class="empty">
              <div class="empty-icon">💬</div>
              <div class="empty-h">Ask anything about your data</div>
              <div class="empty-s">Type a question below or pick a suggestion from the left panel.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="msgs">', unsafe_allow_html=True)
            for msg in st.session_state.msgs:
                if msg["role"] == "user":
                    safe_q = html.escape(msg["content"])
                    st.markdown(f"""
                    <div class="mrow u">
                      <div class="av usr">You</div>
                      <div class="bub usr">{safe_q}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    rendered = render_bold(msg["content"])
                    st.markdown(f"""
                    <div class="mrow">
                      <div class="av bot">{LOGO}</div>
                      <div class="bub bot">{rendered}</div>
                    </div>""", unsafe_allow_html=True)
                    # FIX: chart stored as base64 string, not BytesIO
                    if msg.get("chart_b64"):
                        b64 = msg["chart_b64"]
                        chart_title = html.escape(msg.get("chart_title", "Chart"))
                        img_bytes = base64.b64decode(b64)
                        st.markdown(f"""
                        <div class="cc">
                          <div class="cc-hd">
                            <div class="cc-title">📈 {chart_title}</div>
                            <a class="cc-dl" href="data:image/png;base64,{b64}" download="datatalk_chart.png">↓ PNG</a>
                          </div>
                          <div class="cc-img">""", unsafe_allow_html=True)
                        st.image(img_bytes, width=540)
                        st.markdown("</div></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Input bar
        st.markdown('<div class="ibar-wrap"><div class="ibar">', unsafe_allow_html=True)
        ic1, ic2 = st.columns([6.2, 0.85])
        with ic1:
            # FIX: clear via default value when flag is set — never mutate
            # session_state[key] after the widget with that key is instantiated
            default_q = "" if st.session_state.clear_input else None
            st.session_state.clear_input = False
            q = st.text_input("q", placeholder="Ask a question about your data…",
                              label_visibility="collapsed", key="q_in",
                              value=default_q if default_q is not None else st.session_state.get("q_in", ""))
        with ic2:
            ask_btn = st.button("Ask →", key="ask")
        st.markdown('</div></div>', unsafe_allow_html=True)

        # FIX: also handle pending_hint from clicking a hint button
        active_q = None
        if ask_btn and q.strip():
            active_q = q.strip()
        elif st.session_state.pending_hint:
            active_q = st.session_state.pending_hint
            st.session_state.pending_hint = None

        if active_q:
            typing = st.empty()
            typing.markdown(f"""
            <div class="mrow" style="padding:0 0 8px 20px">
              <div class="av bot">{LOGO}</div>
              <div class="bub bot" style="padding:.5rem .9rem">
                <span class="tyd"></span><span class="tyd"></span><span class="tyd"></span>
              </div>
            </div>""", unsafe_allow_html=True)
            res = ask_ai(active_q, st.session_state.summary, st.session_state.msgs)
            ans = res.get("answer", "Sorry, couldn't process that.")
            spec = res.get("chart", {"type": "none"})
            # FIX: make_chart now returns a base64 string (or None)
            chart_b64 = make_chart(df, spec)
            typing.empty()
            st.session_state.msgs.append({"role": "user", "content": active_q})
            st.session_state.msgs.append({
                "role": "assistant",
                "content": ans,
                "chart_b64": chart_b64,
                "chart_title": spec.get("title", "Chart"),
            })
            # Signal to clear the input on next render, then rerun
            st.session_state.clear_input = True
            st.rerun()
