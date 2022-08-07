class Position:
	def __init__(self, position_type="", entry_time="", exit_time="", leverage="", first_coins_in_position="",
				entry_price="", exit_price="", profit_percent="",
				exit_type="", max_profit_percent="", min_profit_percent="",
				take_profit_price="", stop_loss_price="", exchange_fee="",
				recent_candles_list=[], candles_index=""):
			self.position_type = position_type
			self.entry_time = entry_time
			self.exit_time = exit_time
			self.leverage = leverage
			self.first_coins_in_position = first_coins_in_position
			self.entry_price = entry_price
			self.exit_price = exit_price
			self.profit_percent = profit_percent
			self.exit_type = exit_type
			self.max_profit_percent = max_profit_percent
			self.min_profit_percent = min_profit_percent
			self.take_profit_price = take_profit_price
			self.stop_loss_price = stop_loss_price
			self.exchange_fee = exchange_fee
			self.recent_candles_list = recent_candles_list
			self.candles_index = candles_index
	
	def __repr__(self):
		return str(self.position_type) + "," + \
			   str(self.entry_time) + "," + \
			   str(self.exit_time) + "," + \
			   str(self.leverage) + "," + \
			   str(self.first_coins_in_position) + "," + \
			   str(self.entry_price) + "," + \
			   str(self.exit_price) + "," + \
			   str(self.profit_percent) + "," + \
			   str(self.take_profit_price) + "," + \
			   str(self.stop_loss_price) + "," + \
			   str(self.exit_type)
