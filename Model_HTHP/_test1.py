from __init__ 		 import *
from HeatPump 		 import *
from PostComputation import *
from PreComputation	 import *
from ExcelToPython	 import *


# _test1.py

	# Data and Model of T. B. HERBAS, E. C. BERLINCK, C. A. T URIU, R. P. MARQUES AND J. A. R. PARISE
	# from 'STEADY-STATE SIMULATION OF VAPOUR-COMPRESSION HEAT PUMPS'

	# Aim to plot reproduce the graph of the reference articles
	# Plot for R134a then R12:
	# - The theoritical temperatures (T_2, T_cd, T_ev) vs T_ci
	# - The model temperatures (T_2, T_cd, T_ev) vs T_ci
	# - The error between model and literature


def get_results_geometries(data_list, fluid, verif=False):

	T_2, T_3, T_cd, T_ev, T_ci, P_evap, P_cond, P_comp, ΔT_cd, COP = [], [], [], [], [], [], [], [], [], []
	errors = []

	for data in data_list:
		try:
			# Set the fluid
			data['fluid'] = fluid

			# Compute
			inputs			= PreComputation(data).format_inputs()			# Format the inputs
			heat_pump_model	= HeatPump(inputs)								# See details of the model in the file HeatPump.py
			initial_guess	= [370, 250, 330, 290]							# Initial guesses for T_2, T_3, T_cd, T_ev (in K)
			solution		= heat_pump_model.solve(initial_guess, verif)	# solve
			results			= PostComputation(inputs, solution)				# Formath the outputs

			# Extract results
			T_2.append(solution[0]-273.15)	# results in °C
			T_3.append(solution[1]-273.15)	# results in °C
			T_cd.append(solution[2]-273.15)	# results in °C
			T_ev.append(solution[3]-273.15)	# results in °C
			T_ci.append(data['T_ci'])		# x axis of the plot

			# Extract the post-computation results
			P_evap.append(abs(results.power['evap']))
			P_cond.append(abs(results.power['cond']))
			P_comp.append(abs(results.power['comp']))
			ΔT_cd.append(results.ΔT_cd)
			COP.append(results.COP)

		except Exception as e:
			print(e)
			# The computation may fail (pbm of convergence, not realistic inputs, ...)
			errors.append(data['T_ci'])

	print(f'Non computed values for T_ci = {errors}\n') if errors else None

	return {'T_2'	 : T_2,
		 	'T_3'	 : T_3,
			'T_cd'	 : T_cd,
			'T_ev'	 : T_ev,
			'T_ci'	 : T_ci,
			'P_evap' : P_evap,
			'P_cond' : P_cond,
			'P_comp' : P_comp,
			'ΔT_cd'	 : ΔT_cd,
			'COP'	 : COP,
			'fluid'	 : fluid}


def multiple_graph(list_results):
	# Theoretical values
	theoretical_values = {
		'R134a': {
			'T_2': {'x': [25.28736, 39.36782, 54.71265], 'y': [115.33619, 136.42347, 160.34335]},
			'T_cd': {'x': [25.11494, 40.17241, 54.71265], 'y': [55.85122, 67.49644, 78.82691]},
			'T_ev': {'x': [25.05747, 40.91954, 54.36782], 'y': [2.97569, 2.34623, 1.71674]}
		},
		'R12': {
			'T_2': {'x': [25.28736, 40.4023, 55.11495], 'y': [101.1731, 119.11302, 134.53506]},
			'T_cd': {'x': [25.17241, 39.5977, 55], 'y': [54.59228, 64.97855, 75.99429]},
			'T_ev': {'x': [25.11494, 40.74713, 54.82759], 'y': [4.23464, 4.8641, 4.54937]}
		}
	}

	# Set the colors
	colors = {
		'T_cd': '#D91656',
		'T_ev': '#640D5F',
		'T_2' : '#EB5B00'
	}

	# Create subplots
	fig = make_subplots(
		rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.2,
		subplot_titles=(
			'<b>R134a</b>', '<b>Absolute average error for R134a</b>',
			'<b>R12</b>', '<b>Absolute average error for R12</b>'
		)
	)

	# Plot
	for results in list_results:

		fluid = results['fluid']
		row = 1 if fluid == 'R134a' else 2

		x = results['T_ci']
		y_1 = results['T_cd']
		y_2 = results['T_ev']
		y_3 = results['T_2']

		# Plot for each fluid the 3 lines with legends
		fig.add_trace(go.Scatter(x=x, y=y_1, mode='lines', name=f'{fluid} T_cd', line=dict(dash='solid', color=colors['T_cd']), showlegend=False), row=row, col=1)
		fig.add_trace(go.Scatter(x=x, y=y_2, mode='lines', name=f'{fluid} T_ev', line=dict(dash='solid', color=colors['T_ev']), showlegend=False), row=row, col=1)
		fig.add_trace(go.Scatter(x=x, y=y_3, mode='lines', name=f'{fluid} T_2', line=dict(dash='solid', color=colors['T_2']), showlegend=False), row=row, col=1)

		# Plot theoretical values for the fluid with legends
		fig.add_trace(go.Scatter(x=theoretical_values[fluid]['T_cd']['x'], y=theoretical_values[fluid]['T_cd']['y'], mode='lines', name=f'{fluid} Theoretical T_cd', line=dict(dash='dash', color=colors['T_cd']), showlegend=False), row=row, col=1)
		fig.add_trace(go.Scatter(x=theoretical_values[fluid]['T_ev']['x'], y=theoretical_values[fluid]['T_ev']['y'], mode='lines', name=f'{fluid} Theoretical T_ev', line=dict(dash='dash', color=colors['T_ev']), showlegend=False), row=row, col=1)
		fig.add_trace(go.Scatter(x=theoretical_values[fluid]['T_2']['x'], y=theoretical_values[fluid]['T_2']['y'], mode='lines', name=f'{fluid} Theoretical T_2', line=dict(dash='dash', color=colors['T_2']), showlegend=False), row=row, col=1)

		delta_y = {}
		for temp in ['T_cd', 'T_ev', 'T_2']:
			# Interpolate the theoritical values
			x_theo = np.array(theoretical_values[fluid][temp]['x'])
			y_theo = np.array(theoretical_values[fluid][temp]['y'])
			y_theo_interp = np.interp(x, x_theo, y_theo)

			# Compute the difference between the theoritical and the model values
			delta_y[temp] = y_theo_interp - np.array(results[temp])
			delta_y[temp] = [abs(i) for i in delta_y[temp]]

		# Calculate the average delta_y across all temperature types
		avg_delta_y = np.mean([delta_y['T_cd'], delta_y['T_ev'], delta_y['T_2']], axis=0)

		# Plot the average error
		fig.add_trace(go.Scatter(x=x, y=avg_delta_y, mode='lines', name=f'Average error', line=dict(dash='dot', color='black'), showlegend=False), row=row, col=2)

	# Custom legend entries
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='Literature values', line=dict(dash='dash', color='black')))
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='Modeled values', line=dict(dash='solid', color='black')))
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='Absolute average error (°C)', line=dict(dash='dot', color='black')))
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='T_2', line=dict(color=colors['T_2'])))
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='T_cd', line=dict(color=colors['T_cd'])))
	fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name='T_ev', line=dict(color=colors['T_ev'])))

	# Set the axis
	fig.update_xaxes(title_text="T_ci (°C)", row=1, col=1)
	fig.update_xaxes(title_text="T_ci (°C)", row=2, col=1)
	fig.update_xaxes(title_text="T_ci (°C)", row=1, col=2)
	fig.update_xaxes(title_text="T_ci (°C)", row=2, col=2)
	fig.update_yaxes(title_text="Temperature (°C)", range=[-20, 200], row=1, col=1)
	fig.update_yaxes(title_text="Temperature (°C)", range=[-20, 200], row=2, col=1)
	fig.update_yaxes(title_text="Average error (°C)", range=[-20, 200], row=1, col=2)
	fig.update_yaxes(title_text="Average error (°C)", range=[-20, 200], row=2, col=2)

	# Update layout for font, legend position, and size
	fig.update_layout(
		title='<b>Comparison of modeled values with literature values<b>',
		font=dict(family="Times New Roman"),
		template='simple_white',
		legend=dict(
			x=1.05,
			y=1,
			traceorder="normal",
			font=dict(family="Times New Roman", size=12, color="black")
		),
		width=1000,	# Reduce the width of the plot
		height=800	# Adjust the height if necessary
	)

	fig.show()


if __name__ == '__main__':

	# Run

	print('\nStep 0 : Loading the input file')
	input_file = ExcelToPython(input_file=f'Excel_Inputs/Inputs_T1.xlsx')

	print('\nStep 1 : Loading the input data from the input file')
	input_data = input_file.get_data()

	print('\nStep 2 : Solving the heat pump model')
	list_results = []
	for i in ['R12','R134a']:

		print('\033[1m' + f'\nComputation for {i}' + '\033[0m')
		outputs = get_results_geometries(input_data, i, verif=True)

		list_results.append(outputs)

	print('Step 3 : Plot the graphs')
	multiple_graph(list_results)

	print('\nStep 4 : Write the results in the output file')
	input_file.write_fluid_results(list_results)
