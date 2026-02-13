import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Water Quality Monitor",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Customizado para estilo profissional
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-good { color: #00C851; font-weight: bold; }
    .status-warning { color: #ffbb33; font-weight: bold; }
    .status-danger { color: #ff4444; font-weight: bold; }
    .stAlert { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Gerador de dados sintéticos realistas
@st.cache_data(ttl=300)
def generate_water_quality_data(days=30, stations=5):
    """Gera dados sintéticos de qualidade da água"""
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    
    stations_names = [f"Estação {chr(65+i)}" for i in range(stations)]
    locations = ["Rio Principal", "Afluente Norte", "Afluente Sul", "Reservatório", "Estação de Tratamento"]
    
    data = []
    for station_idx, station in enumerate(stations_names):
        base_ph = 7.0 + np.random.normal(0, 0.3)
        base_temp = 22 + np.random.normal(0, 2)
        
        for date in dates:
            # Simula variações diurnas e sazonais
            hour_factor = np.sin(2 * np.pi * date.hour / 24)
            day_factor = np.sin(2 * np.pi * date.timetuple().tm_yday / 365)
            
            data.append({
                'timestamp': date,
                'station': station,
                'location': locations[station_idx],
                'ph': base_ph + 0.5 * hour_factor + np.random.normal(0, 0.2),
                'turbidity': max(0, 2 + 3 * np.random.exponential(0.5) + hour_factor),
                'dissolved_oxygen': max(0, 8 - 0.5 * hour_factor + np.random.normal(0, 0.5)),
                'temperature': base_temp + 3 * hour_factor + 5 * day_factor + np.random.normal(0, 0.5),
                'conductivity': 200 + 50 * np.random.normal(0, 1) + 20 * hour_factor,
                'total_dissolved_solids': 150 + 30 * np.random.normal(0, 1),
                'chlorine': max(0, 0.5 + 0.2 * np.random.normal(0, 1)) if 'Tratamento' in locations[station_idx] else 0,
                'bacteria_count': max(0, int(50 + 100 * np.random.exponential(0.3))),
                'nitrates': max(0, 2 + 3 * np.random.normal(0, 1)),
                'status': np.random.choice(['Normal', 'Alerta', 'Crítico'], p=[0.85, 0.12, 0.03])
            })
    
    return pd.DataFrame(data)

# Funções de avaliação de qualidade
def get_quality_status(value, param):
    """Retorna status baseado nos limites da OMS/CONAMA"""
    limits = {
        'ph': (6.5, 8.5, 'Bom'),
        'turbidity': (0, 5, 'Bom'),
        'dissolved_oxygen': (6, 14, 'Bom'),
        'temperature': (0, 30, 'Bom'),
        'conductivity': (0, 400, 'Bom'),
        'nitrates': (0, 10, 'Bom')
    }
    
    if param not in limits:
        return 'unknown'
    
    min_val, max_val, _ = limits[param]
    if min_val <= value <= max_val:
        return 'good'
    elif value <= min_val * 0.8 or value >= max_val * 1.2:
        return 'critical'
    else:
        return 'warning'

def get_quality_color(status):
    colors = {'good': '#00C851', 'warning': '#ffbb33', 'critical': '#ff4444', 'unknown': '#9e9e9e'}
    return colors.get(status, '#9e9e9e')

# Sidebar - Filtros
with st.sidebar:
    st.image("https://img.icons8.com/color/96/water.png", width=80)
    st.title("⚙️ Configurações")
    
    # Filtro de período
    st.subheader("Período de Análise")
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
    
    # Filtro de estações
    st.subheader("Estações de Monitoramento")
    df_full = generate_water_quality_data(days=30)
    available_stations = df_full['station'].unique()
    selected_stations = st.multiselect(
        "Selecionar estações",
        available_stations,
        default=available_stations[:3]
    )
    
    # Filtro de parâmetros
    st.subheader("Parâmetros")
    parameters = ['ph', 'turbidity', 'dissolved_oxygen', 'temperature', 
                  'conductivity', 'total_dissolved_solids', 'nitrates']
    param_labels = {
        'ph': 'pH', 'turbidity': 'Turbidez (NTU)', 'dissolved_oxygen': 'Oxigênio Dissolvido (mg/L)',
        'temperature': 'Temperatura (°C)', 'conductivity': 'Condutividade (µS/cm)',
        'total_dissolved_solids': 'Sólidos Totais Dissolvidos (mg/L)', 'nitrates': 'Nitratos (mg/L)'
    }
    selected_params = st.multiselect(
        "Métricas para exibir",
        parameters,
        default=['ph', 'turbidity', 'dissolved_oxygen'],
        format_func=lambda x: param_labels[x]
    )
    
    # Botão de refresh
    if st.button("🔄 Atualizar Dados", type="primary"):
        st.cache_data.clear()
        st.rerun()

# Aplicar filtros de tempo
if time_range == "Últimas 24 horas":
    df = df_full[df_full['timestamp'] >= datetime.now() - timedelta(hours=24)]
elif time_range == "Últimos 7 dias":
    df = df_full[df_full['timestamp'] >= datetime.now() - timedelta(days=7)]
elif time_range == "Últimos 30 dias":
    df = df_full[df_full['timestamp'] >= datetime.now() - timedelta(days=30)]
else:
    df = df_full[(df_full['timestamp'].dt.date >= start_date) & 
                 (df_full['timestamp'].dt.date <= end_date)]

# Filtrar estações
if selected_stations:
    df = df[df['station'].isin(selected_stations)]

# Header principal
st.markdown('<h1 class="main-header">💧 Water Quality Monitoring Dashboard</h1>', 
            unsafe_allow_html=True)

# KPIs Principais
st.subheader("📊 Indicadores em Tempo Real")
latest_data = df.groupby('station').last().reset_index()

cols = st.columns(4)
metrics = [
    ("Estações Ativas", len(df['station'].unique()), "✅"),
    ("Leituras Totais", len(df), "📈"),
    ("Alertas Hoje", len(df[df['timestamp'].dt.date == datetime.now().date()][df['status'] == 'Alerta']), "⚠️"),
    ("Qualidade Média", f"{(len(df[df['status'] == 'Normal']) / len(df) * 100):.1f}%", "🎯")
]

for i, (label, value, icon) in enumerate(metrics):
    with cols[i]:
        st.metric(label=f"{icon} {label}", value=value)

# Gráficos principais
if selected_params:
    st.subheader("📈 Tendências de Qualidade da Água")
    
    # Gráfico de linhas temporal
    fig = go.Figure()
    colors = px.colors.qualitative.Set1
    
    for idx, param in enumerate(selected_params):
        for station_idx, station in enumerate(selected_stations if selected_stations else df['station'].unique()):
            station_data = df[df['station'] == station]
            fig.add_trace(go.Scatter(
                x=station_data['timestamp'],
                y=station_data[param],
                mode='lines',
                name=f"{station} - {param_labels[param]}",
                line=dict(color=colors[station_idx % len(colors)], width=2),
                opacity=0.8
            ))
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        xaxis_title="Data/Hora",
        yaxis_title="Valor",
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Mapa de calor de correlação
    if len(selected_params) > 1:
        st.subheader("🔥 Correlação entre Parâmetros")
        corr_data = df[selected_params].corr()
        fig_heatmap = px.imshow(
            corr_data,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Matriz de Correlação"
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)

# Análise por estação
st.subheader("🏭 Análise Detalhada por Estação")

for station in (selected_stations if selected_stations else df['station'].unique()[:3]):
    with st.expander(f"📍 {station} - {df[df['station']==station]['location'].iloc[0]}", expanded=True):
        station_df = df[df['station'] == station].copy()
        latest = station_df.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Cards de métricas com indicadores de status
        with col1:
            ph_status = get_quality_status(latest['ph'], 'ph')
            st.metric(
                "pH",
                f"{latest['ph']:.2f}",
                delta="Normal" if ph_status == 'good' else "Alerta",
                delta_color="normal" if ph_status == 'good' else "inverse"
            )
            
        with col2:
            turb_status = get_quality_status(latest['turbidity'], 'turbidity')
            st.metric(
                "Turbidez",
                f"{latest['turbidity']:.2f} NTU",
                delta="Dentro do limite" if turb_status == 'good' else "Elevada",
                delta_color="normal" if turb_status == 'good' else "inverse"
            )
            
        with col3:
            do_status = get_quality_status(latest['dissolved_oxygen'], 'dissolved_oxygen')
            st.metric(
                "O₂ Dissolvido",
                f"{latest['dissolved_oxygen']:.2f} mg/L",
                delta="Adequado" if do_status == 'good' else "Baixo",
                delta_color="normal" if do_status == 'good' else "inverse"
            )
            
        with col4:
            temp_status = get_quality_status(latest['temperature'], 'temperature')
            st.metric(
                "Temperatura",
                f"{latest['temperature']:.1f}°C",
                delta="Normal" if temp_status == 'good' else "Extrema",
                delta_color="normal" if temp_status == 'good' else "inverse"
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
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=station
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=300,
            title="Índice de Qualidade (0-100)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

# Alertas e recomendações
st.subheader("🚨 Alertas e Recomendações")

alerts = []
for _, row in latest_data.iterrows():
    if row['ph'] < 6.5 or row['ph'] > 8.5:
        alerts.append(f"⚠️ **{row['station']}**: pH fora do padrão ({row['ph']:.2f})")
    if row['turbidity'] > 5:
        alerts.append(f"⚠️ **{row['station']}**: Turbidez elevada ({row['turbidity']:.2f} NTU)")
    if row['dissolved_oxygen'] < 6:
        alerts.append(f"⚠️ **{row['station']}**: Oxigênio dissolvido baixo ({row['dissolved_oxygen']:.2f} mg/L)")

if alerts:
    for alert in alerts[:5]:  # Mostra apenas os 5 primeiros
        st.warning(alert)
else:
    st.success("✅ Todos os parâmetros estão dentro dos limites aceitáveis!")

# Exportação de dados
st.subheader("📥 Exportar Dados")
col1, col2 = st.columns(2)
with col1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Download CSV",
        data=csv,
        file_name=f"water_quality_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
with col2:
    if st.button("📊 Gerar Relatório PDF"):
        st.info("Funcionalidade de PDF em desenvolvimento...")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🌍 Sistema de Monitoramento de Qualidade da Água v1.0</p>
    <p>Desenvolvido com Streamlit | Dados simulados para demonstração</p>
</div>
""", unsafe_allow_html=True)