class PositionResultAndCandles:

	def __init__(self, open_prices_list=[], high_prices_list=[], low_prices_list=[], close_prices_list=[], win=False):
		self.open_prices_list = open_prices_list
		self.high_prices_list = high_prices_list
		self.low_prices_list = low_prices_list
		self.close_prices_list = close_prices_list
		self.win = win
	
	def __repr__(self):
		return str(self.open_prices_list)[1:-1] + "," + \
			   str(self.high_prices_list)[1:-1] + "," + \
			   str(self.low_prices_list)[1:-1] + "," + \
			   str(self.close_prices_list)[1:-1] + "," + \
			   str(float(self.win))

	def get_data_list(self):
		return self.open_prices_list + self.high_prices_list + self.low_prices_list + self.close_prices_list
	
	def get_target_list(self):
		if self.win == 0:
			return [1.0, 0.0]
		else:
			return [0.0, 1.0]
