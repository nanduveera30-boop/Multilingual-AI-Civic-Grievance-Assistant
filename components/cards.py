import streamlit as st


def render_card(title: str, description: str):
    st.markdown(f"""
    <div class='card'>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
