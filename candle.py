import pandas as pd


class Candle:
	def __init__(self, open_time, open, high, low, close, volume, close_time):
		self.open_time = open_time
		self.open = open
		self.high = high
		self.low = low
		self.close = close
		self.volume = volume
		self.close_time = close_time
	
	def __repr__(self):
		return "open_time:" + str(self.open_time) + \
			", open:" + str(self.open) + \
			", high:" + str(self.high) + \
			", low:" + str(self.low) + \
			", close:" + str(self.close) + \
			", volume:" + str(self.volume) + \
			", close_time:" + str(self.close_time)


	def to_tuple(self):
		return (self.open_time, self.open, self.high, self.low, self.close)


	@staticmethod
	def candles_list_to_tuples_list(candles_list):
		tuples_list = [candle.to_tuple() for candle in candles_list]
		return tuples_list


	@staticmethod
	def candles_list_to_pandas_dataframe(candles_list):
		tuples_list = Candle.candles_list_to_tuples_list(candles_list)
		df = pd.DataFrame(tuples_list, columns=["Date", "Open", "High", "Low", "Close"])
		df.index = pd.DatetimeIndex(df['Date'])
		# df.index.name = "Date"
		return df
