import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
DEFAULT_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"
from streamlit_searchbox import st_searchbox
import streamlit as st
import pickle
import pandas as pd
import requests
import time


from tmdb import (
    fetch_movie_details,
    fetch_trailer,
    fetch_tmdb_recommendations,
    search_tmdb_movie,
    get_external_movie,
    fetch_trending_movies,
    fetch_top_rated_movies
)
from recommender import recommend, get_movie_details, search_movies, convert_runtime
from ui import (
    display_cast,
    display_director
)

st.set_page_config(
    page_title="MOVIZIO",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()



if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "searched_movie" not in st.session_state:
    st.session_state.searched_movie = None
# ---------------- Theme ---------------- #

if "favorites" not in st.session_state:
    st.session_state.favorites = []

@st.cache_resource
def load_data():
    movie_dict = pickle.load(open("movie_dict1.pkl", "rb"))
    movies = pd.DataFrame(movie_dict)

    similarity = pickle.load(open("similarity1.pkl", "rb"))

    return movies, similarity

movies, similarity1 = load_data()

with st.sidebar:

    st.image("movizio_logo.png", use_container_width=True)

    st.markdown(
        "<p style='text-align:center;color:gray;'>Discover • Explore • Enjoy</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    menu = st.radio(
        "",
        [
            "🏠 Home",
            "🔥 Trending",
            "⭐ Top Rated",
            "❤️ Favorites",
            "ℹ️ About"
        ]
    )

    st.info(
        "🎬 Powered by TMDB API\n\n"
        "🤖 AI Recommendation Engine\n\n"
        "⭐ Personalized Suggestions"
    )
from PIL import Image

logo = Image.open("movizio_logo.png")

col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.image(logo, use_container_width=True)

st.markdown(
    """
    <h2 style='text-align:center;
               color:white;
               font-weight:500;
               margin-top:-15px;'>
        AI Powered Movie Recommendation System
    </h2>
    """,
    unsafe_allow_html=True
)
if menu == "🏠 Home":

    def search_wrapper(search_term):
        return search_movies(search_term, API_KEY)


    selected_moviename = st_searchbox(
        search_wrapper,
        placeholder="🎬 Enter a movie name..."
    )

    if st.button("🎬 Recommend"):

        movie_name = selected_moviename.strip()

        if movie_name == "":
            st.warning("⚠ Please enter a movie name.")

        else:

            progress_bar = st.progress(0)
            status = st.empty()

            try:

                with st.spinner("🎬 Please wait while MOVIZIO prepares everything..."):

                    # ---------------------------------
                    # Step 1 : Search Movie
                    # ---------------------------------

                    status.info("🔍 Searching for your movie...")

                    progress_bar.progress(15)

                    dataset = movies["title"].str.lower()

                    if movie_name.lower() in dataset.values:

                        original_name = movies.loc[
                            dataset == movie_name.lower(),
                            "title"
                        ].iloc[0]

                        status.info("🎬 Fetching movie details...")

                        progress_bar.progress(40)

                        st.session_state.searched_movie = get_movie_details(
                            original_name,
                            movies
                        )

                        status.info("🤖 AI is finding similar movies...")

                        progress_bar.progress(70)

                        st.session_state.recommendations = recommend(
                            original_name,
                            movies,
                            similarity1
                        )

                    else:

                        # ---------------------------------
                        # Step 2 : TMDB Search
                        # ---------------------------------

                        status.info("🌍 Searching worldwide movie database...")

                        progress_bar.progress(40)

                        movie = get_external_movie(movie_name)

                        if movie:

                            st.session_state.searched_movie = movie

                            movie_id = search_tmdb_movie(movie_name)

                            # ---------------------------------
                            # Step 3 : TMDB Recommendation
                            # ---------------------------------

                            status.info("🎯 Finding the best recommendations...")

                            progress_bar.progress(70)

                            st.session_state.recommendations = fetch_tmdb_recommendations(movie_id)

                        else:

                            progress_bar.empty()

                            status.error("❌ Movie not found.")

                            st.stop()

                    # ---------------------------------
                    # Final Step
                    # ---------------------------------

                    progress_bar.progress(100)

                    status.success("✅ Everything is ready. Enjoy your movie!")

                    time.sleep(1)

                    progress_bar.empty()

                    status.empty()

            except Exception as e:

                progress_bar.empty()

                status.error("❌ Oops! Something went wrong.")

                st.exception(e)

    if st.session_state.searched_movie:

        movie = st.session_state.searched_movie

        st.divider()

        st.header("🎬 Selected Movie")

        if movie["backdrop"]:
            st.image(
                movie["backdrop"],
                use_container_width=True
            )

        col1, col2 = st.columns([1, 2])

        with col1:
            if movie["poster"]:
                st.image(movie["poster"])
            else:
                st.write("🎬 Poster not available")

        with col2:

            st.subheader(movie["title"])

            st.write("⭐ Rating:", movie["rating"])

            st.write("📅 Release Date:", movie["release_date"])

            st.write("⏱ Runtime:", movie["runtime"])

            st.write(
                "🎭 Genres:",
                " • ".join(movie["genres"])
            )

            st.write("📝 Overview:")
            st.write(movie["overview"])

            st.subheader("🎭 Cast")

            display_cast(movie["cast"])

            st.subheader("🎬 Director")

            display_director(movie["crew"])

            if movie["trailer"]:
                st.video(movie["trailer"])



    if (
            "recommendations" in st.session_state
            and len(st.session_state.recommendations) > 0
    ):

        st.markdown("""
        <h2 style="
            text-align:center;
            color:white;
            margin-top:35px;
            margin-bottom:25px;
            font-size:34px;
            font-weight:bold;
        ">
            🍿 Recommended Movies
        </h2>
        """, unsafe_allow_html=True)

        cols = st.columns(5)

        for idx, movie in enumerate(st.session_state.recommendations):

            with cols[idx]:

                if movie["poster"]:
                    st.image(
                        movie["poster"],
                        use_container_width=True
                    )
                else:
                    st.write("Poster unavailable")

                st.markdown(
                    f"**{movie['title']}**"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("View Details", key=f"view_{idx}"):
                        st.session_state.selected_movie = movie

                with col2:
                    if st.button("❤️", key=f"fav_{idx}"):

                        if movie not in st.session_state.favorites:
                            st.session_state.favorites.append(movie)

                            st.toast("Added to Favorites ❤️")
                    st.session_state.selected_movie = movie

if menu == "ℹ️ About":

    st.title("🎬 About MOVIZIO")

    st.write("""
    **MOVIZIO** is an AI-powered Movie Recommendation System.

    Features:

    ✅ Personalized movie recommendations

    ✅ Posters from TMDB

    ✅ Ratings

    ✅ Genres

    ✅ Cast & Director

    ✅ Official Trailers

    Built with:

    - Python
    - Streamlit
    - Scikit-Learn
    - TMDB API
    """)
if menu == "❤️ Favorites":

    st.title("❤️ My Favorite Movies")

    if len(st.session_state.favorites) == 0:

        st.info("No favorite movies yet.")

    else:

        cols = st.columns(5)

        for idx, movie in enumerate(st.session_state.favorites):

            with cols[idx % 5]:

                st.image(
                    movie["poster"],
                    use_container_width=True
                )

                st.markdown(f"**{movie['title']}**")

                st.write(f"⭐ {movie['rating']}")

                if st.button(
                    "View Details",
                    key=f"favorite_{idx}"
                ):
                    st.session_state.selected_movie = movie

                if st.button(
                    "❌ Remove",
                    key=f"remove_{idx}"
                ):

                    st.session_state.favorites.remove(movie)

                    st.rerun()
if menu == "🔥 Trending":

    st.title("🔥 Trending Movies")

    with st.spinner("Loading Trending Movies..."):

        trending_movies = fetch_trending_movies()

    if not trending_movies:
        st.error("Couldn't load trending movies.")
    else:

        cols = st.columns(5)

        for idx, movie in enumerate(trending_movies):

            with cols[idx % 5]:

                with st.container(border=True):

                    st.image(
                        movie["poster"],
                        use_container_width=True
                    )

                    st.markdown(
                        f"### {movie['title']}"
                    )

                    st.caption(f"⭐ {movie['rating']}")

                    if st.button(
                            "❤️ Add to Favorites",
                            key=f"trend_fav_{idx}",
                            use_container_width=True
                    ):

                        if movie not in st.session_state.favorites:
                            st.session_state.favorites.append(movie)

                            st.toast("Added to Favorites ❤️")

                    if st.button(
                            "🎬 View Details",
                            key=f"trend_view_{idx}",
                            use_container_width=True
                    ):
                        st.session_state.selected_movie = movie
if menu == "⭐ Top Rated":

    st.title("⭐ Top Rated Movies")

    with st.spinner("Loading Top Rated Movies..."):

        movies = fetch_top_rated_movies()

    if not movies:

        st.error("Couldn't load top rated movies.")

    else:

        cols = st.columns(5)

        for idx, movie in enumerate(movies):

            with cols[idx % 5]:

                with st.container(border=True):

                    st.image(
                        movie["poster"],
                        use_container_width=True
                    )

                    st.markdown(f"### {movie['title']}")

                    st.caption(f"⭐ {movie['rating']}")

                    if st.button(
                            "❤️ Add to Favorites",
                            key=f"top_fav_{idx}",
                            use_container_width=True
                    ):
                        if movie not in st.session_state.favorites:
                            st.session_state.favorites.append(movie)
                            st.toast("❤️ Added to Favorites")

                    if st.button(
                            "🎬 View Details",
                            key=f"top_view_{idx}",
                            use_container_width=True
                    ):
                        st.session_state.selected_movie = movie



if st.session_state.selected_movie:

    movie = st.session_state.selected_movie
    if movie["backdrop"]:
        st.image(
            movie["backdrop"],
            use_container_width=True
        )

    st.divider()

    st.markdown(
        f"""
        <h1 style='text-align:center;'>
            🎬 {movie["title"]}
        </h1>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1,2])

    with col1:
        if movie["poster"]:
            st.image(movie["poster"])
        else:
            st.write("Poster not available")

    with col2:

        st.write("📝 Overview")
        st.write(movie["overview"])

        st.write("⭐ Rating:", movie["rating"])

        st.write("📅 Release Date:", movie["release_date"])

        st.write(
            "⏱ Runtime:",
            movie["runtime"]
        )

        st.subheader("🎭 Genres")

        if movie["genres"]:
            st.write(" • ".join(movie["genres"]))
        else:
            st.write("Not Available")

        st.subheader("🎭 Cast")

        cast = movie["cast"]

        if isinstance(cast, list):
            for actor in cast:
                st.write("• " + actor)
        else:
            st.write(cast)

        st.subheader("🎬 Director")

        director = movie["crew"]

        if isinstance(director, list):
            st.write(", ".join(director))
        else:
            st.write(director)
        st.subheader("▶ Official Trailer")

        if movie["trailer"]:
            st.video(movie["trailer"])
        else:
            st.info("Trailer not available.")
    st.divider()

st.markdown("---")
st.caption("Made by B2")