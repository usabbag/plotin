# Plotin - Python finance chart generator & Telegram bot

A simple Python tool to generate finance charts with technical indicators and send them to a Telegram channel.

<img width="458" alt="logo" src="https://github.com/user-attachments/assets/f33b3c5a-8e4b-4a91-87be-c15abf863a41" />

## Features

- Retrieves historical stock data using yfinance
- Calculates 50 and 128 period Simple Moving Averages (SMAs)
- Generates dark-themed candlestick charts with technical indicators
- Sends chart analysis to Telegram (optional)
- Supports scheduled analysis at configurable times
- Fully configurable through YAML configuration file
- Command-line options for different operational modes

## Installation

1. Clone this repository:
```
git clone https://github.com/usabbag/plotin.git
cd plotin
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Configuration

Edit the `config.yaml` file to customize:

- Stock symbols to analyze
- Time period (in days) for historical data
- Chart output directory
- Chart styling preferences
- Telegram bot settings
- Scheduled analysis times

### Secrets and Configuration

For security, the repository includes a `config.yaml.template` file instead of the actual config. To set up your configuration:

1. Copy the template to create your config file:
   ```
   cp config.yaml.template config.yaml
   ```

2. Edit `config.yaml` with your actual values

```yaml
stocks:
  - AAPL
  - MSFT
  - GOOGL

time_period: 30  # days
interval: 4h     # 4-hour interval

output:
  directory: ./output
  
chart:
  up_color: "#26a69a"    # Teal green
  down_color: "#ef5350"  # Light red
  sma_50_color: "#42a5f5"   # Bright blue
  sma_128_color: "#ffb74d"  # Light orange

# Telegram bot configuration
telegram:
  token: "YOUR_BOT_TOKEN"  # Get this from BotFather
  chat_id: "YOUR_CHAT_ID"  # Must be a numeric ID

# Scheduled tasks configuration
schedules:
  - id: "morning_report"
    day_of_week: "mon-fri"   # Monday to Friday
    hour: 9                  # 9 AM
    minute: 0                # At exactly 9:00 AM
```

## Usage

Run the application with:

```
python main.py
```

Charts will be generated in the specified output directory.

### Additional Usage Options

```
# Run with Telegram notifications enabled
python main.py --send

# Run in scheduled mode based on config.yaml schedule settings
python main.py --schedule

# Run in scheduled mode with Telegram notifications
python main.py --schedule --send
```

## Output

The tool generates:
- Candlestick charts with 50 and 128 period SMAs for each stock
- Log file with information about the analysis process

## Deployment Options

### Local Installation
The simplest way to use Plotin is to run it locally as described in the Installation section above.

### Railway Deployment
You can deploy Plotin to Railway to run it in the cloud: https://railway.com/

The included Procfile will automatically configure the app to run in scheduled mode.

### Telegram Notifications
Configure the Telegram bot in `config.yaml`:
```yaml
telegram:
  token: "YOUR_BOT_TOKEN"  # Get from BotFather
  chat_id: "YOUR_CHAT_ID"  # Get from @userinfobot
```

### Scheduled Analysis
Configure automatic analysis schedule in `config.yaml`:
```yaml
schedules:
  - id: "morning_report"
    day_of_week: "mon-fri"  # Monday to Friday
    hour: 9                 # 9 AM
    minute: 0               # At exactly 9:00 AM
```
