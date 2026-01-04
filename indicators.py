"""
Technical Indicators Module
Contains all indicator calculation functions
"""

import pandas as pd
import numpy as np


def calculate_rsi(series, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        series: Price series (typically Close)
        period: RSI period (default: 14)
    
    Returns:
        Series: RSI values
    """
    if len(series) < period + 1:
        return None
    
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_bollinger_bands(series, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    
    Args:
        series: Price series (typically Close)
        period: Moving average period (default: 20)
        std_dev: Standard deviation multiplier (default: 2)
    
    Returns:
        Tuple: (middle_band, upper_band, lower_band, bb_width, bb_position)
    """
    if len(series) < period:
        return None, None, None, None, None
    
    middle_band = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    # BB Width (normalized)
    bb_width = ((upper_band - lower_band) / middle_band) * 100
    
    # BB Position (where price is within bands)
    bb_position = ((series - lower_band) / (upper_band - lower_band)) * 100
    
    return middle_band, upper_band, lower_band, bb_width, bb_position


def calculate_atr(df, period=14):
    """
    Calculate Average True Range (ATR)
    
    Args:
        df: DataFrame with High, Low, Close columns
        period: ATR period (default: 14)
    
    Returns:
        Float: Current ATR value
    """
    if len(df) < period + 1:
        return None
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr.iloc[-1] if not atr.empty else None


def calculate_adx(df, period=14):
    """
    Calculate Average Directional Index (ADX)
    
    Args:
        df: DataFrame with High, Low, Close columns
        period: ADX period (default: 14)
    
    Returns:
        Float: Current ADX value
    """
    if len(df) < period + 1:
        return None
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # Calculate +DM and -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate smoothed TR and DMs
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    
    # Calculate DX and ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.rolling(window=period).mean()
    
    return adx.iloc[-1] if not adx.empty and not pd.isna(adx.iloc[-1]) else None


def calculate_adx_series(df, period=14):
    """
    Calculate ADX series with +DI and -DI for trend analysis
    
    Args:
        df: DataFrame with High, Low, Close columns
        period: ADX period (default: 14)
    
    Returns:
        Tuple: (adx_series, plus_di_series, minus_di_series)
    """
    if len(df) < period + 1:
        return None, None, None
    
    try:
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # Calculate +DM and -DM
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate smoothed ATR
        atr = tr.rolling(window=period).mean()
        
        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    except Exception as e:
        print(f"Error calculating ADX series: {str(e)}")
        return None, None, None


def calculate_stochastic(df, period=14):
    """
    Calculate Stochastic Oscillator
    
    Args:
        df: DataFrame with High, Low, Close columns
        period: Stochastic period (default: 14)
    
    Returns:
        Float: Current Stochastic %K value
    """
    if len(df) < period:
        return None
    
    low_min = df['Low'].rolling(window=period).min()
    high_max = df['High'].rolling(window=period).max()
    
    stoch_k = 100 * ((df['Close'] - low_min) / (high_max - low_min))
    
    return stoch_k.iloc[-1] if not stoch_k.empty and not pd.isna(stoch_k.iloc[-1]) else None


def calculate_vwap(df, lookback=20):
    """
    Calculate Volume Weighted Average Price (VWAP)
    
    Args:
        df: DataFrame with High, Low, Close, Volume columns
        lookback: Number of periods for VWAP calculation
    
    Returns:
        Float: Current VWAP value
    """
    if len(df) < lookback:
        return None
    
    df_temp = df.tail(lookback).copy()
    
    typical_price = (df_temp['High'] + df_temp['Low'] + df_temp['Close']) / 3
    vwap = (typical_price * df_temp['Volume']).sum() / df_temp['Volume'].sum()
    
    return vwap if not pd.isna(vwap) else None


def calculate_sma(series, period=200):
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        series: Price series (typically Close)
        period: SMA period (default: 200)
    
    Returns:
        Float: Current SMA value
    """
    if len(series) < period:
        return None
    
    sma = series.rolling(window=period).mean()
    
    return sma.iloc[-1] if not sma.empty and not pd.isna(sma.iloc[-1]) else None


def calculate_ema(series, period=20):
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        series: Price series (typically Close)
        period: EMA period (default: 20)
    
    Returns:
        Float: Current EMA value
    """
    if len(series) < period:
        return None
    
    ema = series.ewm(span=period, adjust=False).mean()
    
    return ema.iloc[-1] if not ema.empty and not pd.isna(ema.iloc[-1]) else None


def calculate_volume_ratio(df, period=20):
    """
    Calculate volume ratio vs average volume
    
    Args:
        df: DataFrame with Volume column
        period: Lookback period for average (default: 20)
    
    Returns:
        Tuple: (volume_ratio, volume_class)
    """
    if len(df) < period + 1:
        return None, "N/A"
    
    current_volume = df['Volume'].iloc[-1]
    avg_volume = df['Volume'].tail(period).mean()
    
    if avg_volume == 0:
        return None, "N/A"
    
    vol_ratio = current_volume / avg_volume
    
    # Classify volume
    if vol_ratio > 2.0:
        vol_class = "🟢 Very High"
    elif vol_ratio > 1.5:
        vol_class = "🟡 High"
    elif vol_ratio > 0.8:
        vol_class = "⚪ Normal"
    elif vol_ratio > 0.5:
        vol_class = "🟠 Low"
    else:
        vol_class = "🔴 Very Low"
    
    return vol_ratio, vol_class


def calculate_cmf(df, period=21):
    """
    Calculate Chaikin Money Flow (CMF)
    
    Args:
        df: DataFrame with High, Low, Close, Volume columns
        period: CMF period (default: 21)
    
    Returns:
        Float: Current CMF value
    """
    if len(df) < period:
        return None
    
    try:
        # Money Flow Multiplier = [(Close - Low) - (High - Close)] / (High - Low)
        high_low_diff = df['High'] - df['Low']
        
        # Avoid division by zero
        high_low_diff = high_low_diff.replace(0, np.nan)
        
        mf_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / high_low_diff
        mf_multiplier = mf_multiplier.fillna(0)
        
        # Money Flow Volume = MF Multiplier × Volume
        mf_volume = mf_multiplier * df['Volume']
        
        # CMF = Sum(MF Volume, period) / Sum(Volume, period)
        cmf_numerator = mf_volume.rolling(window=period).sum()
        cmf_denominator = df['Volume'].rolling(window=period).sum()
        
        # Avoid division by zero
        cmf_denominator = cmf_denominator.replace(0, np.nan)
        
        cmf = cmf_numerator / cmf_denominator
        
        return cmf.iloc[-1] if not cmf.empty and not pd.isna(cmf.iloc[-1]) else None
    except Exception as e:
        print(f"Error calculating CMF: {str(e)}")
        return None


def calculate_macd(series, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        series: Price series (typically Close)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
    
    Returns:
        Tuple: (macd_line, signal_line, histogram)
    """
    if len(series) < slow + signal:
        return None, None, None
    
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return (
        macd_line.iloc[-1] if not macd_line.empty else None,
        signal_line.iloc[-1] if not signal_line.empty else None,
        histogram.iloc[-1] if not histogram.empty else None
    )


def calculate_momentum(series, period=10):
    """
    Calculate Price Momentum
    
    Args:
        series: Price series (typically Close)
        period: Momentum period (default: 10)
    
    Returns:
        Float: Current momentum value
    """
    if len(series) < period + 1:
        return None
    
    momentum = series.iloc[-1] - series.iloc[-(period + 1)]
    
    return momentum


def calculate_roc(series, period=10):
    """
    Calculate Rate of Change (ROC)
    
    Args:
        series: Price series (typically Close)
        period: ROC period (default: 10)
    
    Returns:
        Float: Current ROC percentage
    """
    if len(series) < period + 1:
        return None
    
    current = series.iloc[-1]
    previous = series.iloc[-(period + 1)]
    
    if previous == 0:
        return None
    
    roc = ((current - previous) / previous) * 100
    
    return roc


def calculate_obv(df):
    """
    Calculate On-Balance Volume (OBV)
    
    Args:
        df: DataFrame with Close and Volume columns
    
    Returns:
        Series: OBV values
    """
    if len(df) < 2:
        return None
    
    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df['Volume'].iloc[0]
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + df['Volume'].iloc[i]
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - df['Volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv
