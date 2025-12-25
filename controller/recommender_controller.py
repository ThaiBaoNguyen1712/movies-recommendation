#controller/ recommender_controller
import numpy as np
import pandas as pd
import os
import streamlit as st
from controller.movies_controller import MoviesController
from ultils.loader import loader

movies_list, similarity = loader.load_models()

class RecommenderController():
    # Hàm gợi ý các phim hot TMDB
    @staticmethod
    @st.cache_data
    def recommend_top_popular(n=5):
        # Lấy đường dẫn file CSV tương đối
        current_dir = os.path.dirname(__file__)  # folder của controller
        csv_path = os.path.join(current_dir, "..", "data", "movies_match_tmdb.csv")
        csv_path = os.path.abspath(csv_path)     # chuyển sang đường dẫn tuyệt đối

        # Đọc file CSV
        movies = pd.read_csv(csv_path) 
        # R - rating
        vote_avg = movies['vote_average']

        # v - number of votes
        vote_count = movies['vote_count']

        # m - minimum votes required
        m = movies['vote_count'].quantile(0.7)

        # C - mean rating across all movies
        c = vote_avg.mean()

        def weighted_rating(x, m=m, c=c):
            v = x['vote_count']
            R = x['vote_average']
            return (v / (v + m) * R) + (m / (v + m) * c)
        
        movies['popular_score'] = movies.apply(weighted_rating, axis=1)
        
        return movies.sort_values('popular_score', ascending=False).head(n)
    
    @st.cache_data
    def recommend_similar_movies(movie_title, top_n=5):
        # Lấy index của movie trong movies_list
        idx_series = movies_list[movies_list['title'] == movie_title].index
        if len(idx_series) == 0:
            return []  # movie không tồn tại
        index = idx_series[0]

        # Lấy danh sách khoảng cách similarity, sắp xếp giảm dần
        distances = sorted(
            list(enumerate(similarity[index])),
            reverse=True,
            key=lambda x: x[1]
        )

        movies_get = []
        for i in distances[1: top_n+1]:  # bỏ chính movie, lấy top_n
            movie_id = movies_list.iloc[i[0]]['id']
            movie_info = MoviesController.search_movie(int(movie_id))
            poster = MoviesController.fetch_poster(int(movie_id))
            movies_get.append({
                'id': movie_id,
                'title': movie_info['title'],
                'release_date': movie_info['release_date'],
                'rating': movie_info['rating'],
                'genres': movie_info['genres'],
                'overview': movie_info['overview'],
                'poster': poster
            })
        
        return movies_get
    
    @st.cache_data
    def recommend_collaborative_movies(movie_name, top_n=5):
        movies, links, final_dataset, knn, csr_data = loader.load_models_collaborative()

        # Tìm phim trong TMDB bằng title
        movie_list = movies[movies['title'].str.contains(movie_name, case=False, na=False)]
        if movie_list.empty:
            return []

        tmdb_id = movie_list.iloc[0]['id']

        movie_id_arr = links.loc[links['tmdbId'] == tmdb_id, 'movieId'].values
        if len(movie_id_arr) == 0:
            return []

        movie_id = movie_id_arr[0]

        idx_series = final_dataset[final_dataset['movieId'] == movie_id].index
        if len(idx_series) == 0:
            return []

        idx = idx_series[0]

        distances, indices = knn.kneighbors(csr_data[idx], n_neighbors=top_n + 1)
        recs = list(zip(indices.squeeze()[1:], distances.squeeze()[1:]))

        movies_get = []
        for i, dist in recs:
            rec_movie_id = final_dataset.iloc[i]['movieId']

            # Lấy info từ movies + links
            tmdb_row = movies.merge(links, left_on='id', right_on='tmdbId')
            movie_info_row = tmdb_row[tmdb_row['movieId'] == rec_movie_id]

            if not movie_info_row.empty:
                row = movie_info_row.iloc[0]
                poster = MoviesController.fetch_poster(int(row['id']))
                movies_get.append({
                    'id': int(row['id']),
                    'title': row['title'],
                    'release_date': row.get('release_date', ''),
                    'rating': row.get('vote_average', 0),
                    'genres': row.get('genres', []),
                    'overview': row.get('overview', ''),
                    'poster': poster,
                    'distance': dist
                })

        return movies_get


    @staticmethod
    @st.cache_data
    def recommend_hybrid_movies(movie_title, top_n=5, alpha=0.6):
        # --- CF recommendation ---
        cf_list = RecommenderController.recommend_collaborative_movies(movie_title, top_n=top_n)

        # --- CB recommendation ---
        cb_list = RecommenderController.recommend_similar_movies(movie_title, top_n=top_n)

        # --- Gộp CF + CB ---
        hybrid_dict = {}

        for movie in cf_list:
            hybrid_dict[movie['title']] = {
                'info': movie,
                'score_cf': movie.get('distance', 0),  # khoảng cách KNN CF
                'score_cb': 0
            }

        for movie in cb_list:
            if movie['title'] in hybrid_dict:
                hybrid_dict[movie['title']]['score_cb'] = 1 - movie.get('distance', 0)  # CB similarity có thể dùng 1 - distance
            else:
                hybrid_dict[movie['title']] = {
                    'info': movie,
                    'score_cf': 0,
                    'score_cb': 1 - movie.get('distance', 0)
                }

        # --- Tính điểm hybrid ---
        for k, v in hybrid_dict.items():
            # score càng cao thì càng được ưu tiên
            v['score'] = alpha * v['score_cf'] + (1 - alpha) * v['score_cb']

        # --- Sắp xếp theo score giảm dần ---
        hybrid_list = sorted(hybrid_dict.values(), key=lambda x: x['score'], reverse=True)

        # --- Trả về list dict giống CF/CB ---
        return [v['info'] for v in hybrid_list[:top_n]]