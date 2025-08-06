from Model_HTHP.__init__ 		 import *
from Model_HTHP.HeatPump 		 import *
from Model_HTHP.PostComputation  import *
from Model_HTHP.PreComputation	 import *
from Model_HTHP.ExcelToPython	 import *
from Interface.CreateSound		 import *


# Class 1 : Simulation for several fluids


class SeveralFluidsSimulation:
	# Main Variables:

		# var_name		=> The name of the variable parameter to be varied
		# 				This has to be set in the Excel input file
		# initial_guess	=> A list representing the initial guess for the non-linear system of equations
		# 				Format: [T_2, T_3, T_cd, T_ev] (in K)
		# list_outputs	=> A list containing the outputs for each fluid in the simulation
		# 				Format: [outputs for fluid 1, outputs for fluid 2, ...]

		# For each value of the variable parameter (var_name):
		# - solutions	=> A list containing the four temperatures that solve the non-linear system of equations
		# 				See details in HeatPump.py
		# - results		=> An object containing all heat pump parameters computed from the solutions
		# 				See details in PostComputation.py
		# - outputs		=> A dictionary that collects relevant heat pump parameters for plotting and analysis
		# 				For example, outputs do not need to contain the entropy at all points (results have this information)
		# - residuals	=> The differences between the left-hand side and right-hand side of the equations in the system
		# 				Residuals should be as close as possible to zero for accurate solutions


	def __init__(self, input_file, var_name,			# values to be set
			first_initial_guess = [370, 250, 330, 290],	# default values
			criteria_1	= 1e-3,							# default values
			criteria_2	= 1e-6,							# default values
			verif		= True,							# default values
			list_fluid	= [								# default values
			'R12', 'R134a', 'R113','R124','R142b', 'R21','R123','R161',
			'R152a', 'R236fa', 'R245fa','R245ca','R365mfc','R1234yf', 'R717',
			'R1234ze(E)', 'R1233zd(E)','R600a', 'R601a', 'R114','R1234ze(Z)'
			],
			):
		
		self.first_initial_guess = first_initial_guess
		self.list_fluid	= list_fluid
		self.input_file	= input_file
		self.var_name	= var_name
		self.criteria_1	= criteria_1
		self.criteria_2	= criteria_2
		self.verif		= verif


	def _computation(self, data, initial_guess):
		# Perform the main computation by solving the heat pump model for a given input and initial guess.
		
		inputs				= PreComputation(data).format_inputs()		# Format the inputs
		heat_pump_model		= HeatPump(inputs)							# See details of the model in the file HeatPump.py
		solution, residuals	= heat_pump_model.solve_v2(initial_guess)	# Solve the non linear system
		results				= PostComputation(inputs, solution)			# Values of the hp, computed thanks to the solutions
		
		return solution, residuals, results


	def _results_extraction(self, data, solution, results, outputs):
		# Extract key results from the computation and append them to the outputs dictionary.

		# Extract the solutions
		outputs['T_2'].append(solution[0]  -273.15)	# results in °C
		outputs['T_3'].append(solution[1]  -273.15)	# results in °C
		outputs['T_cd'].append(solution[2] -273.15)	# results in °C
		outputs['T_ev'].append(solution[3] -273.15)	# results in °C

		# Set the x axis of the graphs
		outputs[self.var_name].append(data[self.var_name])

		# If the COP is too high, do not take into account the results
		if results.COP > 50: raise Exception('COP Divergence')

		# Extract the post-computation results
		outputs['P_evap'].append(abs(results.power['evap']))
		outputs['P_cond'].append(abs(results.power['cond']))
		outputs['P_comp'].append(abs(results.power['comp']))
		outputs['ΔT_cd'].append(results.ΔT_cd)
		outputs['COP'].append(results.COP)
		outputs['ṁ_f'].append(results.ṁ_f)

		return outputs


	def _get_previous_solution(self, outputs, i):
		# Retrieve the solution from the previous iteration to use as the initial guess for better convergence.
		return [
			outputs['T_2'][i-1]  +273.15,	# initial guess in K
			outputs['T_3'][i-1]  +273.15,	# initial guess in K
			outputs['T_cd'][i-1] +273.15,	# initial guess in K
			outputs['T_ev'][i-1] +273.15	# initial guess in K
			]


	def _check_residuals(self, residuals):
		# Verify if the residuals meet the convergence criteria defined above.
		condition_1 = max(abs(r) for r in residuals) > self.criteria_1
		condition_2 = abs(residuals[-1]) 			 > self.criteria_2
		return condition_1 or condition_2


	def _get_outputs(self, data_list, fluid):
		# Compute and collect results for a specific fluid over a range of variable parameter values.

		outputs = {
			'T_cd': [], 'P_cond': [], 'COP'  : [],
			'T_ev': [], 'P_evap': [], 'ṁ_f'  : [],
			'T_2' : [], 'P_comp': [], 'ΔT_cd': [],
			'T_3' : [],
			self.var_name: [], 'fluid': fluid
			}
		errors = []
		i = 0

		for data in data_list:
			try:
				# STEP 1: Set the fluid
				data['fluid'] = fluid

				# STEP 2: Compute with the first initial guess
				solution, residuals, results = self._computation(data, self.first_initial_guess)

				# STEP 3: If the computation diverged, use the previous solution as initial guess
				if i != 0 and self._check_residuals(residuals):
					solution, residuals, results = self._computation(data, self._get_previous_solution(outputs, i))
					if i != 0 and self._check_residuals(residuals):
						solution, residuals, results = self._computation(data, solution)

				# STEP 4: Print residuals if verification is requested
				if self.verif:
					print([f"{abs(num):.3e}" for num in residuals])

				# STEP 5: Do not consider the computation if the results fail to meet the convergence criteria
				if self._check_residuals(residuals):
					raise Exception('Solutions Divergence')

				# STEP 6: Extract outputs from the results
				outputs = self._results_extraction(data, solution, results, outputs)

				i += 1

			except Exception as e:
				# print(e)
				# The computation may fail (pbm of convergence, not realistic inputs, ...)
				errors.append(data[self.var_name])

		print(f'Non computed values for {self.var_name} = {errors}\n') if errors else None

		return outputs


	def _plot_graphs(self, list_outputs):
			# Generate and display graphs comparing the heat pump parameters for different fluids.

			# Subplot with 2 rows and 2 columns
			fig = make_subplots(rows=2, cols=2, subplot_titles=(
				f'T_co (°C) vs {self.var_name}',
				f'COP vs {self.var_name}',
				f'Compressor Work (W) vs {self.var_name}',
				f'Condenser Heat Transfer (W) vs {self.var_name}'))

			# Set the colormap and Create a dictionary to map fluids to colors
			colors = px.colors.qualitative.Alphabet
			fluid_color_map = {outputs['fluid']: colors[i % len(colors)] for i, outputs in enumerate(list_outputs)}

			# Define line styles for different temperatures
			line_styles = {
				'T_cd': 'solid',
				'T_ev': 'dot',
				'T_2' : 'dash',
				'T_3' : 'dashdot'
			}

			# Create the graphs
			for outputs in list_outputs:
				fluid = outputs['fluid']
				color = fluid_color_map[fluid]

				# PLOT 1 for ΔT_cd
				fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['ΔT_cd'], mode='lines', name=f'{fluid}', line=dict(color=color, dash=line_styles['T_cd']), legendgroup=fluid, showlegend=True), row=1, col=1)

				# Filter the COP values
				y_filtered = [y for y in outputs['COP'] if y < 10]									# keep only values when COP < 10
				x_filtered = [x for x, y in zip(outputs[self.var_name], outputs['COP']) if y < 10]	# keep only values when COP < 10
				# PLOT 2 for COP
				fig.add_trace(go.Scatter(x=x_filtered, y=y_filtered, mode='lines', name=fluid, marker=dict(color=color), legendgroup=fluid, showlegend=False), row=1, col=2)

				# PLOT 3 for P_comp
				fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['P_comp'], mode='lines', name=fluid, marker=dict(color=color), legendgroup=fluid, showlegend=False), row=2, col=1)

				# PLOT 3 for ṁ_f
				fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['P_cond'], mode='lines', name=fluid, marker=dict(color=color), legendgroup=fluid, showlegend=False), row=2, col=2)
				
			# Set the layout
			fig.update_layout(height=800,width=1000,title_text='<b>Heat Pump Modelling Outputs<b>',font=dict(family="Times New Roman, serif", size=12), template='simple_white')

			# Show the plot
			fig.show()


	def run(self):

		print('Step 0 : Loading the input file')
		input_file = ExcelToPython(input_file=self.input_file)

		print('Step 1 : Loading the input data from the input file')
		input_data = input_file.get_data()

		print('Step 2 : Solving the heat pump model')
		list_outputs = []
		for i in self.list_fluid:
			print('\033[1m' + f'\nComputation for {i}' + '\033[0m')
			outputs = self._get_outputs(input_data, i)
			list_outputs.append(outputs)
		
		# Notify that the computations are finished
		CreateSound().sound1()
		
		print('Step 3 : Plot the graphs')
		self._plot_graphs(list_outputs)

		print('Step 4 : Write the results in the output file')
		input_file.write_fluid_results(list_outputs)
	

	def run_with_progress(self):
		print('Step 0 : Loading the input file')
		input_file = ExcelToPython(input_file=self.input_file)

		print('Step 1 : Loading the input data from the input file')
		input_data = input_file.get_data()

		print('Step 2 : Solving the heat pump model')
		list_outputs = []
		total_fluids = len(self.list_fluid)

		for idx, fluid in enumerate(self.list_fluid):
			# Compute
			print(f'\nComputation for {fluid}\n')
			outputs = self._get_outputs(input_data, fluid)
			list_outputs.append(outputs)

			# Calculate and yield progress
			progress = int((idx + 1) / total_fluids * 100) - 1
			yield progress

		# Notify that the computations are finished
		CreateSound().sound1()

		print('Step 3 : Plot the graphs (a web page will open, please wait)')
		self._plot_graphs(list_outputs)

		print('Step 4 : Write the results in the output file')
		input_file.write_fluid_results(list_outputs)

		# Final progress yield to ensure 100% is reached
		yield 100


# Class 2 : Simulation for one fluid


class OneFluidSimulation:
	# Main Variables:

		# var_name		=> The name of the variable parameter to be varied
		# 				This has to be set in the Excel input file
		# initial_guess	=> A list representing the initial guess for the non-linear system of equations
		# 				Format: [T_2, T_3, T_cd, T_ev] (in K)

		# For each value of the variable parameter (var_name):
		# - solutions	=> A list containing the four temperatures that solve the non-linear system of equations
		# 				See details in HeatPump.py
		# - results		=> An object containing all heat pump parameters computed from the solutions
		# 				See details in PostComputation.py
		# - outputs		=> A dictionary that collects relevant heat pump parameters for plotting and analysis
		# 				For example, outputs do not need to contain the entropy at all points (results have this information)
		# - residuals	=> The differences between the left-hand side and right-hand side of the equations in the system
		# 				Residuals should be as close as possible to zero for accurate solutions


	def __init__(self, input_file, var_name,				# Input value
			  first_initial_guess	= [370, 250, 330, 290], # Default value
			  verif					= True,					# Default value
			  criteria_1			= 1e-3,					# Default value
			  criteria_2			= 1e-6					# Default value
			  ):
		
		# Input values
		self.input_file	= input_file
		self.var_name	= var_name
		# Default values
		self.verif		= verif
		self.criteria_1	= criteria_1
		self.criteria_2	= criteria_2
		self.first_initial_guess = first_initial_guess


	def _computation(self, data, initial_guess):
		# Perform the main computation by solving the heat pump model for a given input and initial guess.

		inputs				= PreComputation(data).format_inputs()		# Format the inputs
		heat_pump_model		= HeatPump(inputs)							# See details of the model in the file HeatPump.py
		solution, residuals	= heat_pump_model.solve_v2(initial_guess)	# Solve the non linear system
		results				= PostComputation(inputs, solution)			# Values of the hp, computed thanks to the solutions
		
		return solution, residuals, results


	def _results_extraction(self, data, outputs, solution, results):
		# Extract key results from the computation and append them to the outputs dictionary.

		# Extract results
		outputs['T_2'].append(solution[0]-273.15)	# results in °C
		outputs['T_3'].append(solution[1]-273.15)	# results in °C
		outputs['T_cd'].append(solution[2]-273.15)	# results in °C
		outputs['T_ev'].append(solution[3]-273.15)	# results in °C
		# outputs['ΔT_lift'].append(solution[2] - solution[3])
		

		# Set the x axis of the graphs
		outputs[self.var_name].append(data[self.var_name])

		# Extract the post-computation results
		
		outputs['P_evap'].append(results.power['evap'])
		outputs['P_cond'].append(results.power['cond'])
		outputs['P_comp'].append(results.power['comp'])
		outputs['ΔT_lift'].append(results.ΔT_lift)
		outputs['ΔT_cd'].append(results.ΔT_cd)
		outputs['COP'].append(results.COP)
		outputs['ṁ_f'].append(results.ṁ_f)

		return outputs


	def _check_residuals(self, residuals):
		# Verify if the residuals meet the convergence criteria defined above.
		condition_1 = max(abs(r) for r in residuals) > self.criteria_1
		condition_2 = abs(residuals[-1]) 			 > self.criteria_2
		return condition_1 or condition_2


	def _get_previous_solution(self, outputs, i):
		# Retrieve the solution from the previous iteration to use as the initial guess for better convergence.
		return [
			outputs['T_2'][i-1]  +273.15,	# initial guess in K
			outputs['T_3'][i-1]  +273.15,	# initial guess in K
			outputs['T_cd'][i-1] +273.15,	# initial guess in K
			outputs['T_ev'][i-1] +273.15	# initial guess in K
			]
		

	def _get_outputs(self, data_list):
		# Compute and collect results for a specific fluid over a range of variable parameter values.

		outputs = {
			'T_cd': [], 'P_cond': [], 'COP'	   : [],
			'T_ev': [], 'P_evap': [], 'ṁ_f'	   : [],
			'T_2' : [], 'P_comp': [], 'ΔT_cd'  : [],
			'T_3' : [],				  'ΔT_lift': [],
			self.var_name: []
			}
		errors = []
		i = 0

		for data in data_list:
			try:
				# STEP 1: Compute
				solution, residuals, results = self._computation(data, self.first_initial_guess)

				# STEP 2: If the computation diverged, use the previous solution as initial guess
				if i != 0 and self._check_residuals(residuals):
					solution, residuals, results = self._computation(data, self._get_previous_solution(outputs, i))

				# STEP 3: Print residuals if verification is requested
				if self.verif:
					print([f"{abs(num):.3e}" for num in residuals])

				# STEP 4: Do not consider the computation if the results fail to meet the convergence criteria
				if self._check_residuals(residuals):
					raise Exception('Solutions Divergence')

				# STEP 5: Extract outputs from the results
				outputs = self._results_extraction(data, outputs, solution, results)

				i += 1

			except Exception as e:
				# print(e)
				# The computation may fail (pbm of convergence, not realistic inputs, ...)
				errors.append(data[self.var_name])

		print(f'Non computed values for {self.var_name} = {errors}\n') if errors else None

		return outputs


	def _plot_graphs(self, outputs):
		# Subplot with 2 rows and 2 columns
		fig = make_subplots(rows=2, cols=2, subplot_titles=(
			f'Temperature (°C) vs {self.var_name}',
			f'COP vs {self.var_name}',
			f'P_comp (W) vs {self.var_name}',
			f'ṁ_f (kg/s) vs {self.var_name}'))

		# PLOT 1 for Temperatures (T_cd, T_ev, T_2, T_3)
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['T_cd'], mode='markers', name='T_cd', showlegend=True, marker=dict(color='#78206E', size=5)), row=1, col=1)
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['T_ev'], mode='markers', name='T_ev', showlegend=True, marker=dict(color='#4E95D9', size=5)), row=1, col=1)
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['T_2'], mode='markers', name='T_2', showlegend=True, marker=dict(color='#0B3041', size=5)), row=1, col=1)

		# PLOT 2 for COP
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['COP'], mode='markers', showlegend=False, marker=dict(color='#0B3041', size=5)), row=1, col=2)

		# PLOT 3 for P_comp
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['P_comp'], mode='markers', showlegend=False, marker=dict(color='#0B3041', size=5)), row=2, col=1)

		# PLOT 3 for ΔT_cd
		fig.add_trace(go.Scatter(x=outputs[self.var_name], y=outputs['ṁ_f'], mode='markers', showlegend=False, marker=dict(color='#0B3041', size=5)), row=2, col=2)
		
		# Set the layout
		fig.update_layout(height=800,width=1000,title_text='<b>Heat Pump Simulation Outputs<b>',font=dict(family="Times New Roman, serif", size=12), template='simple_white')

		# Show the plot
		fig.show()


	def _plot_COP_graph(self, outputs):

		x_values = outputs['ΔT_lift']
		y_values = outputs['COP']

		def exponential_func(x, A, B):
			return A * np.exp(-B * x)

		# Ensure x_values and y_values are numpy arrays
		x_values = np.array(x_values)
		y_values = np.array(y_values)
		A, B = 7.07, 0.02

		# Generate the trend line
		trend_line = exponential_func(x_values, 7.07, 0.02)

		# Plot the data and the trend line
		plt.plot(x_values, y_values, label='Data')
		plt.plot(x_values, trend_line, '--', label=f'Trend line: COP = {A:.2f} * exp(-{B:.2f} * ΔT_lift)')
		plt.xlabel('ΔT_lift (K)')
		plt.ylabel('COP')
		plt.title('HTHP COP vs ΔT_lift')
		plt.legend()
		plt.show()


	def run_test2(self):

		print('Step 0: Loading the input file')
		input_file = ExcelToPython(input_file=self.input_file)

		print('Step 1: Loading the input data from the input file')
		input_data = input_file.get_data()
		
		print('Step 2: Solving the heat pump model')
		outputs = self._get_outputs(input_data)

		print('Step 3: Plot the results')
		self._plot_graphs(outputs)

		print('Step 4: Write the results in the output file')
		input_file.write_results(**outputs)


	def run_test3(self):

		print('Step 0: Loading the input file')
		input_file = ExcelToPython(input_file=self.input_file)

		print('Step 1: Loading the input data from the input file')
		input_data = input_file.get_data()
		
		print('Step 2: Solving the heat pump model')
		outputs = self._get_outputs(input_data)

		print('Step 3: Plot the results')
		self._plot_COP_graph(outputs)

		print('Step 4: Write the results in the output file')
		input_file.write_results(**outputs)
	

	def run_with_progress(self):

		print('Step 0: Loading the input file')
		input_file = ExcelToPython(input_file=self.input_file)
		yield 10

		print('Step 1: Loading the input data from the input file')
		input_data = input_file.get_data()
		yield 20
		
		print('Step 2: Solving the heat pump model')
		outputs = self._get_outputs(input_data)
		yield 80

		# Notify that the computations are finished
		CreateSound().sound1()

		print('Step 3: Plot the results (a web page will open, please wait)')
		self._plot_graphs(outputs)
		yield 90

		print('Step 4: Write the results in the output file')
		input_file.write_results(**outputs)
		yield 100