import matplotlib.pyplot as plt
import matplotlib
import mplfinance as mpf


class PlotMaker():
	def __init__(self):
		pass

	@staticmethod
	def add_plot(y_axis_label, prices_list, datetimes_list, subplot_rows, subplot_columns, subplot_index):
		plt.subplot(subplot_rows, subplot_columns, subplot_index)
		x_axis = matplotlib.dates.date2num(datetimes_list)
		plt.plot_date(x_axis, prices_list, '-')
		plt.ylabel(y_axis_label)

	@staticmethod
	def add_candles_plot(candles_dataframe, candle_colors_list):
		mpf.plot(candles_dataframe, type="candle", marketcolor_overrides=candle_colors_list, warn_too_much_data=10 ** 10)

	@staticmethod
	def save_candles_plot(candles_dataframe, candle_colors_list, file_path):
		mpf.plot(candles_dataframe, type="candle", marketcolor_overrides=candle_colors_list, warn_too_much_data=10 ** 10, savefig=file_path)

	@staticmethod
	def clear_all_plots():
		plt.clf()
	
	@staticmethod
	def save_plot_to_file(file_path):
		plt.savefig(file_path)

	@staticmethod
	def show_plot():
		plt.show()
