import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Multi-PKL Visualizer (Plotly + Toggle + Zoom)")

uploaded_files = st.file_uploader("Upload one or more .pkl files", type="pkl", accept_multiple_files=True)

# Track plots by unique IDs
if "plots" not in st.session_state:
    st.session_state.plots = [0]

if uploaded_files:
    # Load all uploaded .pkl files
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

            # Plot only if both files and columns are selected
            if selected_files and selected_cols:
                fig = go.Figure()
                for file in selected_files:
                    df = file_data[file]
                    for col in selected_cols:
                        if col in df.columns:
                            fig.add_trace(go.Scatter(
                                x=df.index,
                                y=df[col],
                                mode='lines+markers',
                                name=f"{col} ({file})"
                            ))

                fig.update_layout(
                    title=f"Plot {idx + 1}",
                    xaxis_title="Index",
                    yaxis_title="Value",
                    hovermode="x unified",
                    dragmode="zoom",       # ✅ Enables zooming
                    showlegend=True        # ✅ Always show legend
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Please select at least one file and one column.")

        if st.button("➕ Add another plot"):
            next_id = max(st.session_state.plots, default=0) + 1
            st.session_state.plots.append(next_id)
            st.rerun()
