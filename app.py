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
# STYLES (minimal modern)
# =============================
st.markdown(
    """
<style>
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
.small-muted { color:#6b7280; font-size: 0.92rem; }
.movie-title { font-size: 0.9rem; line-height: 1.15rem; height: 2.3rem; overflow: hidden; }
.card { border: 1px solid rgba(0,0,0,0.08); border-radius: 16px; padding: 14px; background: rgba(255,255,255,0.7); }
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

            with colset[c]:
                if poster:
                    st.image(poster, use_column_width=True)
                else:
                    st.write("🖼️ No poster")

                if st.button("Open", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}"):
                    if tmdb_id:
                        goto_details(tmdb_id)

                st.markdown(
                    f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True
                )


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
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
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
            f"<div style='text-align:center'>Page {page} of {total_pages}</div>",
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
# SIDEBAR (clean)
# =============================
with st.sidebar:
    st.markdown("## 🎬 Menu")
    if st.button("🏠 Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### 🏠 Home Feed (only home)")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )
    if home_category != st.session_state.last_home_category:
        st.session_state.home_page = 1
        st.session_state.last_home_category = home_category
    grid_cols = st.slider("Grid columns", 4, 8, 6)

# =============================
# HEADER
# =============================
st.title("🎬 Movie Recommender")
st.markdown(
    "<div class='small-muted'>Type keyword → dropdown suggestions + matching results → open → details + recommendations</div>",
    unsafe_allow_html=True,
)
st.divider()

# ==========================================================
# VIEW: HOME
# ==========================================================
if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title (keyword)", placeholder="Type: avenger, batman, love..."
    )
    search_term = typed.strip()
    if search_term != st.session_state.last_search_term:
        st.session_state.search_page = 1
        st.session_state.last_search_term = search_term

    st.divider()

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

                st.markdown("### Results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")
                page_controls(
                    page=int(data.get("page", st.session_state.search_page)),
                    total_pages=min(int(data.get("total_pages", 1)), 500),
                    state_key="search_page",
                    key_prefix="search_results_paging",
                )

        st.stop()

    # HOME FEED MODE
    st.markdown(f"### 🏠 Home — {home_category.replace('_',' ').title()}")

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

    # Top bar
    a, b = st.columns([3, 1])
    with a:
        st.markdown("### 📄 Movie Details")
    with b:
        if st.button("← Back to Home"):
            goto_home()

    # Details (your FastAPI safe route)
    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    # Layout: Poster LEFT, Details RIGHT
    left, right = st.columns([1, 2.4], gap="large")

    with left:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        if data.get("poster_url"):
            st.image(data["poster_url"], use_column_width=True)
        else:
            st.write("🖼️ No poster")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"## {data.get('title','')}")
        release = data.get("release_date") or "-"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        st.markdown(
            f"<div class='small-muted'>Release: {release}</div>", unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='small-muted'>Genres: {genres}</div>", unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown("### Overview")
        st.write(data.get("overview") or "No overview available.")
        st.markdown("</div>", unsafe_allow_html=True)

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], use_column_width=True)

    st.divider()
    st.markdown("### ✅ Recommendations")

    # Recommendations (TF-IDF + Genre) via your bundle endpoint
    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
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

            st.markdown("#### 🎭 More Like This (Genre)")
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
            st.markdown("#### 🔎 Similar Movies (TF-IDF)")
            if not tfidf_err and fallback_tfidf:
                for item in fallback_tfidf:
                    st.write(
                        f"- {item.get('title', 'Untitled')} "
                        f"(score: {item.get('score', 0):.3f})"
                    )
            elif tfidf_err:
                st.info(f"TF-IDF recommendations are unavailable: {tfidf_err}")

            st.markdown("#### 🎭 More Like This (Genre)")
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