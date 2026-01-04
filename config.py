"""
Configuration file for Nifty Sectoral Scanner
Contains sector mappings and indicator configurations
"""

# Nifty Sectoral Indices
SECTORS = {
    'NIFTY 50': '^NSEI',
    'BANK (Banknifty)': '^NSEBANK',
    'FINANCIAL SERVICES': '^CNXFINANCE',
    'PSU BANKS': '^CNXPSUBANK',
    'PRIVATE BANKS': '^CNXPVTBANK',
    'AUTO': '^CNXAUTO',
    'IT': '^CNXIT',
    'METAL': '^CNXMETAL',
    'PHARMA': '^CNXPHARMA',
    'FMCG': '^CNXFMCG',
    'OIL & GAS': '^CNXOIL',
    'COMMODITIES': '^CNXCOMMODITIES',
    'CONSUMER DURABLE': '^CNXCONSUM',
    'REALTY': '^CNXREALTY',
    'MEDIA': '^CNXMEDIA',
    'ENERGY': '^CNXENERGY',
    'INFRASTRUCTURE': '^CNXINFRA',
    'SERVICES SECTOR': '^CNXSERVICE',
    'MNC': '^CNXMNC'
}

# Sector-specific indicator configurations
SECTOR_INDICATORS = {
    'FINANCIAL SERVICES': {
        'primary': 'Volatility',
        'indicators': ['BB', 'ATR'],
        'chart_pattern': 'Rectangles/Boxes',
        'logic': 'Compression: Energy storage before blast'
    },
    'PSU BANKS': {
        'primary': 'Trend',
        'indicators': ['ADX', 'EMA'],
        'chart_pattern': 'Channels/Wedges',
        'logic': 'Persistence: Orderly flow within staircase'
    },
    'PRIVATE BANKS': {
        'primary': 'Trend',
        'indicators': ['ADX', 'EMA', 'BB'],
        'chart_pattern': 'Channels/Wedges',
        'logic': 'Persistence: Orderly flow'
    },
    'AUTO': {
        'primary': 'Momentum',
        'indicators': ['RSI', 'Volume'],
        'chart_pattern': 'Flags/Pennants',
        'logic': 'Continuation: Brief rest in sprint'
    },
    'IT': {
        'primary': 'Trend',
        'indicators': ['ADX', 'EMA'],
        'chart_pattern': 'Channels/Wedges',
        'logic': 'Persistence: Orderly flow'
    },
    'METAL': {
        'primary': 'Momentum',
        'indicators': ['Stochastics', 'VWAP'],
        'chart_pattern': 'Parabolic Curves',
        'logic': 'Euphoria: Vertical growth/Blow-off'
    },
    'OIL & GAS': {
        'primary': 'Volatility',
        'indicators': ['ATR', 'BB'],
        'chart_pattern': 'H&S/Double Tops',
        'logic': 'Expansion: Bulls/Bears fighting'
    },
    'FMCG': {
        'primary': 'Mean Reversion',
        'indicators': ['BB', 'RSI', 'SMA'],
        'chart_pattern': 'BB + RSI Overextended',
        'logic': 'Exhaustion: Rubber band snap-back'
    },
    'PHARMA': {
        'primary': 'Trend',
        'indicators': ['ADX', 'EMA'],
        'chart_pattern': 'Channels/Wedges',
        'logic': 'Persistence: Orderly flow'
    },
    'COMMODITIES': {
        'primary': 'Momentum',
        'indicators': ['Stochastics', 'VWAP'],
        'chart_pattern': 'Parabolic Curves',
        'logic': 'Euphoria: Vertical growth'
    },
    'CONSUMER DURABLE': {
        'primary': 'Momentum',
        'indicators': ['RSI', 'Volume'],
        'chart_pattern': 'Flags/Pennants',
        'logic': 'Continuation: Brief rest'
    }
}

# App configuration
APP_CONFIG = {
    'title': 'Nifty Sectoral Scanner v5.3',
    'page_title': 'Nifty Sectoral Scanner',
    'layout': 'wide',
    'cache_ttl': 3600,  # 1 hour
}

# Indicator parameters
INDICATOR_PARAMS = {
    'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
    'BB': {'period': 20, 'std': 2},
    'ADX': {'period': 14},
    'ATR': {'period': 14},
    'STOCH': {'period': 14},
    'EMA': {'period': 20},
    'SMA': {'period': 200},
    'VWAP': {'lookback': 20},
    'CMF': {'period': 21}
}

# Indicator explanations (for tooltips)
INDICATOR_EXPLANATIONS = {
    'ADX': 'Average Directional Index - Measures trend strength (>25 = strong trend)',
    'Norm_ADX': 'Normalized ADX over N sessions (0-100 scale for comparison)',
    'ADX_Trend': 'Direction of ADX movement: Increasing = strengthening, Weakening = fading',
    'DI_Spread': 'Signed difference: +DI minus -DI. Positive = Bullish, Negative = Bearish. Magnitude shows conviction.',
    'Trend': 'Overall trend classification based on ADX strength',
    'CMF': 'Chaikin Money Flow (21-period) - Measures buying/selling pressure through volume',
    'CMF_Trend': 'CMF direction: Accumulation (buying) vs Distribution (selling)',
    'Remark': 'Overall trend signal based on ADX + DI + CMF combined analysis (majority voting)',
    'Signal': 'Aggregated signal from all indicators for this sector',
    'BB_Width': 'Bollinger Band width - Narrow = low volatility (squeeze), Wide = high volatility',
    'BB': 'Bollinger Bands position - Shows if price is at extremes',
    'RSI': 'Relative Strength Index - <30 oversold, >70 overbought',
    'ATR': 'Average True Range - Measures price volatility',
    'Stochastic': 'Stochastic Oscillator - <20 oversold, >80 overbought',
    'VWAP': 'Volume Weighted Average Price - Benchmark for institutional trading',
    'EMA': 'Exponential Moving Average - Trend direction indicator',
    'SMA': 'Simple Moving Average - Long-term trend direction',
    'Volume': 'Volume ratio vs 20-day average - Shows participation strength'
}
