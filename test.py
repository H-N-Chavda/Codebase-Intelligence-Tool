import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load nodes
with open("output/nodes.json") as f:
    nodes = json.load(f)

texts = [n["embedding_text"] for n in nodes]

# Build vectorizer
vectorizer = TfidfVectorizer(ngram_range=(1,2))
X = vectorizer.fit_transform(texts)

# Query
query = "enrich embedding text"
q_vec = vectorizer.transform([query])

# Compute similarity
scores = cosine_similarity(q_vec, X)[0]

# Get top results
top_k = 5
top_indices = scores.argsort()[-top_k:][::-1]

# Print results
for i in top_indices:
    print(f"{nodes[i]['type']} {nodes[i]['name']} | score={scores[i]:.3f}")