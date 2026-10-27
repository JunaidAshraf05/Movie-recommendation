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
        "background": "#12151C",
        "surface": "#1C1F29",
        "surface_elevated": "#2B2F3D",
        "text": "#F9FAFB",
        "text_secondary": "#E3E5EB",
        "muted": "#8B92A2",
        "border": "rgba(227, 229, 235, 0.12)",
        "accent": "#E86360",
        "accent_hover": "#F07874",
        "input": "#1C1F29",
        "shadow": "0 16px 40px rgba(0, 0, 0, 0.24)",
    }
    if st.session_state.dark_mode
    else {
        "background": "#F3F4F6",
        "surface": "#FFFFFF",
        "surface_elevated": "#E9EBF0",
        "text": "#111318",
        "text_secondary": "#1C1F29",
        "muted": "#6C7283",
        "border": "rgba(28, 31, 41, 0.12)",
        "accent": "#E2504C",
        "accent_hover": "#C9403C",
        "input": "#FFFFFF",
        "shadow": "0 16px 40px rgba(17, 19, 24, 0.08)",
    }
)

st.markdown(
    f"""
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
  --rating: #F4B942;
}}
.stApp {{
  background: var(--app-bg);
  color: var(--text-primary);
  transition: background-color 220ms ease, color 220ms ease;
}}
.stApp, button, input, textarea, [data-testid="stSelectbox"] {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.block-container {{ padding: 1.5rem 2rem 3rem; max-width: 1280px; }}
[data-testid="stAppViewContainer"] {{ background: var(--app-bg); }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--border-subtle); }}
[data-testid="stSidebar"] * {{ color: var(--text-primary); }}
h1, h2, h3, p, label {{ color: var(--text-primary); }}
h1, h2, h3 {{ letter-spacing: -0.035em; }}
.stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-muted); }}
.small-muted {{ color: var(--text-muted); font-size: 0.92rem; }}
.app-toolbar {{ display: flex; align-items: center; gap: 0.8rem; min-height: 3.2rem; }}
.brand-mark {{
  display: inline-grid; place-items: center; width: 2.45rem; height: 2.45rem;
  margin-right: 0.55rem; border-radius: 0.85rem; background: var(--accent);
  color: white; font-size: 1.2rem; vertical-align: middle;
}}
.brand-name {{ font-size: 1.2rem; font-weight: 750; letter-spacing: -0.035em; }}
.brand-caption {{ display: block; margin-left: 3.1rem; color: var(--text-muted); font-size: 0.78rem; }}
[data-testid="stTextInput"] input {{
  background: var(--input-bg); color: var(--text-primary);
  border: 1px solid var(--border-subtle); border-radius: 0.85rem; min-height: 3rem;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}}
[data-testid="stTextInput"] input:focus {{
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 18%, transparent);
}}
[data-testid="stSelectbox"] > div > div {{
  background: var(--input-bg); color: var(--text-primary);
  border-color: var(--border-subtle); border-radius: 0.75rem;
}}
button[kind="secondary"], button[kind="primary"] {{
  border-radius: 0.75rem !important;
  transition: transform 160ms ease, background-color 160ms ease, border-color 160ms ease;
}}
button[kind="secondary"] {{
  background: var(--surface); color: var(--text-primary); border: 1px solid var(--border-subtle);
}}
button[kind="secondary"]:hover {{
  border-color: var(--accent); color: var(--accent); transform: translateY(-1px);
}}
button[kind="primary"] {{ background: var(--accent); border-color: var(--accent); }}
button[kind="primary"]:hover {{ background: var(--accent-hover); border-color: var(--accent-hover); }}
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--surface); border-color: var(--border-subtle) !important;
  border-radius: 1rem !important; box-shadow: var(--card-shadow); overflow: hidden;
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}}
[data-testid="stVerticalBlockBorderWrapper"]:hover {{
  border-color: color-mix(in srgb, var(--accent) 60%, var(--border-subtle)) !important;
  box-shadow: var(--card-shadow);
}}
[data-testid="stImage"] img {{ border-radius: 0.7rem; }}
.movie-card-meta {{
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 0.35rem; min-height: 3.25rem; padding: 0.45rem 0.05rem 0.1rem;
}}
.movie-title-card {{
  display: -webkit-box; overflow: hidden; color: var(--text-primary);
  font-size: 0.88rem; font-weight: 650; line-height: 1.25rem;
  -webkit-box-orient: vertical; -webkit-line-clamp: 2;
}}
.movie-rating {{ flex: 0 0 auto; color: var(--rating); font-size: 0.82rem; font-weight: 750; white-space: nowrap; }}
.detail-rating {{
  display: inline-flex; align-items: center; gap: 0.35rem; margin: 0.2rem 0 0.85rem;
  padding: 0.35rem 0.65rem; border: 1px solid rgba(244, 185, 66, 0.25);
  border-radius: 999px; background: rgba(244, 185, 66, 0.1);
  color: var(--rating); font-size: 0.9rem; font-weight: 750;
}}
.poster-placeholder {{
  display: grid; place-items: center; aspect-ratio: 2 / 3;
  border-radius: 0.7rem; background: var(--surface-elevated); color: var(--text-muted);
}}
[data-testid="stAlert"] {{ border-radius: 0.85rem; }}
.section-heading {{ margin: 1.5rem 0 0.8rem; }}
.section-kicker {{ color: var(--text-muted); font-size: 0.85rem; margin-top: -0.35rem; }}
.hero-copy {{ margin: 0.15rem 0 0.8rem; }}
.toolbar-container {{ margin-bottom: 1.5rem; }}
.pagination-status {{ color: var(--text-muted); text-align: center; padding-top: 0.55rem; }}
@media (max-width: 700px) {{
  .block-container {{ padding: 1rem 1rem 2rem; }}
  .brand-caption {{ display: none; }}
  .brand-name {{ font-size: 1.02rem; }}
  .section-heading {{ margin-top: 1rem; }}
  [data-testid="stHorizontalBlock"]:has(.movie-card-meta) {{
    display: grid !important;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }}
  [data-testid="stHorizontalBlock"]:has(.movie-card-meta) > [data-testid="column"] {{
    width: auto !important;
    min-width: 0 !important;
    flex: initial !important;
  }}
}}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ scroll-behavior: auto !important; transition-duration: 0.01ms !important; }}
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


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            rating = m.get("vote_average")
            try:
                rating_label = f"★ {float(rating):.1f}" if rating is not None else ""
            except (TypeError, ValueError):
                rating_label = ""

            with colset[c]:
                with st.container(border=True):
                    if poster:
                        st.image(poster, use_column_width=True)
                    else:
                        st.markdown(
                            "<div class='poster-placeholder'>🎬<br>No poster</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        "<div class='movie-card-meta'>"
                        f"<span class='movie-title-card'>{html.escape(str(title))}</span>"
                        f"<span class='movie-rating'>{rating_label}</span>"
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "View details",
                        key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}",
                        use_container_width=True,
                    ):
                        if tmdb_id:
                            goto_details(tmdb_id)


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
            "<span class='brand-caption'>Discover your next favorite</span>",
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
    "<div class='small-muted hero-copy'>A handpicked cinema experience, powered by TMDB.</div>",
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
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, limit=24
                )

                # Dropdown
                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        # map label -> id
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("<h3 class='section-heading'>Search results</h3>", unsafe_allow_html=True)
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
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

    poster_grid(home_cards.get("results", []), cols=grid_cols, key_prefix="home_feed")
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

    if st.button("← Back to movies", key="details_back"):
        goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        with st.container(border=True):
            if data.get("poster_url"):
                st.image(data["poster_url"], use_column_width=True)
            else:
                st.markdown(
                    "<div class='poster-placeholder'>🎬<br>No poster</div>",
                    unsafe_allow_html=True,
                )

    with right:
        with st.container(border=True):
            st.markdown(f"## {html.escape(data.get('title', ''))}")
            rating = data.get("vote_average")
            if rating is not None:
                st.markdown(
                    f"<span class='detail-rating'>★ {float(rating):.1f}"
                    "<span class='small-muted'>/ 10</span></span>",
                    unsafe_allow_html=True,
                )
            release = data.get("release_date") or "-"
            genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
            st.markdown(
                f"<div class='small-muted'>Release: {html.escape(release)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='small-muted'>Genres: {html.escape(genres)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            st.markdown("### Overview")
            st.write(data.get("overview") or "No overview available.")

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], use_column_width=True)

    st.markdown(
        "<h2 class='section-heading'>Recommendations</h2>"
        "<div class='section-kicker'>More films selected for your next movie night.</div>",
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
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")