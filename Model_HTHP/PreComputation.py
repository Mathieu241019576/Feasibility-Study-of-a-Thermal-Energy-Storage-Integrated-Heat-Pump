from Model_HTHP.__init__ import *


"""
The class formats the inputs for the heat pump model:
	- Converts to SI units (if they are not already)
	- Computes the NTU-effectiveness values
	- Computes the heat capacity for the external fluids

"""


class PreComputation:
	def __init__(self, data):
		# Fluids
		self.fluid		= data['fluid']
		self.fluid_c	= data['fluid_c']
		self.fluid_e	= data['fluid_e']
		# inputs data in SI units
		self.r			= data['r']			# ∅
		self.n			= data['n']			# ∅
		self.Cv			= data['Cv']		# ∅
		self.P_ci		= data['P_ci']		# Pa
		self.ṁ_c		= data['ṁ_c']		# kg/s
		self.UA_cd		= data['UA_cd']		# W/°C = W/K
		self.P_ei		= data['P_ei']		# Pa
		self.ṁ_e		= data['ṁ_e']		# kg/s
		self.UA_ev		= data['UA_ev']		# W/°C = W/K
		self.ΔT_s		= data['ΔT_s']		# Δ°C = ΔK
		# inputs data to convert in SI units
		self.V			= data['V'] * 10 ** (-6)		# cm3 to m3
		self.ω			= data['ω'] * 2 * math.pi / 60	# rpm to rad/s
		self.T_ci		= data['T_ci'] + 273.15			# °C to K
		self.T_ei		= data['T_ei'] + 273.15			# °C to K


	def _get_prop(self, *args):
		# Safely call PropsSI from CoolProp and handle errors.
		try:
			return PropsSI(*args)
		except Exception as e:
			# print(f"CoolProp error with arguments {args}: {e}")
			return float('nan')


	@property
	def cp_e(self):
		return self._get_prop('Cpmass', 'T', self.T_ei, 'P', self.P_ei, self.fluid_e)


	@property
	def cp_c(self):
		return self._get_prop('Cpmass', 'T', self.T_ci, 'P', self.P_ci, self.fluid_c)


	@property
	def ε_cd(self):
		NTU = self.UA_cd / ( self.ṁ_c * self.cp_c )
		return 1 - math.exp(-NTU)


	@property
	def ε_ev(self):
		NTU = self.UA_ev / ( self.ṁ_e * self.cp_e )
		return 1 - math.exp(-NTU)


	def format_inputs(self):
		return {
			# Data for computation
			'fluid'	: self.fluid,	# Refrigirants
			'ΔTs'	: self.ΔT_s,	# Superheating
			'T_ei'	: self.T_ei,	# Temp of the external fluid into the evaporator
			'T_ci'	: self.T_ci,	# Temp of the external fluid into the condensor
			'ṁ_e'	: self.ṁ_e,		# Mass flow rate of the external fluid (evap)
			'ṁ_c'	: self.ṁ_c,		# Mass flow rate of the external fluid (cond)
			'cp_e'	: self.cp_e,	# Heat capacity of the external fluid (evap)	(computed here)
			'cp_c'	: self.cp_c,	# Heat capacity of the external fluid (cond)	(computed here)
			'ε_cd'	: self.ε_cd,	# Effectiveness from NTU of the condensor		(computed here)
			'ε_ev'	: self.ε_ev,	# Effectiveness from NTU of the evaporator		(computed here)
			'n'		: self.n,		# Polytropic index of the compressor
			'r'		: self.r,		# clearance volume ratio
			'Cv'	: self.Cv,		# volumetric coefficient
			'V'		: self.V,		# swept volume
			'ω'		: self.ω,		# rotation speed
			}