import json
from streamlit_cookies_controller import CookieController

class CookiesController:
    _cookies = CookieController()

    #Lấy ra 5 watched movies từ cookie
    @staticmethod
    def get_watched_movies(n=5):
        value = CookiesController._cookies.get("watched_movies")
        if not value:
            return []
        try:
            watched = json.loads(value)
            return watched[:n]
        except:
            return []

    @staticmethod
    def add_watched_movie(movie_id):
        watched = CookiesController.get_watched_movies()
        if movie_id not in watched:
            watched.append(movie_id)
            CookiesController._cookies.set(
                "watched_movies",
                json.dumps(watched)
            )

    @staticmethod
    def remove_watched_movie(movie_id):
        watched = CookiesController.get_watched_movies()
        if movie_id in watched:
            watched.remove(movie_id)
            CookiesController._cookies.set(
                "watched_movies",
                json.dumps(watched)
            )

    @staticmethod
    def latest_movie_watched(movie_title):
        CookiesController._cookies.set("latest_movie_watched", movie_title)
    @staticmethod
    def get_latest_movie_watched():
        return CookiesController._cookies.get('latest_movie_watched')
        