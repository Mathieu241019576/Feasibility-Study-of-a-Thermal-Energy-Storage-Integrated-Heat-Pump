from __init__ import *

'''
This script is used to plot:
The specific heat at constant pressure (c_p in J/kg.°C) VERSUS The temperature (T in °C)

The inputs parameters are:
- the fluids
- the pressure

See the end of the script to run it
'''

class SpecificHeatGraph:
	def __init__(self, fluids, pressure):
		self.fluids = fluids
		self.pressure = pressure


	def _calculate_cp(self, fluid):
		# Get saturation temperature
		T_sat = PropsSI('T', 'P', self.pressure, 'Q', 0, fluid)

		# Define temperature ranges
		T_min = PropsSI('Tmin', fluid)
		T_max = PropsSI('Tmax', fluid)
		T_gas_list = np.linspace(T_sat+1, T_max, 500)  # Gas phase
		T_liq_list = np.linspace(T_min, T_sat-1, 500)  # Liquid phase

		# Initialize lists for specific heat capacities
		cp_gas	 = []
		cp_liq	 = []
		temp_gas = []
		temp_liq = []

		# Calculate specific heat capacities for the gas phase
		for T in T_gas_list:
			try:
				cp = PropsSI('CPMASS', 'T', T, 'P', self.pressure, fluid)
				cp_gas.append(cp)
				temp_gas.append(T-273.15)
			except ValueError:
				continue

		# Calculate specific heat capacities for the liquid phase
		for T in T_liq_list:
			try:
				cp = PropsSI('CPMASS', 'T', T, 'P', self.pressure, fluid)
				cp_liq.append(cp)
				temp_liq.append(T-273.15)
			except ValueError:
				continue

		return temp_gas, cp_gas, temp_liq, cp_liq, T_sat-273.15


	def plot(self):

		num_fluids = len(self.fluids)
		fig, axes = plt.subplots(num_fluids, 1, figsize=(10, 3 * num_fluids))  # Adjust size based on the number of fluids

		# If only one fluid is given, axes will not be an array, so we handle that case
		if num_fluids == 1:
			axes = [axes]

		for idx, fluid in enumerate(self.fluids):
			temp_gas, cp_gas, temp_liq, cp_liq, T_sat = self._calculate_cp(fluid)

			# Plot gas and liquid phases
			axes[idx].plot(temp_gas, cp_gas, label='Gas Phase', color='red')
			axes[idx].plot(temp_liq, cp_liq, label='Liquid Phase', color='blue')

			# Add a vertical line for the saturation temperature
			axes[idx].axvline(T_sat, color='black', linestyle='--', label=f"Saturation Temperature ({T_sat:.2f} °C)")

			# Add labels, title, and legend
			axes[idx].set_title(f"{fluid}")
			axes[idx].set_xlabel("T (°C)")
			axes[idx].set_ylabel("c_p [J/(kg·°C)]")
			axes[idx].legend(loc='upper left', bbox_to_anchor=(1, 1))
			axes[idx].grid()

		# Adjust layout for better spacing
		plt.tight_layout()
		plt.show()


# Run the code


if __name__ == '__main__':
	
	fluids	 = ['water', 'air']
	pressure = 10*101325 # Pa
	plotter	 = SpecificHeatGraph(fluids, pressure)

	plotter.plot()
