import streamlit as st
import plotly.express as px

def visualize_data(df):
    """Render visualizations for query results in Streamlit based on data types."""
    if df is None or df.empty:
        st.warning("⚠ No data available for visualization.")
        return

    st.subheader("📈 Data Visualization")

    # Identify numerical and categorical columns
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    all_cols = df.columns.tolist()

    # Check if data is completely categorical (applies to all cases)
    if not num_cols and cat_cols:
        st.info(
            "Visualization cannot be done as this dataset contains only categorical data"
        )
        return

    # Handle based on number of columns
    if len(all_cols) == 1:  # Single column case
        col = all_cols[0]
        if col in num_cols:
            st.info("Histogram of given single numerical dataset")
            fig = px.histogram(df, x=col, title=f"Distribution of {col}")
            st.plotly_chart(fig, use_container_width=True)
        # No else needed; categorical case is caught by the check above
        return

    # Two columns case
    if len(all_cols) == 2:
        if len(num_cols) == 2:  # Both numerical
            chart_options = ["Scatter", "Line", "Histogram"]
            chart_type = st.selectbox("Select Visualization Type", options=chart_options, index=0)
            if chart_type == "Scatter":
                x_col = st.selectbox("X-axis", num_cols, key="x_scatter")
                y_col = st.selectbox("Y-axis", num_cols, key="y_scatter")
                fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
            elif chart_type == "Line":
                x_col = st.selectbox("X-axis", num_cols, key="x_line")
                y_col = st.selectbox("Y-axis", num_cols, key="y_line")
                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} Trend by {x_col}")
            elif chart_type == "Histogram":
                num_col = st.selectbox("Numerical Column", num_cols, key="hist_col")
                fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
        elif len(num_cols) == 1 and len(cat_cols) == 1:  # One numerical, one categorical
            chart_options = ["Bar", "Pie"]
            chart_type = st.selectbox("Select Visualization Type", options=chart_options, index=0)
            if chart_type == "Bar":
                x_col = cat_cols[0]
                y_col = num_cols[0]
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            elif chart_type == "Pie":
                names_col = cat_cols[0]
                values_col = num_cols[0]
                fig = px.pie(df, names=names_col, values=values_col, title=f"{values_col} Distribution")
        # No need for elif len(cat_cols) == 2; handled by the initial categorical check
        st.plotly_chart(fig, use_container_width=True)
        return

    # Three or more columns case
    if num_cols and cat_cols:  # Mixed data
        chart_options = ["Bar", "Line", "Pie", "Histogram"]
    elif num_cols and not cat_cols:  # All numerical
        chart_options = ["Line", "Scatter", "Histogram"]
    else:
        st.warning("⚠ Unable to determine data types for visualization.")
        return

    chart_type = st.selectbox("Select Visualization Type", options=chart_options, index=0)

    # Visualization logic for 3+ columns
    if chart_type == "Bar":
        x_col = st.selectbox("X-axis (Categories)", cat_cols, key="x_bar")
        y_col = st.selectbox("Y-axis (Values)", num_cols, key="y_bar")
        color_col = st.selectbox("Color (optional)", [None] + all_cols, key="c_bar")
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} by {x_col}")

    elif chart_type == "Line":
        x_col = st.selectbox("X-axis", all_cols, key="x_line")
        y_col = st.selectbox("Y-axis", num_cols, key="y_line")
        color_col = st.selectbox("Color (optional)", [None] + all_cols, key="c_line")
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} Trend by {x_col}")

    elif chart_type == "Pie":
        names_col = st.selectbox("Categories", cat_cols, key="pie_names")
        values_col = st.selectbox("Values", num_cols, key="pie_values")
        fig = px.pie(df, names=names_col, values=values_col, title=f"{values_col} Distribution")

    elif chart_type == "Histogram":
        num_col = st.selectbox("Numerical Column", num_cols, key="hist_col")
        color_col = st.selectbox("Color (optional)", [None] + all_cols, key="hist_color")
        fig = px.histogram(df, x=num_col, color=color_col, title=f"Distribution of {num_col}")

    st.plotly_chart(fig, use_container_width=True)