import html
import os

import requests
import streamlit as st

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# THEME
# =============================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

theme = (
    {
        "background": "#000000",
        "surface": "rgba(28, 28, 30, 0.72)",
        "surface_elevated": "#2C2C2E",
        "text": "#F5F5F7",
        "text_secondary": "rgba(245, 245, 247, 0.92)",
        "muted": "rgba(235, 235, 245, 0.48)",
        "border": "rgba(255, 255, 255, 0.08)",
        "accent": "#0A84FF",
        "accent_hover": "#409CFF",
        "input": "rgba(118, 118, 128, 0.24)",
        "shadow": "0 18px 48px rgba(0, 0, 0, 0.45)",
        "wash": "rgba(10, 132, 255, 0.16)",
        "wash2": "rgba(255, 55, 95, 0.10)",
    }
    if st.session_state.dark_mode
    else {
        "background": "#F2F2F7",
        "surface": "rgba(255, 255, 255, 0.82)",
        "surface_elevated": "#E5E5EA",
        "text": "#1C1C1E",
        "text_secondary": "rgba(28, 28, 30, 0.88)",
        "muted": "rgba(60, 60, 67, 0.48)",
        "border": "rgba(60, 60, 67, 0.12)",
        "accent": "#007AFF",
        "accent_hover": "#0A84FF",
        "input": "rgba(118, 118, 128, 0.12)",
        "shadow": "0 16px 40px rgba(15, 15, 18, 0.08)",
        "wash": "rgba(0, 122, 255, 0.10)",
        "wash2": "rgba(255, 45, 85, 0.06)",
    }
)

st.markdown(
    f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  color-scheme: {"dark" if st.session_state.dark_mode else "light"};
  --app-bg: {theme["background"]};
  --surface: {theme["surface"]};
  --surface-elevated: {theme["surface_elevated"]};
  --text-primary: {theme["text"]};
  --text-secondary: {theme["text_secondary"]};
  --text-muted: {theme["muted"]};
  --border-subtle: {theme["border"]};
  --accent: {theme["accent"]};
  --accent-hover: {theme["accent_hover"]};
  --input-bg: {theme["input"]};
  --card-shadow: {theme["shadow"]};
  --rating: #FFD60A;
  --ease: cubic-bezier(0.22, 1, 0.36, 1);
}}
html, body, .stApp {{
  background: var(--app-bg);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}
.stApp {{
  background:
    radial-gradient(1100px 520px at 8% -12%, {theme["wash"]}, transparent 55%),
    radial-gradient(900px 480px at 100% -8%, {theme["wash2"]}, transparent 50%),
    var(--app-bg);
  color: var(--text-primary);
  transition: background-color 280ms var(--ease), color 280ms var(--ease);
}}
.stApp, button, input, textarea, [data-testid="stSelectbox"], [data-testid="stMarkdownContainer"] {{
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif;
}}
.block-container {{
  padding: 1.15rem 1.6rem 4rem;
  max-width: 1180px;
  animation: rise-in 520ms var(--ease);
}}
@keyframes rise-in {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
[data-testid="stAppViewContainer"] {{ background: transparent; }}
[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton {{
  display: none !important;
}}
[data-testid="stSidebar"] {{
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: saturate(180%) blur(28px);
  -webkit-backdrop-filter: saturate(180%) blur(28px);
  border-right: 1px solid var(--border-subtle);
}}
[data-testid="stSidebar"] * {{ color: var(--text-primary); }}
h1, h2, h3, p, label {{ color: var(--text-primary); }}
h1, h2, h3 {{ letter-spacing: -0.045em; font-weight: 700; }}
.stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-muted); }}
.small-muted {{ color: var(--text-muted); font-size: 0.92rem; }}
.app-toolbar {{ display: flex; align-items: center; gap: 0.8rem; min-height: 2.8rem; }}
.brand-mark {{
  display: inline-grid; place-items: center; width: 2.35rem; height: 2.35rem;
  margin-right: 0.55rem; border-radius: 0.82rem;
  background: linear-gradient(180deg, #FF6B6B, #FF375F);
  color: white; font-size: 1.1rem; vertical-align: middle;
  box-shadow: 0 8px 20px rgba(255, 55, 95, 0.28);
}}
.brand-name {{ font-size: 1.18rem; font-weight: 750; letter-spacing: -0.04em; }}
.brand-caption {{ display: block; margin-left: 3rem; color: var(--text-muted); font-size: 0.76rem; }}
[data-testid="stTextInput"] input {{
  background: var(--input-bg) !important;
  color: var(--text-primary) !important;
  border: 0 !important;
  border-radius: 999px !important;
  min-height: 3.15rem;
  padding-left: 1.1rem !important;
  font-size: 1rem !important;
  transition: background-color 180ms var(--ease), box-shadow 180ms var(--ease);
}}
[data-testid="stTextInput"] input:focus {{
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 22%, transparent) !important;
}}
[data-testid="stSelectbox"] > div > div {{
  background: var(--input-bg);
  color: var(--text-primary);
  border-color: transparent;
  border-radius: 0.9rem;
}}
button[kind="secondary"], button[kind="primary"] {{
  border-radius: 999px !important;
  min-height: 2.55rem;
  font-weight: 600 !important;
  transition: transform 220ms var(--ease), background-color 220ms var(--ease), border-color 220ms var(--ease);
}}
button[kind="secondary"] {{
  background: var(--input-bg) !important;
  color: var(--text-primary) !important;
  border: 0 !important;
}}
button[kind="secondary"]:hover {{
  background: var(--surface-elevated) !important;
  transform: translateY(-1px) scale(1.01);
}}
button[kind="primary"] {{ background: var(--accent) !important; border-color: var(--accent) !important; }}
button[kind="primary"]:hover {{ background: var(--accent-hover) !important; }}
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--surface) !important;
  backdrop-filter: saturate(180%) blur(22px);
  -webkit-backdrop-filter: saturate(180%) blur(22px);
  border: 1px solid var(--border-subtle) !important;
  border-radius: 22px !important;
  box-shadow: none !important;
  overflow: hidden;
}}
[data-testid="stImage"] img {{ border-radius: 1rem; }}
[data-testid="stAlert"] {{
  border-radius: 1.1rem;
  background: var(--surface) !important;
  border: 1px solid var(--border-subtle) !important;
}}
.section-heading {{
  margin: 1.7rem 0 0.35rem;
  font-size: 1.55rem;
}}
.section-kicker {{
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0 0 1rem;
}}
.hero-copy {{ margin: 0.35rem 0 1rem; }}
.pagination-status {{
  color: var(--text-muted);
  text-align: center;
  padding-top: 0.55rem;
  font-size: 0.88rem;
}}
.poster-grid {{
  display: grid;
  grid-template-columns: repeat(var(--cols, 5), minmax(0, 1fr));
  gap: 1.05rem 0.85rem;
}}
.poster-rail {{
  display: flex;
  gap: 0.9rem;
  overflow-x: auto;
  padding: 0.2rem 0.15rem 1.1rem;
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
  transition: transform 320ms var(--ease);
}}
.poster-rail .poster-card {{
  flex: 0 0 158px;
}}
.poster-card:hover {{ transform: translateY(-6px) scale(1.03); }}
.poster-card:active {{ transform: scale(0.98); }}
.poster-art {{
  position: relative;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: 16px;
  background: var(--surface-elevated);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.35);
}}
.poster-art img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 480ms var(--ease);
}}
.poster-card:hover .poster-art img {{ transform: scale(1.06); }}
.poster-placeholder {{
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  color: var(--text-muted);
  font-size: 1.4rem;
}}
.poster-meta {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.35rem;
  padding: 0.55rem 0.1rem 0;
}}
.movie-title-card {{
  display: -webkit-box;
  overflow: hidden;
  color: var(--text-primary);
  font-size: 0.84rem;
  font-weight: 600;
  line-height: 1.2rem;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}}
.movie-rating {{
  flex: 0 0 auto;
  color: var(--rating);
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
}}
.detail-hero {{
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  min-height: 420px;
  margin: 0.4rem 0 1.4rem;
  background: #0b0b0d center/cover no-repeat;
  background-image: linear-gradient(180deg, rgba(0,0,0,0.15), rgba(0,0,0,0.88)), var(--hero-bg);
}}
.detail-hero-inner {{
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 1.6rem;
  padding: 1.6rem;
  align-items: end;
}}
.detail-poster-wrap {{
  overflow: hidden;
  border-radius: 18px;
  box-shadow: 0 22px 50px rgba(0, 0, 0, 0.5);
}}
.detail-poster-wrap img {{ width: 100%; display: block; }}
.detail-copy h1 {{
  margin: 0.15rem 0 0.75rem;
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1.05;
  color: #fff;
}}
.eyebrow {{
  margin: 0;
  color: rgba(255,255,255,0.62);
  font-size: 0.78rem;
  font-weight: 650;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}}
.meta-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 0.9rem;
}}
.chip {{
  display: inline-flex;
  align-items: center;
  padding: 0.32rem 0.7rem;
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  backdrop-filter: blur(12px);
}}
.chip.rating {{ color: var(--rating); background: rgba(255, 214, 10, 0.14); }}
.overview {{
  max-width: 62ch;
  color: rgba(255,255,255,0.82);
  font-size: 0.98rem;
  line-height: 1.55;
  margin: 0;
}}
@media (max-width: 800px) {{
  .block-container {{ padding: 0.9rem 0.9rem 2.4rem; }}
  .brand-caption {{ display: none; }}
  .poster-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .detail-hero-inner {{ grid-template-columns: 1fr; }}
  .detail-poster-wrap {{ max-width: 220px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation: none !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# STATE + ROUTING (single-file pages)
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


def poster_grid(cards, cols=6, key_prefix="grid", layout="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    items = []
    for m in cards:
        tmdb_id = m.get("tmdb_id")
        title = html.escape(str(m.get("title", "Untitled")))
        poster = m.get("poster_url")
        rating = m.get("vote_average")
        try:
            rating_label = f"★ {float(rating):.1f}" if rating is not None else ""
        except (TypeError, ValueError):
            rating_label = ""

        href = f"?view=details&id={int(tmdb_id)}" if tmdb_id else "#"
        if poster:
            art = (
                f'<img src="{html.escape(str(poster), quote=True)}" alt="{title}" />'
            )
        else:
            art = '<div class="poster-placeholder">🎬</div>'

        items.append(
            f'<a class="poster-card" href="{href}" title="{title}">'
            f'<div class="poster-art">{art}</div>'
            f'<div class="poster-meta"><span class="movie-title-card">{title}</span>'
            f'<span class="movie-rating">{rating_label}</span></div></a>'
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
                    "vote_average": tmdb.get("vote_average"),
                }
            )
    return cards


# =============================
# IMPORTANT: Robust TMDB search parsing
# Supports BOTH API shapes:
# 1) raw TMDB: {"results":[{id,title,poster_path,...}]}
# 2) list cards: [{tmdb_id,title,poster_url,...}]
# =============================
def parse_tmdb_search_to_cards(data, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    # A) If API returns dict with 'results'
    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
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

    # B) If API returns already as list
    elif isinstance(data, list):
        raw_items = []
        for m in data:
            # might be {tmdb_id,title,poster_url}
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

    # TMDB already ranks results for the search query. Keep its full page,
    # including localized or alternate titles that don't contain the query.
    final_list = raw_items

    # Suggestions = top 10 labels
    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    # Cards = top N
    cards = [
        {
            "tmdb_id": x["tmdb_id"],
            "title": x["title"],
            "poster_url": x["poster_url"],
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
# TOP TOOLBAR
# =============================
with st.container(border=True):
    toolbar_brand, toolbar_theme = st.columns([5, 2])
    with toolbar_brand:
        st.markdown(
            "<div class='app-toolbar'><span class='brand-mark'>🎬</span>"
            "<span class='brand-name'>ReelGood</span></div>"
            "<span class='brand-caption'>Cinematic picks, made personal</span>",
            unsafe_allow_html=True,
        )
    with toolbar_theme:
        st.toggle(
            "Dark mode",
            key="dark_mode",
            help="Switch between dark and light appearance",
        )


# =============================
# SIDEBAR (clean)
# =============================
with st.sidebar:
    st.markdown("## Discover")
    st.markdown(
        "<span class='small-muted'>Explore the latest movies and find your next watch.</span>",
        unsafe_allow_html=True,
    )
    st.markdown("### Home feed")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    if home_category != st.session_state.last_home_category:
        st.session_state.home_page = 1
        st.session_state.last_home_category = home_category
    grid_cols = st.slider("Grid columns", 3, 6, 5)

# =============================
# HEADER
# =============================
st.markdown(
    "<div class='small-muted hero-copy'>Swipe through what’s on, tap a poster, and find your next watch.</div>",
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    with st.container(border=True):
        st.markdown("### Find your next favorite")
        st.markdown(
            "<div class='section-kicker'>Search across the movie catalog</div>",
            unsafe_allow_html=True,
        )
        typed = st.text_input(
            "Search movies",
            placeholder="Try a title: Dune, Batman, or Arrival...",
            label_visibility="collapsed",
        )
    search_term = typed.strip()
    if search_term != st.session_state.last_search_term:
        st.session_state.search_page = 1
        st.session_state.last_search_term = search_term

    # SEARCH MODE (Autocomplete + word-match results)
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json(
                "/tmdb/search",
                params={"query": search_term, "page": st.session_state.search_page},
            )

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                _, cards = parse_tmdb_search_to_cards(
                    data, limit=24
                )
                if not cards:
                    st.info("No movies matched that search. Try another title.")
                else:
                    st.markdown(
                        "<h3 class='section-heading'>Search results</h3>"
                        "<div class='section-kicker'>Tap a poster to open the film.</div>",
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
    st.markdown(
        f"<h2 class='section-heading'>"
        f"{home_category.replace('_', ' ').title()} movies</h2>"
        "<div class='section-kicker'>Browse what movie fans are watching now.</div>",
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

    if st.button("‹ Movies", key="details_back"):
        goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    title_text = html.escape(data.get("title") or "Untitled")
    overview = html.escape(data.get("overview") or "No overview available.")
    release = html.escape(data.get("release_date") or "—")
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
        rating_chip = (
            f'<span class="chip rating">★ {float(rating):.1f}</span>'
            if rating is not None
            else ""
        )
    except (TypeError, ValueError):
        rating_chip = ""

    st.markdown(
        f'<div class="detail-hero" style="--hero-bg: url(\'{backdrop}\')">'
        f'<div class="detail-hero-inner">'
        f'<div class="detail-poster-wrap">{poster_html}</div>'
        f'<div class="detail-copy">'
        f'<p class="eyebrow">Featured title</p>'
        f"<h1>{title_text}</h1>"
        f'<div class="meta-row">{rating_chip}'
        f'<span class="chip">{release}</span>'
        f'<span class="chip">{genres}</span></div>'
        f'<p class="overview">{overview}</p>'
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h2 class='section-heading'>Because you picked this</h2>"
        "<div class='section-kicker'>Swipe the rows, tap a poster.</div>",
        unsafe_allow_html=True,
    )

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("<h3 class='section-heading'>Similar movies</h3>", unsafe_allow_html=True)
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
                st.markdown("**Similar titles without poster matches**")
                for item in unlinked_items:
                    st.write(
                        f"- {item.get('title', 'Untitled')} "
                        f"(score: {item.get('score', 0):.3f})"
                    )
            elif not tfidf_items:
                st.info("No local similar titles were found for this movie.")

            st.markdown("<h3 class='section-heading'>More like this</h3>", unsafe_allow_html=True)
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
                "The full recommendation request failed. Showing available "
                "recommendations separately."
            )
            fallback_tfidf, tfidf_err = api_get_json(
                "/recommend/tfidf", params={"title": title, "top_n": 12}
            )
            st.markdown("<h3 class='section-heading'>Similar movies</h3>", unsafe_allow_html=True)
            if not tfidf_err and fallback_tfidf:
                for item in fallback_tfidf:
                    st.write(
                        f"- {item.get('title', 'Untitled')} "
                        f"(score: {item.get('score', 0):.3f})"
                    )
            elif tfidf_err:
                st.info(f"TF-IDF recommendations are unavailable: {tfidf_err}")

            st.markdown("<h3 class='section-heading'>More like this</h3>", unsafe_allow_html=True)
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