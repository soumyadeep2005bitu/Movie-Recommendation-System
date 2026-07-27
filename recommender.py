from utils import convert_runtime
import requests
import streamlit as st
from tmdb import fetch_movie_details, fetch_trailer

def recommend(movie, movies, similarity1):
    index = movies[movies['title'] == movie].index[0]

    distances = similarity1[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id

        details = fetch_movie_details(movie_id)
        trailer = fetch_trailer(movie_id)

        recommended_movies.append({

            "title": movies.iloc[i[0]].title,

            "poster": details["poster"],

            "backdrop": details["backdrop"],

            "overview": details["overview"],

            "rating": details["rating"],

            "release_date": details["release_date"],

            "genres": details["genres"],

            "runtime": convert_runtime(details["runtime"]),

            "cast": movies.iloc[i[0]].cast,

            "crew": movies.iloc[i[0]].crew,

            "trailer": trailer
        })

    return recommended_movies

def get_movie_details(movie, movies):

    index = movies[movies['title'] == movie].index[0]

    movie_id = movies.iloc[index].movie_id

    details = fetch_movie_details(movie_id)

    return {

        "title": movies.iloc[index].title,

        "poster": details["poster"],

        "backdrop": details["backdrop"],

        "overview": details["overview"],

        "rating": details["rating"],

        "release_date": details["release_date"],

        "genres": details["genres"],

        "runtime": convert_runtime(details["runtime"]),

        "cast": movies.iloc[index].cast,

        "crew": movies.iloc[index].crew,

        "trailer": fetch_trailer(movie_id)

    }
@st.cache_data(ttl=600)

def search_movies(search_term, API_KEY):

    if not search_term:
        return []

    url = (
        f"https://api.themoviedb.org/3/search/movie"
        f"?api_key={API_KEY}"
        f"&query={search_term}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()

    return [
        movie["title"]
        for movie in data.get("results", [])[:8]
    ]

