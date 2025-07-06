import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair + Column Selection)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

if uploaded_file:
    try:
        data = pickle.load(uploaded_file)

        if not isinstance(data, pd.DataFrame):
            st.error("The uploaded file is not a pandas DataFrame.")
        else:
            st.subheader("Data Preview")
            st.dataframe(data)

            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                st.warning("No numeric columns available for plotting.")
            else:
                # First plot - column selection
                st.markdown("### First Plot")
                selected_cols_1 = st.multiselect(
                    "Select columns to plot (Plot 1)", numeric_cols, default=numeric_cols[:1]
                )

                # Second plot - column selection
                st.markdown("### Second Plot")
                selected_cols_2 = st.multiselect(
                    "Select columns to plot (Plot 2)", numeric_cols, default=numeric_cols[1:2]
                )

                # Use index or reset index as X-axis
                df_reset = data.reset_index()
                x_col = df_reset.columns[0]

                def plot_columns(cols, title):
                    if not cols:
                        st.info(f"Select at least one column for {title}.")
                        return
                    for col in cols:
                        chart = alt.Chart(df_reset).mark_line(point=True).encode(
                            x=alt.X(x_col, title=str(x_col)),
                            y=alt.Y(col, title=col),
                            tooltip=[x_col, col]
                        ).interactive().properties(title=f"{title} – {col}")
                        st.altair_chart(chart, use_container_width=True)

                # Display plots
                plot_columns(selected_cols_1, "First Plot")
                plot_columns(selected_cols_2, "Second Plot")

    except Exception as e:
        st.error(f"Error reading file: {e}")
