import streamlit as st
import pandas as pd
import pickle
import altair as alt
st.set_page_config(layout="wide")
st.title("Multi-PKL Visualizer (Altair + Dynamic Plots per File)")

uploaded_files = st.file_uploader("Upload one or more .pkl files", type="pkl", accept_multiple_files=True)

# Track plots by ID
if "plots" not in st.session_state:
    st.session_state.plots = [0]

if uploaded_files:
    # Load files once into memory
    file_data = {}
    for file in uploaded_files:
        try:
            df = pickle.load(file)
            if isinstance(df, pd.DataFrame):
                file_data[file.name] = df.copy()
            else:
                st.warning(f"{file.name} is not a valid DataFrame.")
        except Exception as e:
            st.error(f"Failed to load {file.name}: {e}")

    if not file_data:
        st.warning("No valid .pkl DataFrames found.")
    else:
        all_file_names = list(file_data.keys())
        all_numeric_cols = sorted(set(
            col for df in file_data.values()
            for col in df.select_dtypes(include='number').columns
        ))

        for idx, plot_id in enumerate(st.session_state.plots):
            st.markdown(f"### Plot {idx + 1}")
            cols = st.columns([0.6, 0.2, 0.2])

            with cols[0]:
                selected_files = st.multiselect(
                    f"Select file(s) for Plot {idx + 1}",
                    all_file_names,
                    default=all_file_names[:1],
                    key=f"files_{plot_id}"
                )
            with cols[1]:
                selected_cols = st.multiselect(
                    f"Columns for Plot {idx + 1}",
                    all_numeric_cols,
                    key=f"cols_{plot_id}"
                )
            with cols[2]:
                if st.button("🗑️ Delete", key=f"delete_{plot_id}"):
                    st.session_state.plots.remove(plot_id)
                    st.rerun()

            # Combine selected data
            if selected_files and selected_cols:
                combined = []
                for file in selected_files:
                    df = file_data[file].reset_index()
                    x_col = df.columns[0]
                    if all(col in df.columns for col in selected_cols):
                        melted = df[[x_col] + selected_cols].melt(
                            id_vars=x_col,
                            var_name="Variable",
                            value_name="Value"
                        )
                        melted["File"] = file
                        combined.append(melted)

                if combined:
                    combined_df = pd.concat(combined)
                    # Create a multi-selection on the legend (by column/variable)
                    highlight = alt.selection_multi(fields=["Variable"], bind="legend")
                    
                    # Main chart with toggleable visibility
                    chart = alt.Chart(combined_df).mark_line(point=True).encode(
                        x=alt.X(x_col, title=str(x_col)),
                        y=alt.Y("Value", title="Value"),
                        color=alt.Color("Variable:N", title="Column"),
                        strokeDash=alt.StrokeDash("File:N", title="File"),
                        tooltip=[x_col, "Variable", "Value", "File"],
                        opacity=alt.condition(highlight, alt.value(1), alt.value(0))
                    ).add_selection(
                        highlight
                    ).properties(
                        title=f"Plot {idx + 1}"
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No matching columns in selected files.")
            else:
                st.info("Please select at least one file and one column.")

        if st.button("➕ Add another plot"):
            next_id = max(st.session_state.plots, default=0) + 1
            st.session_state.plots.append(next_id)
            st.rerun()
