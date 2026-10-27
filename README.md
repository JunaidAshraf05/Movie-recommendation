# Movie Recommendation System

A movie discovery app that combines a local machine learning model with live TMDB data. Search for a film, open its detail page, and get recommendations two ways: similar titles from a TF-IDF model, and genre-based picks from TMDB.

Built with **Python, Streamlit, FastAPI, scikit-learn (TF-IDF)** and the **TMDB API**.

<!-- EDIT: add a screenshot or GIF here, e.g. ![App demo](demo.png) -->

**Live demo:** [add link if deployed]

---

## Features

- **Movie feed:** browse movies right on the home screen
- **Search by title:** find any film quickly
- **Detail pages:** posters, descriptions and metadata for each movie
- **Similar-title recommendations:** powered by a local TF-IDF model
- **Genre-based picks:** pulled live from the TMDB API
- **Clean separation:** Streamlit frontend talks to a FastAPI backend

---

## How It Works

```
Streamlit UI  ──►  FastAPI backend  ──►  Local TF-IDF model + dataset
                         │
                         └────────────►  TMDB API (search, posters, metadata)
```

1. The user searches for a movie or opens one from the feed in the **Streamlit** app.
2. The request goes to the **FastAPI** backend.
3. **Recommendations:** the backend vectorizes movie text with **TF-IDF** (`[fields used, e.g. overview, genres, keywords]`) and ranks similar titles using `[similarity method, e.g. cosine similarity]`.
4. **Metadata and genre picks:** the backend calls **TMDB** for posters, descriptions and genre-based suggestions.
5. Results are sent back and shown in the UI.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Backend | FastAPI, Uvicorn |
| ML / NLP | scikit-learn, TF-IDF |
| Data | Local movie dataset (`[dataset name, N movies]`), TMDB API |

---

## Project Structure

```
Movie-recommendation/
├── app.py              # Streamlit frontend
├── main.py             # FastAPI backend
├── [model/data files]  # TF-IDF model and movie dataset
├── requirements.txt
└── README.md
```

<!-- EDIT: match this to your real folder structure -->

---

## Getting Started

**1. Clone the repo**

```bash
git clone https://github.com/JunaidAshraf05/Movie-recommendation.git
cd Movie-recommendation
```

**2. Create a virtual environment and install dependencies**

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add your TMDB API key**

Get a free key from [themoviedb.org](https://www.themoviedb.org/settings/api), then create a `.env` file:

```
TMDB_API_KEY=your_key_here
```

**4. Start the backend**

```bash
uvicorn main:app --reload
```

**5. Start the frontend** (in a new terminal)

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually `http://localhost:8501`).

---

## API Endpoints

<!-- EDIT: replace with your actual routes -->

| Method | Endpoint | Description |
|---|---|---|
| GET | `/[search-route]` | Search movies by title |
| GET | `/[details-route]` | Get movie details |
| GET | `/[recommend-route]` | Get TF-IDF similar-movie recommendations |

---

## Future Improvements

- Add user ratings and collaborative filtering for hybrid recommendations
- Deploy the backend and frontend online
- Add filters by year, rating and language
- Cache TMDB responses to speed things up

---

## Credits

Movie data and images provided by [The Movie Database (TMDB)](https://www.themoviedb.org/). This project uses the TMDB API but is not endorsed or certified by TMDB.

---

## Author

**Junaid** · [GitHub](https://github.com/JunaidAshraf05) · [Portfolio](https://junaidashraf05.github.io/Portfolio1)
