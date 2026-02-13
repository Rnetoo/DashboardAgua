"""Helper functions for data processing and formatting."""

from datetime import datetime

def format_number(value, decimals=2):
    """Format number with specified decimal places."""
    return f"{value:.{decimals}f}"

def get_quality_status(value, param):
    """Return quality status based on WHO/CONAMA standards."""
    limits = {
        'ph': (6.5, 8.5),
        'turbidity': (0, 5),
        'dissolved_oxygen': (6, 14),
        'temperature': (0, 30),
        'conductivity': (0, 400),
        'nitrates': (0, 10)
    }
    
    if param not in limits:
        return 'unknown'
    
    min_val, max_val = limits[param]
    if min_val <= value <= max_val:
        return 'good'
    elif value <= min_val * 0.8 or value >= max_val * 1.2:
        return 'critical'
    else:
        return 'warning'

def get_quality_color(status):
    """Return color code for status."""
    colors = {
        'good': '#00C851',
        'warning': '#ffbb33',
        'critical': '#ff4444',
        'unknown': '#9e9e9e'
    }
    return colors.get(status, '#9e9e9e')

def calculate_quality_index(readings):
    """Calculate overall water quality index (0-100)."""
    # Simplified WQI calculation
    weights = {'ph': 0.2, 'turbidity': 0.2, 'dissolved_oxygen': 0.3, 
               'temperature': 0.1, 'conductivity': 0.2}
    
    score = 0
    for param, value in readings.items():
        if param in weights:
            status = get_quality_status(value, param)
            if status == 'good':
                score += weights[param] * 100
            elif status == 'warning':
                score += weights[param] * 50
    
    return min(100, max(0, score))

def generate_export_filename():
    """Generate filename for data export."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"water_quality_data_{timestamp}.csv"