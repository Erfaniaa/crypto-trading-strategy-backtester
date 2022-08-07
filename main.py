from operator import le
import backtester
import config


if __name__ == "__main__":
	backtester = backtester.Backtester(coins_symbol=config.COINS_SYMBOL,
									   start_deposit=config.START_DEPOSIT,
									   leverage=config.LEVERAGE,
									   open_position_fee_percent=config.OPEN_POSITION_FEE_PERCENT,
									   close_position_fee_percent=config.CLOSE_POSITION_FEE_PERCENT,
									   use_long_positions=config.USE_LONG_POSITIONS,
									   use_short_positions=config.USE_SHORT_POSITIONS,
									   take_profit_percents_list=config.TAKE_PROFIT_PERCENTS_LIST,
									   stop_loss_percents_list=config.STOP_LOSS_PERCENTS_LIST,
									   start_year=config.START_YEAR,
									   start_month=config.START_MONTH,
									   start_day=config.START_DAY,
									   start_hour=config.START_HOUR,
									   start_minute=config.START_MINUTE,
									   start_second=config.START_SECOND,
									   end_year=config.END_YEAR,
									   end_month=config.END_MONTH,
									   end_day=config.END_DAY,
									   end_hour=config.END_HOUR,
									   end_minute=config.END_MINUTE,
									   end_second=config.END_SECOND,
									   report_percentiles_count=config.REPORT_PERCENTILES_COUNT,
									   train_csv_file_path=config.TRAIN_CSV_FILE_PATH,
									   test_csv_file_path=config.TEST_CSV_FILE_PATH,
									   csv_file_delimiter=config.CSV_FILE_DELIMITER,
									   all_timeframes_list=config.ALL_TIMEFRAMES_LIST,
									   timeframe=config.TIMEFRAME,
									   indicators_timeframe=config.INDICATORS_TIMEFRAME,
									   important_recent_candles_timeframe=config.IMPORTANT_RECENT_CANDLES_TIMEFRAME,
									   important_recent_candles_count=config.IMPORTANT_RECENT_CANDLES_COUNT,
									   minimum_number_of_candles_to_start_trading=config.MINIMUM_NUMBER_OF_CANDLES_TO_START_TRADING,
									   open_position_timeframe=config.OPEN_POSITION_TIMEFRAME,
									   coin_maximum_price=config.COIN_MAXIMUM_PRICE,
									   test_set_size_ratio=config.TEST_SET_SIZE_RATIO,
									   plot_file_path=config.PLOT_FILE_PATH,
									   positions_csv_report_file_path=config.POSITIONS_CSV_REPORT_FILE_PATH,
									   deposit_changes_csv_report_file_path=config.DEPOSIT_CHANGES_CSV_REPORT_FILE_PATH)

	backtester.backtest()
