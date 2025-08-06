from Model_HTHP.__init__ import *


"""
This class performs post-processing calculations for a heat pump model.

Using the results from the heat pump model, it can compute:
	- All the properties (P, T, h, s) at each point of the heat pump (1, 2, 3, 4)
    - All the power outputs of the heat pump (evaporator, compressor, condenser)
    - The Coefficient of Performance (COP)
	- The mass flow rate of the working fluid (ṁ_f)
	- ...

"""


class PostComputation:
	def __init__(self, inputs, solution):
		# data from the inputs
		self.fluid	= inputs['fluid']
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
		# data from the solution
		self.T_2	= solution[0]
		self.T_3	= solution[1]
		self.T_cd	= solution[2]
		self.T_ev	= solution[3]


	def _get_prop(self, *args):
		"""
		Safely call PropsSI from CoolProp and handle errors.
		"""
		try:
			return PropsSI(*args)
		except Exception as e:
			# print(f"CoolProp error with arguments {args}: {e}")
			return float('nan')	# Return NaN for invalid property calls


	@property
	def P_cd(self):
		return self._get_prop('P', 'T', self.T_cd, 'Q', 0, self.fluid)


	@property
	def P_ev(self):
		return self._get_prop('P', 'T', self.T_ev, 'Q', 0, self.fluid)


	@property
	def ṁ_f(self):
		ν_1 = 1 / self._get_prop('D', 'P', self.P_ev, 'T', self.T_ev + self.ΔT_s, self.fluid)
		η_v = self.Cv * (1 + self.r * (1 - (self.P_cd / self.P_ev) ** (1 / self.n)))

		return (self.V * self.ω * η_v) / (ν_1 * 2 * math.pi)


	def _get_thermodynamic_state(self, pt):
		# STEP 1: associate to each point the corresponding T and P
		state_points = {
			'1': {'P':self.P_ev, 'T':self.T_ev+self.ΔT_s},
			'2': {'P':self.P_cd, 'T':self.T_2},
			'3': {'P':self.P_cd, 'T':self.T_3},
			'4': {'P':self.P_ev, 'T':self.T_ev}
		}

		# STEP 2: define the state of the fluid for each point
		def point1():
			P = state_points['1']['P']
			T = state_points['1']['T']
			h = self._get_prop('H', 'P', P, 'T', T, self.fluid)
			s = self._get_prop('S', 'P', P, 'T', T, self.fluid)
			return {'h':h, 's':s, 'T':T, 'P':P}

		def point2():
			P = state_points['2']['P']
			T = state_points['2']['T']
			h = self._get_prop('H', 'P', P, 'T', T, self.fluid)
			s = self._get_prop('S', 'P', P, 'T', T, self.fluid)
			return {'h':h, 's':s, 'T':T, 'P':P}

		def point3():
			P = state_points['3']['P']
			T = state_points['3']['T']
			h = self._get_prop('H', 'Q', 0, 'T', T, self.fluid)
			s = self._get_prop('S', 'Q', 0, 'T', T, self.fluid)
			return {'h':h, 's':s, 'T':T, 'P':P}

		def point4():
			P = state_points['4']['P']
			T = state_points['4']['T']
			h = point3()['h'] # Isenthalpic process
			s = self._get_prop('S', 'P', P, 'H', h, self.fluid)
			return {'h':h, 's':s, 'T':T, 'P':P}
	
		point_functions = {'1': point1, '2': point2, '3': point3, '4': point4}
		return point_functions.get(pt, lambda: None)()


	def _get_power(self, p_in, p_out):
		h_in	= self.point[p_in]['h']
		h_out	= self.point[p_out]['h']
		Ẇ		= self.ṁ_f * abs(h_out - h_in)
		return Ẇ


	@property
	def point(self):
		return {
			'1': self._get_thermodynamic_state(pt='1'),
			'2': self._get_thermodynamic_state(pt='2'),
			'3': self._get_thermodynamic_state(pt='3'),
			'4': self._get_thermodynamic_state(pt='4')
		}


	@property
	def power(self):
		return {
			'evap': self._get_power('4', '1'),
			'cond': self._get_power('2', '3'),
			'comp': self._get_power('1', '2')
		}


	@property
	def COP(self):
		return self.power['cond'] / self.power['comp']


	@property
	def ΔT_cd(self):
		# ΔT_cd = T_co - T_ci
		# Should be maximized
		ΔT_cd = self.ε_cd * (self.T_2 - self.T_ci)
		T_co = ΔT_cd + self.T_ci
		return T_co - 273.15

		'''
		Q̇ = self.ṁ_c * self.cp_c * self.ε_cd * (self.T_2 - self.T_ci)
		T_co = self.T_ci + (Q̇/(self.ṁ_c*self.cp_c))
		return T_co - self.T_ci
		'''


	@property
	def ΔT_lift(self):
		T_co = ( self.ε_cd * (self.T_2 - self.T_ci) ) + self.T_ci
		ΔT_lift = T_co - self.T_ei
		return ΔT_lift