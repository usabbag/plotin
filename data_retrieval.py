import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_stock_data(symbol, period_days=30, interval='4h'):
    """
    Retrieve historical stock data using yfinance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        period_days (int): Number of days of historical data to retrieve
        interval (str): Data interval (e.g., '4h' for 4-hour intervals)
        
    Returns:
        pandas.DataFrame: Historical stock data or None if retrieval fails
    """
    try:
        # Calculate start and end dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Add extra days to ensure we have enough data for indicators
        # For daily charts: need at least 128 days of history for the 128 SMA
        # For 4h charts: need at least 128 periods (roughly 21 days, but add extra for weekends/gaps)
        if interval == '1d':
            # For daily data, ensure we have at least 200 days of history (128 + buffer)
            buffer_days = 200  
        else:
            # For 4h data, add 150 days buffer (was already working well)
            buffer_days = 150
            
        buffer_start_date = start_date - timedelta(days=buffer_days)
        
        logging.info(f"Retrieving {interval} data for {symbol} from {buffer_start_date.date()} to {end_date.date()}")
        
        # Download data
        data = yf.download(
            symbol,
            start=buffer_start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        
        if data.empty:
            logging.error(f"No data found for {symbol}")
            return None
            
        logging.info(f"Successfully retrieved {len(data)} data points for {symbol}")
        return data
        
    except Exception as e:
        logging.error(f"Error retrieving data for {symbol}: {str(e)}")
        return None


def get_multiple_stocks_data(symbols, period_days=30, interval='4h'):
    """
    Retrieve data for multiple stock symbols.
    
    Args:
        symbols (list): List of stock symbols
        period_days (int): Number of days of historical data to retrieve
        interval (str): Data interval
        
    Returns:
        dict: Dictionary mapping symbols to their respective data frames
    """
    stock_data = {}
    
    for symbol in symbols:
        data = get_stock_data(symbol, period_days, interval)
        if data is not None:
            stock_data[symbol] = data
    
    return stock_data 