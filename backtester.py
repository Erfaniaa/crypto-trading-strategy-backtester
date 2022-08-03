import os
import pickle
import random

import pandas as pd
import torch
import typer
import pycm
import skorch

import indicators
import configparser

import datetime
import config
import binance_api
import utils
import position
from position_result_and_candles import PositionResultAndCandles


class Backtester():

	POSITIONS_CSV_REPORT_COLUMN_NAMES = "FOLAN"
	DEPOSIT_CHANGES_CSV_REPORT_COLUMN_NAMES = "BAHMAAN"

	def __init__(self, coins_symbol, start_deposit, leverage,
				 open_position_fee_percent, close_position_fee_percent,
				 use_long_positions, use_short_positions,
				 take_profit_percents_list, stop_loss_percents_list,
				 start_year, start_month, start_day, start_hour, start_minute, start_second,
				 end_year, end_month, end_day, end_hour, end_minute, end_second,
				 report_percentiles_count, positions_dataset_csv_file_path,
				 train_csv_file_path, test_csv_file_path, csv_file_delimiter,
				 maximum_open_positions_count, all_timeframes_list, timeframe, indicators_timeframe,
				 minimum_number_of_candles_to_start_trading, important_recent_candles_timeframe,
				 important_recent_candles_count, coin_maximum_price, open_position_timeframe):
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
					self.start_date_timestamp = self.start_date.timestamp() * 1000
					self.end_date_timestamp = self.end_date.timestamp() * 1000
					self.candles_file_path = {}
					for tf in all_timeframes_list:
						self.candles_file_path[tf] = config.COINS_SYMBOL + "_" + str(config.START_DAY) + str(config.START_MONTH) + str(config.START_YEAR) + "_" + str(config.END_DAY) + str(config.END_MONTH) + str(config.END_YEAR) + "_" + tf + "_candles.pickle"
					self.report_percentiles_count = report_percentiles_count
					self.positions_dataset_csv_file_path = positions_dataset_csv_file_path
					self.train_csv_file_path = train_csv_file_path
					self.test_csv_file_path = test_csv_file_path
					self.csv_file_delimiter = csv_file_delimiter					
					self.all_timeframes_list = all_timeframes_list
					self.timeframe = timeframe
					self.indicators_timeframe = indicators_timeframe
					self.important_recent_candles_timeframe = important_recent_candles_timeframe
					self.important_recent_candles_count = important_recent_candles_count
					self.maximum_open_positions_count = maximum_open_positions_count
					self.open_positions_value = 0
					self.open_long_positions_list = []
					self.open_short_positions_list = []
					self.closed_positions_list = []
					self.total_take_profit_wins = 0
					self.total_wins = 0
					for tf in self.all_timeframes_list:
						self.recent_candles_list[tf] = None
					self.minimum_number_of_candles_to_start_trading = minimum_number_of_candles_to_start_trading
					self.coin_maximum_price = coin_maximum_price
					self.open_position_timeframe = open_position_timeframe
					

	def download_or_load_candles(self, timeframe):
		print("download_or_load_candles", timeframe, "started")
		if os.path.isfile(self.candles_file_path[timeframe]):
			self.candles_list[timeframe] = pickle.load(open(self.candles_file_path[timeframe], "rb"))
		else:
			while True:
				try:
					self.candles_list[timeframe] = binance_api.get_candles(self.start_date_timestamp, self.end_date_timestamp, self.coins_symbol, timeframe)
					pickle.dump(self.candles_list[timeframe], open(self.candles_file_path[timeframe], "wb"))
					break
				except:
					print("ERROR in download_or_load_candles", timeframe)
		print("download_or_load_candles", timeframe, "finished")


	def download_or_load_all_timeframes_candles(self):
		print("download_or_load_all_timeframes_candles started")
		for timeframe in self.all_timeframes_list:
			self.download_or_load_candles(timeframe)
		print("download_or_load_all_timeframes_candles finished")


	def init_candles_statistics(self):
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


	def update_candles_statistics(self):
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


	def init_plot_variables(self):
		self.plot_close_prices = []
		self.plot_datetimes = []
		self.plot_deposits_list = []
		self.plot_deposit_datetimes_list = []


	def init_indicators(self):
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

		self.last_faster_ema = self.candles_list[self.timeframe][0].close
		self.last_fast_ema = self.candles_list[self.timeframe][0].close
		self.last_slow_ema = self.candles_list[self.timeframe][0].close

		self.last_macd_fast_ema = self.candles_list[self.timeframe][0].close
		self.last_macd_slow_ema = self.candles_list[self.timeframe][0].close
		self.last_signal_line = 0


	def init_index_dicts(self):
		for tf in self.all_timeframes_list:
			self.candles_open_time_to_index_dict = {}
		for tf in self.all_timeframes_list:
			self.candles_open_time_to_index_dict[tf] = {}
		for i in range(len(self.candles_list[tf])):
			self.candles_open_time_to_index_dict[tf][self.candles_list[tf][i].open_time] = i


	def is_it_time_to_update_indicators(self):
		if self.timeframe == "m1" and self.indicators_timeframe == "m15":
			return self.current_candle.open_time == utils.round_down_m1_to_m15_time(self.current_candle.open_time)
		else:
			return True


	def update_important_recent_candles(self, important_recent_candles_timeframe):

		if important_recent_candles_timeframe == "m15":
			try:
				recent_candles_list = self.candles_list["m15"][max(self.candles_open_time_to_index_dict["m15"][utils.round_down_m1_to_m15_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["m15"][utils.round_down_m1_to_m15_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "h1":
			try:
				recent_candles_list = self.candles_list["h1"][max(self.candles_open_time_to_index_dict["h1"][utils.round_down_m1_to_h1_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["h1"][utils.round_down_m1_to_h1_time(self.current_candle.open_time)]]
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
				recent_candles_list = self.candles_list["h4"][max(self.candles_open_time_to_index_dict["h4"][utils.round_down_m1_to_h4_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["h4"][utils.round_down_m1_to_h4_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		if important_recent_candles_timeframe == "d1":
			try:
				recent_candles_list = self.candles_list["d1"][max(self.candles_open_time_to_index_dict["d1"][utils.round_down_m1_to_d1_time(self.current_candle.open_time)] - self.important_recent_candles_count, 0):self.candles_open_time_to_index_dict["d1"][utils.round_down_m1_to_d1_time(self.current_candle.open_time)]]
			except:
				print("ERROR in update_important_recent_candles")
				self.important_recent_candles_list = []

		self.recent_open_prices_list = [candle.open / self.coin_maximum_price for candle in recent_candles_list]
		self.recent_high_prices_list = [candle.high / self.coin_maximum_price for candle in recent_candles_list]
		self.recent_low_prices_list = [candle.low / self.coin_maximum_price for candle in recent_candles_list]
		self.recent_close_prices_list = [candle.close / self.coin_maximum_price for candle in recent_candles_list]


	def get_current_candle_in_another_timeframe(self, timeframe, indicators_timeframe, index_offset=-1):
		try:
			if indicators_timeframe == "m15":
				return self.candles_list[indicators_timeframe][self.candles_open_time_to_index_dict[indicators_timeframe][utils.round_down_m1_to_m15_time(self.current_candle.open_time)] + index_offset]
			elif indicators_timeframe == "h1":
				return self.candles_list[indicators_timeframe][self.candles_open_time_to_index_dict[indicators_timeframe][utils.round_down_m1_to_h1_time(self.current_candle.open_time)] + index_offset]
			elif indicators_timeframe == "h2":
				return self.candles_list[indicators_timeframe][self.candles_open_time_to_index_dict[indicators_timeframe][utils.round_down_m1_to_h2_time(self.current_candle.open_time)] + index_offset]
			elif indicators_timeframe == "h4":
				return self.candles_list[indicators_timeframe][self.candles_open_time_to_index_dict[indicators_timeframe][utils.round_down_m1_to_h4_time(self.current_candle.open_time)] + index_offset]
			elif indicators_timeframe == "d1":
				return self.candles_list[indicators_timeframe][self.candles_open_time_to_index_dict[indicators_timeframe][utils.round_down_m1_to_d1_time(self.current_candle.open_time)] + index_offset]
			else:
				print("ERROR in get_current_candle_in_another_timeframe")
		except:
			print("ERROR in get_current_candle_in_another_timeframe")


	def update_indicators(self):
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
		
		self.fast_ema = indicators.get_new_ema(self.last_fast_ema, self.get_current_candle_in_another_timeframe(timeframe=self.timeframe, indicators_timeframe=self.indicators_timeframe, index_offset=-1).close, 1 * config.MOVING_AVERAGE_SIZE)
		self.slow_ema = indicators.get_new_ema(self.last_slow_ema, self.get_current_candle_in_another_timeframe(timeframe=self.timeframe, indicators_timeframe=self.indicators_timeframe, index_offset=-1).close, 2 * config.MOVING_AVERAGE_SIZE)

		self.macd_fast_ema = indicators.get_new_ema(self.last_macd_fast_ema, self.get_current_candle_in_another_timeframe(timeframe=self.timeframe, indicators_timeframe=self.indicators_timeframe, index_offset=-1).close, 12)
		self.macd_slow_ema = indicators.get_new_ema(self.last_macd_slow_ema, self.get_current_candle_in_another_timeframe(timeframe=self.timeframe, indicators_timeframe=self.indicators_timeframe, index_offset=-1).close, 26)

		self.macd_line = self.macd_fast_ema - self.macd_slow_ema
		self.signal_line = indicators.get_new_ema(self.last_signal_line, self.macd_line, 9)

		self.is_macd_increasing = self.macd_line > self.signal_line
		self.is_macd_decreasing = self.macd_line < self.signal_line

		self.is_price_increasing = self.fast_ema > self.slow_ema
		self.is_price_decreasing = self.fast_ema < self.slow_ema


	def init_plot_lists(self):
		self.plot_close_prices = []
		self.plot_datetimes = []
		self.plot_deposit_datetimes_list = []
	

	def update_plot_price_lists(self):
		self.plot_close_prices.append(self.current_candle.close)
		self.plot_datetimes.append(self.current_candle.close_time)


	def update_plot_deposit_lists(self):
		self.plot_deposits_list.append(self.total_first_coins + self.open_positions_value)
		self.plot_deposit_datetimes_list.append(self.current_candle.close_time)


	def is_it_time_to_open_long_position(self):
		main_condition = self.is_price_increasing and not self.is_price_increasing
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


	def is_it_time_to_open_short_position(self, candles_index, current_candle):
		main_condition = self.is_price_decreasing and not self.is_price_decreasing
		is_too_early = candles_index < self.minimum_number_of_candles_to_start_trading
		is_positions_list_empty = len(self.open_long_positions_list) == 0 and len(self.open_short_positions_list) == 0
		is_ontime = False
		if self.open_position_timeframe == "m15":
			is_ontime = current_candle.open_time == utils.round_down_m1_to_m15_time(current_candle.open_time)
		if self.open_position_timeframe == "h1":
			is_ontime = current_candle.open_time == utils.round_down_m1_to_h1_time(current_candle.open_time)
		if self.open_position_timeframe == "h2":
			is_ontime = current_candle.open_time == utils.round_down_m1_to_h2_time(current_candle.open_time)
		if self.open_position_timeframe == "h4":
			is_ontime = current_candle.open_time == utils.round_down_m1_to_h4_time(current_candle.open_time)
		if self.open_position_timeframe == "d1":
			is_ontime = current_candle.open_time == utils.round_down_m1_to_d1_time(current_candle.open_time)
		return is_positions_list_empty and is_ontime and not is_too_early and main_condition


	def open_long_position(self):
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
														  recent_candles_list=[],
														  candles_index=self.candles_index)
				self.open_long_positions_list.append(current_long_position)
		self.total_first_coins = 0


	def open_short_position(self):
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
														   recent_candles_list=[],
														   candles_index=self.candles_index)
				self.open_short_positions_list.append(current_short_position)
		self.total_first_coins = 0


	def update_open_long_positions_statistics(self):
		open_long_positions_count = len(self.open_long_positions_list)
		for i in range(open_long_positions_count):
			self.open_long_positions_list[i].max_profit_percent = max(self.open_long_positions_list[i].max_profit_percent, 100 * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price)
			self.open_long_positions_list[i].min_profit_percent = min(self.open_long_positions_list[i].min_profit_percent, 100 * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price)


	def update_open_short_positions_statistics(self):
		open_short_positions_count = len(self.open_short_positions_list)
		for i in range(open_short_positions_count):
			self.open_short_positions_list[i].max_profit_percent = max(self.open_short_positions_list[i].max_profit_percent, -100 * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price)
			self.open_short_positions_list[i].min_profit_percent = min(self.open_short_positions_list[i].min_profit_percent, -100 * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price)


	def check_conditions_to_close_long_position(self):
		main_condition = self.is_price_decreasing and not self.last_is_price_decreasing
		open_long_positions_count = len(self.open_long_positions_list)
		for i in reversed(range(open_long_positions_count)):
			if self.current_candle.high > self.open_long_positions_list[i].take_profit_price or \
				self.current_candle.low < self.open_long_positions_list[i].stop_loss_price or \
				main_condition:
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
						self.open_long_positions_list[i].exit_price = open_long_positions_list[i].stop_loss_price
						self.open_long_positions_list[i].exit_type = "stop-loss"
						position_result_and_candles.win = False
					elif self.current_candle.high > open_long_positions_list[i].take_profit_price:
						open_long_positions_list[i].exit_price = open_long_positions_list[i].take_profit_price
						open_long_positions_list[i].exit_type = "take-profit"
						position_result_and_candles.win = True
						self.total_take_profit_wins += 1
					else:
						open_long_positions_list[i].exit_price = self.current_candle.close
						open_long_positions_list[i].exit_type = "normal"
					if len(recent_candles_list) == self.important_recent_candles_count:
						self.position_result_and_candles_list.append(position_result_and_candles)
					self.open_long_positions_list[i].profit_percent = 100 * (open_long_positions_list[i].exit_price - open_long_positions_list[i].entry_price) / open_long_positions_list[i].entry_price
					current_position_value = (1 + open_long_positions_list[i].profit_percent * open_long_positions_list[i].leverage / 100) * open_long_positions_list[i].first_coins_in_position
					current_position_profit = (open_long_positions_list[i].profit_percent * open_long_positions_list[i].leverage / 100) * open_long_positions_list[i].first_coins_in_position
					if current_position_profit > 0:
						self.total_wins += 1
					self.total_first_coins += current_position_value
					self.closed_positions_list.append(open_long_positions_list[i])
					open_long_positions_list = open_long_positions_list[:-1]


	def check_conditions_to_close_short_position(self):
		main_condition = self.is_price_increasing and not self.last_is_price_increasing
		open_short_positions_count = len(self.open_short_positions_list)
		for i in reversed(range(open_short_positions_count)):
			if self.current_candle.high < self.open_short_positions_list[i].take_profit_price or \
				self.current_candle.low > self.open_short_positions_list[i].stop_loss_price or \
				main_condition:
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
						self.open_short_positions_list[i].exit_price = open_short_positions_list[i].stop_loss_price
						self.open_short_positions_list[i].exit_type = "stop-loss"
						position_result_and_candles.win = False
					elif self.current_candle.high < open_short_positions_list[i].take_profit_price:
						open_short_positions_list[i].exit_price = open_short_positions_list[i].take_profit_price
						open_short_positions_list[i].exit_type = "take-profit"
						position_result_and_candles.win = True
						self.total_take_profit_wins += 1
					else:
						open_short_positions_list[i].exit_price = self.current_candle.close
						open_short_positions_list[i].exit_type = "normal"
					if len(recent_candles_list) == self.important_recent_candles_count:
						self.position_result_and_candles_list.append(position_result_and_candles)
					self.open_short_positions_list[i].profit_percent = 100 * (open_short_positions_list[i].entry_price - open_short_positions_list[i].exit_price) / open_short_positions_list[i].entry_price
					current_position_value = (1 + open_short_positions_list[i].profit_percent * open_short_positions_list[i].leverage / 100) * open_short_positions_list[i].first_coins_in_position
					current_position_profit = (open_short_positions_list[i].profit_percent * open_short_positions_list[i].leverage / 100) * open_short_positions_list[i].first_coins_in_position
					if current_position_profit > 0:
						self.total_wins += 1
					self.total_first_coins += current_position_value
					self.closed_positions_list.append(open_short_positions_list[i])
					open_short_positions_list = open_short_positions_list[:-1]


	def update_open_long_positions_value(self):
		self.open_long_positions_value = 0
		open_long_positions_count = len(self.open_long_positions_list)
		for i in range(open_long_positions_count):
			self.open_long_positions_value += (1 + config.LEVERAGE * (self.current_candle.close - self.open_long_positions_list[i].entry_price) / self.open_long_positions_list[i].entry_price) * self.open_long_positions_list[i].first_coins_in_position
		self.open_positions_value = self.open_short_positions_value + self.open_long_positions_value


	def update_open_short_positions_value(self):
		self.open_short_positions_value = 0
		open_short_positions_count = len(self.open_short_positions_list)
		for i in range(0, open_short_positions_count):
			self.open_short_positions_value += (1 - config.LEVERAGE * (self.current_candle.close - self.open_short_positions_list[i].entry_price) / self.open_short_positions_list[i].entry_price) * self.open_short_positions_list[i].first_coins_in_position
		self.open_positions_value = self.open_short_positions_value + self.open_long_positions_value


	def print_main_backtest_results(self):
		print("final deposit:", self.total_first_coins + self.open_positions_value)
		print("closed positions count:", len(self.closed_positions_list))
		print("win rate:", self.total_wins / len(self.closed_positions_list), "\n")
		print("take profits win rate:", self.total_take_profit_wins / len(self.closed_positions_list), "\n")


	def iterate_candles(self):
		print("Backtesting...")
		for candles_index in range(1, len(self.candles_list[self.timeframe]) - 1):
			self.candles_index = candles_index
			last_progress_percent = int(100 * (candles_index - 1) / len(self.candles_list[self.timeframe]))
			progress_percent = int(100 * (candles_index) / len(self.candles_list[self.timeframe]))
			if progress_percent > last_progress_percent and progress_percent % 5 == 0:
				print(str(progress_percent) + "%")
			
			self.current_candle = self.candles_list[self.timeframe][candles_index]

			if self.is_it_time_to_update_indicators():
				self.update_indicators()

			self.update_candles_statistics()

			self.update_plot_deposit_lists()

			self.update_important_recent_candles(self.important_recent_candles_timeframe)

			if self.use_long_positions:
				if self.is_it_time_to_open_long_position():
					self.open_long_position()

				self.update_open_long_positions_statistics()

				self.check_conditions_to_close_long_position()

				self.update_open_long_positions_value()

			if self.use_short_positions:
				if self.is_it_time_to_open_short_position():
					self.open_short_position()

				self.update_open_short_positions_statistics()

				self.check_conditions_to_close_short_position()

				self.update_open_short_positions_value()

			self.update_plot_deposit_lists()
		
		print("Backtesting finished.\n")
		self.print_main_backtest_results()