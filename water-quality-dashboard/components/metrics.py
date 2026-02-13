"""Metric card components for KPIs."""

import streamlit as st
from utils import get_quality_status, get_quality_color

def create_metric_card(label, value, delta=None, status="good"):
    """Create a styled metric card."""
    color = get_quality_color(status)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<div style='color:{color};font-size:2rem'>●</div>", 
                   unsafe_allow_html=True)
    with col2:
        st.metric(label=label, value=value, delta=delta)
    
    return None

def create_status_indicator(status):
    """Create a colored status indicator."""
    colors = {
        'good': '#00C851',
        'warning': '#ffbb33', 
        'critical': '#ff4444'
    }
    color = colors.get(status, '#9e9e9e')
    return f"<span style='color:{color};font-size:1.2rem'>● {status.upper()}</span>"

def create_kpi_row(metrics_list):
    """Create a row of KPI cards."""
    cols = st.columns(len(metrics_list))
    for idx, metric in enumerate(metrics_list):
        with cols[idx]:
            create_metric_card(**metric)