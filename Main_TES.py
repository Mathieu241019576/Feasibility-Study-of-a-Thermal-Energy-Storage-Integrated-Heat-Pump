from Model_TES.ThermalEnergyStorage import *
from Model_TES.Simulation           import *
from Interface.CreateSound          import *


if __name__ == "__main__":

    inputs = {
        # Side 1 : TE Storage
        'fluid_s'	: 'water',
        'ṁ_s'		: 0.25,
        'P_s'		: 10*101325,
        'T_s_min'	: 30,
        'COP'		: (580.77, -0.511),
        # Side 2 : Process
        'fluid_p'	: 'air',
        'ṁ_p'		: 1,
        'P_p'		: 101325,
        'T_pi'		: 20,
        'T_po'		: 170,
        't_p_start'	: 8,
        't_p_end'	: 18,
        # Efficiencies
        'η_pv'	 : 0.176,
        'η_mec'	 : 0.9,
        'η_elec' : 0.9,
    }

    Simulation(inputs).run()