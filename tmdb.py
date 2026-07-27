API_KEY = "ef9fc1c35c8a6f1c46b5e40bb2645c55"
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"
import streamlit as st
import requests
from utils import convert_runtime
@st.cache_data(ttl=3600)
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []
    data = response.json()

    return {
        "poster": (
            "https://image.tmdb.org/t/p/w500" + data["poster_path"]
            if data.get("poster_path")
            else DEFAULT_POSTER
        ),

        "backdrop": (
            "https://image.tmdb.org/t/p/original" + data["backdrop_path"]
            if data.get("backdrop_path")
            else ""
        ),
        "overview": data.get("overview", "No overview available"),
        "rating": data.get("vote_average", "N/A"),
        "release_date": data.get("release_date", "N/A"),
        "genres": [genre["name"] for genre in data.get("genres", [])],
        "runtime": data.get("runtime", 0)
    }
    st.write(data)
@st.cache_data(ttl=3600)
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []
    data = response.json()

    for video in data.get("results", []):
        if video["site"] == "YouTube" and video["type"] in ["Trailer", "Teaser"]:
            return f"https://www.youtube.com/watch?v={video['key']}"

    return None
@st.cache_data(ttl=3600)
def fetch_tmdb_recommendations(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()

    recommendations = []

    for movie in data.get("results", [])[:10]:

        # Skip movies without posters
        if not movie.get("poster_path"):
            continue

        details = fetch_movie_details(movie["id"])

        cast, director = fetch_cast_and_director(movie["id"])

        recommendations.append({

            "title": movie["title"],

            "poster": details["poster"],

            "backdrop": details["backdrop"],

            "overview": details["overview"],

            "rating": details["rating"],

            "release_date": details["release_date"],

            "genres": details["genres"],

            "runtime": convert_runtime(details["runtime"]),

            "cast": cast,

            "crew": director,

            "trailer": fetch_trailer(movie["id"])
        })


        if len(recommendations) == 5:
            break


    return recommendations
@st.cache_data(ttl=3600)
def search_tmdb_movie(movie_name):

    url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    data = response.json()

    if not data.get("results"):
        return None


    # Prefer exact title match

    for movie in data["results"]:

        if movie["title"].lower() == movie_name.lower():

            return movie["id"]


    # Otherwise most popular

    results = sorted(
        data["results"],
        key=lambda x:x.get("popularity",0),
        reverse=True
    )

    return results[0]["id"]
@st.cache_data(ttl=3600)
def fetch_cast_and_director(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    if response.status_code != 200:
        return [], []

    data = response.json()

    cast = []

    for actor in data.get("cast", [])[:10]:
        cast.append(actor["name"])

    director = []

    for member in data.get("crew", []):
        if member["job"] == "Director":
            director.append(member["name"])

    return cast, director
@st.cache_data(ttl=3600)
def get_external_movie(movie_name):

    movie_id = search_tmdb_movie(movie_name)

    if movie_id is None:
        return None

    details = fetch_movie_details(movie_id)

    cast, director = fetch_cast_and_director(movie_id)

    trailer = fetch_trailer(movie_id)

    return {

        "title": movie_name,

        "poster": details["poster"],

        "backdrop": details["backdrop"],

        "overview": details["overview"],

        "rating": details["rating"],

        "release_date": details["release_date"],

        "genres": details["genres"],

        "runtime": convert_runtime(details["runtime"]),

        "cast": cast,

        "crew": director,

        "trailer": trailer

    }
@st.cache_data(ttl=3600)
def fetch_trending_movies():

    url = f"https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    data = response.json()

    trending = []

    for movie in data.get("results", [])[:10]:

        details = fetch_movie_details(movie["id"])

        cast, director = fetch_cast_and_director(movie["id"])

        trending.append({

            "title": movie["title"],

            "poster": details["poster"],

            "backdrop": details["backdrop"],

            "overview": details["overview"],

            "rating": details["rating"],

            "release_date": details["release_date"],

            "genres": details["genres"],

            "runtime": convert_runtime(details["runtime"]),

            "cast": cast,

            "crew": director,

            "trailer": fetch_trailer(movie["id"])

        })

    return trending
@st.cache_data(ttl=3600)
def fetch_top_rated_movies():

    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return []

    data = response.json()

    top_rated = []

    for movie in data.get("results", [])[:10]:

        details = fetch_movie_details(movie["id"])

        cast, director = fetch_cast_and_director(movie["id"])

        top_rated.append({

            "title": movie["title"],

            "poster": details["poster"],

            "backdrop": details["backdrop"],

            "overview": details["overview"],

            "rating": details["rating"],

            "release_date": details["release_date"],

            "genres": details["genres"],

            "runtime": convert_runtime(details["runtime"]),

            "cast": cast,

            "crew": director,

            "trailer": fetch_trailer(movie["id"])

        })

    return top_rated