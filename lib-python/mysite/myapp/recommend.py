import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_books(user_id, books_df, user_history_dict, top_n=10):
    if books_df.empty:
        return books_df.head(top_n)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(books_df['combined'])

    user_books = books_df[books_df['id'].isin(user_history_dict.get(user_id, []))]
    if user_books.empty:
        return books_df.head(top_n)

    # .mean(axis=0) trả về np.matrix → dùng np.asarray() để chuyển sang array
    user_vector = np.asarray(tfidf.transform(user_books['combined']).mean(axis=0))
    similarities = cosine_similarity(user_vector, tfidf_matrix)

    books_df = books_df.copy()
    books_df['similarity'] = similarities.flatten()
    recommended = books_df.sort_values(by='similarity', ascending=False)

    return recommended[['id', 'title', 'similarity']].head(top_n)
