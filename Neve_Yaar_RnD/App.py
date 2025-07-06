import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair + Dynamic Plots)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

# Initialize session state for additional plots
if "plot_count" not in st.session_state:
    st.session_state.plot_count = 1

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
                df_reset = data.reset_index()
                x_col = df_reset.columns[0]

                # Function to create a column selector and plot
                def show_plot(plot_id):
                    st.markdown(f"### Plot {plot_id + 1}")
                    selected_cols = st.multiselect(
                        f"Select columns for Plot {plot_id + 1}",
                        numeric_cols,
                        key=f"col_select_{plot_id}"
                    )
                    if selected_cols:
                        for col in selected_cols:
                            chart = alt.Chart(df_reset).mark_line(point=True).encode(
                                x=alt.X(x_col, title=str(x_col)),
                                y=alt.Y(col, title=col),
                                tooltip=[x_col, col]
                            ).interactive().properties(title=f"Plot {plot_id + 1} – {col}")
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("Please select at least one column to plot.")

                # Render existing plots
                for i in range(st.session_state.plot_count):
                    show_plot(i)

                # Add another plot
                if st.button("➕ Add another plot"):
                    st.session_state.plot_count += 1

    except Exception as e:
        st.error(f"Error reading file: {e}")
