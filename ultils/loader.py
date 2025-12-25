import pickle
import streamlit as st
import pandas as pd

class loader():
    @st.cache_resource
    def load_models():
        movies = pickle.load(open("artifacts/movie_list.pkl", "rb"))
        similarity = pickle.load(open("artifacts/similary.pkl", "rb"))

        return movies, similarity

    @st.cache_resource
    def load_models_collaborative():
        movies = pd.read_pickle('models/movies.pkl')
        links = pd.read_pickle('models/links.pkl')
        final_dataset = pd.read_pickle('models/final_dataset.pkl')
        with open('models/knn_model.pkl', 'rb') as f:
            knn = pickle.load(f)
        with open('models/csr_data.pkl', 'rb') as f:
            csr_data = pickle.load(f)
            
        return movies, links, final_dataset, knn, csr_data