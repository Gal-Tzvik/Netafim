import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair Version)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

if uploaded_file:
    try:
        data = pickle.load(uploaded_file)

        if isinstance(data, pd.DataFrame):
            st.subheader("Data Preview")
            st.dataframe(data)

            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                selected_cols = st.multiselect("Select columns to plot", numeric_cols, default=numeric_cols[:1])

                if selected_cols:
                    df_reset = data.reset_index()
                    x_col = df_reset.columns[0]  # Assume first col is index or Date

                    for col in selected_cols:
                        st.altair_chart(
                            alt.Chart(df_reset).mark_line().encode(
                                x=alt.X(x_col, title='Index'),
                                y=alt.Y(col, title=col),
                                tooltip=[x_col, col]
                            ).interactive(),
                            use_container_width=True
                        )
                else:
                    st.info("Please select at least one numeric column.")
            else:
                st.warning("No numeric columns found.")
        else:
            st.warning("The uploaded file does not contain a DataFrame.")
    except Exception as e:
        st.error(f"Error: {e}")
