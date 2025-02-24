import streamlit as st
import plotly.express as px

def visualize_data(df):
    """Render visualizations for query results in Streamlit."""
    if df is None or df.empty:
        st.warning("⚠ No data available for visualization.")
        return

    st.subheader("📈 Data Visualization")

    chart_type = st.selectbox(
        "Select Visualization Type",
        options=["Bar", "Line", "Pie", "Scatter", "Histogram"],
        index=0
    )

    if chart_type == "Bar":
        x_col = st.selectbox("X-axis", df.columns, key="x_bar")
        y_col = st.selectbox("Y-axis", df.columns, key="y_bar")
        color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="c_bar")
        
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} by {x_col}")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Line":
        x_col = st.selectbox("X-axis", df.columns, key="x_line")
        y_col = st.selectbox("Y-axis", df.columns, key="y_line")
        color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="c_line")
        
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} Trend by {x_col}")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Pie":
        names_col = st.selectbox("Categories", df.columns, key="pie_names")
        values_col = st.selectbox("Values", df.columns, key="pie_values")
        
        fig = px.pie(df, names=names_col, values=values_col, title=f"{values_col} Distribution")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Scatter":
        x_col = st.selectbox("X-axis", df.columns, key="x_scatter")
        y_col = st.selectbox("Y-axis", df.columns, key="y_scatter")
        color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="c_scatter")
        
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} vs {x_col}")
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Histogram":
        num_col = st.selectbox("Numerical Column", df.select_dtypes(include='number').columns, key="hist_col")
        color_col = st.selectbox("Color (optional)", [None] + list(df.columns), key="hist_color")
        
        fig = px.histogram(df, x=num_col, color=color_col, title=f"Distribution of {num_col}")
        st.plotly_chart(fig, use_container_width=True)
