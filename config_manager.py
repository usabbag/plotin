import yaml
import logging
import os

def load_config(config_file='config.yaml'):
    """
    Load configuration from YAML file, with fallback to template and environment overrides.
    """
    try:
        # Try to load config.yaml first (local development)
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
        # If config.yaml doesn't exist, try template (Railway deployment)
        elif os.path.exists('config.yaml.template'):
            logging.info("config.yaml not found, using config.yaml.template")
            with open('config.yaml.template', 'r') as file:
                config = yaml.safe_load(file)
        else:
            logging.error("Neither config.yaml nor config.yaml.template found")
            return None
        
        # Override with environment variables if they exist (for Railway)
        # Log available environment variables for debugging
        logging.info("Checking for environment variable overrides...")
        
        if os.getenv('STOCKS'):
            stocks_env = os.getenv('STOCKS')
            # Convert comma-separated string to list
            config['stocks'] = [stock.strip() for stock in stocks_env.split(',')]
            logging.info(f"Overriding stocks from environment: {config['stocks']}")
        else:
            logging.info("No STOCKS environment variable found")
            
        # Ensure telegram section exists before trying to update it
        if 'telegram' not in config:
            config['telegram'] = {}
            
        if os.getenv('TELEGRAM_TOKEN'):
            config['telegram']['token'] = os.getenv('TELEGRAM_TOKEN')
            logging.info("Telegram token loaded from environment variable")
        else:
            logging.warning("No TELEGRAM_TOKEN environment variable found")
            
        if os.getenv('TELEGRAM_CHAT_ID'):
            config['telegram']['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
            logging.info(f"Telegram chat ID loaded from environment: {config['telegram']['chat_id']}")
        else:
            logging.warning("No TELEGRAM_CHAT_ID environment variable found")
            
        # Check if Telegram values are still placeholders after env override attempt
        if config.get('telegram', {}).get('token') in ['YOUR_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE', None, '']:
            logging.warning("Telegram token is not configured properly (still has placeholder value)")
            if 'telegram' in config:
                config['telegram']['token'] = None
                
        if config.get('telegram', {}).get('chat_id') in ['YOUR_CHAT_ID', 'YOUR_CHAT_ID_HERE', None, '']:
            logging.warning("Telegram chat ID is not configured properly (still has placeholder value)")
            if 'telegram' in config:
                config['telegram']['chat_id'] = None
        
        validate_config(config)
        return config
        
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        return None
        
def validate_config(config):
    """
    Validate configuration and set defaults if needed.
    
    Args:
        config (dict): Configuration dictionary
    """
    # Ensure required sections exist
    if 'stocks' not in config:
        logging.warning("No stocks defined in config. Using default: AAPL")
        config['stocks'] = ['AAPL']
        
    if 'time_period' not in config:
        logging.warning("No time period defined in config. Using default: 30 days")
        config['time_period'] = 30
        
    if 'interval' not in config:
        logging.warning("No interval defined in config. Using default: 4h")
        config['interval'] = '4h'
        
    if 'output' not in config:
        logging.warning("No output directory defined in config. Using default: ./output")
        config['output'] = {'directory': './output'}
    elif 'directory' not in config['output']:
        config['output']['directory'] = './output'
        
    # Ensure chart config exists with defaults
    if 'chart' not in config:
        config['chart'] = {}
        
    chart_defaults = {
        'up_color': 'green',
        'down_color': 'red',
        'sma_50_color': 'blue',
        'sma_128_color': 'orange'
    }
    
    for key, default_value in chart_defaults.items():
        if key not in config['chart']:
            config['chart'][key] = default_value
    
    if 'notifications' not in config:
        config['notifications'] = {}
    
    notifications_defaults = {
        'enabled': True,
        'near_cross_threshold_pct': 0.75,
        'cooldown_hours': 6,
        'alignment_enabled': True
    }
    
    for key, default_value in notifications_defaults.items():
        if key not in config['notifications']:
            config['notifications'][key] = default_value
    
    if not config['notifications'].get('state_file'):
        output_dir = config['output']['directory']
        config['notifications']['state_file'] = os.path.join(output_dir, 'signal_state.json')
