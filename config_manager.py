import yaml
import logging
import os

def load_config(config_file='config.yaml'):
    """
    Load configuration from YAML file.
    
    Args:
        config_file (str): Path to config file
        
    Returns:
        dict: Configuration dictionary or None if loading fails
    """
    try:
        if not os.path.exists(config_file):
            logging.error(f"Config file not found: {config_file}")
            return None
            
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
            
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