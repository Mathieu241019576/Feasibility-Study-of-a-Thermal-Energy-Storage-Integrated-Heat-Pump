from __init__	import *
from Simulation	import *


# _test4.py

	# Model of T. B. HERBAS, E. C. BERLINCK, C. A. T URIU, R. P. MARQUES AND J. A. R. PARISE
	# from 'STEADY-STATE SIMULATION OF VAPOUR-COMPRESSION HEAT PUMPS'

	# Test 1 could
	# - only compute for one fluid
	# - only vary T_ci among the inputs.
	# Test 4 aims to:
	# - compute for several fluids
	# - vary other inputs

	# For example:
	# - In the Excel file, vary the compressor volume V (fix the other values)
	# - In the Python file, indicate which input is variable (here var_name = 'V')
	# => The code will plot the graphs as a function of V

	# Caution!
	# For this code, you do not need to specify a fluid in the Excel input file
	# Simply enter "_" in the fluid field
	# The code will automatically test several possible fluids

	# => see details in SeveralFluidsSimulation.py


if __name__ == '__main__':

	input_file	= 'Excel_Inputs/Inputs_T4_sizing_plot.xlsx'
	var_name	= 'V'
	list_fluid	= [
		'R12', 'R134a','R124','R142b', 'R21','R161',
		'R152a', 'R236fa', 'R245fa','R245ca','R365mfc','R1234yf', 'R717',
		'R1234ze(E)', 'R1233zd(E)','R600a', 'R114','R1234ze(Z)'
		]

	SeveralFluidsSimulation(input_file, var_name, list_fluid=list_fluid).run()
