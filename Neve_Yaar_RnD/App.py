import streamlit as st
import pandas as pd
import pickle

st.title("PKL File Visualizer")

# File uploader widget in the sidebar or main view
uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

# Run this block only if a file is uploaded
if uploaded_file:
    try:
        # Load the uploaded PKL file using pickle
        data = pickle.load(uploaded_file)
        
        # Check if the loaded object is a DataFrame
        if isinstance(data, pd.DataFrame):
            st.subheader("Data Preview")
            st.dataframe(data)  # Show the table interactively

            # Optionally: only select numeric columns for plotting
            st.subheader("Line Chart (Numeric Data Only)")
            st.line_chart(data.select_dtypes(include='number'))
        else:
            st.warning("The uploaded file is not a DataFrame.")
    except Exception as e:
        st.error(f"Failed to load .pkl file: {e}")