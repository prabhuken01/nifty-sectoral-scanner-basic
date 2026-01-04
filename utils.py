"""
Utility Functions Module
Helper functions for data formatting, validation, and analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


def format_number(value, decimal_places=2, prefix="", suffix=""):
    """
    Format number with specified decimal places and prefix/suffix
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places
        prefix: String to prepend (e.g., '₹', '$')
        suffix: String to append (e.g., '%', 'M')
    
    Returns:
        Formatted string
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        formatted = f"{value:.{decimal_places}f}"
        return f"{prefix}{formatted}{suffix}"
    except (ValueError, TypeError):
        return "N/A"


def format_percentage(value, decimal_places=2, show_sign=True):
    """
    Format percentage value
    
    Args:
        value: Percentage value
        decimal_places: Number of decimal places
        show_sign: Whether to show +/- sign
    
    Returns:
        Formatted percentage string
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        if show_sign:
            return f"{value:+.{decimal_places}f}%"
        else:
            return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_currency(value, symbol="₹", decimal_places=2):
    """
    Format currency value with Indian numbering system
    
    Args:
        value: Currency value
        symbol: Currency symbol
        decimal_places: Number of decimal places
    
    Returns:
        Formatted currency string
    """
    if value is None or pd.isna(value):
        return "N/A"
    
    try:
        # Convert to crores if value is large
        if abs(value) >= 10000000:  # 1 Crore
            crore_value = value / 10000000
            return f"{symbol}{crore_value:.2f}Cr"
        elif abs(value) >= 100000:  # 1 Lakh
            lakh_value = value / 100000
            return f"{symbol}{lakh_value:.2f}L"
        else:
            return f"{symbol}{value:.{decimal_places}f}"
    except (ValueError, TypeError):
        return "N/A"


def get_signal_emoji(value, thresholds, reverse=False):
    """
    Get emoji based on value and thresholds
    
    Args:
        value: Numeric value to evaluate
        thresholds: Dict with 'high', 'medium', 'low' keys
        reverse: If True, reverse the emoji logic (lower is better)
    
    Returns:
        Emoji string
    """
    if value is None or pd.isna(value):
        return "⚪"
    
    try:
        if not reverse:
            if value >= thresholds.get('high', 70):
                return "🟢"
            elif value >= thresholds.get('medium', 40):
                return "🟡"
            elif value >= thresholds.get('low', 20):
                return "🟠"
            else:
                return "🔴"
        else:
            if value <= thresholds.get('low', 30):
                return "🟢"
            elif value <= thresholds.get('medium', 50):
                return "🟡"
            elif value <= thresholds.get('high', 70):
                return "🟠"
            else:
                return "🔴"
    except (ValueError, TypeError):
        return "⚪"


def get_trend_emoji(current, previous):
    """
    Get trend emoji based on comparison
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Emoji string (up/down/flat arrow)
    """
    if current is None or previous is None:
        return "➡️"
    
    if pd.isna(current) or pd.isna(previous):
        return "➡️"
    
    diff = current - previous
    
    if abs(diff) < 0.01:  # Essentially flat
        return "➡️"
    elif diff > 0:
        return "⬆️"
    else:
        return "⬇️"


def calculate_percentage_change(current, previous):
    """
    Calculate percentage change between two values
    
    Args:
        current: Current value
        previous: Previous value
    
    Returns:
        Percentage change
    """
    if current is None or previous is None or previous == 0:
        return None
    
    if pd.isna(current) or pd.isna(previous):
        return None
    
    return ((current - previous) / abs(previous)) * 100


def normalize_value(value, min_val, max_val, target_min=0, target_max=100):
    """
    Normalize value to target range using min-max scaling
    
    Args:
        value: Value to normalize
        min_val: Minimum value in dataset
        max_val: Maximum value in dataset
        target_min: Target minimum (default: 0)
        target_max: Target maximum (default: 100)
    
    Returns:
        Normalized value
    """
    if value is None or min_val is None or max_val is None:
        return None
    
    if pd.isna(value) or pd.isna(min_val) or pd.isna(max_val):
        return None
    
    if max_val == min_val:
        return target_min + (target_max - target_min) / 2
    
    normalized = ((value - min_val) / (max_val - min_val)) * (target_max - target_min) + target_min
    
    return normalized


def calculate_z_score(value, mean, std):
    """
    Calculate z-score for a value
    
    Args:
        value: Value to calculate z-score for
        mean: Mean of the dataset
        std: Standard deviation of the dataset
    
    Returns:
        Z-score
    """
    if value is None or mean is None or std is None or std == 0:
        return None
    
    if pd.isna(value) or pd.isna(mean) or pd.isna(std):
        return None
    
    return (value - mean) / std


def is_outlier(value, mean, std, threshold=3):
    """
    Check if value is an outlier using z-score method
    
    Args:
        value: Value to check
        mean: Mean of the dataset
        std: Standard deviation of the dataset
        threshold: Z-score threshold (default: 3)
    
    Returns:
        Boolean indicating if value is an outlier
    """
    z_score = calculate_z_score(value, mean, std)
    
    if z_score is None:
        return False
    
    return abs(z_score) > threshold


def get_time_until_next_hour():
    """
    Calculate time remaining until next hour
    
    Returns:
        Timedelta object
    """
    now = datetime.now()
    next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    return next_hour - now


def format_timedelta(td):
    """
    Format timedelta as human-readable string
    
    Args:
        td: Timedelta object
    
    Returns:
        Formatted string (e.g., "45 minutes")
    """
    if td is None:
        return "N/A"
    
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds} seconds"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def is_market_open():
    """
    Check if Indian stock market is currently open
    
    Returns:
        Boolean indicating if market is open
    """
    now = datetime.now()
    
    # Market is closed on weekends
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Market hours: 9:15 AM to 3:30 PM IST
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= now <= market_close


def get_market_status():
    """
    Get current market status with emoji
    
    Returns:
        Tuple: (status_text, emoji)
    """
    if is_market_open():
        return "Market Open", "🟢"
    else:
        now = datetime.now()
        if now.weekday() >= 5:
            return "Weekend - Market Closed", "🔴"
        elif now.hour < 9 or (now.hour == 9 and now.minute < 15):
            return "Pre-Market", "🟡"
        else:
            return "After-Hours", "🟠"


def safe_divide(numerator, denominator, default=None):
    """
    Safely divide two numbers with error handling
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails
    
    Returns:
        Result of division or default value
    """
    if numerator is None or denominator is None:
        return default
    
    if pd.isna(numerator) or pd.isna(denominator):
        return default
    
    if denominator == 0:
        return default
    
    try:
        return numerator / denominator
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def calculate_moving_average(series, window):
    """
    Calculate simple moving average with error handling
    
    Args:
        series: Pandas Series
        window: Window size
    
    Returns:
        Series with moving average or None
    """
    if series is None or len(series) < window:
        return None
    
    try:
        return series.rolling(window=window).mean()
    except Exception:
        return None


def dataframe_to_csv(df, filename=None):
    """
    Convert dataframe to CSV for download
    
    Args:
        df: DataFrame to convert
        filename: Optional filename
    
    Returns:
        CSV string
    """
    if df is None or df.empty:
        return None
    
    try:
        return df.to_csv(index=False).encode('utf-8')
    except Exception as e:
        st.error(f"Error converting to CSV: {str(e)}")
        return None


def create_download_button(df, filename="sector_data.csv", label="📥 Download CSV"):
    """
    Create Streamlit download button for dataframe
    
    Args:
        df: DataFrame to download
        filename: Filename for download
        label: Button label
    
    Returns:
        None (displays button in Streamlit)
    """
    if df is None or df.empty:
        return
    
    csv = dataframe_to_csv(df, filename)
    
    if csv:
        st.download_button(
            label=label,
            data=csv,
            file_name=filename,
            mime="text/csv"
        )


def highlight_top_values(df, column, top_n=3, color='lightgreen'):
    """
    Highlight top N values in a dataframe column
    
    Args:
        df: DataFrame
        column: Column name to highlight
        top_n: Number of top values to highlight
        color: Highlight color
    
    Returns:
        Styled DataFrame
    """
    if df is None or df.empty or column not in df.columns:
        return df
    
    def highlight(s):
        if s.name == column:
            # Get top N values
            top_vals = s.nlargest(top_n).values
            return [f'background-color: {color}' if v in top_vals else '' for v in s]
        return ['' for _ in s]
    
    return df.style.apply(highlight, axis=0)


def calculate_correlation_matrix(sector_data_dict):
    """
    Calculate correlation matrix between sectors
    
    Args:
        sector_data_dict: Dictionary of sector dataframes
    
    Returns:
        Correlation matrix DataFrame
    """
    if not sector_data_dict:
        return None
    
    try:
        # Extract close prices for all sectors
        close_prices = {}
        for sector, df in sector_data_dict.items():
            if 'Close' in df.columns and len(df) > 0:
                close_prices[sector] = df['Close']
        
        if not close_prices:
            return None
        
        # Create combined dataframe
        combined_df = pd.DataFrame(close_prices)
        
        # Calculate percentage changes
        pct_change_df = combined_df.pct_change().dropna()
        
        # Calculate correlation
        correlation_matrix = pct_change_df.corr()
        
        return correlation_matrix
    except Exception as e:
        print(f"Error calculating correlation: {str(e)}")
        return None


def get_summary_statistics(df, column='Close'):
    """
    Get summary statistics for a column
    
    Args:
        df: DataFrame
        column: Column name
    
    Returns:
        Dictionary with statistics
    """
    if df is None or df.empty or column not in df.columns:
        return None
    
    try:
        series = df[column].dropna()
        
        return {
            'count': len(series),
            'mean': series.mean(),
            'median': series.median(),
            'std': series.std(),
            'min': series.min(),
            'max': series.max(),
            'q25': series.quantile(0.25),
            'q75': series.quantile(0.75)
        }
    except Exception as e:
        print(f"Error calculating statistics: {str(e)}")
        return None


def validate_numeric_range(value, min_val=None, max_val=None):
    """
    Validate if value is within specified range
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Tuple: (is_valid, error_message)
    """
    if value is None or pd.isna(value):
        return False, "Value is None or NaN"
    
    try:
        value = float(value)
        
        if min_val is not None and value < min_val:
            return False, f"Value must be >= {min_val}"
        
        if max_val is not None and value > max_val:
            return False, f"Value must be <= {max_val}"
        
        return True, "Valid"
    except (ValueError, TypeError):
        return False, "Value is not numeric"


def create_color_gradient(value, min_val, max_val, start_color='red', end_color='green'):
    """
    Create color gradient based on value position between min and max
    
    Args:
        value: Value to evaluate
        min_val: Minimum value
        max_val: Maximum value
        start_color: Color for minimum value
        end_color: Color for maximum value
    
    Returns:
        RGB color string
    """
    if value is None or min_val is None or max_val is None:
        return "rgb(128, 128, 128)"  # Gray
    
    if max_val == min_val:
        return "rgb(128, 128, 128)"
    
    # Normalize value between 0 and 1
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Clamp between 0 and 1
    
    # Simple color interpolation (red to green)
    if start_color == 'red' and end_color == 'green':
        r = int(255 * (1 - normalized))
        g = int(255 * normalized)
        b = 0
        return f"rgb({r}, {g}, {b})"
    
    return "rgb(128, 128, 128)"


def log_error(error_message, context=""):
    """
    Log error message with timestamp and context
    
    Args:
        error_message: Error message
        context: Additional context information
    
    Returns:
        None (prints to console)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] ERROR"
    
    if context:
        log_entry += f" ({context})"
    
    log_entry += f": {error_message}"
    
    print(log_entry)
