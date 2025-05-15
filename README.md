# Plotin - Stock Analysis Tool

A simple Python tool for retrieving stock data, calculating technical indicators, and generating candlestick charts.

## Features

- Retrieves historical stock data using yfinance
- Calculates 50 and 128 period Simple Moving Averages (SMAs)
- Generates candlestick charts with technical indicators
- Configurable through YAML configuration file

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd plotin
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

Note: This application requires Python 3.9 or higher.

## Configuration

Edit the `config.yaml` file to customize:

- Stock symbols to analyze
- Time period (in days) for historical data
- Chart output directory
- Chart styling preferences

Example configuration:
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
  up_color: green
  down_color: red
  sma_50_color: blue
  sma_128_color: orange
```

## Usage

Run the application with:

```
python main.py
```

Charts will be generated in the specified output directory.

## Output

The tool generates:
- Candlestick charts with 50 and 128 period SMAs for each stock
- Log file with information about the analysis process 