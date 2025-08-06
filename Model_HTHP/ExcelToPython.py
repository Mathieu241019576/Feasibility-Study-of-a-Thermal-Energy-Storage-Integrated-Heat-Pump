from Model_HTHP.__init__ import *


class ExcelToPython:
	def __init__(self, input_file="Excel_Inputs/Inputs.xlsx"):
		# Load the original file
		self.input_file		= input_file
		self.output_file	= self._new_file_name()
		# Create a new file
		copyfile(self.input_file, self.output_file)
		self.input_sheet	= load_workbook(self.output_file, data_only=True)['inputs']		# data_only=True else we get the formulas instead of the values
		self.output_sheet	= load_workbook(self.output_file, data_only=True)['outputs']	# e.g., we want 20 not '=D6+10'


	def _new_file_name(self):
		current_date = datetime.now()
		return f"Excel_Outputs/Outputs_{current_date.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"


	def _get_excel_column_name(self, n):
		column_name = ""
		while n > 0:
			n, remainder = divmod(n - 1, 26)
			column_name = chr(65 + remainder) + column_name
		return column_name


	def get_data(self):
		# Starting data column index
		column_nb	 = 4  # Column D
		data_columns = [] # List with all the data of each column

		while True:
			column = self._get_excel_column_name(column_nb)
			fluid_value = self.input_sheet[f"{column}3"].value

			# Break if no more data in the column
			if fluid_value is None or column_nb>500:
				break

			# Read data from the current column
			data = {
				'fluid':	self.input_sheet[f"{column}3"].value,
				'V':		self.input_sheet[f"{column}6"].value,
				'r':		self.input_sheet[f"{column}7"].value,
				'n':		self.input_sheet[f"{column}8"].value,
				'Cv':		self.input_sheet[f"{column}9"].value,
				'ω':		self.input_sheet[f"{column}11"].value,
				'ω':		self.input_sheet[f"{column}11"].value,
				'fluid_c':	self.input_sheet[f"{column}13"].value,
				'T_ci':		self.input_sheet[f"{column}14"].value,
				'P_ci':		self.input_sheet[f"{column}15"].value,
				'ṁ_c':		self.input_sheet[f"{column}16"].value,
				'UA_cd':	self.input_sheet[f"{column}17"].value,
				'fluid_e':	self.input_sheet[f"{column}19"].value,
				'T_ei':		self.input_sheet[f"{column}20"].value,
				'P_ei':		self.input_sheet[f"{column}21"].value,
				'ṁ_e':		self.input_sheet[f"{column}22"].value,
				'UA_ev':	self.input_sheet[f"{column}23"].value,
				'ΔT_s':		self.input_sheet[f"{column}26"].value,
			}

			# Increment
			data_columns.append(data)
			column_nb += 1

		return data_columns


	def write_results(self, **kwargs):
		"""
		Take the values of each list (listed in the kwargs) and put in a excel column
		"""
		column_nb = 1  # start at column n°1 (A)

		for var_name, list_result in kwargs.items():

			# get the name of the column (from number to letter)
			column = self._get_excel_column_name(column_nb)
			# start at line 1, first line is the name of the list
			line = 1
			self.output_sheet[f"{column}{line}"] = var_name

			# take each value of the list an put it in the coresponding excel cell
			for result in list_result:
				line += 1
				self.output_sheet[f"{column}{line}"] = result
			column_nb += 1
		
		# write the list values in the excel
		self.output_sheet.parent.save(self.output_file)

		# Print that the data are written in the file
		print(f'\n\n\nThe results data are written ine the file:\n{self.output_file}\n\n\n')


	def write_fluid_results(self, list_results):
		"""
		Same as previous but for the case where the fluid is a variable

		list_results = [					# list_results contains the results of each fluids
		{'T_2' : [], 'T_3' : [], ...},		# result contains => name : list_values
		{'T_2' : [], 'T_3' : [], ...},		# result contains => name : list_values
		...									# ...
		]

		"""
		column_nb = 1  # start at column n°1 (A)

		for results in list_results:
			for name, list_values in results.items():

				# get the name of the column (from number to letter)
				column = self._get_excel_column_name(column_nb)

				# start at line 1, first line is the name of the list
				line = 1
				self.output_sheet[f"{column}{line}"] = name + '_' + results['fluid']

				# take each value of the list an put it in the coresponding excel cell
				for value in list_values:
					line += 1
					self.output_sheet[f"{column}{line}"] = value
				column_nb += 1
		
		# write the list values in the excel
		self.output_sheet.parent.save(self.output_file)

		# Print that the data are written in the file
		print(f'\n\n\nThe results data are written ine the file:\n{self.output_file}\n\n\n')