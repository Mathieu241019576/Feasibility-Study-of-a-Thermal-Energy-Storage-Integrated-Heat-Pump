from Model_TES.__init__ import *


class ThermalEnergyStorage:
	def __init__(self, inputs, A_pv, E_start, file_path='Csv_Inputs/PV-data.csv'):

		self.file_path	= file_path

		# Side 1 : TE Storage
		self.fluid_s = inputs['fluid_s']
		self.ṁ_s	 = inputs['ṁ_s']
		self.P_s	 = inputs['P_s']
		self.T_s_min = inputs['T_s_min'] + 273.15	# in K
		# self.COP	 = inputs['COP']				# To replace by a function !
	
		# Side 2 : Process
		self.fluid_p	= inputs['fluid_p']
		self.ṁ_p		= inputs['ṁ_p']
		self.P_p		= inputs['P_p']
		self.T_pi		= inputs['T_pi'] + 273.15	# in K
		self.T_po		= inputs['T_po'] + 273.15	# in K
		self.t_p_start	= inputs['t_p_start']		# Process start hour
		self.t_p_end	= inputs['t_p_end']			# Process end hour
		self.a, self.b	= inputs['COP']

		# Side 3 : PV power plant
		self.A_pv		= A_pv				# Area of the solar panels
		self.E_start	= E_start			# Energy stored at the start

		# Efficiencies
		self.η_pv	= inputs['η_pv']
		self.η_mec	= inputs['η_mec']
		self.η_elec	= inputs['η_elec']


	def _csv_extracter(self):
		format_time = '%Y%m%d:%H%M'
		pv_Gi = []
		pv_time = []
		# Extract data from the CSV file
		with open(self.file_path, mode='r') as csv_file:
			reader	 = csv.DictReader(csv_file)
			for row in reader:
				pv_time.append(datetime.strptime(row['time'], format_time))	# Extract and format (time)  the time
				pv_Gi.append(float(row['G(i)']))							# Extract and format (float) the Global irradiance on the inclined plane (W/m2)
		return pv_time, pv_Gi


	@property
	def pv_time(self):
		pv_time = self._csv_extracter()[0]
		pv_time = np.array(pv_time)
		return pv_time


	@property
	def P_solar(self):
		pv_Gi = self._csv_extracter()[1]
		pv_Gi = np.array(pv_Gi)
		P_solar = pv_Gi * self.A_pv * self.η_pv
		return P_solar
	

	@property
	def Q̇_req(self):
		T_p_avg	  = ( self.T_po + self.T_pi ) / 2
		cp_air	  = PropsSI('CPMASS', 'P', self.P_p, 'T', T_p_avg, self.fluid_p)
		Q̇_req = self.ṁ_p * cp_air * (self.T_po - self.T_pi)
		return Q̇_req


	@property
	def Q̇_process(self):

		# The process operates only in the working hours
		Q̇_process = []
		for t in self.pv_time:
			t = t.hour
			Q̇_process_at_t = self.Q̇_req if t>=self.t_p_start and t<=self.t_p_end else 0
			Q̇_process.append(Q̇_process_at_t)

		return np.array(Q̇_process)
	

	@property
	def Ẇ_comp(self):
		return self.P_solar * self.η_mec * self.η_elec


	@property
	def COP(self):
		# COP = a(Ẇ_comp)ᵇ => from results of the HTHP model
		# Ensure that the computation takes place for Ẇ_comp > 0.
		return np.where(self.Ẇ_comp > 0, self.a * self.Ẇ_comp ** self.b, 0)


	@property
	def Q̇_cd(self):
		Q̇_cd = self.COP * self.Ẇ_comp
		return Q̇_cd


	@property
	def Q_stored(self):
		
		Q_cd	  = 3600 * self.Q̇_cd		# from W to J (t = 1h = 3600s)
		Q_process = 3600 * self.Q̇_process	# from W to J (t = 1h = 3600s)

		Q_stored = np.cumsum(Q_cd - Q_process)
		Q_stored += self.E_start

		return Q_stored


	@property
	def max_Q̇_cd(self):
		return max(self.Q̇_cd)


	@property
	def max_Q_stored(self):
		return max(abs(self.Q_stored))


	def plot_P_solar(self):
		# Create the bar chart
		plt.figure(figsize=(10, 6))
		plt.bar(self.pv_time, self.P_solar, edgecolor='blue', width=0.03)
		plt.scatter(self.pv_time, self.Q̇_process, color='green', s=1)

		# Customize the plot
		plt.xlabel("Time", fontsize=14)
		plt.ylabel("Power (W)", fontsize=14)
		plt.title("PV Power vs Time", fontsize=16)
		plt.xticks(rotation=45)
		# Set the major ticks to show every hour (or any desired frequency)
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=20))  # Show ticks every 5 days
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))  # Format as 'month-day'

		# Show the plot
		plt.tight_layout()  # Adjust layout to prevent clipping
		plt.show()


	def plot_distribution_graph(self):

		# Define the bins (tranches)
		num_bins = 20  # Number of bins
		bins = np.linspace(min(self.Q_stored), max(self.Q_stored), num_bins + 1)

		# Calculate the occurrences (histogram)
		occurrences, bin_edges = np.histogram(self.Q_stored, bins=bins)

		# Prepare data for plotting
		bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Midpoints of bins

		# Plot the histogram
		plt.figure(figsize=(10, 6))
		plt.bar(bin_centers, occurrences, width=np.diff(bin_edges), edgecolor='black', align='center', alpha=0.7)
		plt.xlabel("Stored Energy Value (units)")
		plt.ylabel("Occurrences")
		plt.title("Distribution of Stored Energy Values")
		plt.grid(True, linestyle="--", alpha=0.6)
		plt.tight_layout()
		plt.show()

		return occurrences, bins


	@property
	def T_s_max(self):
		# What to choose ??
		Q̇ = self.Q̇_req 
		# Q̇ = self.max_Q̇_cd

		# Initial guess for T_s_max
		T_s_max = self.T_s_min + (self.T_po - self.T_pi)

		# Calculation of T_s_max => convection formula
		def get_T(T_guess):
			T_s_avg		= (T_guess + self.T_s_min) / 2
			cp_water	= PropsSI('CPMASS', 'P', self.P_s, 'T', T_s_avg, self.fluid_s)
			T_s_max_new = (Q̇ / (self.ṁ_s * cp_water)) + self.T_s_min
			return T_s_max_new

		# Iterate until convergence
		while not np.isclose(get_T(T_s_max), T_s_max, atol=1e-3):
			T_s_max = get_T(T_s_max)

		return T_s_max


	@property
	def storage_volume(self):
		Q	  = self.max_Q_stored
		T_avg = ( self.T_s_max + self.T_s_min ) / 2
		ρ	  = PropsSI('D', 'T', T_avg, 'P', self.P_s, self.fluid_s)
		cp	  = PropsSI('CPMASS', 'T', T_avg, 'P', self.P_s, self.fluid_s)
		v	  = Q / (ρ * cp * (self.T_s_max - self.T_s_min))
		return v


	@property
	def storage_lenght(self):
		v = self.storage_volume
		l = v**(1/3)
		return l

		
