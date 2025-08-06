from __init__	import *
from Simulation	import *


# _test2.py

	# Model of T. B. HERBAS, E. C. BERLINCK, C. A. T URIU, R. P. MARQUES AND J. A. R. PARISE
	# from 'STEADY-STATE SIMULATION OF VAPOUR-COMPRESSION HEAT PUMPS'

	# Main Objective: Validate the model predictions by comparing them to experimental values.
	# Reference for experimental values: https://www.sciencedirect.com/science/article/pii/S0196890417308944?ref=pdf_download&fr=RR-2&rr=942ddb261ea1b881

	# This code is the most basic form of the HP modeling, with the following features:
	# - Allows selection of a variable (which will correspond to the x-axis of the graphs)
	# - Plots temperatures, COP, compressor power, and mass flow rate
	# - Requires the input Excel file to be correctly filled out

	# => see details in OneFluidSimulation.py


if __name__ == '__main__':

	input_file = 'Excel_Inputs/Inputs_T2.xlsx'
	var_name = 'T_ci'

	OneFluidSimulation(input_file, var_name).run_test2()


