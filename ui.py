import streamlit as st

def display_cast(cast):

    if isinstance(cast, list):

        for actor in cast:
            st.write("• " + actor)

    else:
        st.write(cast)

def display_director(crew):

    if isinstance(crew, list):

        for person in crew:
            st.write("• " + person)

    else:
        st.write(crew)

import streamlit as st

def movie_card(movie, key_prefix):

    st.image(movie["poster"], use_container_width=True)

    st.markdown(
        f"""
        <div style="
            height:120px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
            align-items:center;
            text-align:center;
        ">

            <h5 style="
                margin-bottom:10px;
                line-height:1.3;
            ">
                {movie['title']}
            </h5>

            <h4 style="
                color:#FFD700;
                margin:0;
            ">
                ⭐ {movie['rating']}
            </h4>

        </div>
        """,
        unsafe_allow_html=True
    )

    view = st.button(
        "🎬 View Details",
        key=f"{key_prefix}_view",
        use_container_width=True
    )

    favorite = st.button(
        "❤️ Add to Favorites",
        key=f"{key_prefix}_fav",
        use_container_width=True
    )

    return view, favorite