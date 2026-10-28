import os, pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'movies_metadata.csv')
DF_PATH = os.path.join(BASE_DIR, 'df.pkl')
INDICES_PATH = os.path.join(BASE_DIR, 'indices.pkl')
TFIDF_PATH = os.path.join(BASE_DIR, 'tfidf.pkl')
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, 'tfidf_matrix.pkl')

print('Loading CSV')
df = pd.read_csv(CSV_PATH, low_memory=False)
# Ensure there's a title column (common column name in dataset)
if 'title' not in df.columns:
    raise RuntimeError('CSV missing title column')
# Fill missing titles
df['title'] = df['title'].fillna('').astype(str)

print('Building TFIDF on titles')
vectorizer = TfidfVectorizer(stop_words='english')
# Fit on titles
tfidf_matrix = vectorizer.fit_transform(df['title'])

# Build indices map: title (lower stripped) -> row index
indices_obj = {title.strip().lower(): idx for idx, title in enumerate(df['title'])}

# Save pickles
print('Saving pickles')
with open(DF_PATH, 'wb') as f:
    pickle.dump(df, f)
with open(INDICES_PATH, 'wb') as f:
    pickle.dump(indices_obj, f)
with open(TFIDF_PATH, 'wb') as f:
    pickle.dump(vectorizer, f)
with open(TFIDF_MATRIX_PATH, 'wb') as f:
    pickle.dump(tfidf_matrix, f)

print('Done')

