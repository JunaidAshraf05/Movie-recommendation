import html
import os

import requests
import streamlit as st

# =============================
# CONFIG & PAGE SETUP
# =============================
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Movie Recommendation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================
# THEME CONFIGURATION
# =============================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

theme = (
    {
        "background": "#08090C",
        "surface": "rgba(20, 22, 29, 0.72)",
        "surface_elevated": "rgba(30, 34, 46, 0.85)",
        "sidebar_bg": "rgba(12, 14, 19, 0.92)",
        "text": "#F5F6F8",
        "text_secondary": "rgba(240, 242, 247, 0.88)",
        "muted": "rgba(165, 172, 190, 0.62)",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_subtle": "rgba(255, 255, 255, 0.06)",
        "accent": "#0A84FF",
        "accent_hover": "#409CFF",
        "imdb_yellow": "#F5C518",
        "input": "rgba(255, 255, 255, 0.06)",
        "shadow": "0 18px 48px rgba(0, 0, 0, 0.55)",
        "wash": "rgba(10, 132, 255, 0.12)",
        "wash2": "rgba(245, 197, 24, 0.06)",
    }
    if st.session_state.dark_mode
    else {
        "background": "#F2F4F7",
        "surface": "rgba(255, 255, 255, 0.85)",
        "surface_elevated": "#FFFFFF",
        "sidebar_bg": "rgba(245, 247, 250, 0.95)",
        "text": "#12141A",
        "text_secondary": "rgba(35, 38, 48, 0.88)",
        "muted": "rgba(85, 92, 108, 0.65)",
        "border": "rgba(0, 0, 0, 0.08)",
        "border_subtle": "rgba(0, 0, 0, 0.05)",
        "accent": "#007AFF",
        "accent_hover": "#0A84FF",
        "imdb_yellow": "#E2B616",
        "input": "rgba(0, 0, 0, 0.05)",
        "shadow": "0 16px 40px rgba(0, 0, 0, 0.08)",
        "wash": "rgba(0, 122, 255, 0.08)",
        "wash2": "rgba(226, 182, 22, 0.05)",
    }
)

# =============================
# INJECT MODERN FLUID IOS STYLING
# =============================
st.markdown(
    f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  color-scheme: {"dark" if st.session_state.dark_mode else "light"};
  --app-bg: {theme["background"]};
  --surface: {theme["surface"]};
  --surface-elevated: {theme["surface_elevated"]};
  --sidebar-bg: {theme["sidebar_bg"]};
  --text-primary: {theme["text"]};
  --text-secondary: {theme["text_secondary"]};
  --text-muted: {theme["muted"]};
  --border-subtle: {theme["border_subtle"]};
  --border-strong: {theme["border"]};
  --accent: {theme["accent"]};
  --accent-hover: {theme["accent_hover"]};
  --input-bg: {theme["input"]};
  --card-shadow: {theme["shadow"]};
  --imdb-yellow: {theme["imdb_yellow"]};
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}}

html, body, .stApp {{
  background: var(--app-bg) !important;
  color: var(--text-primary) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

.stApp {{
  background:
    radial-gradient(1200px 550px at 10% -10%, {theme["wash"]}, transparent 50%),
    radial-gradient(1000px 500px at 100% -5%, {theme["wash2"]}, transparent 45%),
    var(--app-bg) !important;
  color: var(--text-primary);
  transition: background-color 280ms var(--ease), color 280ms var(--ease);
}}

.stApp, button, input, textarea, [data-testid="stSelectbox"], [data-testid="stMarkdownContainer"] {{
  font-family: "Plus Jakarta Sans", "Inter", -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}}

/* Main Block Layout */
.block-container {{
  padding: 1.2rem 2.2rem 4rem !important;
  max-width: 1260px !important;
  animation: rise-in 420ms var(--ease);
}}

@keyframes rise-in {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

[data-testid="stAppViewContainer"] {{ background: transparent !important; }}
[data-testid="stHeader"] {{ background: transparent !important; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton {{
  display: none !important;
}}

/* ========================================= */
/* FIX SIDEBAR BORDER & DOCKING              */
/* ========================================= */
section[data-testid="stSidebar"] {{
  background: var(--sidebar-bg) !important;
  backdrop-filter: blur(35px) saturate(200%) !important;
  -webkit-backdrop-filter: blur(35px) saturate(200%) !important;
  border-right: 1px solid var(--border-subtle) !important;
  box-shadow: 4px 0 28px rgba(0, 0, 0, 0.35) !important;
  height: 100vh !important;
  top: 0 !important;
  margin: 0 !important;
  border-radius: 0 !important;
}}

section[data-testid="stSidebar"] > div:first-child {{
  padding-top: 1.8rem !important;
  padding-left: 1.1rem !important;
  padding-right: 1.1rem !important;
  background: transparent !important;
  border-radius: 0 !important;
}}

[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {{
  background: transparent !important;
  border-radius: 0 !important;
}}

/* ========================================= */
/* FIX AWKWARD CONTAINER BORDER CLIPPING     */
/* ========================================= */
[data-testid="stVerticalBlockBorderWrapper"] {{
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  overflow: visible !important;
  padding: 0 !important;
}}

/* ========================================= */
/* FLUID iOS TASKBAR & HEADER                */
/* ========================================= */
.ios-taskbar {{
  background: var(--surface);
  backdrop-filter: blur(30px) saturate(210%);
  -webkit-backdrop-filter: blur(30px) saturate(210%);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  padding: 0.85rem 1.4rem;
  margin-bottom: 1.8rem;
  box-shadow: 0 10px 32px -4px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.ios-taskbar-brand {{
  display: flex;
  align-items: center;
  gap: 0.95rem;
}}

.ios-icon-squircle {{
  width: 44px;
  height: 44px;
  border-radius: 13px;
  background: linear-gradient(135deg, #FF3B30 0%, #FF9500 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  box-shadow: 0 6px 18px rgba(255, 59, 48, 0.38);
  flex-shrink: 0;
  transition: transform 0.3s ease;
}}

.ios-icon-squircle:hover {{
  transform: scale(1.05) rotate(-3deg);
}}

.ios-brand-text {{
  display: flex;
  flex-direction: column;
  gap: 2px;
}}

.ios-title-row {{
  display: flex;
  align-items: center;
  gap: 8px;
}}

.ios-brand-name {{
  font-size: 1.32rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--text-primary);
  line-height: 1.2;
}}

.ios-badge-pro {{
  background: rgba(10, 132, 255, 0.15);
  color: var(--accent);
  border: 1px solid rgba(10, 132, 255, 0.32);
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: 6px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}}

.ios-brand-caption {{
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
  letter-spacing: -0.01em;
}}

/* ========================================= */
/* SPOTLIGHT SEARCH HERO                     */
/* ========================================= */
.search-hero {{
  text-align: center;
  padding: 1rem 1rem 0.6rem;
  margin-bottom: 0.6rem;
}}

.search-pill-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 999px;
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.25);
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}}

.search-hero-title {{
  font-size: clamp(1.8rem, 3.2vw, 2.3rem);
  font-weight: 800;
  letter-spacing: -0.04em;
  margin: 0 0 0.35rem;
  color: var(--text-primary);
}}

.search-hero-desc {{
  font-size: 0.94rem;
  color: var(--text-muted);
  max-width: 520px;
  margin: 0 auto 1.2rem;
  line-height: 1.45;
}}

/* Modern Search Input */
[data-testid="stTextInput"] input {{
  background: var(--input-bg) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 999px !important;
  min-height: 3.35rem !important;
  padding-left: 1.4rem !important;
  padding-right: 1.4rem !important;
  font-size: 1.02rem !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
  transition: all 220ms var(--ease) !important;
}}

[data-testid="stTextInput"] input:focus {{
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.25), 0 12px 30px rgba(0, 0, 0, 0.35) !important;
  background: var(--surface-elevated) !important;
}}

/* Custom Selectbox & Sliders */
[data-testid="stSelectbox"] > div > div {{
  background: var(--input-bg) !important;
  color: var(--text-primary) !important;
  border-color: var(--border-strong) !important;
  border-radius: 0.9rem !important;
}}

/* Sidebar Content Styling */
.sidebar-header {{
  margin-bottom: 1.5rem;
}}
.sidebar-title {{
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  display: block;
}}
.sidebar-caption {{
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 3px;
}}
.sidebar-group-title {{
  font-size: 0.72rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 0.45rem;
}}

/* Headings & Section Typography */
.section-heading {{
  margin: 1.6rem 0 0.3rem;
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  color: var(--text-primary);
}}
.section-kicker {{
  color: var(--text-muted);
  font-size: 0.88rem;
  margin: 0 0 1rem;
}}

/* ========================================= */
/* MOVIE CARD WITH IMDb YELLOW BADGE         */
/* ========================================= */
.poster-grid {{
  display: grid;
  grid-template-columns: repeat(var(--cols, 5), minmax(0, 1fr));
  gap: 1.3rem 1.05rem;
}}

.poster-rail {{
  display: flex;
  gap: 1.05rem;
  overflow-x: auto;
  padding: 0.3rem 0.2rem 1.2rem;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}}
.poster-rail::-webkit-scrollbar {{ display: none; }}

.poster-card {{
  display: block;
  color: inherit;
  text-decoration: none;
  min-width: 0;
  scroll-snap-align: start;
  position: relative;
  transition: transform 300ms var(--ease);
}}

.poster-rail .poster-card {{
  flex: 0 0 168px;
}}

.poster-card:hover {{
  transform: translateY(-7px);
}}

.poster-card:active {{
  transform: scale(0.98);
}}

.poster-art {{
  position: relative;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: 16px;
  background: var(--surface-elevated);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.42);
  border: 1px solid var(--border-subtle);
  transition: box-shadow 300ms var(--ease), border-color 300ms var(--ease);
}}

.poster-art::after {{
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.18) 0%, transparent 45%, rgba(0,0,0,0.72) 100%);
  pointer-events: none;
  opacity: 0.85;
  transition: opacity 300ms ease;
}}

.poster-card:hover .poster-art {{
  border-color: rgba(245, 197, 24, 0.45);
  box-shadow: 0 20px 45px -8px rgba(0, 0, 0, 0.7), 0 0 22px rgba(245, 197, 24, 0.16);
}}

.poster-card:hover .poster-art::after {{
  opacity: 0.5;
}}

.poster-art img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 450ms var(--ease);
}}

.poster-card:hover .poster-art img {{
  transform: scale(1.06);
}}

.poster-placeholder {{
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  font-size: 1.6rem;
}}

/* Official IMDb Yellow Badge Overlay */
.imdb-badge-overlay {{
  position: absolute;
  top: 9px;
  left: 9px;
  z-index: 5;
  pointer-events: none;
}}

.imdb-badge {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(14, 15, 20, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  padding: 3px 7px 3px 4px;
  border-radius: 8px;
  border: 1px solid rgba(245, 197, 24, 0.45);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.5);
  transition: transform 0.25s ease, border-color 0.25s ease;
}}

.poster-card:hover .imdb-badge {{
  transform: translateY(-1px);
  border-color: rgba(245, 197, 24, 0.85);
  box-shadow: 0 6px 20px rgba(245, 197, 24, 0.3);
}}

.imdb-tag {{
  background: #F5C518;
  color: #000000;
  font-weight: 900;
  font-size: 0.64rem;
  line-height: 1.1;
  padding: 2px 4px;
  border-radius: 4px;
  letter-spacing: 0.02em;
  font-family: "Impact", "Plus Jakarta Sans", sans-serif;
}}

.imdb-star {{
  color: #F5C518;
  font-size: 0.78rem;
  line-height: 1;
}}

.imdb-rating-val {{
  color: #FFFFFF;
  font-weight: 800;
  font-size: 0.78rem;
  letter-spacing: -0.01em;
}}

/* Year Badge Overlay */
.year-badge-overlay {{
  position: absolute;
  top: 9px;
  right: 9px;
  z-index: 5;
  pointer-events: none;
}}

.year-badge {{
  background: rgba(10, 11, 15, 0.78);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.7rem;
  font-weight: 650;
  padding: 3px 6px;
  border-radius: 7px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}}

/* Card Meta Below Poster */
.poster-meta {{
  padding: 0.65rem 0.15rem 0.15rem;
  display: flex;
  flex-direction: column;
  gap: 3px;
}}

.movie-title-card {{
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
  color: var(--text-primary);
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.25;
  transition: color 200ms ease;
}}

.poster-card:hover .movie-title-card {{
  color: var(--accent);
}}

.movie-card-footer {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.77rem;
}}

.movie-card-year {{
  color: var(--text-muted);
  font-weight: 500;
}}

.movie-card-score {{
  display: inline-flex;
  align-items: center;
  gap: 3px;
  color: #F5C518;
  font-weight: 750;
  font-size: 0.8rem;
}}

.movie-card-score .max-scale {{
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 450;
}}

/* ========================================= */
/* DETAILS VIEW HERO & BADGES                */
/* ========================================= */
.detail-hero {{
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  min-height: 430px;
  margin: 0.4rem 0 1.6rem;
  background: #090a0e center/cover no-repeat;
  background-image: linear-gradient(180deg, rgba(8, 9, 13, 0.25) 0%, rgba(8, 9, 13, 0.92) 100%), var(--hero-bg);
  border: 1px solid var(--border-subtle);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}}

.detail-hero-inner {{
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 230px minmax(0, 1fr);
  gap: 1.8rem;
  padding: 2rem;
  align-items: end;
}}

.detail-poster-wrap {{
  overflow: hidden;
  border-radius: 20px;
  box-shadow: 0 22px 50px rgba(0, 0, 0, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.12);
}}

.detail-poster-wrap img {{ width: 100%; display: block; }}

.detail-copy h1 {{
  margin: 0.15rem 0 0.85rem;
  font-size: clamp(2rem, 4.2vw, 3.2rem);
  line-height: 1.08;
  color: #FFFFFF;
  font-weight: 850;
  letter-spacing: -0.04em;
}}

.eyebrow {{
  margin: 0;
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}}

.meta-row {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.1rem;
}}

.imdb-badge-large {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(18, 19, 26, 0.9);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1.5px solid rgba(245, 197, 24, 0.5);
  padding: 5px 12px;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5), 0 0 16px rgba(245, 197, 24, 0.2);
}}

.imdb-tag-lg {{
  background: #F5C518;
  color: #000;
  font-weight: 900;
  font-size: 0.8rem;
  line-height: 1;
  padding: 3px 6px;
  border-radius: 5px;
  letter-spacing: 0.03em;
  font-family: "Impact", "Plus Jakarta Sans", sans-serif;
}}

.imdb-star-lg {{
  color: #F5C518;
  font-size: 1.05rem;
}}

.imdb-val-lg {{
  color: #FFF;
  font-weight: 850;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
}}

.imdb-scale {{
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  font-weight: 500;
}}

.chip {{
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: #FFFFFF;
  font-size: 0.82rem;
  font-weight: 600;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}}

.overview {{
  max-width: 66ch;
  color: rgba(255, 255, 255, 0.84);
  font-size: 1.02rem;
  line-height: 1.6;
  margin: 0;
}}

/* Pagination Controls */
.pagination-status {{
  color: var(--text-muted);
  text-align: center;
  padding-top: 0.6rem;
  font-size: 0.9rem;
  font-weight: 600;
}}

/* Button Tweaks */
button[kind="secondary"], button[kind="primary"] {{
  border-radius: 999px !important;
  min-height: 2.6rem;
  font-weight: 650 !important;
  transition: transform 200ms var(--ease), background-color 200ms var(--ease) !important;
}}

button[kind="secondary"] {{
  background: var(--input-bg) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-subtle) !important;
}}

button[kind="secondary"]:hover {{
  background: var(--surface-elevated) !important;
  transform: translateY(-1px);
}}

button[kind="primary"] {{
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 6px 18px rgba(10, 132, 255, 0.35) !important;
}}

button[kind="primary"]:hover {{
  background: var(--accent-hover) !important;
  transform: translateY(-1px);
}}

/* Responsive */
@media (max-width: 860px) {{
  .block-container {{ padding: 0.8rem 1rem 3rem !important; }}
  .poster-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .detail-hero-inner {{ grid-template-columns: 1fr; gap: 1.2rem; }}
  .detail-poster-wrap {{ max-width: 190px; }}
  .ios-taskbar {{ padding: 0.75rem 1rem; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE & ROUTING
# =============================
if "view" not in st.session_state:
    st.session_state.view = "home"  # home | details
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "search_page" not in st.session_state:
    st.session_state.search_page = 1
if "home_page" not in st.session_state:
    st.session_state.home_page = 1
if "last_search_term" not in st.session_state:
    st.session_state.last_search_term = ""
if "last_home_category" not in st.session_state:
    st.session_state.last_home_category = "trending"

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


# =============================
# API HELPERS
# =============================
@st.cache_data(ttl=30)
def _api_get_json_cached(path: str, params: dict | None = None):
    r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
    if r.status_code >= 400:
        try:
            detail = r.json().get("detail", r.text[:300])
        except ValueError:
            detail = r.text[:300]
        raise requests.HTTPError(f"HTTP {r.status_code}: {detail}", response=r)
    return r.json()


def api_get_json(path: str, params: dict | None = None):
    try:
        return _api_get_json_cached(path, params), None
    except requests.RequestException as e:
        return None, f"Request failed: {e}"
    except ValueError as e:
        return None, f"Invalid JSON response: {e}"


# =============================
# POSTER GRID WITH IMDb YELLOW BADGE
# =============================
def poster_grid(cards, cols=5, key_prefix="grid", layout="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    items = []
    for m in cards:
        tmdb_id = m.get("tmdb_id")
        title = html.escape(str(m.get("title", "Untitled")))
        poster = m.get("poster_url")
        rating = m.get("vote_average")
        release_date = m.get("release_date") or ""
        year = str(release_date)[:4] if release_date else ""

        # Format IMDb rating
        try:
            val = float(rating)
            if val > 0:
                rating_str = f"{val:.1f}"
                badge_html = (
                    f'<div class="imdb-badge-overlay">'
                    f'<div class="imdb-badge">'
                    f'<span class="imdb-tag">IMDb</span>'
                    f'<span class="imdb-star">★</span>'
                    f'<span class="imdb-rating-val">{rating_str}</span>'
                    f'</div></div>'
                )
                score_footer = f'<span class="movie-card-score">★ {rating_str}<span class="max-scale">/10</span></span>'
            else:
                badge_html = (
                    f'<div class="imdb-badge-overlay">'
                    f'<div class="imdb-badge">'
                    f'<span class="imdb-tag">IMDb</span>'
                    f'<span class="imdb-rating-val">NR</span>'
                    f'</div></div>'
                )
                score_footer = '<span class="movie-card-score" style="color:var(--text-muted)">NR</span>'
        except (TypeError, ValueError):
            badge_html = ""
            score_footer = ""

        # Year badge
        year_badge = (
            f'<div class="year-badge-overlay"><span class="year-badge">{year}</span></div>'
            if year
            else ""
        )

        href = f"?view=details&id={int(tmdb_id)}" if tmdb_id else "#"
        if poster:
            art = f'<img src="{html.escape(str(poster), quote=True)}" alt="{title}" loading="lazy" />'
        else:
            art = '<div class="poster-placeholder">🎬</div>'

        items.append(
            f'<a class="poster-card" href="{href}" title="{title}">'
            f'<div class="poster-art">'
            f'{badge_html}'
            f'{year_badge}'
            f'{art}'
            f'</div>'
            f'<div class="poster-meta">'
            f'<div class="movie-title-card">{title}</div>'
            f'<div class="movie-card-footer">'
            f'<span class="movie-card-year">{year or "Film"}</span>'
            f'{score_footer}'
            f'</div>'
            f'</div>'
            f'</a>'
        )

    if layout == "rail":
        markup = f'<div class="poster-rail">{"".join(items)}</div>'
    else:
        markup = (
            f'<div class="poster-grid" style="--cols:{int(cols)}">'
            f'{"".join(items)}</div>'
        )
    st.markdown(markup, unsafe_allow_html=True)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date"),
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, limit: int = 24):
    raw_items = []
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    else:
        return [], []

    final_list = raw_items
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
            "release_date": x.get("release_date"),
            "vote_average": x.get("vote_average"),
        }
        for x in final_list[:limit]
    ]
    return suggestions, cards


def page_controls(page: int, total_pages: int, state_key: str, key_prefix: str):
    if total_pages <= 1:
        return

    previous, status, next_page = st.columns([1, 2, 1])
    with previous:
        if st.button(
            "← Previous",
            key=f"{key_prefix}_previous",
            disabled=page <= 1,
        ):
            st.session_state[state_key] = page - 1
            st.rerun()
    with status:
        st.markdown(
            f"<div class='pagination-status'>Page {page} of {total_pages}</div>",
            unsafe_allow_html=True,
        )
    with next_page:
        if st.button(
            "Next →",
            key=f"{key_prefix}_next",
            disabled=page >= total_pages,
        ):
            st.session_state[state_key] = page + 1
            st.rerun()


# =============================
# FLUID iOS TASKBAR (TOP NAVIGATION)
# =============================
toolbar_container = st.container()
with toolbar_container:
    t_left, t_right = st.columns([5, 1.8], vertical_alignment="center")
    with t_left:
        st.markdown(
            """
            <div class="ios-taskbar-brand">
                <div class="ios-icon-squircle">🎬</div>
                <div class="ios-brand-text">
                    <div class="ios-title-row">
                        <span class="ios-brand-name">Movie Recommendation</span>
                        <span class="ios-badge-pro">PRO</span>
                    </div>
                    <span class="ios-brand-caption">Intelligent cinema discovery & similarity engine</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with t_right:
        st.toggle(
            "Dark mode",
            key="dark_mode",
            help="Switch between dark and light appearance",
        )

# =============================
# SIDEBAR
# =============================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header">
            <span class="sidebar-title">Discover</span>
            <p class="sidebar-caption">Explore curated feeds & customize grid view.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-group-title'>FEED CATEGORY</div>", unsafe_allow_html=True)
    category_options = {
        "trending": "🔥 Trending Today",
        "popular": "🌟 Most Popular",
        "top_rated": "🏆 Highest Rated",
        "now_playing": "🍿 In Theaters",
        "upcoming": "🚀 Upcoming Releases",
    }
    home_category = st.selectbox(
        "Category",
        options=list(category_options.keys()),
        format_func=lambda x: category_options.get(x, x.title()),
        index=0,
        label_visibility="collapsed",
    )
    if home_category != st.session_state.last_home_category:
        st.session_state.home_page = 1
        st.session_state.last_home_category = home_category

    st.markdown("<div class='sidebar-group-title' style='margin-top: 1.4rem;'>GRID COLUMNS</div>", unsafe_allow_html=True)
    grid_cols = st.slider("Grid columns", 3, 6, 5, label_visibility="collapsed")


# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    # Spotlight Search Hero Section
    st.markdown(
        """
        <div class="search-hero">
            <div class="search-pill-badge">⚡ Instant Cinema Search</div>
            <h2 class="search-hero-title">Find your next favorite</h2>
            <p class="search-hero-desc">Search thousands of movies with real-time similarity & IMDb ratings</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    typed = st.text_input(
        "Search movies",
        placeholder="Try a title: Dune, Batman, Interstellar, or Arrival...",
        label_visibility="collapsed",
    )

    search_term = typed.strip()
    if search_term != st.session_state.last_search_term:
        st.session_state.search_page = 1
        st.session_state.last_search_term = search_term

    # SEARCH RESULTS MODE
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for search results.")
        else:
            data, err = api_get_json(
                "/tmdb/search",
                params={"query": search_term, "page": st.session_state.search_page},
            )

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                _, cards = parse_tmdb_search_to_cards(data, limit=24)
                if not cards:
                    st.info("No movies matched that search. Try another title.")
                else:
                    st.markdown(
                        "<h3 class='section-heading'>Search results</h3>"
                        "<div class='section-kicker'>Tap a poster to explore full details and recommendations.</div>",
                        unsafe_allow_html=True,
                    )
                    poster_grid(
                        cards,
                        cols=grid_cols,
                        key_prefix="search_results",
                        layout="grid",
                    )
                page_controls(
                    page=int(data.get("page", st.session_state.search_page)),
                    total_pages=min(int(data.get("total_pages", 1)), 500),
                    state_key="search_page",
                    key_prefix="search_results_paging",
                )

        st.stop()

    # HOME FEED MODE
    cat_label = category_options.get(home_category, home_category.replace('_', ' ').title())
    st.markdown(
        f"<h2 class='section-heading'>{cat_label}</h2>"
        "<div class='section-kicker'>Curated selection of top films streaming and trending worldwide.</div>",
        unsafe_allow_html=True,
    )

    home_cards, err = api_get_json(
        "/home/paged",
        params={
            "category": home_category,
            "limit": 20,
            "page": st.session_state.home_page,
        },
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards.get("results", []), cols=grid_cols, key_prefix="home_feed", layout="grid")
    page_controls(
        page=int(home_cards.get("page", st.session_state.home_page)),
        total_pages=int(home_cards.get("total_pages", 1)),
        state_key="home_page",
        key_prefix="home_feed_paging",
    )

# ==========================================================
# VIEW: DETAILS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    if st.button("‹ Back to All Movies", key="details_back"):
        goto_home()

    # Details
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    title_text = html.escape(data.get("title") or "Untitled")
    overview = html.escape(data.get("overview") or "No overview available.")
    release = html.escape(data.get("release_date") or "—")
    release_year = release[:4] if release != "—" else ""
    genres = html.escape(
        ", ".join([g["name"] for g in data.get("genres", [])]) or "—"
    )
    backdrop = html.escape(str(data.get("backdrop_url") or ""), quote=True)
    poster = data.get("poster_url")
    if poster:
        poster_html = (
            f'<img src="{html.escape(str(poster), quote=True)}" alt="{title_text}" />'
        )
    else:
        poster_html = '<div class="poster-placeholder">🎬</div>'

    rating = data.get("vote_average")
    try:
        val = float(rating)
        if val > 0:
            rating_chip = (
                f'<div class="imdb-badge-large">'
                f'<span class="imdb-tag-lg">IMDb</span>'
                f'<span class="imdb-star-lg">★</span>'
                f'<span class="imdb-val-lg">{val:.1f}</span>'
                f'<span class="imdb-scale">/10</span>'
                f'</div>'
            )
        else:
            rating_chip = '<div class="imdb-badge-large"><span class="imdb-tag-lg">IMDb</span><span class="imdb-val-lg">NR</span></div>'
    except (TypeError, ValueError):
        rating_chip = ""

    st.markdown(
        f'<div class="detail-hero" style="--hero-bg: url(\'{backdrop}\')">'
        f'<div class="detail-hero-inner">'
        f'<div class="detail-poster-wrap">{poster_html}</div>'
        f'<div class="detail-copy">'
        f'<p class="eyebrow">Featured Title</p>'
        f"<h1>{title_text}</h1>"
        f'<div class="meta-row">{rating_chip}'
        f'<span class="chip">📅 {release}</span>'
        f'<span class="chip">🎭 {genres}</span></div>'
        f'<p class="overview">{overview}</p>'
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 class='section-heading'>Because you picked this</h2>"
        "<div class='section-kicker'>AI-calculated similarity and genre recommendations.</div>",
        unsafe_allow_html=True,
    )

    # Recommendations
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("<h3 class='section-heading'>Similar Movies (Content Matching)</h3>", unsafe_allow_html=True)
            tfidf_items = bundle.get("tfidf_recommendations", [])
            tfidf_cards = to_cards_from_tfidf_items(tfidf_items)
            if tfidf_cards:
                poster_grid(
                    tfidf_cards,
                    cols=grid_cols,
                    key_prefix="details_tfidf",
                    layout="rail",
                )
            unlinked_items = [
                item
                for item in tfidf_items
                if not (item.get("tmdb") or {}).get("tmdb_id")
            ]
            if unlinked_items:
                st.markdown("**Additional Local Title Matches:**")
                for item in unlinked_items:
                    st.write(
                        f"- **{item.get('title', 'Untitled')}** "
                        f"(similarity score: {item.get('score', 0):.3f})"
                    )
            elif not tfidf_items:
                st.info("No local similar titles were found for this movie.")

            st.markdown("<h3 class='section-heading'>More Like This (Genre Discovery)</h3>", unsafe_allow_html=True)
            genre_recs = bundle.get("genre_recommendations", [])
            if genre_recs:
                poster_grid(
                    genre_recs,
                    cols=grid_cols,
                    key_prefix="details_genre",
                    layout="rail",
                )
            elif bundle.get("genre_error"):
                st.warning(bundle["genre_error"])
            else:
                st.info("No genre recommendations were found for this movie.")
        else:
            st.warning(
                "The full recommendation bundle failed. Showing available recommendations separately."
            )
            fallback_tfidf, tfidf_err = api_get_json(
                "/recommend/tfidf", params={"title": title, "top_n": 12}
            )
            st.markdown("<h3 class='section-heading'>Similar Movies</h3>", unsafe_allow_html=True)
            if not tfidf_err and fallback_tfidf:
                for item in fallback_tfidf:
                    st.write(
                        f"- **{item.get('title', 'Untitled')}** "
                        f"(score: {item.get('score', 0):.3f})"
                    )
            elif tfidf_err:
                st.info(f"TF-IDF recommendations are unavailable: {tfidf_err}")

            st.markdown("<h3 class='section-heading'>More Like This</h3>", unsafe_allow_html=True)
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only,
                    cols=grid_cols,
                    key_prefix="details_genre_fallback",
                    layout="rail",
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")
