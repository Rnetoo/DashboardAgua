# 💧 Water Quality Monitoring Dashboard

Dashboard interativo para monitoramento de indicadores de qualidade da água, desenvolvido com Python e Streamlit.

## 🚀 Funcionalidades

- **Monitoramento em Tempo Real**: Visualização de dados atualizados de múltiplas estações
- **Múltiplos Parâmetros**: pH, Turbidez, Oxigênio Dissolvido, Temperatura, Condutividade, Sólidos Totais, Nitratos
- **Análise Visual**: Gráficos de linhas, mapa de calor de correlação e gráficos de radar
- **Alertas Inteligentes**: Notificações automáticas baseadas nos limites da OMS/CONAMA
- **Filtros Dinâmicos**: Seleção por período, estação e parâmetros específicos
- **Exportação de Dados**: Download em formato CSV

## 📊 Parâmetros Monitorados

| Parâmetro | Unidade | Limite Aceitável |
|-----------|---------|------------------|
| pH | - | 6.5 - 8.5 |
| Turbidez | NTU | &lt; 5 |
| Oxigênio Dissolvido | mg/L | &gt; 6 |
| Temperatura | °C | &lt; 30 |
| Condutividade | µS/cm | &lt; 400 |
| Nitratos | mg/L | &lt; 10 |

## 🛠️ Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/water-quality-dashboard.git
cd water-quality-dashboard

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o dashboard
streamlit run app.py