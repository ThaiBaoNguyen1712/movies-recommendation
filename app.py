import streamlit as st
import pandas as pd
import numpy as np 
import time
from config import api_key
from ultils.loader import loader
from controller.movies_controller import MoviesController
from controller.cookies_controller import CookiesController
from controller.recommender_controller import RecommenderController
import streamlit.components.v1 as components
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

movies_list, similarity = loader.load_models()
movie_dict = dict(zip(movies_list['title'], movies_list['id']))


# Page config
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="auto"
)


#sidebar
st.sidebar.title("Movie Recommendation System")
page = st.sidebar.selectbox("Choose a page", ["Home", "Movies", "Recommendations"])

if page == "Home":
    st.title("Welcome to Movie Recommendation System")
    st.write("Discover new movies based on your preferences!")
    st.markdown('HOT MOVIES')
    movies = RecommenderController.recommend_top_popular(5)
    if not movies.empty:
        for idx, movie in movies.iterrows():
            movie_id = int(movie['id'])
            movie_get = MoviesController.search_movie(movie_id)
            poster = MoviesController.fetch_poster(movie_id)

            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(poster, use_container_width=True)
            with col2:
                st.markdown(f"**{movie_get['title']}**")
                st.write(f"Release Date: {movie_get['release_date']}")
                st.write(f"Rating: {movie_get['rating']}")
                st.write(f"Genres: {movie_get['genres']}")
                st.write(movie_get['overview'])


elif page == "Movies":
    st.title("Movies")
     # Search movies
      # --- Search bằng selectbox có autocomplete ---
    def on_select_change():
        st.session_state.selected_movie = st.session_state.selected_title
        st.session_state.page = "details"

    search_query = st.selectbox(
            "Search movie title...",
            options=movie_dict.keys(),
            index=None,
            key="selected_title",
            placeholder="Start typing movie title...",
            on_change=on_select_change
        )
    
    if search_query:
        movie_id = movie_dict[search_query]
        movie_data = MoviesController.search_movie(movie_id)
        movie_title = movie_data['title'] 
        poster = MoviesController.fetch_poster(movie_id)
        movie_trailer = MoviesController.fetch_trailer(movie_id)

            # ===== TITLE =====
        st.markdown(f"## {movie_data['title']}")

        # ===== MAIN LAYOUT =====
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(poster, use_container_width=True)

        with col2:
            st.markdown(
                f"""
                **Release Date:** {movie_data['release_date']}  
                **Rating:** {movie_data['rating']}  
                **Genres:** {movie_data['genres']}
                """
            )

            st.markdown("### Overview")
            st.write(movie_data['overview'])

        # ===== TRAILER =====
        if movie_trailer:
            st.markdown("---")
            st.markdown("### Trailer")
            components.iframe(
                movie_trailer,
                height=480,
                scrolling=False
            )

        #==== Rating Section =====
        st.markdown("---")
        st.markdown("### Rate this movie")
        watched = st.checkbox("I have watched this movie")
        rating = st.slider("Select your rating (1-10):", 1, 10, 5)
        if st.button("Submit Rating"):
            if watched:
                CookiesController.add_watched_movie(movie_id)
            st.success(f"Thank you for rating {movie_data['title']} with a score of {rating}!")
            if rating > 7:
                CookiesController.latest_movie_watched(movie_title)
        

        #==== Similar Movies Section =====
        st.markdown("---")
        st.markdown("### Similar Movies for you")
        movies_sim = RecommenderController.recommend_similar_movies(movie_title)
        if movies_sim:
           for movie in movies_sim:
            with st.expander(f"{movie['title']}"):
                st.write(f"**Overview:** {movie['overview']}")
                st.write(f"**Genres:** {movie['genres']} ")
                st.write(f"**Rating:** {movie['rating']}/10")
                
                # Get and display trailer
                try:
                    video_url = MoviesController.fetch_trailer(movie['id'])
                    if video_url:
                        st.video(video_url)
                    else:
                        st.warning("Không tìm thấy trailer cho phim này")
                except Exception as e:
                    st.warning(f"Không thể tải trailer: {str(e)}")
        
        else:
            st.write('There are no films that match in terms of content.')

                
elif page == "Recommendations":
    st.title("Movie Recommendations")
    # Select recommendation type
    rcm_type = st.selectbox(
        "Choose recommendation type",
        ["Collaborative Filtering", "Content-based Filtering", "Hybrid Filtering"]
    )

    # Lấy latest movie
    latest_movie = CookiesController.get_latest_movie_watched()
    if latest_movie:
        latest_title = latest_movie
    else:
        latest_title = "Avatar"
    
    if rcm_type =='Collaborative Filtering':
        try:
            rcm_movies = RecommenderController.recommend_collaborative_movies(latest_title,top_n = 10)
        except Exception as e:
            st.error(f"Lỗi khi recommend: {e}")
            rcm_movies = []

        if rcm_movies:
            for movie in rcm_movies:
                with st.expander(f"{movie['title']}"):
                    st.write(f"**Overview:** {movie['overview']}")
                    st.write(f"**Genres:** {movie['genres']} ")
                    st.write(f"**Rating:** {movie['rating']}/10")
                    
                    # Get and display trailer
                    try:
                        video_url = MoviesController.fetch_trailer(movie['id'])
                        if video_url:
                            st.video(video_url)
                        else:
                            st.warning("Không tìm thấy trailer cho phim này")
                    except Exception as e:
                        st.warning(f"Không thể tải trailer: {str(e)}")
        
        else:
            st.warning('Đã có lỗi')
            
    elif rcm_type == 'Content-based Filtering':
        try:
            rcm_movies = RecommenderController.recommend_similar_movies(latest_title,top_n=10)
        except Exception as e:
            st.error(f"Lỗi khi recommend: {e}")
            rcm_movies = []

        if rcm_movies:
            for movie in rcm_movies:
                with st.expander(f"{movie['title']}"):
                    st.write(f"**Overview:** {movie['overview']}")
                    st.write(f"**Genres:** {movie['genres']} ")
                    st.write(f"**Rating:** {movie['rating']}/10")
                    
                    # Get and display trailer
                    try:
                        video_url = MoviesController.fetch_trailer(movie['id'])
                        if video_url:
                            st.video(video_url)
                        else:
                            st.warning("Không tìm thấy trailer cho phim này")
                    except Exception as e:
                        st.warning(f"Không thể tải trailer: {str(e)}")
        
        else:
            st.warning('Đã có lỗi')
        
    else:
        try:
            rcm_movies = RecommenderController.recommend_hybrid_movies(latest_title,top_n=10)
        except Exception as e:
            st.error(f"Lỗi khi recommend: {e}")
            rcm_movies = []

        if rcm_movies:
            for movie in rcm_movies:
                with st.expander(f"{movie['title']}"):
                    st.write(f"**Overview:** {movie['overview']}")
                    st.write(f"**Genres:** {movie['genres']} ")
                    st.write(f"**Rating:** {movie['rating']}/10")
                    
                    # Get and display trailer
                    try:
                        video_url = MoviesController.fetch_trailer(movie['id'])
                        if video_url:
                            st.video(video_url)
                        else:
                            st.warning("Không tìm thấy trailer cho phim này")
                    except Exception as e:
                        st.warning(f"Không thể tải trailer: {str(e)}")
        
        else:
            st.warning('Đã có lỗi')
