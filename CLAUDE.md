# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plotin is a Python finance chart generator and Telegram bot that retrieves historical stock data, calculates technical indicators (50 and 128 period SMAs), and generates dark-themed candlestick charts. It can send these charts to Telegram channels and supports scheduled analysis.

## Commands

### Running the Application

```bash
# Basic run (generates charts only)
python main.py

# Run with Telegram notifications enabled
python main.py --send

# Run in scheduled mode based on config.yaml schedule settings
python main.py --schedule

# Run in scheduled mode with Telegram notifications
python main.py --schedule --send
```

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt
```

### Configuration Setup

```bash
# Create config from template
cp config.yaml.template config.yaml
# Then edit config.yaml with your values
```

## Architecture

### Core Modules

1. **main.py**: Entry point that orchestrates the analysis process. Uses asyncio for asynchronous operations and integrates all components.

2. **data_retrieval.py**: Handles stock data fetching using yfinance. Fetches both daily (1d) and 4-hour (4h) interval data with appropriate buffers to ensure sufficient history for technical indicators.

3. **technical_analysis.py**: Calculates Simple Moving Averages (50 and 128 periods) using pandas rolling window functions.

4. **chart_generation.py**: Generates candlestick charts using mplfinance with dark theme styling. Creates separate charts for daily and 4-hour intervals.

5. **config_manager.py**: Loads configuration from YAML files with environment variable override support (for deployment platforms like Railway).

6. **telegram_bot.py**: Manages Telegram API interactions using python-telegram-bot library for sending charts and messages.

7. **scheduler.py**: Implements scheduled task execution using APScheduler with cron-like triggers.

### Data Flow

1. Configuration is loaded from config.yaml (or environment variables)
2. Stock data is retrieved for specified symbols (both 1d and 4h intervals)
3. Technical indicators (SMAs) are calculated on the data
4. Charts are generated and saved to the output directory
5. If enabled, charts are sent to configured Telegram chat
6. If in scheduled mode, the process repeats at configured times

### Deployment

- **Local**: Run directly with Python
- **Railway/Heroku**: Uses Procfile to run in scheduled mode by default
- Environment variables can override config values:
  - STOCKS (comma-separated list, e.g., "AAPL,MSFT,GOOGL")
  - TELEGRAM_TOKEN (from @BotFather on Telegram)
  - TELEGRAM_CHAT_ID (numeric ID from @userinfobot on Telegram)

### Testing Configuration

```bash
# Test if configuration and environment variables are loaded correctly
python test_config.py
```