import mplfinance as mpf
import pandas as pd
import numpy as np
import os
import logging

def generate_chart(data, symbol, output_dir, chart_config=None, interval='4h'):
    """
    Generate a candlestick chart with technical indicators for a stock.
    
    Args:
        data (pandas.DataFrame): Stock data with indicators
        symbol (str): Stock symbol
        output_dir (str): Directory to save the chart
        chart_config (dict): Chart configuration
        interval (str): Data interval ('4h' or '1d')
        
    Returns:
        bool: True if successful, False otherwise
    """
    if chart_config is None:
        chart_config = {
            'up_color': 'green',
            'down_color': 'red',
            'sma_50_color': 'blue',
            'sma_128_color': 'orange'
        }
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define file path (include interval in filename)
        filepath = os.path.join(output_dir, f"{symbol}_{interval}_chart.png")
        
        # Debug info
        logging.info(f"Data shape: {data.shape}")
        logging.info(f"Index type: {type(data.index)}")
        
        # Convert index to datetime if not already
        if not isinstance(data.index, pd.DatetimeIndex):
            logging.info("Converting index to DatetimeIndex")
            data.index = pd.to_datetime(data.index)
        
        # Create a new DataFrame with explicitly converted types to avoid mplfinance issues
        new_data = pd.DataFrame(index=data.index)
        new_data['Open'] = data['Open'].astype(np.float64)
        new_data['High'] = data['High'].astype(np.float64)
        new_data['Low'] = data['Low'].astype(np.float64)
        new_data['Close'] = data['Close'].astype(np.float64)
        new_data['Volume'] = data['Volume'].astype(np.float64)
        new_data['SMA50'] = data['SMA50'].astype(np.float64)
        new_data['SMA128'] = data['SMA128'].astype(np.float64)
        
        # Filter to visualize appropriate number of periods based on interval
        if interval == '1d':
            last_n_rows = min(30, len(new_data))  # 30 daily candles
            background_color = '#262626'  # Slightly lighter background for daily charts
            title_suffix = 'Daily Chart with SMAs'
        else:  # 4h interval
            last_n_rows = min(30 * 6, len(new_data))  # 6 4-hour candles per day
            background_color = '#1f1f1f'  # Darker background for 4h charts
            title_suffix = '4-Hour Chart with SMAs'
            
        data_to_plot = new_data.iloc[-last_n_rows:].copy()
        
        logging.info(f"Plot data shape: {data_to_plot.shape}")
        
        # Set colors
        mc = mpf.make_marketcolors(
            up=chart_config['up_color'],
            down=chart_config['down_color'],
            edge='inherit',
            wick='inherit',
            volume='inherit'
        )
        
        # Set style with dark background - adjusted based on interval
        s = mpf.make_mpf_style(
            marketcolors=mc,
            figcolor=background_color,    # Background varies by interval
            facecolor='#2d2d2d',          # Dark plot area background
            edgecolor='#444444',          # Edge color
            gridcolor='#444444',          # Grid lines
            gridstyle=':',                # Dotted grid
            y_on_right=True,              # Price axis on right side
            rc={'axes.labelcolor': 'white', 
                'axes.edgecolor': 'white',
                'xtick.color': 'white',
                'ytick.color': 'white',
                'text.color': 'white'}
        )
        
        # Adjust line width based on interval
        line_width = 2.0 if interval == '1d' else 2.5
        
        # Plot additional indicators
        sma_50 = mpf.make_addplot(data_to_plot['SMA50'], color=chart_config['sma_50_color'], width=line_width)
        sma_128 = mpf.make_addplot(data_to_plot['SMA128'], color=chart_config['sma_128_color'], width=line_width)
        
        # Create the plot
        mpf.plot(
            data_to_plot,
            type='candle',
            style=s,
            title=f'{symbol} - {title_suffix}',
            addplot=[sma_50, sma_128],
            savefig=filepath,
            figsize=(12, 8)
        )
        
        logging.info(f"{interval} chart generated successfully for {symbol}. Saved to {filepath}")
        return True
        
    except Exception as e:
        logging.error(f"Error generating {interval} chart for {symbol}: {str(e)}")
        for col in ['Open', 'High', 'Low', 'Close']:
            if col in data.columns:
                non_float = [x for x in data[col] if not isinstance(x, (float, int))]
                if non_float:
                    logging.error(f"Non-numeric values in {col}: {non_float[:5]}")
        return False 