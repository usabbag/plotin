#!/usr/bin/env python3
"""
Test script to verify configuration loading, especially with environment variables.
Run this to check if your Railway environment variables are being loaded correctly.
"""

import os
import sys
from config_manager import load_config

def test_config():
    print("=== Configuration Test ===\n")
    
    # Show current environment variables
    print("Environment Variables:")
    print(f"STOCKS: {os.getenv('STOCKS', 'NOT SET')}")
    print(f"TELEGRAM_TOKEN: {'SET' if os.getenv('TELEGRAM_TOKEN') else 'NOT SET'}")
    print(f"TELEGRAM_CHAT_ID: {os.getenv('TELEGRAM_CHAT_ID', 'NOT SET')}")
    print()
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    
    if not config:
        print("ERROR: Failed to load configuration!")
        return False
    
    print("\nLoaded Configuration:")
    print(f"Stocks: {config.get('stocks', [])}")
    print(f"Time Period: {config.get('time_period', 'NOT SET')}")
    print(f"Interval: {config.get('interval', 'NOT SET')}")
    
    # Check Telegram configuration
    telegram_config = config.get('telegram', {})
    token = telegram_config.get('token')
    chat_id = telegram_config.get('chat_id')
    
    print(f"\nTelegram Configuration:")
    if token and token not in ['YOUR_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE', None]:
        print(f"Token: CONFIGURED (ends with ...{token[-10:]})")
    else:
        print("Token: NOT CONFIGURED or using placeholder")
        
    if chat_id and chat_id not in ['YOUR_CHAT_ID', 'YOUR_CHAT_ID_HERE', None]:
        print(f"Chat ID: {chat_id}")
    else:
        print("Chat ID: NOT CONFIGURED or using placeholder")
    
    # Check if Telegram will work
    print("\nTelegram Status:")
    if token and token not in ['YOUR_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE', None] and \
       chat_id and chat_id not in ['YOUR_CHAT_ID', 'YOUR_CHAT_ID_HERE', None]:
        print("✓ Telegram is properly configured and should work!")
        return True
    else:
        print("✗ Telegram is NOT properly configured. Charts will NOT be sent.")
        print("\nTo fix this on Railway:")
        print("1. Go to your Railway project")
        print("2. Go to Variables section")
        print("3. Add these variables:")
        print("   - TELEGRAM_TOKEN: Your bot token from @BotFather")
        print("   - TELEGRAM_CHAT_ID: Your numeric chat ID from @userinfobot")
        print("   - STOCKS: Comma-separated list like 'AAPL,MSFT,GOOGL' (optional)")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)