"""
Water Quality Monitoring Dashboard
==================================
Dashboard interativo para monitoramento de qualidade da água.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ✅ IMPORTAÇÃO DO GERADOR DE DADOS
from data_generator import generate_water_quality_data

# Importações dos nossos pacotes modulares
from components import (
    create_line_chart,
    create_radar_chart,
    create_heatmap,
    create_metric_card,
    create_kpi_row,
    create_sidebar_filters
)
from utils import (
    get_quality_status,
    get_quality_color,
    format_number,
    calculate_quality_index,
    generate_export_filename
)

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="Water Quality Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# GERAÇÃO DE DADOS
# =============================================================================

# Removida a função generate_water_quality_data() do app.py
# E adicione esta importação:

from data_generator import WaterQualityDataGenerator

# No main():
generator = WaterQualityDataGenerator(seed=42)
df_full = generator.generate(days=30)

# Você pode até adicionar anomalias para testar alertas:
df_full = generator.add_anomaly(
    df_full, 
    station="Estação A",
    parameter="ph", 
    start_time=datetime.now() - timedelta(days=2),
    duration_hours=5
)


def apply_time_filter(df: pd.DataFrame, filter_config: dict) -> pd.DataFrame:
    """Aplica filtro temporal aos dados."""
    if filter_config['type'] == 'preset':
        preset = filter_config['value']
        now = datetime.now()
        
        if preset == "Últimas 24 horas":
            return df[df['timestamp'] >= now - timedelta(hours=24)]
        elif preset == "Últimos 7 dias":
            return df[df['timestamp'] >= now - timedelta(days=7)]
        elif preset == "Últimos 30 dias":
            return df[df['timestamp'] >= now - timedelta(days=30)]
    
    elif filter_config['type'] == 'custom':
        start = pd.Timestamp(filter_config['start'])
        end = pd.Timestamp(filter_config['end'])
        return df[(df['timestamp'].dt.date >= start.date()) & 
                  (df['timestamp'].dt.date <= end.date())]
    
    return df


# =============================================================================
# COMPONENTES PRINCIPAIS
# =============================================================================

def render_header():
    """Renderiza o cabeçalho do dashboard."""
    st.markdown('<h1 class="main-header">💧Dashboard Qualidade da Água</h1>', 
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Monitoramento em tempo real da qualidade da água</p>', 
                unsafe_allow_html=True)


def render_kpis(df: pd.DataFrame):
    """Renderiza os indicadores principais (KPIs)."""
    st.subheader("📊 Indicadores em Tempo Real")
    
    latest_data = df.groupby('station').last().reset_index()
    today = datetime.now().date()
    today_alerts = len(df[
        (df['timestamp'].dt.date == today) & 
        (df['status'] == 'Alerta')
    ])
    
    quality_score = calculate_quality_index({
        'ph': latest_data['ph'].mean(),
        'turbidity': latest_data['turbidity'].mean(),
        'dissolved_oxygen': latest_data['dissolved_oxygen'].mean(),
        'temperature': latest_data['temperature'].mean(),
        'conductivity': latest_data['conductivity'].mean()
    })
    
    metrics = [
        {
            "label": "Estações Ativas",
            "value": len(df['station'].unique()),
            "delta": None,
            "status": "good"
        },
        {
            "label": "Leituras Totais",
            "value": f"{len(df):,}".replace(",", "."),
            "delta": None,
            "status": "good"
        },
        {
            "label": "Alertas Hoje",
            "value": today_alerts,
            "delta": "Atenção" if today_alerts > 0 else None,
            "status": "warning" if today_alerts > 0 else "good"
        },
        {
            "label": "Índice de Qualidade",
            "value": f"{quality_score:.0f}/100",
            "delta": "Excelente" if quality_score > 80 else "Bom" if quality_score > 60 else "Regular",
            "status": "good" if quality_score > 80 else "warning" if quality_score > 60 else "critical"
        }
    ]
    
    create_kpi_row(metrics)


def render_charts(df: pd.DataFrame, selected_params: list, selected_stations: list):
    """Renderiza os gráficos principais."""
    if not selected_params or not selected_stations:
        st.info("👈 Selecione parâmetros e estações no menu lateral para visualizar os gráficos.")
        return
    
    st.subheader("📈 Tendências de Qualidade da Água")
    
    # Gráfico de linhas temporal
    param_labels = {
        'ph': 'pH',
        'turbidity': 'Turbidez (NTU)',
        'dissolved_oxygen': 'Oxigênio Dissolvido (mg/L)',
        'temperature': 'Temperatura (°C)',
        'conductivity': 'Condutividade (µS/cm)',
        'total_dissolved_solids': 'Sólidos Totais Dissolvidos (mg/L)',
        'nitrates': 'Nitratos (mg/L)'
    }
    
    # Cria gráfico para o primeiro parâmetro selecionado
    primary_param = selected_params[0]
    
    fig = create_line_chart(
        df[df['station'].isin(selected_stations)],
        x='timestamp',
        y=primary_param,
        color='station',
        title=f"Evolução de {param_labels.get(primary_param, primary_param)}"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Mapa de calor de correlação se houver múltiplos parâmetros
    if len(selected_params) > 1:
        st.subheader("🔥 Correlação entre Parâmetros")
        corr_data = df[selected_params].corr()
        fig_heatmap = create_heatmap(corr_data)
        st.plotly_chart(fig_heatmap, use_container_width=True)


def render_station_details(df: pd.DataFrame, selected_stations: list):
    """Renderiza análise detalhada por estação."""
    if not selected_stations:
        return
    
    st.subheader("🏭 Análise Detalhada por Estação")
    
    for station in selected_stations:
        station_df = df[df['station'] == station]
        if station_df.empty:
            continue
            
        latest = station_df.iloc[-1]
        location = station_df['location'].iloc[0]
        
        with st.expander(f"📍 {station} - {location}", expanded=True):
            # Métricas em colunas
            cols = st.columns(4)
            
            params_to_show = [
                ('ph', 'pH', ''),
                ('turbidity', 'Turbidez', ' NTU'),
                ('dissolved_oxygen', 'O₂ Dissolvido', ' mg/L'),
                ('temperature', 'Temperatura', '°C')
            ]
            
            for idx, (param, label, unit) in enumerate(params_to_show):
                with cols[idx]:
                    value = latest[param]
                    status = get_quality_status(value, param)
                    formatted_value = format_number(value) + unit
                    
                    st.metric(
                        label=label,
                        value=formatted_value,
                        delta="Normal" if status == 'good' else "Atenção" if status == 'warning' else "Crítico",
                        delta_color="normal" if status == 'good' else "inverse"
                    )
            
            # Gráfico de radar para qualidade geral
            categories = ['pH', 'Turbidez', 'O₂', 'Temperatura', 'Condutividade']
            values = [
                min(100, max(0, (latest['ph'] / 8.5) * 100)),
                min(100, max(0, 100 - (latest['turbidity'] / 5) * 100)),
                min(100, max(0, (latest['dissolved_oxygen'] / 10) * 100)),
                min(100, max(0, 100 - abs(latest['temperature'] - 25) * 2)),
                min(100, max(0, 100 - (latest['conductivity'] / 400) * 100))
            ]
            
            fig_radar = create_radar_chart(categories, values, f"Índice de Qualidade - {station}")
            st.plotly_chart(fig_radar, use_container_width=True)


def render_alerts(df: pd.DataFrame):
    """Renderiza seção de alertas e recomendações."""
    st.subheader("🚨 Alertas e Recomendações")
    
    latest_data = df.groupby('station').last().reset_index()
    alerts = []
    
    for _, row in latest_data.iterrows():
        if row['ph'] < 6.5 or row['ph'] > 8.5:
            alerts.append(f"⚠️ **{row['station']}**: pH fora do padrão ({format_number(row['ph'])})")
        if row['turbidity'] > 5:
            alerts.append(f"⚠️ **{row['station']}**: Turbidez elevada ({format_number(row['turbidity'])} NTU)")
        if row['dissolved_oxygen'] < 6:
            alerts.append(f"⚠️ **{row['station']}**: Oxigênio dissolvido baixo ({format_number(row['dissolved_oxygen'])} mg/L)")
    
    if alerts:
        for alert in alerts[:5]:
            st.warning(alert)
        if len(alerts) > 5:
            st.info(f"... e mais {len(alerts) - 5} alertas. Exporte os dados para análise completa.")
    else:
        st.success("✅ Todos os parâmetros estão dentro dos limites aceitáveis!")


def render_export(df: pd.DataFrame):
    """Renderiza opções de exportação de dados."""
    st.subheader("📥 Exportar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        filename = generate_export_filename()
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("📊 Gerar Relatório PDF", use_container_width=True):
            st.info("📋 Funcionalidade de PDF em desenvolvimento...")


def render_footer():
    """Renderiza o rodapé."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🌍 Sistema de Monitoramento de Qualidade da Água v1.0</p>
        <p>Desenvolvido com Python, Streamlit e Plotly | Dados simulados para demonstração</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal do aplicativo."""
    
    # Renderiza header
    render_header()
    
    # Carrega dados
    df_full = generate_water_quality_data(days=30)
    
    # Sidebar com filtros
    filters = create_sidebar_filters(df_full)
    
    # Aplica filtros
    df_filtered = apply_time_filter(df_full, filters['date'])
    if filters['stations']:
        df_filtered = df_filtered[df_filtered['station'].isin(filters['stations'])]
    
    # Renderiza seções do dashboard
    render_kpis(df_filtered)
    
    st.divider()
    render_charts(df_filtered, filters['parameters'], filters['stations'])
    
    st.divider()
    render_station_details(df_filtered, filters['stations'])
    
    st.divider()
    render_alerts(df_filtered)
    
    st.divider()
    render_export(df_filtered)
    
    render_footer()


if __name__ == "__main__":
    main()