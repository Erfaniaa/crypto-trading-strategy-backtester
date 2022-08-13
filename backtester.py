import os
import pickle
import random
import datetime

import indicators
import config
import binance_api
import utils
import position
import plot_maker
import report_maker
import candle
from position_result_and_candles import PositionResultAndCandles


class Backtester():

	POSITIONS_CSV_REPORT_COLUMN_NAMES = "Position type,Entry time,Exit time,Leverage,USDTs in position (no leverage),Entry price,Exit price,Profit % (no leverage),Take-profit price,Stop-loss price,Exit type"
	DEPOSIT_CHANGES_CSV_REPORT_COLUMN_NAMES = "Start deposit,Final deposit,Total profit %,Min monthly deposit change %,Avg monthly deposit change %,Max monthly deposit change %,Min trimonthly deposit change %,Avg trimonthly deposit change %,Max trimonthly deposit change %,Min yearly deposit change %,Avg yearly deposit change %,Max yearly deposit change %"
	
	NO_POSITION = 0
	OPEN_LONG_POSITION = 1
	CLOSE_LONG_POSITION = 2
	OPEN_SHORT_POSITION = 3
	CLOSE_SHORT_POSITION = 4

	def __init__(self, coins_symbol, start_deposit, leverage,
				 open_position_fee_percent, close_position_fee_percent,
				 use_long_positions, use_short_positions,
				 take_profit_percents_list, stop_loss_percents_list,
				 start_year, start_month, start_day, start_hour, start_minute, start_second,
				 end_year, end_month, end_day, end_hour, end_minute, end_second,
				 report_percentiles_count,
				 train_csv_file_path, test_csv_file_path, csv_file_delimiter,
				 all_timeframes_list, timeframe, indicators_timeframe,
				 minimum_number_of_candles_to_start_trading, important_recent_candles_timeframe,
				 important_recent_candles_count, coin_maximum_price, open_position_timeframe,
				 test_set_size_ratio, plot_file_path, positions_csv_report_file_path,
				 deposit_changes_csv_report_file_path, candles_plot_file_path):
					self.coins_symbol = coins_symbol
					self.start_deposit = start_deposit
					self.total_first_coins = start_deposit
					self.leverage = leverage
					self.open_position_fee_percent = open_position_fee_percent
					self.close_position_fee_percent = close_position_fee_percent
					self.use_long_positions = use_long_positions
					self.use_short_positions = use_short_positions
					self.take_profit_percents_list = take_profit_percents_list
					self.stop_loss_percents_list = stop_loss_percents_list
					self.start_date = datetime.datetime(start_year, start_month, start_day, start_hour, start_minute, start_second)
					self.end_date = datetime.datetime(end_year, end_month, end_day, end_hour, end_minute, end_second)
					self.start_date_timestamp = int(self.start_date.timestamp() * 1000)
					self.end_date_timestamp = int(self.end_date.timestamp() * 1000)
					self.candles_file_path = {}
					for tf in all_timeframes_list:
						self.candles_file_path[tf] = config.COINS_SYMBOL + "_" + str(config.START_DAY) + str(config.START_MONTH) + str(config.START_YEAR) + "_" + str(config.END_DAY) + str(config.END_MONTH) + str(config.END_YEAR) + "_" + tf + "_candles.pickle"
					self.report_percentiles_count = report_percentiles_count
					self.train_csv_file_path = train_csv_file_path
					self.test_csv_file_path = test_csv_file_path
					self.csv_file_delimiter = csv_file_delimiter					
					self.all_timeframes_list = all_timeframes_list
					self.timeframe = timeframe
					self.indicators_timeframe = indicators_timeframe
					self.important_recent_candles_timeframe = important_recent_candles_timeframe
					self.important_recent_candles_count = important_recent_candles_count
					self.maximum_open_positions_count = len(take_profit_percents_list)
					self.open_positions_value = 0
					self.open_long_positions_list = []
					self.open_short_positions_list = []
					self.closed_positions_list = []
					self.total_take_profit_wins = 0
					self.total_wins = 0
					self.important_recent_candles_list = {}
					self.minimum_number_of_candles_to_start_trading = minimum_number_of_candles_to_start_trading
					self.coin_maximum_price = coin_maximum_price
					self.open_position_timeframe = open_position_timeframe
					self.test_set_size_ratio = test_set_size_ratio
					self.plot_file_path = plot_file_path
					self.positions_csv_report_file_path = positions_csv_report_file_path
					self.deposit_changes_csv_report_file_path = deposit_changes_csv_report_file_path
					self.candles_plot_file_path = candles_plot_file_path
					self.candles_list = {}
					self.open_short_positions_value = 0
					self.open_long_positions_value = 0
					

	def _download_or_load_candles(self, timeframe):
		print("download_or_load_candles", timeframe, "started")
		if os.path.isfile(self.candles_file_path[timeframe]):
			self.candles_list[timeframe] = pickle.load(open(self.candles_file_path[timeframe], "rb"))
		else:
			while True:
				try:
					self.candles_list[timeframe] = binance_api.get_candles(timeframe, self.start_date_timestamp, self.end_date_timestamp, self.coins_symbol)
					pickle.dump(self.candles_list[timeframe], open(self.candles_file_path[timeframe], "wb"))
					break
				except:
					print("ERROR in download_or_load_candles", timeframe)
		print("download_or_load_candles", timeframe, "finished")


	def _download_or_load_all_timeframes_candles(self):
		print("download_or_load_all_timeframes_candles started")
		for timeframe in self.all_timeframes_list:
			self._download_or_load_candles(timeframe)
		print("download_or_load_all_timeframes_candles finished")


	def _init_candles_statistics(self):
		self.position_result_and_candles_list = []
		self.candles_open_to_close_list = []
		self.candles_open_to_close_abs_list = []
		self.candles_open_to_close_random_signed_list = []
		self.candles_open_to_high_list = []
		self.candles_open_to_low_list = []
		self.candles_low_to_high_list = []
		self.candles_low_and_high_to_open_list = []
		self.candles_low_and_high_to_open_abs_list = []
		self.candles_open_to_close_percent_list = []
		self.candles_open_to_close_abs_percent_list = []
		self.candles_open_to_close_random_signed_percent_list = []
		self.candles_open_to_high_percent_list = []
		self.candles_open_to_low_percent_list = []
		self.candles_low_to_high_percent_list = []
		self.candles_low_and_high_to_open_percent_list = []
		self.candles_low_and_high_to_open_abs_percent_list = []


	def _update_candles_statistics(self):
		self.candles_open_to_close_list.append(self.current_candle.close - self.current_candle.open)
		self.candles_open_to_close_abs_list.append(abs(self.current_candle.close - self.current_candle.open))
		self.candles_open_to_close_random_signed_list.append(random.randint(-1, 1) * abs(self.current_candle.close - self.current_candle.open))
		self.candles_open_to_low_list.append(self.current_candle.low - self.current_candle.open)
		self.candles_open_to_high_list.append(self.current_candle.high - self.current_candle.open)
		self.candles_low_to_high_list.append(self.current_candle.high - self.current_candle.low)
		self.candles_low_and_high_to_open_list.append(self.current_candle.low - self.current_candle.open)
		self.candles_low_and_high_to_open_list.append(self.current_candle.high - self.current_candle.open)
		self.candles_low_and_high_to_open_abs_list.append(abs(self.current_candle.low - self.current_candle.open))
		self.candles_low_and_high_to_open_abs_list.append(abs(self.current_candle.high - self.current_candle.open))

		self.candles_open_to_close_percent_list.append(100 * (self.current_candle.close - self.current_candle.open) / self.current_candle.open)
		self.candles_open_to_close_abs_percent_list.append(100 * abs(self.current_candle.close - self.current_candle.open) / self.current_candle.open)
		self.candles_open_to_close_random_signed_percent_list.append(random.randint(-1, 1) * 100 * abs(self.current_candle.close - self.current_candle.open) / self.current_candle.open)
		self.candles_open_to_low_percent_list.append(100 * (self.current_candle.low - self.current_candle.open) / self.current_candle.open)
		self.candles_open_to_high_percent_list.append(100 * (self.current_candle.high - self.current_candle.open) / self.current_candle.open)
		self.candles_low_to_high_percent_list.append(100 * (self.current_candle.high - self.current_candle.low) / self.current_candle.low)
		self.candles_low_and_high_to_open_percent_list.append(100 * (self.current_candle.low - self.current_candle.open) / self.current_candle.open)
		self.candles_low_and_high_to_open_percent_list.append(100 * (self.current_candle.high - self.current_candle.open) / self.current_candle.open)
		self.candles_low_and_high_to_open_abs_percent_list.append(100 * abs(self.current_candle.low - self.current_candle.open) / self.current_candle.open)
		self.candles_low_and_high_to_open_abs_percent_list.append(100 * abs(self.current_candle.high - self.current_candle.open) / self.current_candle.open)


	def _init_indicators(self):
		self.is_price_increasing = False
		self.is_price_decreasing = False
		self.last_is_price_increasing = False
		self.last_is_price_decreasing = False

		self.is_macd_increasing = False
		self.is_macd_decreasing = False
		self.last_is_macd_increasing = False
		self.last_is_macd_decreasing = False

		self.fast_ema = self.candles_list[self.timeframe][0].close
		self.slow_ema = self.candles_list[self.timeframe][0].close

		self.macd_fast_ema = self.candles_list[self.timeframe][0].close
		self.macd_slow_ema = self.candles_list[self.timeframe][0].close
		self.signal_line = 0
		self.macd_line = 0

		self.last_faster_ema = self.candles_list[self.timeframe][0].close
		self.last_fast_ema = self.candles_list[self.timeframe][0].close
		self.last_slow_ema = self.candles_list[self.timeframe][0].close

		self.last_macd_fast_ema = self.candles_list[self.timeframe][0].close
		self.last_macd_slow_ema = self.candles_list[self.timeframe][0].close
		self.last_signal_line = 0


	def _init_index_dicts(self):
		for tf in self.all_timeframes_list:
			self.candles_open_time_to_index_dict = {}
		for tf in self.all_timeframes_list:
			self.candles_open_time_to_index_dict[tf] = {}
			for i in range(len(self.candles_list[tf])):
				self.candles_open_time_to_index_dict[tf][self.candles_list[tf][i].open_time] = i


	def _is_it_time_to_update_indicators(self):
		if self.timeframe == "m1" and self.indicators_timeframe == "m15":
			return self.current_candle.open_time == utils.round_down_m1_to_m15_time(self.current_candle.open_time)
		else:
			return True


	def _update_important_recent_candles(self, important_recent_candles_timeframe):

		if important_recent_candles_timeframe == "m15":
			try:
				self.important_recent_candles_list = self.candles_list["m15"][max(self.candles_open_time_to_index_dict["m15"][utils.round_down_m1_to_m15_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["m15"][utils.round_down_m1_to_m15_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "h1":
			try:
				self.important_recent_candles_list = self.candles_list["h1"][max(self.candles_open_time_to_index_dict["h1"][utils.round_down_m1_to_h1_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["h1"][utils.round_down_m1_to_h1_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "h2":
			try:
				recent_candles_list = self.candles_list["h2"][max(self.candles_open_time_to_index_dict["h2"][utils.round_down_m1_to_h2_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["h2"][utils.round_down_m1_to_h2_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "h4":
			try:
				self.important_recent_candles_list = self.candles_list["h4"][max(self.candles_open_time_to_index_dict["h4"][utils.round_down_m1_to_h4_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["h4"][utils.round_down_m1_to_h4_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "d1":
			try:
				self.important_recent_candles_list = self.candles_list["d1"][max(self.candles_open_time_to_index_dict["d1"][utils.round_down_m1_to_d1_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["d1"][utils.round_down_m1_to_d1_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		self.recent_open_prices_list = [candle.open / self.coin_maximum_price for candle in self.important_recent_candles_list]
		self.recent_high_prices_list = [candle.high / self.coin_maximum_price for candle in self.important_recent_candles_list]
		self.recent_low_prices_list = [candle.low / self.coin_maximum_price for candle in self.important_recent_candles_list]
		self.recent_close_prices_list = [candle.close / self.coin_maximum_price for candle in self.important_recent_candles_list]


	def _get_current_candle_in_another_timeframe(self, timeframe, index_offset):
		try:
			if timeframe == "m15":
				return self.candles_list[timeframe][self.candles_open_time_to_index_dict[timeframe][utils.round_down_m1_to_m15_time(self.current_candle.open_time)] + index_offset]
			elif timeframe == "h1":
				return self.candles_list[timeframe][self.candles_open_time_to_index_dict[timeframe][utils.round_down_m1_to_h1_time(self.current_candle.open_time)] + index_offset]
			elif timeframe == "h2":
				return self.candles_list[timeframe][self.candles_open_time_to_index_dict[timeframe][utils.round_down_m1_to_h2_time(self.current_candle.open_time)] + index_offset]
			elif timeframe == "h4":
				return self.candles_list[timeframe][self.candles_open_time_to_index_dict[timeframe][utils.round_down_m1_to_h4_time(self.current_candle.open_time)] + index_offset]
			elif timeframe == "d1":
				return self.candles_list[timeframe][self.candles_open_time_to_index_dict[timeframe][utils.round_down_m1_to_d1_time(self.current_candle.open_time)] + index_offset]
			else:
				print("ERROR in get_current_candle_in_another_timeframe")
		except:
			print("ERROR in get_current_candle_in_another_timeframe")


	def _update_indicators(self):
		self.last_fast_ema = self.fast_ema
		self.last_slow_ema = self.slow_ema

		self.last_macd_fast_ema = self.macd_fast_ema
		self.last_macd_slow_ema = self.macd_slow_ema

		self.last_macd_line = self.macd_line
		self.last_signal_line = self.signal_line

		self.last_is_macd_increasing = self.is_macd_increasing
		self.last_is_macd_decreasing = self.is_macd_decreasing

		self.last_is_price_increasing = self.is_price_increasing
		self.last_is_price_decreasing = self.is_price_decreasing
		
		self.fast_ema = indicators.get_new_ema(self.last_fast_ema, self._get_current_candle_in_another_timeframe(timeframe=self.indicators_timeframe, index_offset=-1).close, 1 * config.MOVING_AVERAGE_SIZE)
		self.slow_ema = indicators.get_new_ema(self.last_slow_ema, self._get_current_candle_in_another_timeframe(timeframe=self.indicators_timeframe, index_offset=-1).close, 2 * config.MOVING_AVERAGE_SIZE)

		self.macd_fast_ema = indicators.get_new_ema(self.last_macd_fast_ema, self._get_current_candle_in_another_timeframe(timeframe=self.indicators_timeframe, index_offset=-1).close, 12)
		self.macd_slow_ema = indicators.get_new_ema(self.last_macd_slow_ema, self._get_current_candle_in_another_timeframe(timeframe=self.indicators_timeframe, index_offset=-1).close, 26)

		self.macd_line = self.macd_fast_ema - self.macd_slow_ema
		self.signal_line = indicators.get_new_ema(self.last_signal_line, self.macd_line, 9)

		self.is_macd_increasing = self.macd_line > self.signal_line
		self.is_macd_decreasing = self.macd_line < self.signal_line

		self.is_price_increasing = self.fast_ema > self.slow_ema
		self.is_price_decreasing = self.fast_ema < self.slow_ema


	def _init_plot_lists(self):
		self.plot_close_prices_list = []
		self.plot_close_prices_datetimes_list = []
		self.plot_deposits_list = []
		self.plot_deposit_datetimes_list = []
		self.plot_candles_list = []
		self.plot_candle_colors_list = []
	

	def _update_plot_price_lists(self):
		self.plot_close_prices_list.append(self.current_candle.close)
		self.plot_close_prices_datetimes_list.append(self.current_candle.close_time)


	def _update_plot_deposit_lists(self):
		self.plot_deposits_list.append(self.total_first_coins + self.open_positions_value)
		self.plot_deposit_datetimes_list.append(self.current_candle.close_time)


	def _is_it_time_to_open_long_position(self):
		main_condition = self.is_price_increasing and not self.last_is_price_increasing
		is_too_early = self.candles_index < self.minimum_number_of_candles_to_start_trading
		is_positions_list_empty = len(self.open_long_positions_list) == 0 and len(self.open_short_positions_list) == 0
		is_ontime = False
		if self.open_position_timeframe == "m15":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_m15_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h1_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h2":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h2_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h4":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h4_time(self.current_candle.open_time)
		if self.open_position_timeframe == "d1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_d1_time(self.current_candle.open_time)
		return is_positions_list_empty and is_ontime and not is_too_early and main_condition


	def _is_it_time_to_open_short_position(self):
		main_condition = self.is_price_decreasing and not self.last_is_price_decreasing
		is_too_early = self.candles_index < self.minimum_number_of_candles_to_start_trading
		is_positions_list_empty = len(self.open_long_positions_list) == 0 and len(self.open_short_positions_list) == 0
		is_ontime = False
		if self.open_position_timeframe == "m15":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_m15_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h1_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h2":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h2_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h4":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h4_time(self.current_candle.open_time)
		if self.open_position_timeframe == "d1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_d1_time(self.current_candle.open_time)
		return is_positions_list_empty and is_ontime and not is_too_early and main_condition


	def _update_plot_candles_list(self):
		is_ontime = False
		if self.open_position_timeframe == "m15":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_m15_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h1_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h2":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h2_time(self.current_candle.open_time)
		if self.open_position_timeframe == "h4":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_h4_time(self.current_candle.open_time)
		if self.open_position_timeframe == "d1":
			is_ontime = self.current_candle.open_time == utils.round_down_m1_to_d1_time(self.current_candle.open_time)
		if is_ontime:
			candle = self._get_current_candle_in_another_timeframe(timeframe=self.open_position_timeframe, index_offset=0)
			self.plot_candles_list.append(candle)
			if self.position_status == self.NO_POSITION:
				if candle.close >= candle.open:
					self.plot_candle_colors_list.append("white")
				else:
					self.plot_candle_colors_list.append("white")
			if self.position_status == self.OPEN_LONG_POSITION:
				self.plot_candle_colors_list.append("green")
			if self.position_status == self.OPEN_SHORT_POSITION:
				self.plot_candle_colors_list.append("red")
			if self.position_status == self.CLOSE_LONG_POSITION or self.position_status == self.CLOSE_SHORT_POSITION:
				self.plot_candle_colors_list.append("black")


	def _open_long_position(self):
		for i in range(self.maximum_open_positions_count):
				current_long_position = position.Position(position_type="long",
														  entry_time=self.current_candle.open_time,
														  exit_time="",
														  leverage=config.LEVERAGE,
														  first_coins_in_position=(self.total_first_coins / self.maximum_open_positions_count) * (1 - self.open_position_fee_percent / 100),
														  entry_price=self.current_candle.open,
														  exit_price="",
														  profit_percent="",
														  exit_type="",
														  max_profit_percent=-100,
														  min_profit_percent=100,
														  take_profit_price=self.current_candle.open * (1 + self.take_profit_percents_list[i] / 100),
														  stop_loss_price=self.current_candle.open * (1 + self.stop_loss_percents_list[i] / 100),
														  recent_candles_list=self.important_recent_candles_list,
														  candles_index=self.candles_index)
				self.open_long_positions_list.append(current_long_position)
		self.total_first_coins = 0


	def _open_short_position(self):
		for i in range(self.maximum_open_positions_count):
				current_short_position = position.Position(position_type="short",
														   entry_time=self.current_candle.open_time,
														   exit_time="",
														   leverage=config.LEVERAGE,
														   first_coins_in_position=(self.total_first_coins / self.maximum_open_positions_count) * (1 - self.open_position_fee_percent / 100),
														   entry_price=self.current_candle.open,
														   exit_price="",
														   profit_percent="",
														   exit_type="",
														   max_profit_percent=-100,
														   min_profit_percent=100,
														   take_profit_price=self.current_candle.open * (1 - self.take_profit_percents_list[i] / 100),
														   stop_loss_price=self.current_candle.open * (1 - self.stop_loss_percents_list[i] / 100),
														   recent_candles_list=self.important_recent_candles_list,
														   candles_index=self.candles_index)
				self.open_short_positions_list.append(current_short_position)
		self.total_first_coins = 0


	def _update_open_long_positions_statistics(self):
		open_long_positions_count = len(self.open_long_positions_list)
		for i in range(open_long_positions_count):
			self.open_long_positions_list[i].max_profit_percent = max(self.open_long_positions_list[i].max_profit_percent, 100 * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price)
			self.open_long_positions_list[i].min_profit_percent = min(self.open_long_positions_list[i].min_profit_percent, 100 * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price)


	def _update_open_short_positions_statistics(self):
		open_short_positions_count = len(self.open_short_positions_list)
		for i in range(open_short_positions_count):
			self.open_short_positions_list[i].max_profit_percent = max(self.open_short_positions_list[i].max_profit_percent, -100 * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price)
			self.open_short_positions_list[i].min_profit_percent = min(self.open_short_positions_list[i].min_profit_percent, -100 * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price)


	def _check_conditions_to_close_long_position(self):
		main_condition = self.is_price_decreasing and not self.last_is_price_decreasing
		open_long_positions_count = len(self.open_long_positions_list)
		for i in reversed(range(open_long_positions_count)):
			if self.current_candle.high > self.open_long_positions_list[i].take_profit_price or \
				self.current_candle.low < self.open_long_positions_list[i].stop_loss_price or \
				main_condition:
					self.position_status = self.CLOSE_LONG_POSITION
					recent_candles_list = self.open_long_positions_list[i].recent_candles_list
					recent_candles_close_list = [candle.close for candle in recent_candles_list]
					recent_candles_open_list = [candle.open for candle in recent_candles_list]
					recent_candles_high_list = [candle.high for candle in recent_candles_list]
					recent_candles_low_list = [candle.low for candle in recent_candles_list]
					position_result_and_candles = PositionResultAndCandles(open_prices_list=recent_candles_open_list,
																		   close_prices_list=recent_candles_close_list,
																		   high_prices_list=recent_candles_high_list,
																		   low_prices_list=recent_candles_low_list)
					self.open_long_positions_list[i].exit_time = self.current_candle.close_time
					if self.current_candle.low < self.open_long_positions_list[i].stop_loss_price:
						self.open_long_positions_list[i].exit_price = self.open_long_positions_list[i].stop_loss_price
						self.open_long_positions_list[i].exit_type = "stop-loss"
						position_result_and_candles.win = False
					elif self.current_candle.high > self.open_long_positions_list[i].take_profit_price:
						self.open_long_positions_list[i].exit_price = self.open_long_positions_list[i].take_profit_price
						self.open_long_positions_list[i].exit_type = "take-profit"
						position_result_and_candles.win = True
						self.total_take_profit_wins += 1
					else:
						self.open_long_positions_list[i].exit_price = self.current_candle.close
						self.open_long_positions_list[i].exit_type = "normal"
					if len(recent_candles_list) == self.important_recent_candles_count:
						self.position_result_and_candles_list.append(position_result_and_candles)
					self.open_long_positions_list[i].profit_percent = 100 * (self.open_long_positions_list[i].exit_price - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price
					current_position_value = (1 + self.open_long_positions_list[i].profit_percent * self.open_long_positions_list[i].leverage / 100) * self.open_long_positions_list[i].first_coins_in_position
					current_position_profit = (self.open_long_positions_list[i].profit_percent * self.open_long_positions_list[i].leverage / 100) * self.open_long_positions_list[i].first_coins_in_position
					if current_position_profit > 0:
						self.total_wins += 1
					self.total_first_coins += current_position_value * (1 - self.close_position_fee_percent / 100)
					self.closed_positions_list.append(self.open_long_positions_list[i])
					self.open_long_positions_list = self.open_long_positions_list[:-1]


	def _check_conditions_to_close_short_position(self):
		main_condition = self.is_price_increasing and not self.last_is_price_increasing
		open_short_positions_count = len(self.open_short_positions_list)
		for i in reversed(range(open_short_positions_count)):
			if self.current_candle.high < self.open_short_positions_list[i].take_profit_price or \
				self.current_candle.low > self.open_short_positions_list[i].stop_loss_price or \
				main_condition:
					self.position_status = self.CLOSE_SHORT_POSITION
					recent_candles_list = self.open_short_positions_list[i].recent_candles_list
					recent_candles_close_list = [candle.close for candle in recent_candles_list]
					recent_candles_open_list = [candle.open for candle in recent_candles_list]
					recent_candles_high_list = [candle.high for candle in recent_candles_list]
					recent_candles_low_list = [candle.low for candle in recent_candles_list]
					position_result_and_candles = PositionResultAndCandles(open_prices_list=recent_candles_open_list,
																		   close_prices_list=recent_candles_close_list,
																		   high_prices_list=recent_candles_high_list,
																		   low_prices_list=recent_candles_low_list)
					self.open_short_positions_list[i].exit_time = self.current_candle.close_time
					if self.current_candle.low > self.open_short_positions_list[i].stop_loss_price:
						self.open_short_positions_list[i].exit_price = self.open_short_positions_list[i].stop_loss_price
						self.open_short_positions_list[i].exit_type = "stop-loss"
						position_result_and_candles.win = False
					elif self.current_candle.high < self.open_short_positions_list[i].take_profit_price:
						self.open_short_positions_list[i].exit_price = self.open_short_positions_list[i].take_profit_price
						self.open_short_positions_list[i].exit_type = "take-profit"
						position_result_and_candles.win = True
						self.total_take_profit_wins += 1
					else:
						self.open_short_positions_list[i].exit_price = self.current_candle.close
						self.open_short_positions_list[i].exit_type = "normal"
					if len(recent_candles_list) == self.important_recent_candles_count:
						self.position_result_and_candles_list.append(position_result_and_candles)
					self.open_short_positions_list[i].profit_percent = 100 * (self.open_short_positions_list[i].entry_price - self.open_short_positions_list[i].exit_price) / self.open_short_positions_list[i].entry_price
					current_position_value = (1 + self.open_short_positions_list[i].profit_percent * self.open_short_positions_list[i].leverage / 100) * self.open_short_positions_list[i].first_coins_in_position
					current_position_profit = (self.open_short_positions_list[i].profit_percent * self.open_short_positions_list[i].leverage / 100) * self.open_short_positions_list[i].first_coins_in_position
					if current_position_profit > 0:
						self.total_wins += 1
					self.total_first_coins += current_position_value * (1 - self.close_position_fee_percent / 100)
					self.closed_positions_list.append(self.open_short_positions_list[i])
					self.open_short_positions_list = self.open_short_positions_list[:-1]


	def _update_open_long_positions_value(self):
		self.open_long_positions_value = 0
		open_long_positions_count = len(self.open_long_positions_list)
		for i in range(open_long_positions_count):
			self.open_long_positions_value += (1 + config.LEVERAGE * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price) * self.open_long_positions_list[i].first_coins_in_position
		self.open_positions_value = self.open_short_positions_value + self.open_long_positions_value
		self.final_deposit = self.total_first_coins + self.open_positions_value


	def _update_open_short_positions_value(self):
		self.open_short_positions_value = 0
		open_short_positions_count = len(self.open_short_positions_list)
		for i in range(open_short_positions_count):
			self.open_short_positions_value += (1 - config.LEVERAGE * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price) * self.open_short_positions_list[i].first_coins_in_position
		self.open_positions_value = self.open_short_positions_value + self.open_long_positions_value
		self.final_deposit = self.total_first_coins + self.open_positions_value


	def _print_main_backtest_results(self):
		print("final deposit:", self.total_first_coins + self.open_positions_value)
		print("closed positions count:", len(self.closed_positions_list))
		if len(self.closed_positions_list) > 0:
			print("win rate percent:", 100 * self.total_wins / len(self.closed_positions_list))
			print("take profits win rate percent:", 100 * self.total_take_profit_wins / len(self.closed_positions_list), "\n")
		else:
			print("win rate percent:", 0)
			print("take profits win rate percent:", 0, "\n")


	def _prepare_train_set_and_test_set(self):
		self.train_set_list = []
		self.test_set_list = []
		position_result_and_candles_list_len = len(self.position_result_and_candles_list)

		for i in range(position_result_and_candles_list_len):
			if i >= (1 - self.test_set_size_ratio) * position_result_and_candles_list_len:
				self.test_set_list.append(self.position_result_and_candles_list[i])
			else:
				self.train_set_list.append(self.position_result_and_candles_list[i])


	def _save_train_set_and_test_set_to_csv(self):
		print("Writing to " + self.train_csv_file_path + " ...")
		with open(self.train_csv_file_path, 'w') as positions_dataset_csv_file:
			for position_result_and_candle in self.train_set_list:
				positions_dataset_csv_file.write(str(position_result_and_candle) + "\n")
		print("Writing to " + self.train_csv_file_path + " finished.\n")

		print("Writing to " + self.test_csv_file_path + " ...")
		with open(self.test_csv_file_path, 'w') as positions_dataset_csv_file:
			for position_result_and_candle in self.test_set_list:
				positions_dataset_csv_file.write(str(position_result_and_candle) + "\n")
		print("Writing to " + self.test_csv_file_path + " finished.\n")


	def _save_plots_to_file(self):
		plot_maker.PlotMaker.add_plot("deposit", self.plot_deposits_list, self.plot_deposit_datetimes_list, 2, 1, 1)
		plot_maker.PlotMaker.add_plot(self.coins_symbol + " price", self.plot_close_prices_list, self.plot_close_prices_datetimes_list, 2, 1, 2)
		plot_maker.PlotMaker.save_plot_to_file(self.plot_file_path)


	def _show_and_save_candles_plot_to_file(self):
		plot_maker.PlotMaker.add_candles_plot(candle.Candle.candles_list_to_pandas_dataframe(self.plot_candles_list), self.plot_candle_colors_list)
		plot_maker.PlotMaker.save_candles_plot(candle.Candle.candles_list_to_pandas_dataframe(self.plot_candles_list), self.plot_candle_colors_list, self.candles_plot_file_path)


	def _show_plots(self):
		plot_maker.PlotMaker.show_plot()


	def _print_candles_statistical_parameters(self):
		report_maker.print_statistical_parameters("candles_open_to_close_list", self.candles_open_to_close_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_close_abs_list", self.candles_open_to_close_abs_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_close_random_signed_list", self.candles_open_to_close_random_signed_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_low_list", self.candles_open_to_low_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_high_list", self.candles_open_to_high_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_to_high_list", self.candles_low_to_high_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_and_high_to_open_list", self.candles_low_and_high_to_open_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_and_high_to_open_abs_list", self.candles_low_and_high_to_open_abs_list, self.report_percentiles_count)

		report_maker.print_statistical_parameters("candles_open_to_close_percent_list", self.candles_open_to_close_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_close_abs_percent_list", self.candles_open_to_close_abs_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_close_random_signed_percent_list", self.candles_open_to_close_random_signed_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_low_percent_list", self.candles_open_to_low_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_open_to_high_percent_list", self.candles_open_to_high_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_to_high_percent_list", self.candles_low_to_high_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_and_high_to_open_percent_list", self.candles_low_and_high_to_open_percent_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("candles_low_and_high_to_open_abs_percent_list", self.candles_low_and_high_to_open_abs_percent_list, self.report_percentiles_count)


	def _prepare_closed_positions_statistics(self):
		self.closed_positions_max_profit_percents_list = []
		self.closed_positions_min_profit_percents_list = []
		self.closed_positions_profit_percents_list = []
		for closed_position in self.closed_positions_list:
			self.closed_positions_max_profit_percents_list.append(closed_position.max_profit_percent)
			self.closed_positions_min_profit_percents_list.append(closed_position.min_profit_percent)
			self.closed_positions_profit_percents_list.append(closed_position.profit_percent)


	def _print_closed_positions_statistics(self):
		report_maker.print_statistical_parameters("max_profit_percents", self.closed_positions_max_profit_percents_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("min_profit_percents", self.closed_positions_min_profit_percents_list, self.report_percentiles_count)
		report_maker.print_statistical_parameters("profit_percents", self.closed_positions_profit_percents_list, self.report_percentiles_count)


	def _prepare_deposit_changes_statistics(self):
		self.deposit_daily_changes_percent = []
		self.deposit_weekly_changes_percent = []
		self.deposit_biweekly_changes_percent = []
		self.deposit_monthly_changes_percent = []
		self.deposit_bimonthly_changes_percent = []
		self.deposit_trimonthly_changes_percent = []
		self.deposit_yearly_changes_percent = []
		for i in range(len(self.plot_deposits_list)):
			if i >= utils.convert_candles_count(self.timeframe, "d1"):
				self.deposit_daily_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "d1")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "d1")])
			if i >= utils.convert_candles_count(self.timeframe, "w1"):
				self.deposit_weekly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "w1")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "w1")])
			if i >= utils.convert_candles_count(self.timeframe, "w2"):
				self.deposit_biweekly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "w2")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "w2")])
			if i >= utils.convert_candles_count(self.timeframe, "M1"):
				self.deposit_monthly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M1")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M1")])
			if i >= utils.convert_candles_count(self.timeframe, "M2"):
				self.deposit_bimonthly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M2")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M2")])
			if i >= utils.convert_candles_count(self.timeframe, "M3"):
				self.deposit_trimonthly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M3")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "M3")])
			if i >= utils.convert_candles_count(self.timeframe, "y1"):
				self.deposit_yearly_changes_percent.append(100 * (self.plot_deposits_list[i] - self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "y1")]) / self.plot_deposits_list[i - utils.convert_candles_count(self.timeframe, "y1")])


	def _print_deposit_changes_statistics(self):
		report_maker.print_statistical_parameters("deposit_daily_changes_percent", self.deposit_daily_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_weekly_changes_percent", self.deposit_weekly_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_biweekly_changes_percent", self.deposit_biweekly_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_monthly_changes_percent", self.deposit_monthly_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_bimonthly_changes_percent", self.deposit_bimonthly_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_trimonthly_changes_percent", self.deposit_trimonthly_changes_percent, self.report_percentiles_count)
		report_maker.print_statistical_parameters("deposit_yearly_changes_percent", self.deposit_yearly_changes_percent, self.report_percentiles_count)


	def _save_closed_positions_to_csv(self):
		print("Writing to " + self.positions_csv_report_file_path + " ...")
		report_maker.generate_positions_csv_report(self.positions_csv_report_file_path, self.POSITIONS_CSV_REPORT_COLUMN_NAMES, self.closed_positions_list)
		print("Writing to " + self.positions_csv_report_file_path + " finished.\n")


	def _save_deposit_changes_to_csv(self):
		print("Writing to " + self.deposit_changes_csv_report_file_path + " ...")
		report_maker.generate_deposit_changes_csv_report(self.deposit_changes_csv_report_file_path, self.DEPOSIT_CHANGES_CSV_REPORT_COLUMN_NAMES, self.start_deposit, self.final_deposit, self.deposit_monthly_changes_percent, self.deposit_trimonthly_changes_percent, self.deposit_yearly_changes_percent)
		print("Writing to " + self.deposit_changes_csv_report_file_path + " finished.\n")


	def _iterate_candles(self):
		print("Backtesting...")
		for candles_index in range(1, len(self.candles_list[self.timeframe]) - 1):
			self.candles_index = candles_index
			last_progress_percent = int(100 * (candles_index - 1) / len(self.candles_list[self.timeframe]))
			progress_percent = int(100 * (candles_index) / len(self.candles_list[self.timeframe]))
			if progress_percent > last_progress_percent and progress_percent % 5 == 0:
				print(str(progress_percent) + "%")
			
			self.current_candle = self.candles_list[self.timeframe][candles_index]
			self._update_plot_price_lists()

			if self._is_it_time_to_update_indicators():
				self._update_indicators()

			self._update_candles_statistics()

			self._update_plot_deposit_lists()

			self._update_important_recent_candles(self.important_recent_candles_timeframe)

			self.position_status = self.NO_POSITION

			if self.use_long_positions:
				if self._is_it_time_to_open_long_position():
					self.position_status = self.OPEN_LONG_POSITION
					self._open_long_position()

				self._update_open_long_positions_statistics()

				self._check_conditions_to_close_long_position()

				self._update_open_long_positions_value()

			if self.use_short_positions:
				if self._is_it_time_to_open_short_position():
					self.position_status = self.OPEN_SHORT_POSITION
					self._open_short_position()

				self._update_open_short_positions_statistics()

				self._check_conditions_to_close_short_position()

				self._update_open_short_positions_value()

			self._update_plot_candles_list()
			self._update_plot_deposit_lists()
		
		print("Backtesting finished.\n")


	def backtest(self):
		self._download_or_load_all_timeframes_candles()

		self._init_plot_lists()
		self._init_indicators()
		self._init_candles_statistics()
		self._init_index_dicts()

		self._iterate_candles()

		self._print_main_backtest_results()

		self._prepare_train_set_and_test_set()
		self._save_train_set_and_test_set_to_csv()

		self._show_and_save_candles_plot_to_file()
		self._save_plots_to_file()

		self._print_candles_statistical_parameters()

		self._prepare_closed_positions_statistics()
		self._print_closed_positions_statistics()

		self._prepare_deposit_changes_statistics()
		self._print_deposit_changes_statistics()

		self._save_closed_positions_to_csv()
		self._save_deposit_changes_to_csv()

		self._prepare_train_set_and_test_set()
		self._save_train_set_and_test_set_to_csv()
