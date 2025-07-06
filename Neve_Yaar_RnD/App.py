import streamlit as st
import pandas as pd
import pickle
import plotly.express as px

st.title("PKL File Visualizer")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

if uploaded_file:
    try:
        data = pickle.load(uploaded_file)
        
        if isinstance(data, pd.DataFrame):
            st.subheader("Data Preview")
            st.dataframe(data)

            # Select numeric columns for plotting
            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                selected_cols = st.multiselect("Select columns to plot", numeric_cols, default=numeric_cols[:1])

                if selected_cols:
                    fig = px.line(data.reset_index(), x=data.index.name or data.reset_index().columns[0], y=selected_cols)
                    fig.update_layout(
                        xaxis_title="Index",
                        yaxis_title="Value",
                        dragmode="zoom",  # enable zooming
                        hovermode="closest"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Please select at least one numeric column to plot.")
            else:
                st.warning("No numeric columns found for plotting.")
        else:
            st.warning("The uploaded file is not a DataFrame.")
    except Exception as e:
        st.error(f"Failed to load .pkl file: {e}")