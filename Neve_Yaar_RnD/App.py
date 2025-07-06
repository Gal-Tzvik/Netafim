import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair + Dynamic Plots in One Chart)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

# Initialize session state to track number of plots
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

            # Get numeric columns
            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                st.warning("No numeric columns available for plotting.")
            else:
                df_reset = data.reset_index()
                x_col = df_reset.columns[0]

                # Function to plot multiple series on the same chart
                def show_plot(plot_id):
                    st.markdown(f"### Plot {plot_id + 1}")
                    selected_cols = st.multiselect(
                        f"Select columns for Plot {plot_id + 1}",
                        numeric_cols,
                        key=f"col_select_{plot_id}"
                    )
                    if selected_cols:
                        melted = df_reset[[x_col] + selected_cols].melt(id_vars=x_col, var_name="Variable", value_name="Value")
                        chart = alt.Chart(melted).mark_line(point=True).encode(
                            x=alt.X(x_col, title=str(x_col)),
                            y=alt.Y("Value", title="Value"),
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive().properties(title=f"Plot {plot_id + 1}")
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("Please select at least one column.")

                # Render existing plots
                for i in range(st.session_state.plot_count):
                    show_plot(i)

                # Add new plot
                if st.button("➕ Add another plot"):
                    st.session_state.plot_count += 1

    except Exception as e:
        st.error(f"Error reading file: {e}")
