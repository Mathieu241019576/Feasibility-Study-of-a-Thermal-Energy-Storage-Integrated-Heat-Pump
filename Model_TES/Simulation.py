from Model_TES.__init__				import *
from Model_TES.ThermalEnergyStorage import *
from Interface.CreateSound          import *



class Simulation:
	def __init__(self, inputs,
				A_pv_initial_guess=100,
				A_pv_bounds=(100, 10000),
				E_start_bounds=(0, None)):
		# Inputs to be set
		self.inputs = inputs
		# Default values
		self.A_pv_initial_guess = A_pv_initial_guess
		self.A_pv_bounds		= A_pv_bounds
		self.E_start_bounds		= E_start_bounds
		

	def _find_A_pv(self):
		
		# By default computation starts with E_start = 0 J
		E_start = 0

		def objective(A_pv):
			TES = ThermalEnergyStorage(self.inputs, A_pv, E_start)	# Compute the TES
			return TES.storage_volume								# Minimize the storage volume

		# Run optimization
		result = minimize(
			fun=objective,
			x0=[self.A_pv_initial_guess],	# Initial guess for A_pv
			bounds=[self.A_pv_bounds],		# Bounds for A_pv
			method='Nelder-Mead'			# Optimization method
		)

		# Result of the minimization
		optimized_A_pv = result.x[0]

		return optimized_A_pv


	def _find_E_start(self, A_pv):

		# Step 1: Compute the PV area (with 0 J of energy stored at the start)
		E_start = 0

		# Step 2: Calculate the required E_start value in order to ensure that the storage is never empty.
		TES_initial	 = ThermalEnergyStorage(self.inputs, A_pv, E_start)		# TES computation if E_start = 0
		Q_stored_min = min(TES_initial.Q_stored)							# Find the min value of stored energy and ensure it is > 0
		E_start		 = -Q_stored_min + 1000 if Q_stored_min < 0 else 0		# add a safety factor of 1000 J

		return E_start
	

	def run(self, display=True):

		# Step 1: find A_pv
		A_pv = self._find_A_pv()

		# Step 2: find E_start
		E_start = self._find_E_start(A_pv)

		# Step 3: Compute the TES with the minimized values
		TES = ThermalEnergyStorage(self.inputs, A_pv, E_start)

		# Display the results if asked:
		if display:
			print("\nRESULTS\n")
			print(f"Minimized A_pv:\t\t{A_pv:.2f} m²")
			print(f"Required E_start:\t{E_start:.2e} J")
			print(f"Storage volume:\t\t{TES.storage_volume:.2f} m³")
			print(f"Storage cube lenght:\t{TES.storage_lenght:.2f} m")
			print(f"Is the TES never empty? {min(TES.Q_stored>0)}\n")
		
		return A_pv, E_start, TES




	# This does not work, as it is unable to find a better solution than the one previously found.
	def _optimize(self, sound=True):

		A_pv_initial_guess	  = self._find_A_pv()
		E_start_initial_guess = self._find_E_start(A_pv_initial_guess)

		def objective(x):
			A_pv = x[0]		# Extract A_pv from the input list
			E_in = x[1]		# Extract E_in from the input list
			TES = ThermalEnergyStorage(self.inputs, A_pv, E_in)
			return TES.storage_volume

		def constraint(x):
			A_pv = x[0]											# Extract A_pv from the input list
			E_in = x[1]											# Extract E_in from the input list
			TES = ThermalEnergyStorage(self.inputs, A_pv, E_in)	# Compute the TES
			return min(TES.Q_stored)							# Ensure Q_stored is always > 0

		# Define constraints
		constraints = {'type': 'ineq', 'fun': constraint}

		# Run optimization
		result = minimize(
			fun=objective,
			x0=[A_pv_initial_guess, E_start_initial_guess],	# Initial guesses
			bounds=[self.A_pv_bounds, self.E_start_bounds],	# Bounds
			constraints=constraints,						# Constraints
			method='trust-constr'							# Optimization method
		)

		# Notify when computation finished
		CreateSound().sound1() if sound else None

		optimized_A_pv = result.x[0]
		optimized_E_in = result.x[1]
		minimized_storage_volume = result.fun

		print(f"Optimized A_pv: {optimized_A_pv:.2f} m²")
		print(f"Optimized E_in: {optimized_E_in:.2f} J")
		print(f"Minimized Storage Volume: {minimized_storage_volume:.2f} m³")

		return optimized_A_pv, optimized_E_in, minimized_storage_volume
