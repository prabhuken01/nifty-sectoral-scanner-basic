"""
Trend Analysis Module
Functions for analyzing trend indicators over N sessions
"""

import pandas as pd
import numpy as np
from indicators import calculate_adx_series, calculate_cmf


def calculate_trend_indicators(df, sector_name, n_sessions=4):
    """
    Calculate trend indicators over last N sessions
    
    Args:
        df: DataFrame with OHLCV data
        sector_name: Name of the sector
        n_sessions: Number of sessions to analyze (default: 4)
    
    Returns:
        Dictionary with trend analysis results
    """
    if len(df) < n_sessions + 20:  # Need buffer for indicator calculation
        return None
    
    try:
        # Calculate ADX series
        adx_series, plus_di_series, minus_di_series = calculate_adx_series(df, period=14)
        
        if adx_series is None:
            return None
        
        # Get last N sessions
        recent_adx = adx_series.tail(n_sessions)
        recent_plus_di = plus_di_series.tail(n_sessions)
        recent_minus_di = minus_di_series.tail(n_sessions)
        
        # Current values
        current_adx = recent_adx.iloc[-1]
        current_plus_di = recent_plus_di.iloc[-1]
        current_minus_di = recent_minus_di.iloc[-1]
        
        # Normalized ADX (0-100 scale using min-max scaling over N sessions)
        adx_min = recent_adx.min()
        adx_max = recent_adx.max()
        norm_adx = ((current_adx - adx_min) / (adx_max - adx_min) * 100) if adx_max > adx_min else 50.0
        
        # ADX Trend (Increasing/Weakening/Flat)
        adx_trend_value = recent_adx.iloc[-1] - recent_adx.iloc[0]
        if adx_trend_value > 2:
            adx_trend_emoji = "🟢"
            adx_trend_text = "Increasing"
        elif adx_trend_value < -2:
            adx_trend_emoji = "🔴"
            adx_trend_text = "Weakening"
        else:
            adx_trend_emoji = "⚪"
            adx_trend_text = "Flat"
        
        # DI Spread (SIGNED: positive if +DI > -DI, negative if +DI < -DI)
        di_spread = current_plus_di - current_minus_di
        
        # Emoji based on spread magnitude and direction
        if di_spread > 20:
            di_emoji = "🟢"  # Strong bullish
        elif di_spread > 10:
            di_emoji = "🟡"  # Moderate bullish
        elif di_spread > 0:
            di_emoji = "⚪"  # Weak bullish
        elif di_spread > -10:
            di_emoji = "⚪"  # Weak bearish
        elif di_spread > -20:
            di_emoji = "🟠"  # Moderate bearish
        else:
            di_emoji = "🔴"  # Strong bearish
        
        # Trend Strength based on ADX
        if current_adx > 25:
            trend_strength = "Strong"
        elif current_adx > 20:
            trend_strength = "Moderate"
        else:
            trend_strength = "Weak"
        
        # CMF Calculation (21-period)
        cmf_value = calculate_cmf(df, period=21)
        
        if cmf_value is not None:
            # CMF Trend (check last N sessions)
            cmf_series = []
            for i in range(n_sessions):
                temp_df = df.iloc[:-(n_sessions-i-1)] if i < n_sessions-1 else df
                cmf = calculate_cmf(temp_df, period=21)
                if cmf:
                    cmf_series.append(cmf)
            
            if len(cmf_series) >= 2:
                cmf_trend_value = cmf_series[-1] - cmf_series[0]
                if cmf_trend_value > 0.05:
                    cmf_trend_emoji = "🟢"
                    cmf_trend_text = "Accumulation"
                elif cmf_trend_value < -0.05:
                    cmf_trend_emoji = "🔴"
                    cmf_trend_text = "Distribution"
                else:
                    cmf_trend_emoji = "⚪"
                    cmf_trend_text = "Flat"
            else:
                cmf_trend_emoji = "⚪"
                cmf_trend_text = "N/A"
        else:
            cmf_value = 0.0
            cmf_trend_emoji = "⚪"
            cmf_trend_text = "N/A"
        
        # Generate Remark (based on combined signals - MAJORITY VOTING)
        bullish_signals = 0
        bearish_signals = 0
        
        # Signal 1: ADX trend
        if adx_trend_text == "Increasing":
            bullish_signals += 1
        elif adx_trend_text == "Weakening":
            bearish_signals += 1
        
        # Signal 2: DI spread direction
        if di_spread > 0:
            bullish_signals += 1
        elif di_spread < 0:
            bearish_signals += 1
        
        # Signal 3: CMF trend
        if cmf_trend_text == "Accumulation":
            bullish_signals += 1
        elif cmf_trend_text == "Distribution":
            bearish_signals += 1
        
        # Determine overall remark (Majority voting logic)
        if bullish_signals >= 2 and bearish_signals == 0:
            remark = "🟢 Bullish"
        elif bearish_signals >= 2 and bullish_signals == 0:
            remark = "🔴 Bearish"
        elif bullish_signals > bearish_signals:
            remark = "🟡 Bullish Bias"
        elif bearish_signals > bullish_signals:
            remark = "🟠 Bearish Bias"
        else:
            remark = "⚪ Sideway"
        
        return {
            'Sector': sector_name,
            'ADX': current_adx,
            'Norm_ADX': norm_adx,
            'ADX_Trend': f"{adx_trend_emoji} {adx_trend_text}",
            'DI_Spread': di_spread,  # Raw signed value for ranking
            'DI_Spread_Display': f"{di_emoji} {di_spread:+.1f}",  # For display with emoji and +/- sign
            'Trend': trend_strength,
            'CMF': cmf_value,
            'CMF_Trend': f"{cmf_trend_emoji} {cmf_trend_text}",
            'Remark': remark
        }
        
    except Exception as e:
        print(f"Error calculating trend for {sector_name}: {str(e)}")
        return None


def rank_by_trend_strength(trend_data):
    """
    Rank sectors by trend strength
    
    Args:
        trend_data: List of trend indicator dictionaries
    
    Returns:
        List of ranked dictionaries
    """
    if not trend_data:
        return []
    
    # Create scoring system
    for item in trend_data:
        score = 0
        
        # ADX contribution (0-40 points)
        # Higher ADX = stronger trend regardless of direction
        score += min(item['ADX'], 40)
        
        # Normalized ADX contribution (0-30 points)
        # Shows relative strength within recent sessions
        score += item['Norm_ADX'] * 0.3
        
        # DI Spread absolute magnitude contribution (0-20 points)
        # Larger spread = clearer directional bias
        score += min(abs(item['DI_Spread']), 20)
        
        # CMF absolute value contribution (0-10 points)
        # Stronger money flow = more conviction
        score += min(abs(item['CMF']) * 100, 10)
        
        item['_score'] = score
    
    # Sort by score (descending) - Highest score = strongest trend
    ranked = sorted(trend_data, key=lambda x: x['_score'], reverse=True)
    
    # Add rank and remove internal score
    for i, item in enumerate(ranked, 1):
        item['Rank'] = i
        del item['_score']
    
    return ranked


def get_trend_summary(trend_data):
    """
    Get summary statistics of trend analysis
    
    Args:
        trend_data: List of trend indicator dictionaries
    
    Returns:
        Dictionary with summary stats
    """
    if not trend_data:
        return None
    
    bullish_count = sum(1 for item in trend_data if '🟢' in item['Remark'])
    bearish_count = sum(1 for item in trend_data if '🔴' in item['Remark'])
    neutral_count = sum(1 for item in trend_data if '⚪' in item['Remark'])
    
    avg_adx = np.mean([item['ADX'] for item in trend_data])
    avg_di_spread = np.mean([item['DI_Spread'] for item in trend_data])
    avg_cmf = np.mean([item['CMF'] for item in trend_data])
    
    strong_trends = sum(1 for item in trend_data if item['Trend'] == 'Strong')
    
    return {
        'total_sectors': len(trend_data),
        'bullish_count': bullish_count,
        'bearish_count': bearish_count,
        'neutral_count': neutral_count,
        'strong_trends': strong_trends,
        'avg_adx': avg_adx,
        'avg_di_spread': avg_di_spread,
        'avg_cmf': avg_cmf
    }


def filter_by_trend_strength(trend_data, min_adx=20):
    """
    Filter sectors by minimum ADX threshold
    
    Args:
        trend_data: List of trend indicator dictionaries
        min_adx: Minimum ADX value (default: 20)
    
    Returns:
        Filtered list of dictionaries
    """
    if not trend_data:
        return []
    
    return [item for item in trend_data if item['ADX'] >= min_adx]


def filter_by_remark(trend_data, remark_type='Bullish'):
    """
    Filter sectors by remark type
    
    Args:
        trend_data: List of trend indicator dictionaries
        remark_type: Type of remark to filter ('Bullish', 'Bearish', 'Sideway')
    
    Returns:
        Filtered list of dictionaries
    """
    if not trend_data:
        return []
    
    return [item for item in trend_data if remark_type in item['Remark']]
