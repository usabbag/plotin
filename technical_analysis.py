import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any

def calculate_sma(data, period):
    """
    Calculate Simple Moving Average (SMA) for the given period.
    
    Args:
        data (pandas.DataFrame): Stock price data
        period (int): SMA period
        
    Returns:
        pandas.Series: SMA values
    """
    try:
        sma = data['Close'].rolling(window=period).mean()
        return sma
    except Exception as e:
        logging.error(f"Error calculating {period}-period SMA: {str(e)}")
        return None

def add_indicators(data):
    """
    Add technical indicators to stock data.
    
    Args:
        data (pandas.DataFrame): Stock price data
        
    Returns:
        pandas.DataFrame: Data with technical indicators added
    """
    if len(data) < 128:
        logging.warning(f"Insufficient data for 128-period SMA. Data length: {len(data)}, need at least 128 data points.")
        return None
    
    try:
        # Create a copy of the dataframe to avoid warnings
        data_copy = data.copy()
        
        # Ensure OHLC columns are float
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data_copy.columns:
                data_copy[col] = data_copy[col].astype(float)
        
        # Add 50-period SMA
        data_copy['SMA50'] = calculate_sma(data_copy, 50)
        
        # Add 128-period SMA
        data_copy['SMA128'] = calculate_sma(data_copy, 128)
        
        # Remove rows with NaN indicator values (due to rolling window)
        data_with_indicators = data_copy.dropna()
        
        logging.info(f"Successfully added indicators. Data reduced from {len(data)} to {len(data_with_indicators)} valid rows")
        
        return data_with_indicators
    except Exception as e:
        logging.error(f"Error adding indicators: {str(e)}")
        return None

def analyze_golden_cross_state(data: pd.DataFrame, near_cross_threshold_pct: float = 0.75) -> Optional[Dict[str, Any]]:
    """
    Inspect the latest candles and classify the SMA 50/128 relationship.
    
    Returns:
        dict with keys:
            - state: 'golden', 'near', or 'neutral'
            - is_fresh_cross: bool
            - spread_pct: float
            - close: float
            - sma50: float
            - sma128: float
            - sma128_slope: 'rising' | 'falling' | 'flat'
            - timestamp: ISO formatted string of the latest candle
    """
    if data is None or len(data) < 2:
        logging.warning("Not enough data to analyze golden cross state.")
        return None
    
    latest = data.iloc[-1]
    previous = data.iloc[-2]
    
    try:
        sma50 = float(latest['SMA50'])
        sma128 = float(latest['SMA128'])
        prev_sma50 = float(previous['SMA50'])
        prev_sma128 = float(previous['SMA128'])
        close_price = float(latest['Close'])
    except KeyError as e:
        logging.error(f"Missing required SMA column while analyzing golden cross: {e}")
        return None
    
    spread_pct = abs(sma50 - sma128) / sma128 * 100 if sma128 else float('inf')
    sma128_slope = 'rising' if sma128 > prev_sma128 else 'falling' if sma128 < prev_sma128 else 'flat'
    
    is_fresh_cross = sma50 >= sma128 and prev_sma50 < prev_sma128
    state = 'golden' if sma50 >= sma128 else 'neutral'
    
    # Treat tight spreads as near-cross signals when still below but converging upward
    if state != 'golden' and spread_pct <= near_cross_threshold_pct and sma50 >= prev_sma50:
        state = 'near'
    
    result = {
        'state': state,
        'is_fresh_cross': bool(is_fresh_cross),
        'spread_pct': spread_pct,
        'close': close_price,
        'sma50': sma50,
        'sma128': sma128,
        'sma128_slope': sma128_slope,
        'timestamp': latest.name.isoformat() if hasattr(latest.name, 'isoformat') else str(latest.name)
    }
    
    return result
