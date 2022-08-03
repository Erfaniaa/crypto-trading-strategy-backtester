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
