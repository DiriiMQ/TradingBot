# Trading Bot

A Python-based trading bot for managing stock symbols and trading operations.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TradingBot
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Usage

After installation, you can run the trading bot using:

```bash
trading-bot
```

### Features

- View favorite stock symbols
- View all available symbols
- Add symbols to favorites
- Remove symbols from favorites

## Development

To run the development version:

```bash
python -m src.cli
```

## Requirements

- Python 3.7+
- pandas
- vnstock
- python-dotenv 