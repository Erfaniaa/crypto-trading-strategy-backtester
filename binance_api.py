from datetime import datetime
from candle import Candle
import requests
import json
from types import SimpleNamespace
import math
import pytz


def count_m1_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 60000)) / 1000)))


def count_m5_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 300000)) / 1000)))


def count_m15_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 900000)) / 1000)))


def count_m30_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 1800000)) / 1000)))


def count_h1_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 3600000)) / 1000)))


def count_h2_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 7200000)) / 1000)))


def count_h4_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 14400000)) / 1000)))


def count_d1_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 86400000)) / 1000)))


def count_w1_candles(start_timestamp, end_timestamp):
	return int(math.ceil((round(((end_timestamp - start_timestamp) / 604800000)) / 1000)))


def get_candles_in_range(symbol, interval, start_time, end_time, limit='1000'):
	start_time = int(start_time)
	end_time = int(end_time)
	headers = {'Content-Type': 'application/json; charset=utf-8', 'X-MBX-APIKEY': 'i8322dmyBsrk9A8dNBliUExbVHmDPbNn1cqvOAHZPWdYc7KGJ6kX767V3Dg7jWmo'}
	r = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&limit={limit}&startTime={start_time}&endTime={end_time}&interval={interval}", headers=headers)
	m = json.loads(r.content, object_hook=lambda d: SimpleNamespace(**d))
	candles = []
	i = 0
	for u in m: 
		otime = datetime.utcfromtimestamp(int(''.join(str(u[0]).split())[:-3])).replace(tzinfo=pytz.UTC)
		ctime = datetime.utcfromtimestamp(int(''.join(str(u[6]).split())[:-3])).replace(tzinfo=pytz.UTC)
		i += 1
		candles.append(Candle(otime.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S'), float(u[1]), float(u[2]), float(u[3]), float(u[4]), u[5], ctime.astimezone(pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')))
	return candles


def get_candles_m1(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (60000 * 999) + start_timestamp_temp
	total_candles_count = count_m1_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading m1 candles...")
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'1m', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'1m', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 60000
		end_date_timestamp_temp = (60000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m1 candles finished.")
	return arr


def get_candles_m5(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (300000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m5 candles...")
	total_candles_count = count_m5_candles(start_timestamp, end_timestamp)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'5m', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'5m', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 300000
		end_date_timestamp_temp = (300000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m5 candles finished.")
	return arr


def get_candles_m15(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (900000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m15 candles...")
	total_candles_count = count_m15_candles(start_timestamp, end_timestamp)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if(end_date_timestamp_temp <= end_timestamp):
			candles = get_candles_in_range(symbol,  f'15m', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'15m', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 900000
		end_date_timestamp_temp = (900000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m15 candles finished.")
	return arr


def get_candles_m30(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (1800000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m30 candles...")
	total_candles_count = count_m30_candles(start_timestamp, end_timestamp)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if(end_date_timestamp_temp <= end_timestamp):
			candles = get_candles_in_range(symbol,  f'30m', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'30m', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 1800000
		end_date_timestamp_temp = (1800000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading m30 candles finished.")
	return arr


# This function is not tested completely:
def get_candles_h1(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (3600000 * 999) + start_timestamp_temp
	total_candles_count = count_h1_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading h1 candles...")
		print("total_candles_count:", total_candles_count)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'1h', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'1h', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 3600000
		end_date_timestamp_temp = (3600000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading h1 candles finished.")
	return arr


def get_candles_h2(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (7200000 * 999) + start_timestamp_temp
	total_candles_count = count_h2_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading h2 candles...")
		print("total_candles_count:", total_candles_count)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'2h', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'2h', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 7200000
		end_date_timestamp_temp = (7200000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading h2 candles finished.")
	return arr


# This function is not tested completely:
def get_candles_h4(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (14400000 * 999) + start_timestamp_temp
	total_candles_count = count_h4_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading h4 candles...")
		print("total_candles_count:", total_candles_count)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'4h', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'4h', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 14400000
		end_date_timestamp_temp = (14400000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading h4 candles finished.")
	return arr


# This function is not tested completely:
def get_candles_d1(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (86400000 * 999) + start_timestamp_temp
	total_candles_count = count_d1_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading d1 candles...")
		print("total_candles_count:", total_candles_count)
	total_candles_count = count_d1_candles(start_timestamp, end_timestamp)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'1d', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'1d', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 86400000
		end_date_timestamp_temp = (86400000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading d1 candles finished.")
	return arr


# This function is not tested completely:
def get_candles_w1(start_timestamp, end_timestamp, symbol, show_log=True):
	arr = []
	start_timestamp = start_timestamp
	start_timestamp_temp = start_timestamp
	end_date_timestamp_temp = (604800000 * 999) + start_timestamp_temp
	total_candles_count = count_w1_candles(start_timestamp, end_timestamp)
	if show_log:
		print("Downloading w1 candles...")
		print("total_candles_count:", total_candles_count)
	total_candles_count = count_w1_candles(start_timestamp, end_timestamp)
	for item in range(total_candles_count):
		if show_log and (item % 10 == 0 or item == total_candles_count - 1):
			print(item, "/", total_candles_count)
		if end_date_timestamp_temp <= end_timestamp:
			candles = get_candles_in_range(symbol,  f'1h', str(start_timestamp_temp), str(end_date_timestamp_temp), '1000')
		else:
			candles = get_candles_in_range(symbol,  f'1h', str(start_timestamp_temp), str(end_timestamp), '1000')
		for candle in candles:
			arr.append(candle)
		start_timestamp_temp = end_date_timestamp_temp + 604800000
		end_date_timestamp_temp = (604800000 * 999) + start_timestamp_temp
	if show_log:
		print("Downloading w1 candles finished.")
	return arr


def get_candles(timeframe, start_timestamp, end_timestamp, symbol, show_log=True):
	if timeframe == "m1":
		return get_candles_m1(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "m5":
		return get_candles_m5(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "m15":
		return get_candles_m15(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "m30":
		return get_candles_m30(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "h1":
		return get_candles_h1(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "h2":
		return get_candles_h2(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "h4":
		return get_candles_h4(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "d1":
		return get_candles_d1(start_timestamp, end_timestamp, symbol, show_log)
	if timeframe == "w1":
		return get_candles_w1(start_timestamp, end_timestamp, symbol, show_log)
	return None
