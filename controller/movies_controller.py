# controller/movies_controller.py
import pandas as pd
import pickle
import requests
from config import api_key
import streamlit as st

class MoviesController():

    #Hàm lấy thông tin phim từ API The Movie DB
    @staticmethod
    @st.cache_data(show_spinner=False)
    def search_movie(id):
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US"
        try:
            data = requests.get(url).json()
            title = data.get('title', 'N/A')
            overview = data.get('overview', 'No description available.')
            rating = data.get('vote_average', 'N/A')
            release_date = data.get('release_date', 'N/A')
            genres = ', '.join([genre['name'] for genre in data.get('genres', [])])
            description = data.get('overview')
            return {
                'title': title,
                'overview': overview,
                'rating': rating,
                'release_date': release_date,
                'genres': genres,
                'description': description
            }
        except:
            return {
                'title': 'N/A',
                'overview': 'No description available.',
                'rating': 'N/A',
                'release_date': 'N/A',
                'genres': 'N/A',
                'description': 'No description available.'
            }


    # Hàm lấy poster 
    @staticmethod
    @st.cache_data(show_spinner=False)
    def fetch_poster(id):
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={api_key}&language=en-US"
        try:
            data = requests.get(url).json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return "https://via.placeholder.com/150x225?text=No+Image"
        except:
            return "https://via.placeholder.com/150x225?text=No+Image"

    #Hàm lấy trailer phim
    @staticmethod
    def fetch_trailer(id):
        url = f"https://api.themoviedb.org/3/movie/{id}/videos?api_key={api_key}&language=en-US"
        try:
            data = requests.get(url).json()
            for video in data.get('results', []):
                if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                    return "https://www.youtube.com/embed/" + video['key']
            return "No trailer available."
        except:
            return "No trailer available."