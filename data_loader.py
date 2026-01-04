"""
Data loading and validation module
Handles downloading and preprocessing of market data
"""

import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta


@st.cache_data(ttl=3600)
def load_sector_data(sectors, period='6mo', interval='1d'):
    """
    Load historical data for all sectors
    
    Args:
        sectors: Dictionary of sector names and ticker symbols
        period: Data period (default: 6 months)
        interval: Data interval (default: daily)
    
    Returns:
        Dictionary of DataFrames with sector data
    """
    data = {}
    failed_sectors = []
    
    for name, ticker in sectors.items():
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if not df.empty and len(df) > 50:
                # Flatten multi-index columns if present
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Ensure required columns exist
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if all(col in df.columns for col in required_cols):
                    df = df[required_cols].copy()
                    df = df.dropna()
                    data[name] = df
                else:
                    failed_sectors.append(name)
            else:
                failed_sectors.append(name)
                
        except Exception as e:
            failed_sectors.append(name)
            print(f"Error loading {name}: {str(e)}")
    
    if failed_sectors:
        st.warning(f"⚠️ Failed to load data for: {', '.join(failed_sectors)}")
    
    return data


def validate_data(df, min_rows=50):
    """
    Validate DataFrame has sufficient data
    
    Args:
        df: DataFrame to validate
        min_rows: Minimum required rows
    
    Returns:
        Boolean indicating if data is valid
    """
    if df is None or df.empty:
        return False
    
    if len(df) < min_rows:
        return False
    
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in df.columns for col in required_cols):
        return False
    
    return True


def get_latest_price(df):
    """
    Get latest closing price from DataFrame
    
    Args:
        df: DataFrame with Close column
    
    Returns:
        Float: Latest close price or None
    """
    if not validate_data(df):
        return None
    
    return df['Close'].iloc[-1]


def get_price_change(df, periods=1):
    """
    Calculate price change over specified periods
    
    Args:
        df: DataFrame with Close column
        periods: Number of periods to look back
    
    Returns:
        Tuple: (absolute_change, percentage_change)
    """
    if not validate_data(df) or len(df) < periods + 1:
        return None, None
    
    current_price = df['Close'].iloc[-1]
    previous_price = df['Close'].iloc[-(periods + 1)]
    
    abs_change = current_price - previous_price
    pct_change = (abs_change / previous_price) * 100
    
    return abs_change, pct_change


def resample_data(df, interval='1W'):
    """
    Resample data to different timeframe
    
    Args:
        df: DataFrame with OHLCV data
        interval: Target interval (e.g., '1W', '1M')
    
    Returns:
        Resampled DataFrame
    """
    if not validate_data(df):
        return None
    
    resampled = df.resample(interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    
    return resampled.dropna()


def get_date_range(df):
    """
    Get start and end dates from DataFrame
    
    Args:
        df: DataFrame with datetime index
    
    Returns:
        Tuple: (start_date, end_date)
    """
    if df is None or df.empty:
        return None, None
    
    return df.index[0], df.index[-1]


def filter_by_date(df, start_date=None, end_date=None):
    """
    Filter DataFrame by date range
    
    Args:
        df: DataFrame with datetime index
        start_date: Start date (optional)
        end_date: End date (optional)
    
    Returns:
        Filtered DataFrame
    """
    if not validate_data(df):
        return None
    
    filtered_df = df.copy()
    
    if start_date:
        filtered_df = filtered_df[filtered_df.index >= pd.to_datetime(start_date)]
    
    if end_date:
        filtered_df = filtered_df[filtered_df.index <= pd.to_datetime(end_date)]
    
    return filtered_df


def calculate_returns(df, period='1d'):
    """
    Calculate returns over specified period
    
    Args:
        df: DataFrame with Close column
        period: Period for returns calculation
    
    Returns:
        Series of returns
    """
    if not validate_data(df):
        return None
    
    return df['Close'].pct_change()


def get_trading_days(df):
    """
    Get number of trading days in dataset
    
    Args:
        df: DataFrame with datetime index
    
    Returns:
        Integer: Number of trading days
    """
    if not validate_data(df):
        return 0
    
    return len(df)


def check_data_freshness(df, max_age_hours=24):
    """
    Check if data is recent enough
    
    Args:
        df: DataFrame with datetime index
        max_age_hours: Maximum age in hours
    
    Returns:
        Boolean: True if data is fresh
    """
    if not validate_data(df):
        return False
    
    latest_date = df.index[-1]
    age = datetime.now() - latest_date.to_pydatetime()
    
    return age.total_seconds() / 3600 <= max_age_hours


def get_summary_stats(df):
    """
    Get summary statistics for the data
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        Dictionary with summary statistics
    """
    if not validate_data(df):
        return None
    
    return {
        'total_days': len(df),
        'latest_price': df['Close'].iloc[-1],
        'highest_price': df['High'].max(),
        'lowest_price': df['Low'].min(),
        'avg_volume': df['Volume'].mean(),
        'start_date': df.index[0].strftime('%Y-%m-%d'),
        'end_date': df.index[-1].strftime('%Y-%m-%d')
    }
