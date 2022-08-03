def generate_positions_csv_report(file_path, csv_columns_str, positions):
	output_file = open(file_path, "w")
	output_file.write(csv_columns_str + "\n")
	for closed_position in positions:
		output_file.write(str(closed_position) + "\n")
	output_file.close()


def generate_deposit_changes_csv_report(file_path, csv_columns_str, start_deposit, final_deposit, deposit_monthly_changes_percent, deposit_trimonthly_changes_percent, deposit_yearly_changes_percent):
	output_file = open(file_path, "w")
	output_file.write(csv_columns_str + "\n")
	output_file.write(str(start_deposit) + ",")
	output_file.write(str(final_deposit) + ",")
	output_file.write(str(100 * (final_deposit - start_deposit) / start_deposit) + ",")
	if len(deposit_monthly_changes_percent) > 0:
		output_file.write(str(min(deposit_monthly_changes_percent)) + ",")
		output_file.write(str(sum(deposit_monthly_changes_percent) / len(deposit_monthly_changes_percent)) + ",")
		output_file.write(str(max(deposit_monthly_changes_percent)) + ",")
	if len(deposit_trimonthly_changes_percent) > 0:
		output_file.write(str(min(deposit_trimonthly_changes_percent)) + ",")
		output_file.write(str(sum(deposit_trimonthly_changes_percent) / len(deposit_trimonthly_changes_percent)) + ",")
		output_file.write(str(max(deposit_trimonthly_changes_percent)) + ",")
	if len(deposit_yearly_changes_percent) > 0:
		output_file.write(str(min(deposit_yearly_changes_percent)) + ",")
		output_file.write(str(sum(deposit_yearly_changes_percent) / len(deposit_yearly_changes_percent)) + ",")
		output_file.write(str(max(deposit_yearly_changes_percent)) + "\n")
	output_file.close()


def print_statistical_parameters(list_name, input_list, percentiles_count):
	input_list_len = len(input_list)
	if input_list_len == 0:
		return
	input_list = sorted(input_list)
	print("")
	print("minimum", list_name + ":", min(input_list))
	print("average", list_name + ":", sum(input_list) / input_list_len)
	print("maximum", list_name + ":", max(input_list))
	print(list_name, "percentiles:")
	for i in range(percentiles_count + 1):
		idx = max(min(int(i * input_list_len / percentiles_count + 0.5), input_list_len - 1), 0)
		print(str(i) + ":", input_list[idx])
	print("")