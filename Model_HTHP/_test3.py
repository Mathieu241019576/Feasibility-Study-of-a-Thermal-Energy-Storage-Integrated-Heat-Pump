from __init__	import *
from Simulation	import *


# _test3.py

	# Model of T. B. HERBAS, E. C. BERLINCK, C. A. T URIU, R. P. MARQUES AND J. A. R. PARISE
	# from 'STEADY-STATE SIMULATION OF VAPOUR-COMPRESSION HEAT PUMPS'

	# The aim is to plot the COP vs ΔT_lift
	# As it is down in the following website : https://high-temperature-heat-pumps.com/dashboard
	# Main aim : verify if the code can correctly predict HTHP behaviours
	
    # => see details in OneFluidSimulation.py


if __name__ == '__main__':
	
	input_file = 'Excel_Inputs/Inputs_T3a.xlsx'
	var_name = 'T_ci'

	OneFluidSimulation(input_file, var_name).run_test3()