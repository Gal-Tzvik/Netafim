import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair + Dynamic Plots with Deletion)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

# Initialize session state
if "plots" not in st.session_state:
    st.session_state.plots = [0]  # list of plot IDs (not just count)

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

                to_delete = []

                for idx, plot_id in enumerate(st.session_state.plots):
                    st.markdown(f"### Plot {idx + 1}")
                    cols = st.columns([0.85, 0.15])
                    with cols[0]:
                        selected_cols = st.multiselect(
                            f"Select columns to plot in Plot {idx + 1}",
                            numeric_cols,
                            key=f"col_select_{plot_id}"
                        )
                    with cols[1]:
                        if st.button("🗑️ Delete", key=f"delete_{plot_id}"):
                            st.session_state.plots.remove(plot_id)
                            st.experimental_rerun()
                
                    if selected_cols:
                        melted = df_reset[[x_col] + selected_cols].melt(
                            id_vars=x_col, var_name="Variable", value_name="Value"
                        )
                        chart = alt.Chart(melted).mark_line(point=True).encode(
                            x=alt.X(x_col, title=str(x_col)),
                            y=alt.Y("Value", title="Value"),
                            color="Variable",
                            tooltip=[x_col, "Variable", "Value"]
                        ).interactive().properties(title=f"Plot {idx + 1}")
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.info("Please select at least one column.")

                # Remove deleted plots
                if to_delete:
                    st.session_state.plots = [pid for pid in st.session_state.plots if pid not in to_delete]

                # Add new plot
                if st.button("➕ Add another plot"):
                    next_id = max(st.session_state.plots) + 1 if st.session_state.plots else 0
                    st.session_state.plots.append(next_id)

    except Exception as e:
        st.error(f"Error reading file: {e}")
