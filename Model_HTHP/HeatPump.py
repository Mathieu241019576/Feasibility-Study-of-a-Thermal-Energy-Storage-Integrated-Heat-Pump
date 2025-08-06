from Model_HTHP.__init__ import *


"""
The class compute the system of equations explained in the the article:
		'STEADY-STATE SIMULATION OF VAPOUR-COMPRESSION HEAT PUMPS'
		of
		T. B. HERBAS, E. C. BERLINCK, C. A. T URIU, R. P. MARQUES AND J. A. R. PARISE

inputs = {
	'fluid'	: ,		Refrigirants
	'ΔTs'	: ,		Superheating
	'T_ei'	: ,		Temp of the external fluid into the evaporator
	'T_ci'	: ,		Temp of the external fluid into the condensor
	'ṁ_e'	: ,		Mass flow rate of the external fluid (evap)
	'ṁ_c'	: ,		Mass flow rate of the external fluid (cond)
	'cp_e'	: ,		Heat capacity of the external fluid (evap)
	'cp_c'	: ,		Heat capacity of the external fluid (cond)
	'ε_cd'	: ,		Effectiveness from NTU of the condensor
	'ε_ev'	: ,		Effectiveness from NTU of the evaporator
	'n'		: ,		Polytropic index of the compressor
	'r'		: ,		clearance volume ratio
	'Cv'	: ,		volumetric coefficient
	'V'		: ,		swept volume
	'ω'		: ,		rotation speed
}

"""


class HeatPump:
	def __init__(self, inputs):
		self.fluid 	= inputs['fluid']
		self.ΔT_s	= inputs['ΔTs']
		self.T_ei	= inputs['T_ei']
		self.T_ci	= inputs['T_ci']
		self.ṁ_e	= inputs['ṁ_e']
		self.ṁ_c	= inputs['ṁ_c']
		self.cp_e	= inputs['cp_e']
		self.cp_c	= inputs['cp_c']
		self.ε_cd	= inputs['ε_cd']
		self.ε_ev	= inputs['ε_ev']
		self.n		= inputs['n']
		self.r		= inputs['r']
		self.Cv		= inputs['Cv']
		self.V		= inputs['V']
		self.ω		= inputs['ω']


	def _get_prop(self, *args):
		# Safely call PropsSI from CoolProp and handle errors.
		try:
			return PropsSI(*args)
		except Exception as e:
			# print(f"CoolProp error with arguments {args}: {e}")
			return float('nan')


	def _get_ṁ_f(self, P_cd, P_ev, ν_1):
		η_v = self.Cv * (1 + self.r * (1 - (P_cd / P_ev) ** (1 / self.n)))
		return (self.V * self.ω * η_v) / (ν_1 * 2 * math.pi)


	def _get_T_3(self, T_cd, P_cd, ṁ_f, h_lv_cd, T_2):
		'''
		# Approximate the c_p at their saturation values
		cp_f_l = self._get_prop('Cpmass', 'P', P_cd, 'Q', 0, self.fluid)
		cp_f_v = self._get_prop('Cpmass', 'P', P_cd, 'Q', 1, self.fluid)
		# Computation of T_3
		T_3 = T_cd - (1/cp_f_l)*(
			+ (self.ṁ_c/ṁ_f) * self.cp_c * self.ε_cd * (T_2 - self.T_ci)
			- h_lv_cd
			- cp_f_v * (T_2 - T_cd)
		)
		'''
		return T_cd


	def _get_x4(self, ṁ_f, T_ev, P_ev, h_lv_ev):
		# cp of the fluid in the evaporator
		# at the mean temp : (T_ev + T_1) / 2 = T_ev + (ΔT_s / 2)
		cp_f = self._get_prop('Cpmass', 'T', T_ev+self.ΔT_s/2, 'P', P_ev, self.fluid)
		# Computation of x4
		x4 = ( 1
			- (self.ṁ_e * self.cp_e * self.ε_ev * (self.T_ei - T_ev)) / (ṁ_f * h_lv_ev)
			+ cp_f * self.ΔT_s / h_lv_ev)
		return x4


	def _equations(self, vars):
		T_2, T_3, T_cd, T_ev = vars

		# Pressure (Pa)
		P_cd = self._get_prop('P', 'T', T_cd, 'Q', 0, self.fluid)
		P_ev = self._get_prop('P', 'T', T_ev, 'Q', 0, self.fluid)
		
		# Specific values (m3/kg)
		ν_1 = 1 / self._get_prop('D', 'P', P_ev, 'T', T_ev + self.ΔT_s, self.fluid)
		ν_2 = 1 / self._get_prop('D', 'P', P_cd, 'T', T_2, self.fluid)
		
		# Saturated enthalpies (J/kg)
		h_l_cd = self._get_prop('H', 'T', T_cd, 'Q', 0, self.fluid)
		h_v_cd = self._get_prop('H', 'T', T_cd, 'Q', 1, self.fluid)
		h_l_ev = self._get_prop('H', 'T', T_ev, 'Q', 0, self.fluid)
		h_v_ev = self._get_prop('H', 'T', T_ev, 'Q', 1, self.fluid)
		# Differences of enthalpies (J/kg)
		h_lv_ev = h_v_ev - h_l_ev
		h_lv_cd = h_v_cd - h_l_cd
		
		# Computation of ṁ_f and T_3
		ṁ_f = self._get_ṁ_f(P_cd, P_ev, ν_1)
		x4  = self._get_x4(ṁ_f, T_ev, P_ev, h_lv_ev)
		
		# Enthalpies (J/kg)
		h_1 = self._get_prop('H', 'P', P_ev, 'T', T_ev + self.ΔT_s, self.fluid)
		h_2 = self._get_prop('H', 'P', P_cd, 'T', T_2, self.fluid)
		h_3 = self._get_prop('H', 'T', T_3, 'Q', 0, self.fluid)
		h_4 = h_3
		
		# System of equations
		eq1 = (h_4 - h_l_ev) - h_lv_ev * (x4)
		eq2 = ν_2 - ν_1 * ((P_ev / P_cd) ** (1 / self.n))
		eq3 = ṁ_f * (h_2 - h_1) - self.ṁ_c * self.cp_c * self.ε_cd * (T_2 - self.T_ci) + self.ṁ_e * self.cp_e * self.ε_ev * (self.T_ei - T_ev)
		eq4 = ( T_3 - self._get_T_3(T_cd, P_cd, ṁ_f, h_lv_cd, T_2) ) + max(0, T_3-T_cd)

		return [eq1, eq2, eq3, eq4]


	def solve(self, initial_guess, verif):
		# fsolve from scipy to solve the 3 non-linear equations
		solution = fsolve(
			self._equations,
			initial_guess,
			maxfev=10000
		)

		# The residuals should be close to 0 (printed if asked)
		residuals = self._equations(solution)
		print([f"{abs(num):.3e}" for num in residuals]) if verif else None

		# Don't take into account results with too high residuals
		# Do not hesitate to modify the limit
		if max(abs(i) for i in residuals) > 1e-3 or abs(residuals[-1]) > 1e-20:
			return None
		else:
			return solution


# TEST for _test4.py


	def solve_v2(self, initial_guess):
		# fsolve from scipy to solve the 3 non-linear equations
		solution = fsolve(
			self._equations,
			initial_guess,
			maxfev=10000
		)

		# The residuals should be close to 0
		residuals = self._equations(solution)

		return solution, residuals