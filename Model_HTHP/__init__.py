# Libraries for Heat Pump model
from CoolProp.CoolProp	import PropsSI
from scipy.optimize		import least_squares, minimize, root, fsolve, newton, broyden1, anderson, fixed_point, curve_fit

# Libraries for plot
from matplotlib			 import pyplot as plt 
import matplotlib.cm	 as cm
import plotly.graph_objs as go
import plotly.express	 as px
from plotly.subplots	 import make_subplots

# Usefull Libraries
import random
import numpy as np
import sounddevice as sd
import math
import sys
import os

# Libraries for Excel format
from openpyxl	import load_workbook
from shutil		import copyfile
from datetime	import datetime

# Add the project root to Python's search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))