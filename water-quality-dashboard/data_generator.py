"""
Data Generator Module
=====================
Módulo responsável pela geração de dados sintéticos de qualidade da água.
Simula sensores IoT em estações de monitoramento ambiental.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class WaterQualityDataGenerator:
    """
    Gerador de dados sintéticos de qualidade da água.
    
    Simula leituras de sensores em múltiplas estações de monitoramento
    com variações realistas baseadas em padrões temporais (diurnos e sazonais).
    """
    
    # Configurações padrão das estações
    DEFAULT_STATIONS = [
        {"name": "Estação A", "location": "Rio Principal", "base_ph": 7.0, "base_temp": 22},
        {"name": "Estação B", "location": "Afluente Norte", "base_ph": 6.8, "base_temp": 20},
        {"name": "Estação C", "location": "Afluente Sul", "base_ph": 7.2, "base_temp": 24},
        {"name": "Estação D", "location": "Reservatório", "base_ph": 7.1, "base_temp": 23},
        {"name": "Estação E", "location": "Estação de Tratamento", "base_ph": 7.0, "base_temp": 21},
    ]
    
    # Probabilidades de status
    STATUS_PROBABILITIES = [0.85, 0.12, 0.03]  # Normal, Alerta, Crítico
    
    def __init__(self, seed: int = 42):
        """
        Inicializa o gerador com seed para reprodutibilidade.
        
        Args:
            seed: Seed para o gerador de números aleatórios
        """
        self.seed = seed
        np.random.seed(seed)
    
    def generate(
        self,
        days: int = 30,
        stations: Optional[List[Dict]] = None,
        frequency: str = 'H'
    ) -> pd.DataFrame:
        """
        Gera dados sintéticos de qualidade da água.
        
        Args:
            days: Número de dias de dados históricos
            stations: Lista de configurações de estações (usa default se None)
            frequency: Frequência das leituras ('H' = horária, 'D' = diária)
        
        Returns:
            DataFrame com dados de qualidade da água
        """
        if stations is None:
            stations = self.DEFAULT_STATIONS
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq=frequency)
        
        data = []
        for station_config in stations:
            station_data = self._generate_station_data(
                station_config, dates
            )
            data.extend(station_data)
        
        return pd.DataFrame(data)
    
    def _generate_station_data(
        self,
        station_config: Dict,
        dates: pd.DatetimeIndex
    ) -> List[Dict]:
        """
        Gera dados para uma estação específica.
        
        Args:
            station_config: Configuração da estação
            dates: Índice de datas para geração
        
        Returns:
            Lista de dicionários com leituras da estação
        """
        station_name = station_config["name"]
        location = station_config["location"]
        base_ph = station_config["base_ph"] + np.random.normal(0, 0.3)
        base_temp = station_config["base_temp"] + np.random.normal(0, 2)
        
        readings = []
        for date in dates:
            # Fatores temporais
            hour_factor = np.sin(2 * np.pi * date.hour / 24)
            day_of_year = date.timetuple().tm_yday
            day_factor = np.sin(2 * np.pi * day_of_year / 365)
            
            # Variação aleatória do dia
            daily_noise = np.random.normal(0, 0.2)
            
            reading = {
                'timestamp': date,
                'station': station_name,
                'location': location,
                'ph': self._calculate_ph(base_ph, hour_factor, daily_noise),
                'turbidity': self._calculate_turbidity(hour_factor),
                'dissolved_oxygen': self._calculate_dissolved_oxygen(hour_factor),
                'temperature': self._calculate_temperature(base_temp, hour_factor, day_factor),
                'conductivity': self._calculate_conductivity(hour_factor),
                'total_dissolved_solids': self._calculate_tds(),
                'nitrates': self._calculate_nitrates(),
                'status': self._determine_status()
            }
            readings.append(reading)
        
        return readings
    
    def _calculate_ph(self, base: float, hour_factor: float, noise: float) -> float:
        """Calcula pH com variação diurna."""
        return np.clip(base + 0.5 * hour_factor + noise, 4.0, 10.0)
    
    def _calculate_turbidity(self, hour_factor: float) -> float:
        """Calcula turbidez (NTU)."""
        return max(0, 2 + 3 * np.random.exponential(0.5) + hour_factor * 0.5)
    
    def _calculate_dissolved_oxygen(self, hour_factor: float) -> float:
        """Calcula oxigênio dissolvido (mg/L)."""
        return max(0, 8 - 0.5 * hour_factor + np.random.normal(0, 0.5))
    
    def _calculate_temperature(
        self,
        base: float,
        hour_factor: float,
        day_factor: float
    ) -> float:
        """Calcula temperatura (°C) com variação diurna e sazonal."""
        return base + 3 * hour_factor + 5 * day_factor + np.random.normal(0, 0.5)
    
    def _calculate_conductivity(self, hour_factor: float) -> float:
        """Calcula condutividade (µS/cm)."""
        return max(0, 200 + 50 * np.random.normal(0, 1) + 20 * hour_factor)
    
    def _calculate_tds(self) -> float:
        """Calcula sólidos totais dissolvidos (mg/L)."""
        return max(0, 150 + 30 * np.random.normal(0, 1))
    
    def _calculate_nitrates(self) -> float:
        """Calcula nitratos (mg/L)."""
        return max(0, 2 + 3 * np.random.normal(0, 1))
    
    def _determine_status(self) -> str:
        """Determina o status da leitura baseado em probabilidades."""
        return np.random.choice(
            ['Normal', 'Alerta', 'Crítico'],
            p=self.STATUS_PROBABILITIES
        )
    
    def add_anomaly(
        self,
        df: pd.DataFrame,
        station: str,
        parameter: str,
        start_time: datetime,
        duration_hours: int,
        severity: str = 'high'
    ) -> pd.DataFrame:
        """
        Adiciona uma anomalia artificial aos dados (para testes).
        
        Args:
            df: DataFrame original
            station: Nome da estação
            parameter: Parâmetro a ser alterado
            start_time: Início da anomalia
            duration_hours: Duração em horas
            severity: 'low', 'medium', 'high'
        
        Returns:
            DataFrame modificado com anomalia
        """
        df_modified = df.copy()
        
        mask = (
            (df_modified['station'] == station) &
            (df_modified['timestamp'] >= start_time) &
            (df_modified['timestamp'] <= start_time + timedelta(hours=duration_hours))
        )
        
        multipliers = {'low': 1.3, 'medium': 1.6, 'high': 2.0}
        multiplier = multipliers.get(severity, 1.5)
        
        df_modified.loc[mask, parameter] *= multiplier
        
        return df_modified


# =============================================================================
# FUNÇÃO DE INTERFACE SIMPLIFICADA (para compatibilidade)
# =============================================================================

def generate_water_quality_data(
    days: int = 30,
    stations: int = 5,
    seed: int = 42
) -> pd.DataFrame:
    """
    Função simplificada para gerar dados (interface antiga).
    
    Args:
        days: Número de dias de dados
        stations: Número de estações (máximo 5)
        seed: Seed para reprodutibilidade
    
    Returns:
        DataFrame com dados de qualidade da água
    """
    generator = WaterQualityDataGenerator(seed=seed)
    
    # Seleciona apenas o número de estações solicitado
    selected_stations = generator.DEFAULT_STATIONS[:stations]
    
    return generator.generate(days=days, stations=selected_stations)


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Teste do gerador
    print("🔄 Gerando dados de teste...")
    
    generator = WaterQualityDataGenerator(seed=42)
    df = generator.generate(days=7, frequency='H')
    
    print(f"✅ Dados gerados: {len(df)} leituras")
    print(f"\n📊 Resumo por estação:")
    print(df.groupby('station')['ph'].agg(['mean', 'std', 'min', 'max']))
    
    print(f"\n📈 Primeiras 5 leituras:")
    print(df.head())
    
    # Teste de anomalia
    print("\n⚠️ Adicionando anomalia de teste...")
    anomaly_start = df['timestamp'].iloc[100]
    df_anomaly = generator.add_anomaly(
        df, 
        station="Estação A",
        parameter="ph",
        start_time=anomaly_start,
        duration_hours=5,
        severity="high"
    )
    
    print("✅ Anomalia adicionada com sucesso!")