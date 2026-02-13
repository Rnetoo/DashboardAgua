"""Custom chart components using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def create_line_chart(df, x, y, color=None, title=""):
    """Create an interactive line chart."""
    fig = px.line(df, x=x, y=y, color=color, title=title)
    fig.update_layout(template='plotly_white')
    return fig

def create_radar_chart(categories, values, title="Quality Index"):
    """Create a radar chart for water quality."""
    fig = go.Figure(data=go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=title
    )
    return fig

def create_heatmap(corr_data, title="Correlation Matrix"):
    """Create a correlation heatmap."""
    fig = px.imshow(
        corr_data,
        text_auto=True,
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title=title
    )
    return fig

def create_gauge_chart(value, title, max_val=100):
    """Create a gauge chart for single metric."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={'axis': {'range': [None, max_val]}}
    ))
    return fig