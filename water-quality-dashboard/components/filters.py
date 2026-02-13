"""Filter components for sidebar."""

import streamlit as st
from datetime import datetime, timedelta

def create_date_filter():
    """Create date range filter."""
    st.subheader("📅 Período de Análise")
    
    time_range = st.selectbox(
        "Selecione o período",
        ["Últimas 24 horas", "Últimos 7 dias", "Últimos 30 dias", "Personalizado"]
    )
    
    if time_range == "Personalizado":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Início", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("Fim", datetime.now())
        return {"type": "custom", "start": start_date, "end": end_date}
    
    return {"type": "preset", "value": time_range}

def create_station_filter(available_stations):
    """Create station multi-select filter."""
    st.subheader("🏭 Estações")
    
    selected = st.multiselect(
        "Selecionar estações",
        available_stations,
        default=available_stations[:3] if len(available_stations) >= 3 else available_stations
    )
    
    return selected

def create_sidebar_filters(df):
    """Create complete sidebar with all filters."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/water.png", width=80)
        st.title("⚙️ Configurações")
        
        date_filter = create_date_filter()
        stations = create_station_filter(df['station'].unique())
        
        st.subheader("📊 Parâmetros")
        parameters = st.multiselect(
            "Métricas",
            ['ph', 'turbidity', 'dissolved_oxygen', 'temperature'],
            default=['ph', 'turbidity']
        )
        
        if st.button("🔄 Atualizar", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    return {
        "date": date_filter,
        "stations": stations,
        "parameters": parameters
    }