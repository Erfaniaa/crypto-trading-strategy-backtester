def get_wma(prices_list):
	if len(prices_list) == 0:
		return 0
	if len(prices_list) == 1:
		return prices_list[0]
	coe = 1
	base = 2 ** (1 / (len(prices_list) - 1))
	coe_sum = 0
	sum = 0
	for i in range(len(prices_list)):
		sum += prices_list[i] * coe
		coe *= base
		coe_sum += coe
	return sum / coe_sum


def get_ma(prices_list):
  if len(prices_list) == 0:
    return 0
  ret = 0
  for item in range(len(prices_list)):
        ret += float(prices_list[item])
  ret = ret / len(prices_list)
  return ret


def get_new_ema(lastEMA, price, count):
  m = 2 / (count + 1)
  price = price
  s1 = (float(price) * float(m))
  s2 = float(lastEMA) * float((1 - m))
  return (s1 + s2)
