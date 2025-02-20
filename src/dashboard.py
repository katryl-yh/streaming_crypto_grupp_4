import streamlit as st
import pandas as pd
from read_write_postgres import read_from_db

def layout():
    
    st.markdown("# Cryptocurrency data")
    st.markdown("## Latest data")
    
        
    st.markdown("## Bitcoin latest price in USD")


if __name__ == "__main__":
    layout()
