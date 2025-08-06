from Interface.HeatPumpInterface import *
from Interface.__init__			 import *


# verify the library
# downlond automatically the ones that are not here
# run the code

# => .exe file

if __name__ == "__main__":
	# Run the program
	app = QApplication(sys.argv)
	window = HeatPumpInterface()
	window.show()
	
	# Start the app event loop
	result = app.exec_()
	sys.exit(result)
