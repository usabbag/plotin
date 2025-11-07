import logging
import os
import argparse
import asyncio
from datetime import datetime, timezone
from config_manager import load_config
from data_retrieval import get_multiple_stocks_data
from technical_analysis import add_indicators, analyze_golden_cross_state
from chart_generation import generate_chart
from telegram_bot import create_telegram_manager
from scheduler import create_schedule_manager_from_config
from notifications import (
    load_signal_state,
    save_signal_state,
    get_previous_state,
    update_state,
    should_send_notification,
    build_signal_message,
    build_alignment_message,
    DEFAULT_STATE_FILENAME
)

POSITIVE_STATES = {'golden', 'near'}

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
    interval = config['interval']  # This will be used for 4h charts
    output_dir = config['output']['directory']
    chart_config = config['chart']
    notification_config = config.get('notifications', {})
    notifications_enabled = notification_config.get('enabled', False)
    near_cross_threshold = float(notification_config.get('near_cross_threshold_pct', 0.75))
    cooldown_hours = float(notification_config.get('cooldown_hours', 6))
    alignment_enabled = notification_config.get('alignment_enabled', True)
    state_file = notification_config.get('state_file') or os.path.join(output_dir, DEFAULT_STATE_FILENAME)
    
    signal_state = load_signal_state(state_file) if notifications_enabled else {}
    state_dirty = False
    
    logging.info(f"Analyzing {len(symbols)} stocks: {', '.join(symbols)}")
    
    # Initialize Telegram manager if needed
    telegram_manager = None
    if send_to_telegram:
        telegram_manager = create_telegram_manager(config)
        if not telegram_manager:
            logging.error("Failed to initialize Telegram manager. Charts and alerts won't be sent.")
            send_to_telegram = False
    
    if notifications_enabled and not send_to_telegram:
        logging.info("Notifications enabled but --send flag not provided. Alerts will be logged only.")
    
    # Retrieve stock data - for both daily and 4h intervals
    daily_stock_data = get_multiple_stocks_data(symbols, period_days, '1d')
    if not daily_stock_data:
        logging.error("Failed to retrieve any daily stock data.")
        return False
    
    hourly_stock_data = get_multiple_stocks_data(symbols, period_days, interval)
    if not hourly_stock_data:
        logging.error("Failed to retrieve any hourly stock data.")
        return False
    
    success_count = 0
    # Process each stock
    for symbol in symbols:
        logging.info(f"Processing {symbol}")
        timeframe_states = {}
        
        # Process daily data first
        if symbol in daily_stock_data:
            daily_data = daily_stock_data[symbol]
            
            # Add technical indicators
            daily_data_with_indicators = add_indicators(daily_data)
            if daily_data_with_indicators is not None:
                if notifications_enabled:
                    daily_signal = analyze_golden_cross_state(daily_data_with_indicators, near_cross_threshold)
                    if daily_signal:
                        timeframe_states['1d'] = daily_signal
                
                # Generate daily chart
                daily_chart_path = os.path.join(output_dir, f"{symbol}_1d_chart.png")
                daily_success = generate_chart(daily_data_with_indicators, symbol, output_dir, chart_config, interval='1d')
                if daily_success:
                    logging.info(f"Successfully generated daily chart for {symbol}")
                    
                    # Send to Telegram if requested
                    if send_to_telegram and telegram_manager:
                        logging.info(f"Sending {symbol} daily chart to Telegram")
                        await telegram_manager.send_stock_analysis(
                            symbol, 
                            daily_chart_path, 
                            f"Daily analysis for {symbol} using {period_days} days of data."
                        )
                else:
                    logging.error(f"Failed to generate daily chart for {symbol}")
            else:
                logging.error(f"Failed to add indicators for {symbol} daily data. Skipping.")
        else:
            logging.error(f"No daily data available for {symbol}. Skipping.")
            
        # Then process 4h data
        if symbol in hourly_stock_data:
            hourly_data = hourly_stock_data[symbol]
            
            # Add technical indicators
            hourly_data_with_indicators = add_indicators(hourly_data)
            if hourly_data_with_indicators is not None:
                if notifications_enabled:
                    hourly_signal = analyze_golden_cross_state(hourly_data_with_indicators, near_cross_threshold)
                    if hourly_signal:
                        timeframe_states['4h'] = hourly_signal
                
                # Generate 4h chart
                hourly_chart_path = os.path.join(output_dir, f"{symbol}_4h_chart.png")
                hourly_success = generate_chart(hourly_data_with_indicators, symbol, output_dir, chart_config, interval='4h')
                if hourly_success:
                    logging.info(f"Successfully generated 4h chart for {symbol}")
                    success_count += 1
                    
                    # Send to Telegram if requested
                    if send_to_telegram and telegram_manager:
                        logging.info(f"Sending {symbol} 4h chart to Telegram")
                        await telegram_manager.send_stock_analysis(
                            symbol, 
                            hourly_chart_path, 
                            f"4-hour analysis for {symbol} using {period_days} days of data."
                        )
                else:
                    logging.error(f"Failed to generate 4h chart for {symbol}")
            else:
                logging.error(f"Failed to add indicators for {symbol} 4h data. Skipping.")
        else:
            logging.error(f"No 4h data available for {symbol}. Skipping.")
        
        if notifications_enabled and timeframe_states:
            symbol_dirty = await handle_symbol_notifications(
                symbol=symbol,
                timeframe_states=timeframe_states,
                signal_state=signal_state,
                telegram_manager=telegram_manager if send_to_telegram else None,
                near_cross_threshold=near_cross_threshold,
                cooldown_hours=cooldown_hours,
                alignment_enabled=alignment_enabled
            )
            state_dirty = state_dirty or symbol_dirty
            
    if notifications_enabled and state_dirty:
        save_signal_state(signal_state, state_file)
    
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
        lambda: asyncio.run(scheduled_task(config))
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

async def handle_symbol_notifications(symbol, timeframe_states, signal_state, telegram_manager,
                                      near_cross_threshold, cooldown_hours, alignment_enabled):
    state_dirty = False
    sent_flags = {}
    
    for timeframe, state_info in timeframe_states.items():
        previous = get_previous_state(signal_state, symbol, timeframe)
        should_send = should_send_notification(previous, state_info, cooldown_hours)
        new_entry = dict(state_info)
        
        if should_send:
            message = build_signal_message(symbol, timeframe, state_info, near_cross_threshold)
            if telegram_manager:
                await telegram_manager.send_message(message)
            else:
                logging.info(f"[Notification] {message}")
            new_entry['last_notified_at'] = datetime.now(timezone.utc).isoformat()
        elif previous and previous.get('last_notified_at'):
            new_entry['last_notified_at'] = previous['last_notified_at']
        
        update_state(signal_state, symbol, timeframe, new_entry)
        sent_flags[timeframe] = should_send
        state_dirty = True
    
    if alignment_enabled:
        fast_state = timeframe_states.get('4h')
        slow_state = timeframe_states.get('1d')
        if fast_state and slow_state:
            fast_positive = fast_state.get('state') in POSITIVE_STATES
            slow_positive = slow_state.get('state') in POSITIVE_STATES
            if fast_positive and slow_positive and sent_flags.get('4h'):
                alignment_record = {
                    'state': 'alignment',
                    'timestamp': fast_state.get('timestamp'),
                    'fast_state': fast_state.get('state'),
                    'slow_state': slow_state.get('state'),
                    'is_fresh_cross': fast_state.get('is_fresh_cross', False)
                }
                previous_alignment = get_previous_state(signal_state, symbol, 'alignment')
                send_alignment = should_send_notification(previous_alignment, alignment_record, cooldown_hours)
                
                if send_alignment:
                    message = build_alignment_message(symbol, '4h', fast_state, '1d', slow_state)
                    if telegram_manager:
                        await telegram_manager.send_message(message)
                    else:
                        logging.info(f"[Notification] {message}")
                    alignment_record['last_notified_at'] = datetime.now(timezone.utc).isoformat()
                elif previous_alignment and previous_alignment.get('last_notified_at'):
                    alignment_record['last_notified_at'] = previous_alignment['last_notified_at']
                
                update_state(signal_state, symbol, 'alignment', alignment_record)
                state_dirty = True
    
    return state_dirty

if __name__ == "__main__":
    main() 
