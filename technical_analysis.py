import pandas as pd
import numpy as np
import logging

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
        logging.warning(f"Insufficient data for 128-period SMA. Data length: {len(data)}")
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