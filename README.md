# Crypto Trading Strategy Backtester

Easy-to-use cryptocurrency trading strategy simulator

![backtester](https://user-images.githubusercontent.com/7780269/183297986-e82d509c-7c3c-4a50-b25b-39d0412c82a4.png)


## Features

- You can run it fast, and it is easy to use.
- There are no complexities and no database usage in this project. Even dependencies are a few.
- It is easy to modify and customize.
- It generates many different statistical parameters in a complete report.
- This project generates practical datasets for data scientists.
- You can read the code for educational purposes.

## Run

1. Clone the repository.
2. Run `pip3 install -r requirements.txt`.
3. Run `python3 main.py`.

This will backtest an example strategy for trading Bitcoin.

## Config

To define the strategy, you can:

- Change `config.py` constants.
- Define new indicators in `indicators.py`.
- Change `_is_it_time_to_open_long_position` and `_is_it_time_to_open_short_position` methods.
- Change `_check_conditions_to_close_long_position` and `_check_conditions_to_close_short_position` methods.

## Config.py Description

- `COINS_SYMBOL`: The trading pair
- `START_DEPOSIT`: How much money do we have to start trading with? 
- `LEVERAGE`: Futures trading leverage
- `OPEN_POSITION_FEE_PERCENT` and `CLOSE_POSITION_FEE_PERCENT`: Exchange fees
- `USE_LONG_POSITIONS` and `USE_SHORT_POSITIONS`: Are we trading in the futures market?
- `TAKE_PROFIT_PERCENTS_LIST` and `STOP_LOSS_PERCENTS_LIST`: Set multiple take profit and stop losses for your positions
- `MOVING_AVERAGE_SIZE` and`INDICATORS_TIMEFRAME`: If use some indicators, you can set them up here.
- `START_YEAR`, `START_MONTH`, `START_DAY`, `START_HOUR`, `START_MINUTE` , and `START_SECOND`: Starting time for trading
- `END_YEAR`, `END_MONTH`, `END_DAY`, `END_HOUR`, `END_MINUTE` , and `END_SECOND`: Starting time for trading
- `TIMEFRAME`: The main time frame used for iterating candles and checking the take profits and stop losses
- `IMPORTANT_RECENT_CANDLES_TIMEFRAME`: Generated output dataset candles timeframe
- `IMPORTANT_RECENT_CANDLES_COUNT`: Number of candles in the generated output dataset
- `OPEN_POSITION_TIMEFRAME`: We want to open the position at some exact rounded times
- `REPORT_PERCENTILES_COUNT`: Number of percentiles used in the statistical analysis report
- `TEST_SET_SIZE_RATIO`: How big is the final generated test set of our dataset?
- `MINIMUM_NUMBER_OF_CANDLES_TO_START_TRADING`: Do not start trading soon!

## Output

- A plot in `plot.png`, for example:

![plot](https://user-images.githubusercontent.com/7780269/183297991-5bfc0537-138d-4d8b-909c-f6272538ff59.png)
- A complete report on candles statistics (as the program text output)
- A complete report on opened and closed positions (as the program text output)
- A complete report on the strategy (in `deposit_changes.csv`)
- A spreadsheet containing opened and closed positions (in `positions.csv`)
- Two datasets for data science and machine learning purposes (`test.csv` and `train.csv`)

## See Also

- [Binance Futures Trading Bot](https://github.com/erfaniaa/binance-futures-trading-bot)
- [Binance Spot Trading Bot](https://github.com/smzerehpoush/binance-spot-trading-bot)

## Credits

[Erfan Alimohammadi](https://github.com/Erfaniaa) and [Amir Reza Shahmiri](https://github.com/Amirrezashahmiri)
