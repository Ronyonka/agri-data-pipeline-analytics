"""Streamlit dashboard placeholder."""

import streamlit as st


def main() -> None:
    """Render the initial dashboard page."""
    st.set_page_config(page_title="Agri Data Pipeline Analytics", layout="wide")
    st.title("Agri Data Pipeline Analytics")
    st.write("Dashboard scaffolding is ready. Pipeline metrics will appear here.")


if __name__ == "__main__":
    main()
