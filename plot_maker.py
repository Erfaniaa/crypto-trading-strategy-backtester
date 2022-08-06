import matplotlib.pyplot as plt
import matplotlib


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
	def save_plot_to_file(file_path):
		plt.savefig(file_path)

	@staticmethod
	def show_plot():
		plt.show()
