"""
Nifty Sectoral Scanner v5.3
Main Streamlit application
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Import modules
from config import SECTORS, SECTOR_INDICATORS, APP_CONFIG, INDICATOR_PARAMS, INDICATOR_EXPLANATIONS
from data_loader import load_sector_data, validate_data, get_latest_price, get_price_change
from indicators import (
    calculate_rsi, calculate_bollinger_bands, calculate_atr,
    calculate_adx, calculate_stochastic, calculate_vwap,
    calculate_sma, calculate_ema, calculate_volume_ratio
)
from trend_analysis import (
    calculate_trend_indicators, rank_by_trend_strength,
    get_trend_summary, filter_by_trend_strength
)


# Page configuration
st.set_page_config(
    page_title=APP_CONFIG['page_title'],
    page_icon="📊",
    layout=APP_CONFIG['layout'],
    initial_sidebar_state="expanded"
)


def display_header():
    """Display application header with timestamp"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("📊 " + APP_CONFIG['title'])
        st.markdown("*Real-time sectoral rotation analysis with advanced technical indicators*")
    
    with col2:
        # Display last updated time
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.markdown(f"**Last Updated:**")
        st.markdown(f"🕐 `{current_time}`")


def calculate_sector_indicators(sector_data):
    """
    Calculate all indicators for a sector
    
    Args:
        sector_data: DataFrame with OHLCV data
    
    Returns:
        Dictionary with indicator values
    """
    if not validate_data(sector_data):
        return None
    
    indicators = {}
    
    # Price data
    close = sector_data['Close']
    indicators['price'] = get_latest_price(sector_data)
    abs_change, pct_change = get_price_change(sector_data, periods=1)
    indicators['change'] = pct_change
    
    # RSI
    rsi = calculate_rsi(close, period=INDICATOR_PARAMS['RSI']['period'])
    indicators['rsi'] = rsi.iloc[-1] if rsi is not None and len(rsi) > 0 else None
    
    # Bollinger Bands
    bb_middle, bb_upper, bb_lower, bb_width, bb_pos = calculate_bollinger_bands(
        close,
        period=INDICATOR_PARAMS['BB']['period'],
        std_dev=INDICATOR_PARAMS['BB']['std']
    )
    indicators['bb_width'] = bb_width.iloc[-1] if bb_width is not None and len(bb_width) > 0 else None
    indicators['bb_position'] = bb_pos.iloc[-1] if bb_pos is not None and len(bb_pos) > 0 else None
    
    # ADX
    indicators['adx'] = calculate_adx(sector_data, period=INDICATOR_PARAMS['ADX']['period'])
    
    # ATR
    indicators['atr'] = calculate_atr(sector_data, period=INDICATOR_PARAMS['ATR']['period'])
    
    # Stochastic
    indicators['stoch'] = calculate_stochastic(sector_data, period=INDICATOR_PARAMS['STOCH']['period'])
    
    # VWAP
    indicators['vwap'] = calculate_vwap(sector_data, lookback=INDICATOR_PARAMS['VWAP']['lookback'])
    
    # Moving Averages
    indicators['ema'] = calculate_ema(close, period=INDICATOR_PARAMS['EMA']['period'])
    indicators['sma'] = calculate_sma(close, period=INDICATOR_PARAMS['SMA']['period'])
    
    # Volume
    vol_ratio, vol_class = calculate_volume_ratio(sector_data, period=20)
    indicators['volume_ratio'] = vol_ratio
    indicators['volume_class'] = vol_class
    
    return indicators


def get_indicator_signal(indicator_name, value, sector_config):
    """
    Determine signal based on indicator value
    
    Args:
        indicator_name: Name of the indicator
        value: Current indicator value
        sector_config: Sector-specific configuration
    
    Returns:
        Tuple: (signal, emoji)
    """
    if value is None:
        return "N/A", "⚪"
    
    primary = sector_config.get('primary', 'Trend')
    
    # RSI signals
    if indicator_name == 'RSI':
        if value > 70:
            return "Overbought", "🔴"
        elif value < 30:
            return "Oversold", "🟢"
        else:
            return "Neutral", "⚪"
    
    # ADX signals
    elif indicator_name == 'ADX':
        if value > 25:
            return "Strong Trend", "🟢"
        elif value > 20:
            return "Moderate", "🟡"
        else:
            return "Weak", "🔴"
    
    # BB signals
    elif indicator_name == 'BB_Width':
        if value < 2:
            return "Squeeze", "🟡"
        elif value > 10:
            return "Expansion", "🟢"
        else:
            return "Normal", "⚪"
    
    elif indicator_name == 'BB_Position':
        if value > 80:
            return "Upper Band", "🔴"
        elif value < 20:
            return "Lower Band", "🟢"
        else:
            return "Middle", "⚪"
    
    # Stochastic signals
    elif indicator_name == 'Stochastic':
        if value > 80:
            return "Overbought", "🔴"
        elif value < 20:
            return "Oversold", "🟢"
        else:
            return "Neutral", "⚪"
    
    # ATR (volatility)
    elif indicator_name == 'ATR':
        return f"{value:.2f}", "⚪"
    
    # VWAP
    elif indicator_name == 'VWAP':
        return f"{value:.2f}", "⚪"
    
    # EMA/SMA
    elif indicator_name in ['EMA', 'SMA']:
        return f"{value:.2f}", "⚪"
    
    return "N/A", "⚪"


def create_indicator_table(sector_data_dict, n_sessions):
    """
    Create comprehensive indicator table for all sectors
    
    Args:
        sector_data_dict: Dictionary of sector dataframes
        n_sessions: Number of sessions for trend analysis
    
    Returns:
        DataFrame with all indicators
    """
    rows = []
    
    for sector, df in sector_data_dict.items():
        if not validate_data(df):
            continue
        
        indicators = calculate_sector_indicators(df)
        if indicators is None:
            continue
        
        sector_config = SECTOR_INDICATORS.get(sector, {'primary': 'Trend'})
        
        # Get signals
        rsi_signal, rsi_emoji = get_indicator_signal('RSI', indicators['rsi'], sector_config)
        adx_signal, adx_emoji = get_indicator_signal('ADX', indicators['adx'], sector_config)
        bb_width_signal, bb_width_emoji = get_indicator_signal('BB_Width', indicators['bb_width'], sector_config)
        bb_pos_signal, bb_pos_emoji = get_indicator_signal('BB_Position', indicators['bb_position'], sector_config)
        stoch_signal, stoch_emoji = get_indicator_signal('Stochastic', indicators['stoch'], sector_config)
        
        # Aggregate signal
        signals = [rsi_emoji, adx_emoji, bb_width_emoji, bb_pos_emoji, stoch_emoji]
        green_count = signals.count("🟢")
        red_count = signals.count("🔴")
        
        if green_count >= 3:
            aggregate_signal = "🟢 Bullish"
        elif red_count >= 3:
            aggregate_signal = "🔴 Bearish"
        elif green_count > red_count:
            aggregate_signal = "🟡 Bullish Bias"
        elif red_count > green_count:
            aggregate_signal = "🟠 Bearish Bias"
        else:
            aggregate_signal = "⚪ Neutral"
        
        row = {
            'Sector': sector,
            'Price': f"₹{indicators['price']:.2f}" if indicators['price'] else "N/A",
            'Change %': f"{indicators['change']:+.2f}%" if indicators['change'] else "N/A",
            'Primary': sector_config.get('primary', 'N/A'),
            'RSI': f"{rsi_emoji} {indicators['rsi']:.1f}" if indicators['rsi'] else "⚪ N/A",
            'ADX': f"{adx_emoji} {indicators['adx']:.1f}" if indicators['adx'] else "⚪ N/A",
            'BB Width': f"{bb_width_emoji} {indicators['bb_width']:.2f}" if indicators['bb_width'] else "⚪ N/A",
            'BB Pos': f"{bb_pos_emoji} {indicators['bb_position']:.0f}" if indicators['bb_position'] else "⚪ N/A",
            'Stoch': f"{stoch_emoji} {indicators['stoch']:.1f}" if indicators['stoch'] else "⚪ N/A",
            'Volume': indicators['volume_class'] if indicators['volume_class'] else "⚪ N/A",
            'Signal': aggregate_signal
        }
        
        rows.append(row)
    
    df_result = pd.DataFrame(rows)
    
    # Sort by Signal strength (Bullish first)
    signal_order = {"🟢 Bullish": 0, "🟡 Bullish Bias": 1, "⚪ Neutral": 2, "🟠 Bearish Bias": 3, "🔴 Bearish": 4}
    df_result['_sort'] = df_result['Signal'].map(signal_order)
    df_result = df_result.sort_values('_sort').drop('_sort', axis=1).reset_index(drop=True)
    
    return df_result


def create_trend_indicator_table(sector_data_dict, n_sessions):
    """
    Create Trend Indicator section table
    
    Args:
        sector_data_dict: Dictionary of sector dataframes
        n_sessions: Number of sessions for analysis
    
    Returns:
        DataFrame with trend analysis
    """
    trend_data = []
    
    for sector, df in sector_data_dict.items():
        if not validate_data(df):
            continue
        
        trend_info = calculate_trend_indicators(df, sector, n_sessions)
        
        if trend_info:
            trend_data.append(trend_info)
    
    if not trend_data:
        return None
    
    # Rank by trend strength
    ranked_data = rank_by_trend_strength(trend_data)
    
    # Create display dataframe
    display_rows = []
    for item in ranked_data:
        display_rows.append({
            'Rank': item['Rank'],
            'Sector': item['Sector'],
            'ADX': f"{item['ADX']:.1f}",
            'Norm ADX': f"{item['Norm_ADX']:.1f}",
            'ADX Trend': item['ADX_Trend'],
            'DI Spread': item['DI_Spread_Display'],
            'Trend': item['Trend'],
            'CMF': f"{item['CMF']:.3f}",
            'CMF Trend': item['CMF_Trend'],
            'Remark': item['Remark']
        })
    
    df_trend = pd.DataFrame(display_rows)
    return df_trend


def display_sector_details(sector_data_dict):
    """
    Display detailed analysis for selected sectors
    
    Args:
        sector_data_dict: Dictionary of sector dataframes
    """
    st.markdown("---")
    st.subheader("🔍 Detailed Sector Analysis")
    
    selected_sector = st.selectbox(
        "Select a sector for detailed analysis:",
        list(sector_data_dict.keys())
    )
    
    if selected_sector:
        df = sector_data_dict[selected_sector]
        indicators = calculate_sector_indicators(df)
        sector_config = SECTOR_INDICATORS.get(selected_sector, {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Current Price",
                f"₹{indicators['price']:.2f}" if indicators['price'] else "N/A",
                f"{indicators['change']:.2f}%" if indicators['change'] else "N/A"
            )
        
        with col2:
            st.metric(
                "Primary Strategy",
                sector_config.get('primary', 'N/A')
            )
        
        with col3:
            st.metric(
                "Chart Pattern",
                sector_config.get('chart_pattern', 'N/A')
            )
        
        # Indicator values
        st.markdown("#### 📊 Technical Indicators")
        
        ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)
        
        with ind_col1:
            st.markdown(f"**RSI (14):** {indicators['rsi']:.1f}" if indicators['rsi'] else "**RSI:** N/A")
            st.markdown(f"**ADX (14):** {indicators['adx']:.1f}" if indicators['adx'] else "**ADX:** N/A")
        
        with ind_col2:
            st.markdown(f"**BB Width:** {indicators['bb_width']:.2f}" if indicators['bb_width'] else "**BB Width:** N/A")
            st.markdown(f"**ATR (14):** {indicators['atr']:.2f}" if indicators['atr'] else "**ATR:** N/A")
        
        with ind_col3:
            st.markdown(f"**Stochastic:** {indicators['stoch']:.1f}" if indicators['stoch'] else "**Stochastic:** N/A")
            st.markdown(f"**VWAP:** {indicators['vwap']:.2f}" if indicators['vwap'] else "**VWAP:** N/A")
        
        with ind_col4:
            st.markdown(f"**EMA (20):** {indicators['ema']:.2f}" if indicators['ema'] else "**EMA:** N/A")
            st.markdown(f"**SMA (200):** {indicators['sma']:.2f}" if indicators['sma'] else "**SMA:** N/A")
        
        # Strategy logic
        st.markdown("#### 💡 Strategy Logic")
        st.info(f"**{sector_config.get('logic', 'Standard technical analysis approach')}**")
        
        # Recommended indicators
        if 'indicators' in sector_config:
            st.markdown("**Key Indicators:** " + ", ".join(sector_config['indicators']))


def sidebar_controls():
    """
    Create sidebar controls
    
    Returns:
        Dictionary with control values
    """
    st.sidebar.title("⚙️ Settings")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Data Configuration")
    
    period = st.sidebar.selectbox(
        "Data Period",
        ["3mo", "6mo", "1y", "2y"],
        index=1,
        help="Historical data period to analyze"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Trend Analysis")
    
    n_sessions = st.sidebar.slider(
        "Number of Sessions (N)",
        min_value=2,
        max_value=10,
        value=4,
        step=1,
        help="Number of recent sessions for trend indicator analysis"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Auto Refresh")
    
    auto_refresh = st.sidebar.checkbox(
        "Enable Hourly Auto-Refresh",
        value=True,
        help="Automatically refresh data every hour"
    )
    
    if auto_refresh:
        st.sidebar.info("⏱️ Data refreshes every 1 hour")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.markdown("""
    **Nifty Sectoral Scanner v5.3**
    
    Advanced sectoral rotation analysis with:
    - Real-time indicator tracking
    - Trend strength analysis
    - Multi-session momentum
    - Volume & money flow analysis
    
    *Data Source: Yahoo Finance*
    """)
    
    return {
        'period': period,
        'n_sessions': n_sessions,
        'auto_refresh': auto_refresh
    }


def main():
    """Main application logic"""
    
    # Display header
    display_header()
    
    # Sidebar controls
    controls = sidebar_controls()
    
    # Load data
    with st.spinner("📡 Loading market data..."):
        sector_data = load_sector_data(
            SECTORS,
            period=controls['period'],
            interval='1d'
        )
    
    if not sector_data:
        st.error("❌ Failed to load market data. Please try again later.")
        return
    
    st.success(f"✅ Loaded data for {len(sector_data)} sectors")
    
    # Display tabs
    tab1, tab2, tab3 = st.tabs(["📊 Indicator Overview", "📈 Trend Analysis", "🔍 Sector Details"])
    
    with tab1:
        st.subheader("📊 Comprehensive Indicator Matrix")
        st.markdown("*All sectors with primary strategy and key technical indicators*")
        
        df_indicators = create_indicator_table(sector_data, controls['n_sessions'])
        
        if df_indicators is not None and not df_indicators.empty:
            st.dataframe(
                df_indicators,
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            bullish = len(df_indicators[df_indicators['Signal'].str.contains('🟢')])
            bearish = len(df_indicators[df_indicators['Signal'].str.contains('🔴')])
            neutral = len(df_indicators[df_indicators['Signal'].str.contains('⚪')])
            
            with col1:
                st.metric("🟢 Bullish Sectors", bullish)
            with col2:
                st.metric("🔴 Bearish Sectors", bearish)
            with col3:
                st.metric("⚪ Neutral Sectors", neutral)
            with col4:
                st.metric("📊 Total Sectors", len(df_indicators))
        else:
            st.warning("⚠️ No indicator data available")
    
    with tab2:
        st.subheader("📈 Trend Indicator Analysis")
        st.markdown(f"*Trend strength and momentum over last **{controls['n_sessions']} sessions***")
        
        df_trend = create_trend_indicator_table(sector_data, controls['n_sessions'])
        
        if df_trend is not None and not df_trend.empty:
            st.dataframe(
                df_trend,
                use_container_width=True,
                hide_index=True,
                height=600
            )
            
            # Trend summary
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            
            strong_trends = len(df_trend[df_trend['Trend'] == 'Strong'])
            bullish_trends = len(df_trend[df_trend['Remark'].str.contains('🟢')])
            bearish_trends = len(df_trend[df_trend['Remark'].str.contains('🔴')])
            
            with summary_col1:
                st.metric("💪 Strong Trends", strong_trends)
            with summary_col2:
                st.metric("🟢 Bullish Trends", bullish_trends)
            with summary_col3:
                st.metric("🔴 Bearish Trends", bearish_trends)
            
            # Indicator explanations
            with st.expander("ℹ️ Understanding Trend Indicators"):
                st.markdown(f"""
                - **ADX**: {INDICATOR_EXPLANATIONS['ADX']}
                - **Norm ADX**: {INDICATOR_EXPLANATIONS['Norm_ADX']}
                - **ADX Trend**: {INDICATOR_EXPLANATIONS['ADX_Trend']}
                - **DI Spread**: {INDICATOR_EXPLANATIONS['DI_Spread']}
                - **CMF**: {INDICATOR_EXPLANATIONS['CMF']}
                - **CMF Trend**: {INDICATOR_EXPLANATIONS['CMF_Trend']}
                - **Remark**: {INDICATOR_EXPLANATIONS['Remark']}
                """)
        else:
            st.warning("⚠️ No trend data available")
    
    with tab3:
        display_sector_details(sector_data)
    
    # Auto-refresh logic
    if controls['auto_refresh']:
        time.sleep(3600)  # Sleep for 1 hour
        st.rerun()


if __name__ == "__main__":
    main()
