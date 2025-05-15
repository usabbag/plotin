import logging
import os
import argparse
import time
import asyncio
from config_manager import load_config
from data_retrieval import get_multiple_stocks_data
from technical_analysis import add_indicators
from chart_generation import generate_chart
from telegram_bot import create_telegram_manager
from scheduler import create_schedule_manager_from_config

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("plotin.log"),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting Stock Analysis Tool")

async def process_stocks(config, send_to_telegram=False):
    """
    Process stocks according to configuration.
    
    Args:
        config (dict): Configuration dictionary
        send_to_telegram (bool): Whether to send results to Telegram
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Extract configuration values
    symbols = config['stocks']
    period_days = config['time_period']
    interval = config['interval']
    output_dir = config['output']['directory']
    chart_config = config['chart']
    
    logging.info(f"Analyzing {len(symbols)} stocks: {', '.join(symbols)}")
    
    # Initialize Telegram manager if needed
    telegram_manager = None
    if send_to_telegram:
        telegram_manager = create_telegram_manager(config)
        if not telegram_manager:
            logging.error("Failed to initialize Telegram manager. Charts won't be sent.")
            send_to_telegram = False
    
    # Retrieve stock data
    stock_data = get_multiple_stocks_data(symbols, period_days, interval)
    if not stock_data:
        logging.error("Failed to retrieve any stock data. Exiting.")
        return False
    
    success_count = 0
    # Process each stock
    for symbol, data in stock_data.items():
        logging.info(f"Processing {symbol}")
        
        # Add technical indicators
        data_with_indicators = add_indicators(data)
        if data_with_indicators is None:
            logging.error(f"Failed to add indicators for {symbol}. Skipping.")
            continue
            
        # Generate chart
        chart_path = os.path.join(output_dir, f"{symbol}_chart.png")
        success = generate_chart(data_with_indicators, symbol, output_dir, chart_config)
        if success:
            logging.info(f"Successfully generated chart for {symbol}")
            success_count += 1
            
            # Send to Telegram if requested
            if send_to_telegram and telegram_manager:
                logging.info(f"Sending {symbol} chart to Telegram")
                await telegram_manager.send_stock_analysis(
                    symbol, 
                    chart_path, 
                    f"Analysis for {symbol} using {period_days} days of data with {interval} interval."
                )
        else:
            logging.error(f"Failed to generate chart for {symbol}")
    
    if success_count > 0:
        logging.info(f"Successfully processed {success_count} out of {len(symbols)} stocks")
        return True
    else:
        logging.error("Failed to process any stocks")
        return False

async def scheduled_task(config):
    """
    Function to be called by the scheduler.
    
    Args:
        config (dict): Configuration dictionary
    """
    logging.info("Running scheduled stock analysis task")
    await process_stocks(config, send_to_telegram=True)

def main():
    """
    Main function to run the stock analysis tool.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Stock Analysis Tool')
    parser.add_argument('--schedule', action='store_true', help='Run in scheduled mode')
    parser.add_argument('--send', action='store_true', help='Send results to Telegram')
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Load configuration
    config = load_config()
    if not config:
        logging.error("Failed to load configuration. Exiting.")
        return
    
    if args.schedule:
        # Run in scheduled mode
        logging.info("Starting in scheduled mode")
        
        # Create schedule manager and run scheduled tasks
        asyncio.run(run_scheduled_mode(config, args.send))
    else:
        # Run once
        asyncio.run(process_stocks(config, send_to_telegram=args.send))
    
    logging.info("Stock analysis completed")

async def run_scheduled_mode(config, run_initial=False):
    """
    Run the bot in scheduled mode.
    
    Args:
        config (dict): Configuration dictionary
        run_initial (bool): Whether to run an initial analysis immediately
    """
    # Create schedule manager
    schedule_manager = create_schedule_manager_from_config(
        config, 
        lambda: asyncio.create_task(scheduled_task(config))
    )
    
    try:
        # Run a test task immediately if requested
        if run_initial:
            logging.info("Running initial analysis and sending to Telegram")
            await process_stocks(config, send_to_telegram=True)
        
        # Keep the main thread alive while scheduler runs in background
        logging.info("Scheduler is running. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Received exit signal. Shutting down...")
        schedule_manager.shutdown()

if __name__ == "__main__":
    main() 