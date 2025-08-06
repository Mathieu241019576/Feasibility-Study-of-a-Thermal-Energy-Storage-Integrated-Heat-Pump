from __init__ import *

'''
This script is used to plot:
The pressure (P in Pa) VERSUS The enthalpy (kJ/kg)

The inputs parameters are:
- fluid (str): The name of the fluid (compatible with CoolProp)
- isothermal (bool): Indicates whether isothermal lines should be displayed
- isentropic (bool): Indicates whether isentropic lines should be displayed.
- step_T / step_s (int): Indicated the step between each isothermal/isentropic lines

See the end of the script to run it
'''

class PhGraph:
	def __init__(self, fluid, isothermal=True, isentropic=True, coolprop_info=True, step_T=25, step_s=50):
		
		self.fluid = fluid
		self.Tmin  = PropsSI('Tmin', self.fluid)  # min temp in coolprop
		self.Tcrit = PropsSI('Tcrit', self.fluid) # max temp of substance in liquid state
		self.Tmax  = PropsSI('Tmax', self.fluid)  # max temp in coolprop
		
		sat_val = self._saturated_values()
		self.H_liquid = sat_val.get('H_liquid')
		self.P_liquid = sat_val.get('P_liquid')
		self.H_vapor  = sat_val.get('H_vapor')
		self.P_vapor  = sat_val.get('P_vapor')
		self.Hcrit 	  = sat_val.get('Hcrit')
		self.Pcrit 	  = sat_val.get('Pcrit')
		
		self.isothermal		= isothermal
		self.isentropic		= isentropic
		self.coolprop_info	= coolprop_info
		self.step_T			= step_T
		self.step_s			= step_s


	def _saturated_values(self):

		temperatures = np.linspace(self.Tmin, self.Tcrit, 100)

		P_liquid = []
		H_liquid = []
		P_vapor  = []
		H_vapor  = []

		for T in temperatures:
			P_liquid.append(PropsSI("P", "T", T, "Q", 0, self.fluid))       # Saturated liquid pressure (Q=0) in Pa
			H_liquid.append(PropsSI("H", "T", T, "Q", 0, self.fluid)/1000)  # Saturated liquid enthalpy (Q=0) in kJ/kg
			P_vapor.append(PropsSI("P", "T", T, "Q", 1, self.fluid))        # Saturated vapor pressure  (Q=1) in Pa
			H_vapor.append(PropsSI("H", "T", T, "Q", 1, self.fluid)/1000)   # Saturated vapor enthalpy  (Q=1) in kJ/kg
		
		P_liquid = np.array(P_liquid)   # Logarithmic scale
		P_vapor = np.array(P_vapor)     # Logarithmic scale

		Pcrit = PropsSI("Pcrit", self.fluid)
		Hcrit = PropsSI("H", "T", self.Tcrit, "P", Pcrit, self.fluid)/1000

		return {'P_liquid':P_liquid,
				'H_liquid':H_liquid,
				'P_vapor' :P_vapor,
				'H_vapor' :H_vapor,
				'Pcrit':Pcrit,
				'Hcrit':Hcrit}


	def _add_isothermal_lines(self, step=20):

		temp_range = np.arange(self.Tmin + (step - self.Tmin % step), self.Tmax - self.Tmax % step + 1, step)

		for T in temp_range:
			P_isothermal = []
			H_isothermal = []
			
			# For the given constant T, compute the lists for x-axis (h) and y-axis (P)
			for P in np.logspace(np.log10(min(self.P_liquid)), np.log10(max(self.P_liquid)), 100):
				try:
					H = PropsSI("H", "P", P, "T", T, self.fluid)/1000  # Enthalpy in kJ/kg
					P_isothermal.append(P)
					H_isothermal.append(H)
				except ValueError:
					continue 
			
			if P_isothermal and H_isothermal: 
				plt.plot(H_isothermal, P_isothermal, linestyle="--", color='black', linewidth=0.5)
				plt.text(H_isothermal[-1], P_isothermal[-1], f'{T:.2f} K', color='black', fontsize=5)


	def _add_isentropic_lines(self, step=20):

		S_min = PropsSI("S", "T", self.Tcrit, "Q", 0, self.fluid)
		S_max = PropsSI("S", "T", self.Tmax, "P", max(self.P_liquid), self.fluid)
		entropies = np.arange(S_min + (step - S_min % step), S_max - S_max % step + 1, step)
		
		for S in entropies:
			P_isentropic = []
			H_isentropic = []

			# For the given constant s, compute the lists for x-axis (h) and y-axis (P)
			for P in np.logspace(np.log10(min(self.P_liquid)), np.log10(max(self.P_liquid)), 100):
				try:
					H = PropsSI("H", "P", P, "S", S, self.fluid) / 1000  # Enthalpy in kJ/kg
					P_isentropic.append(P)
					H_isentropic.append(H)
				except ValueError:
					continue  

			if P_isentropic and H_isentropic:
				plt.plot(H_isentropic, P_isentropic, linestyle="--", color='green', linewidth=0.5)
				plt.text(H_isentropic[30], P_isentropic[30], f'{S / 1000:.2f} kJ/kg·K', color='green', fontsize=5, rotation=60, ha='center')


	def display(self):

		plt.rcParams['font.family'] = 'Times New Roman'
		plt.style.use('seaborn-v0_8-dark-palette')

		# Plot the Ph diagram
		plt.figure(figsize=(10, 6))
		plt.semilogy(self.H_liquid, self.P_liquid, label="Saturated Liquid (Q=0)", color="blue")
		plt.semilogy(self.H_vapor, self.P_vapor, label="Saturated Vapor (Q=1)", color="red")

		# Label the critical point
		plt.scatter([self.Hcrit], [self.Pcrit], color="black", label="Critical Point", zorder=5)

		# Add the options
		self._add_isothermal_lines(step=self.step_T) if self.isothermal else None
		self._add_isentropic_lines(step=self.step_s) if self.isentropic else None

		# Customize the plot
		plt.title(f"Ph Diagram for {self.fluid}")
		plt.xlabel("Specific Enthalpy (h in kJ/kg)")
		plt.ylabel("Pressure (P in Pa)")
		plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
		plt.grid(False)
		plt.tight_layout()
		plt.xlim(min(self.H_liquid)-10, max(self.H_vapor)+100)

		plt.show()


# Run the code


if __name__ == '__main__':
	
	fluid1 = 'R12'
	fluid2 = 'R134a'
	fluid3 = 'R1234ze(E)'
	fluid = 'water'

	PhGraph(fluid, isothermal=True, isentropic=True).display()