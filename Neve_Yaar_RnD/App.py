import streamlit as st
import pandas as pd
import pickle
import altair as alt

st.title("PKL File Visualizer (Altair + Label Selection)")

uploaded_file = st.file_uploader("Upload a .pkl file", type="pkl")

if uploaded_file:
    try:
        data = pickle.load(uploaded_file)

        if not isinstance(data, pd.DataFrame):
            st.error("The uploaded file is not a pandas DataFrame.")
        else:
            st.subheader("Data Preview")
            st.dataframe(data)

            # Identify numeric columns
            numeric_cols = data.select_dtypes(include='number').columns.tolist()
            if not numeric_cols:
                st.warning("No numeric columns available for plotting.")
            else:
                # Select numeric columns to plot
                selected_cols = st.multiselect("Select numeric columns to plot", numeric_cols, default=numeric_cols[:1])

                # Select label/group column
                label_col = st.selectbox("Select a column for grouping (labels)", data.columns)

                if label_col:
                    unique_labels = data[label_col].dropna().unique().tolist()

                    # First plot: Select label(s) to show
                    st.markdown("### First Plot")
                    selected_labels_1 = st.multiselect("Choose labels to display (plot 1)", unique_labels, default=unique_labels[:1])

                    # Second plot: Select other label(s)
                    st.markdown("### Second Plot")
                    selected_labels_2 = st.multiselect("Choose labels to display (plot 2)", unique_labels, default=unique_labels[1:2])

                    # Plotting function
                    def plot_filtered(data, labels, label_col, y_cols, title):
                        if not labels or not y_cols:
                            st.info(f"Please select labels and columns for {title}.")
                            return

                        df_filtered = data[data[label_col].isin(labels)].reset_index()
                        x_col = df_filtered.columns[0]

                        for y_col in y_cols:
                            chart = alt.Chart(df_filtered).mark_line(point=True).encode(
                                x=alt.X(x_col, title=x_col),
                                y=alt.Y(y_col, title=y_col),
                                color=label_col,
                                tooltip=[x_col, y_col, label_col]
                            ).interactive().properties(title=f"{title} – {y_col}")

                            st.altair_chart(chart, use_container_width=True)

                    # Show both plots
                    plot_filtered(data, selected_labels_1, label_col, selected_cols, "First Plot")
                    plot_filtered(data, selected_labels_2, label_col, selected_cols, "Second Plot")

    except Exception as e:
        st.error(f"Error reading file: {e}")
