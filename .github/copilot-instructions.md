# Nifty Sectoral Scanner - AI Agent Instructions

## Project Overview
Real-time sectoral rotation analysis tool for Indian Nifty indices. Multi-sector technical analysis using RSI-based ranking, trend indicators (ADX/DI), and volatility metrics. Streamlit-based dashboard fetching live data via yfinance.

## Architecture

### Core Data Flow
**yfinance → data_loader.py → indicators.py + trend_analysis.py → app.py (Streamlit UI)**

- **config.py**: 19 sector mappings (NIFTY 50, BANK, PHARMA, etc.) + sector-specific indicator configurations + indicator parameters/explanations
- **data_loader.py**: Downloads 6-month OHLCV data, validates required columns, handles multi-index flattening from yfinance
- **indicators.py**: ~10 technical indicators (RSI, BB, ADX, ATR, Stochastic, VWAP, SMA, EMA) - returns scalar values for dashboard
- **trend_analysis.py**: ADX trend analysis over N sessions (default: 4), DI spread calculation, CMF (Chaikin Money Flow), majority-vote signal aggregation
- **utils.py**: Formatting (percentage/currency with Indian numbering), emoji-based signal display, momentum classification
- **app.py**: Streamlit dashboard with sector ranking, detailed tabs, tooltips from INDICATOR_EXPLANATIONS

### Key Design Patterns

1. **Sector-Specific Configurations**: Each sector has `primary` trend type + custom indicators (SECTOR_INDICATORS in config.py)
   - Financial Services: Volatility-focused (BB, ATR)
   - PSU/Private Banks: Trend-focused (ADX, EMA)
   - Auto: Momentum-focused (RSI, Volume)
   
2. **Indicator Abstraction**: `calculate_*()` functions return either scalar (latest bar) or series (multi-bar analysis)
   - Single values: ADX, ATR, RSI - used for quick ranking
   - Series: ADX series for trend_analysis.py to compute momentum over 4 sessions

3. **Signal Aggregation**: 3-metric voting (ADX trend + DI direction + CMF trend) → final signal emoji + remark (trend_analysis.py)

4. **Caching Strategy**: `@st.cache_data(ttl=3600)` on data loading (1-hour TTL) and indicator calculations to optimize live updates

## Critical Developer Workflows

### Running the Application
```bash
pip install -r requirements.txt
streamlit run app.py
```
Runs on `http://localhost:8501` with auto-reload on file changes.

### Adding a New Sector
1. Add ticker mapping to `SECTORS` dict in config.py
2. (Optional) Define sector-specific config in `SECTOR_INDICATORS` with primary trend type
3. Indicators auto-calculate via `calculate_sector_indicators()` - no code changes needed

### Adding a New Indicator
1. Implement `calculate_<indicator>()` in indicators.py (return scalar or series)
2. Call it in `calculate_sector_indicators()` and store in `indicators` dict
3. Add tooltip to `INDICATOR_EXPLANATIONS` in config.py
4. Reference in app.py UI tabs if needed

### Debugging Data Issues
- `validate_data()` checks: ≥50 rows, required OHLCV columns, no NaN
- yfinance multi-index: handled by `df.columns.get_level_values(0)` in load_sector_data()
- Failed sectors logged to terminal + shown as warning toast in Streamlit

## Code Conventions

- **Type hints**: Minimal usage (legacy codebase); focus on docstrings with Args/Returns
- **Error handling**: Try-catch with silent failure (append to `failed_sectors`), user notification via st.warning()
- **Data validation**: Upstream in data_loader.py; later functions assume valid data
- **Naming**: Descriptive (e.g., `calculate_adx_series()`, `norm_adx`, `di_spread`)
- **Constants**: All in config.py (INDICATOR_PARAMS, APP_CONFIG, SECTORS)

## Common Modifications

### Changing Indicator Parameters
Edit `INDICATOR_PARAMS` in config.py (e.g., RSI period, BB std dev). Cached results expire after 1 hour.

### Adjusting ADX Trend Detection Threshold
In trend_analysis.py, `calculate_trend_indicators()`: change `if adx_trend_value > 2` threshold (currently ±2 for "Increasing"/"Weakening").

### Adding New Sector Signal Logic
Extend trend_analysis.py voting logic or modify `rank_by_trend_strength()` scoring formula.

## External Dependencies
- **yfinance**: Live OHLCV data for NSE indices
- **Streamlit**: UI framework with caching, tooltips, multi-column layout
- **pandas**: Data manipulation (resample, rolling, diff)
- **ta**: Technical analysis library (rarely used; most indicators implemented manually)
- **plotly**: Interactive charts (for future enhancement)

## Notes for AI Agents
- Sector data is time-indexed (dates in index), not column-based - use `.iloc[]` for position, `.loc[]` for date ranges
- ADX normalization uses min-max over 4 sessions, not 0-100 scale - check edge cases with short series
- Trend emojis (🟢/🟡/🟠/🔴) based on thresholds; validate logic in utils.py `get_signal_emoji()`
- Cache invalidation: Streamlit re-runs entire script on file change; monitor for stale indicator values
