def round_down_m1_to_h1_time(m1_time):
	return m1_time[:14] + "00:00"


def round_up_m1_to_h1_time(m1_time):
	return m1_time[:14] + "59:00"


def round_down_m1_to_d1_time(m1_time):
	return m1_time[:11] + "00:00:00"


def round_up_m1_to_d1_time(m1_time):
	return m1_time[:11] + "23:59:00"


def round_down_m1_to_h2_time(m1_time):
	h = int(m1_time[11:13])
	h_round_down = 2 * (h // 2)
	h_round_down_str = str(h_round_down)
	if len(h_round_down_str) == 1:
		h_round_down_str = "0" + h_round_down_str
	return m1_time[:11] + h_round_down_str + ":00:00"


def round_up_m1_to_h2_time(m1_time):
	h = int(m1_time[11:13])
	h_round_up = 2 * (h // 2) + 1
	h_round_up_str = str(h_round_up)
	if len(h_round_up_str) == 1:
		h_round_up_str = "0" + h_round_up_str
	return m1_time[:11] + h_round_up_str + ":00:00"


def round_down_m1_to_m15_time(m1_time):
	m = int(m1_time[14:16])
	m_round_down = 15 * (m // 15)
	m_round_down_str = str(m_round_down)
	if len(m_round_down_str) == 1:
		m_round_down_str = "0" + m_round_down_str
	return m1_time[:14] + m_round_down_str + ":00"


def round_up_m1_to_m15_time(m1_time):
	m = int(m1_time[14:16])
	m_round_up = 15 * (m // 15) + 15
	m_round_up_str = str(m_round_up)
	if len(m_round_up_str) == 1:
		m_round_up_str = "0" + m_round_up_str
	return m1_time[:14] + m_round_up_str + ":00"


def round_down_m1_to_h4_time(m1_time):
	h = int(m1_time[11:13])
	h_round_down = 4 * (h // 4)
	h_round_down_str = str(h_round_down)
	if len(h_round_down_str) == 1:
		h_round_down_str = "0" + h_round_down_str
	return m1_time[:11] + h_round_down_str + ":00:00"


def round_up_m1_to_h4_time(m1_time):
	h = int(m1_time[11:13])
	h_round_up = 4 * (h // 4) + 3
	h_round_up_str = str(h_round_up)
	if len(h_round_up_str) == 1:
		h_round_up_str = "0" + h_round_up_str
	return m1_time[:11] + h_round_up_str + ":00:00"


def convert_candles_count(lower_time_frame, higher_timeframe):
	if lower_time_frame == "m1":
		if higher_timeframe == "m5":
			return 5
		if higher_timeframe == "m15":
			return 15
		if higher_timeframe == "m30":
			return 30
		if higher_timeframe == "h1":
			return 60
		if higher_timeframe == "h2":
			return 120
		if higher_timeframe == "h4":
			return 240
		if higher_timeframe == "d1":
			return 1440
		if higher_timeframe == "w1":
			return 1440 * 7
		if higher_timeframe == "w2":
			return 1440 * 14
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90
		if higher_timeframe == "y1":
			return 1440 * 365
	if lower_time_frame == "m5":
		if higher_timeframe == "m15":
			return 15 // 5
		if higher_timeframe == "m30":
			return 30 // 5
		if higher_timeframe == "h1":
			return 60 // 5
		if higher_timeframe == "h2":
			return 120 // 5
		if higher_timeframe == "h4":
			return 240 // 5
		if higher_timeframe == "d1":
			return 1440 // 5
		if higher_timeframe == "w1":
			return 1440 * 7 // 5
		if higher_timeframe == "w2":
			return 1440 * 14 // 5
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 5
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 5
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 5
		if higher_timeframe == "y1":
			return 1440 * 365 // 5
	if lower_time_frame == "m15":
		if higher_timeframe == "m30":
			return 30 // 15
		if higher_timeframe == "h1":
			return 60 // 15
		if higher_timeframe == "h2":
			return 120 // 15
		if higher_timeframe == "h4":
			return 240 // 15
		if higher_timeframe == "d1":
			return 1440 // 15
		if higher_timeframe == "w1":
			return 1440 * 7 // 15
		if higher_timeframe == "w2":
			return 1440 * 14 // 15
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 15
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 15
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 15
		if higher_timeframe == "y1":
			return 1440 * 365 // 15
	if lower_time_frame == "m30":
		if higher_timeframe == "h1":
			return 60 // 30
		if higher_timeframe == "h2":
			return 120 // 30
		if higher_timeframe == "h4":
			return 240 // 30
		if higher_timeframe == "d1":
			return 1440 // 30
		if higher_timeframe == "w1":
			return 1440 * 7 // 30
		if higher_timeframe == "w2":
			return 1440 * 14 // 30
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 30
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 30
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 30
		if higher_timeframe == "y1":
			return 1440 * 365 // 30
	if lower_time_frame == "h1":
		if higher_timeframe == "h2":
			return 120 // 60
		if higher_timeframe == "h4":
			return 240 // 60
		if higher_timeframe == "d1":
			return 1440 // 60
		if higher_timeframe == "w1":
			return 1440 * 7 // 60
		if higher_timeframe == "w2":
			return 1440 * 14 // 60
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 60
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 60
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 60
		if higher_timeframe == "y1":
			return 1440 * 365 // 60
	if lower_time_frame == "h2":
		if higher_timeframe == "h4":
			return 240 // 120
		if higher_timeframe == "d1":
			return 1440 // 120
		if higher_timeframe == "w1":
			return 1440 * 7 // 120
		if higher_timeframe == "w2":
			return 1440 * 14 // 120
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 120
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 120
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 120
		if higher_timeframe == "y1":
			return 1440 * 365 // 120
	if lower_time_frame == "h4":
		if higher_timeframe == "d1":
			return 1440 // 480
		if higher_timeframe == "w1":
			return 1440 * 7 // 480
		if higher_timeframe == "w2":
			return 1440 * 14 // 480
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 480
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 480
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 480
		if higher_timeframe == "y1":
			return 1440 * 365 // 480
	if lower_time_frame == "d1":
		if higher_timeframe == "w1":
			return 1440 * 7 // 1440
		if higher_timeframe == "w2":
			return 1440 * 14 // 1440
		if higher_timeframe == "M1" or higher_timeframe == "d30":
			return 1440 * 30 // 1440
		if higher_timeframe == "M2" or higher_timeframe == "d60":
			return 1440 * 60 // 1440
		if higher_timeframe == "M3" or higher_timeframe == "d90":
			return 1440 * 90 // 1440
		if higher_timeframe == "y1":
			return 1440 * 365 // 1440
	return 0
