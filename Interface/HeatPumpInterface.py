from Interface.__init__ import *
from Model_HTHP.Simulation import *


class ProgressWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set the window properties
        self.setWindowTitle("Progress Window")
        self.setFixedSize(800, 950)
        self.setFont(QFont("Bahnschrift Light", 11))
        
        # Create the layout
        layout = QVBoxLayout()
        
        # Add progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # Add a label
        self.status_label = QLabel("Simulation in progress...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add a text edit to display the terminal
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)  # Make it read-only
        self.log_output.setFont(QFont("Consolas", 10))
        
        # Organise the widgets
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        
        # Redirect stdout and stderr
        self.terminal_output = TerminalOutput(self.log_output)
        sys.stdout = self.terminal_output
        sys.stderr = self.terminal_output


    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.status_label.setText("Simulation Complete!")
            # Restore the original stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__



class TerminalOutput:
    # Redirects stdout and stderr to a QTextEdit widget.

    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, message):
        # Append the message to the QTextEdit
        self.text_edit.append(message.strip())
        # Ensure the text view always scrolls to the bottom
        self.text_edit.moveCursor(QTextCursor.End)

    def flush(self):
        pass  # No action required for flush



class SimulationThread(QThread):
    progress = pyqtSignal(int)  # Signal to communicate progress
    finished = pyqtSignal(str) # Signal to communicate when done


    def __init__(self, simulation_type, file_path, variable_parameter):
        super().__init__()
        self.simulation_type = simulation_type
        self.file_path = file_path
        self.variable_parameter = variable_parameter


    def run(self):
        try:
            if self.simulation_type == "One fluid simulation":
                simulation = OneFluidSimulation(self.file_path, self.variable_parameter)
            elif self.simulation_type == "Several fluids simulation":
                simulation = SeveralFluidsSimulation(self.file_path, self.variable_parameter)
            else:
                raise ValueError("Invalid simulation type.")

            # Simulate progress during the simulation
            for progress in simulation.run_with_progress():  # Assuming `run_with_progress()` yields progress
                self.progress.emit(progress)  # Emit progress update
            self.finished.emit("Simulation complete!")
        except Exception as e:
            self.finished.emit(f"Simulation failed: {str(e)}")



class HeatPumpInterface(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window
        self.setWindowTitle("Heat Pump Modelling")
        self.setFixedSize(800, 950)
        self.setFont(QFont("Bahnschrift Light", 11))
        self.label_width = 310  # Set a fixed width for all labels

        # Main layout
        self.layout = QVBoxLayout()
        
        # Add each component to the layout
        self._add_title_description()
        self._add_program_description()
        self._add_image()
        self._add_warning()
        self._add_file_input()
        self._add_simulation_type_checkboxes()
        self._add_variable_parameter_dropdown()
        self._add_run_button()

        self.setLayout(self.layout)


    def _add_title_description(self):
        main_layout = QHBoxLayout()

        # Create QLabel for logo image (left)
        logo_label = QLabel(self)
        pixmap_logo = QPixmap("./Interface/logo.png")
        scaled_logo = pixmap_logo.scaled(75, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # scale as needed
        logo_label.setPixmap(scaled_logo)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)  # left-align, vertically centered
        logo_label.setFixedWidth(150)

        # Create QLabel for text (right)
        label = QLabel(
            """<br><b>HEAT PUMP MODELLING</b><br>
            This program aims to simulate heat pumps.<br>""", self
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

        # Add widgets to horizontal layout
        main_layout.addWidget(logo_label)
        main_layout.addWidget(label)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(main_layout)
    

    def _add_program_description(self):

        description_layout = QHBoxLayout()

        # Create QLabel for text (right)
        description_label = QLabel(
            """
            It was developed by Mathieu Mercier as part of his master's thesis titled <u>Feasibility study of a TESIHP</u> at the University of Limerick.<br>
            The simulation is primarily based on the article <u>Steady-state simulation of vapour-compression heat pumps</u> by T.B. Herbas, et al.<br><br>
            Below is a schematic of the modelled heat pump.
            """, self
        )
        description_label.setWordWrap(True)

        description_layout.addWidget(description_label)
        self.layout.addLayout(description_layout)


    def _add_warning(self):

        warning_layout = QHBoxLayout()

        # Create QLabel for text (right)
        warning_label = QLabel(
            """Please ensure that the input file is filled out correctly.<br>
            An example can be found in the file: <u>./Excel_Inputs/Inputs.xlsx</u>.<br>
            Make sure to enter the correct file name and path.<br>
            """, self
        )
        warning_label.setWordWrap(True)

        warning_layout.addWidget(warning_label)
        self.layout.addLayout(warning_layout)


    def _add_image(self):

        # Define
        self.jpg_label = QLabel(self)
        pixmap = QPixmap("./Interface/heat_pump.jpg")
        scaled_pixmap = pixmap.scaled(498, 296, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Organise
        self.jpg_label.setPixmap(scaled_pixmap)
        self.jpg_label.setAlignment(Qt.AlignCenter)

        # Add to interface
        self.layout.addWidget(self.jpg_label)


    def _add_file_input(self):

        # Create horizontal layout
        file_layout = QHBoxLayout()

        # Define the label
        file_label = QLabel("Enter the path to the input file:")
        file_label.setAlignment(Qt.AlignLeft)  # Align the text to the left
        file_label.setFixedWidth(self.label_width)
        
        # Define the edit zone
        self.file_entry = QLineEdit(self)
        self.file_entry.setText("./Excel_Inputs/")
        self.file_entry.setPlaceholderText("Path to input file (default: ./Excel_Inputs/)")
        self.file_entry.setAlignment(Qt.AlignLeft)  # Align the text inside the edit zone to the left

        # Organise layouts
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_entry)
        self.layout.addLayout(file_layout)


    def _add_simulation_type_checkboxes(self):

        # Create layouts
        checkbox_layout = QHBoxLayout()         # Horizontal for label // check cases
        checkbox_zone_layout = QVBoxLayout()    # vertical for case1 // case2

        # Define the label       => in checkbox_layout
        simulation_label = QLabel("Select simulation type:")
        simulation_label.setAlignment(Qt.AlignLeft)  # Align the text to the left
        simulation_label.setFixedWidth(self.label_width)
        
        # Define the ckeck cases => in checkbox_zone_layout
        self.one_fluid_check = QCheckBox("One fluid simulation (to be set in excel file)")
        self.several_fluids_check = QCheckBox("Several fluids simulation")

        # Ensure only one checkbox can be selected
        self.one_fluid_check.stateChanged.connect(self._handle_simulation_type)
        self.several_fluids_check.stateChanged.connect(self._handle_simulation_type)

        # Organise layouts
        checkbox_zone_layout.addWidget(self.one_fluid_check)
        checkbox_zone_layout.addWidget(self.several_fluids_check)
        checkbox_layout.addWidget(simulation_label)
        checkbox_layout.addLayout(checkbox_zone_layout)
        self.layout.addLayout(checkbox_layout)


    def _add_variable_parameter_dropdown(self):

        # Create a horizontal layout
        dropdown_layout = QHBoxLayout()

        # Define the label
        dropdown_label = QLabel("Select variable parameter:")
        dropdown_label.setAlignment(Qt.AlignLeft)
        dropdown_label.setFixedWidth(self.label_width)

        # Define the dropdown
        self.variable_dropdown = QComboBox(self)
        self.variable_dropdown.addItems(['V','ω','T_ci','T_co','ṁ_c','ṁ_e','UA_cd','UA_ev'])
        
        # Organise layouts
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.variable_dropdown)
        self.layout.addLayout(dropdown_layout)


    def _add_run_button(self):
        self.button = QPushButton("Run Simulation", self)
        self.button.clicked.connect(self._on_button_click)
        self.layout.addWidget(self.button)


    def _handle_simulation_type(self, state):
        """Ensures only one simulation type checkbox is active."""
        if state == Qt.Checked:
            sender = self.sender()
            if sender == self.one_fluid_check:
                self.several_fluids_check.setChecked(False)
            elif sender == self.several_fluids_check:
                self.one_fluid_check.setChecked(False)


    def _on_button_click(self):
        # Gather input values
        simulation_type = "One fluid simulation" if self.one_fluid_check.isChecked() else "Several fluids simulation"
        file_path = self.file_entry.text()
        variable_parameter = self.variable_dropdown.currentText()

        # Start simulation in a separate thread
        self.simulation_thread = SimulationThread(simulation_type, file_path, variable_parameter)
        self.simulation_thread.progress.connect(self._on_progress_update)
        self.simulation_thread.finished.connect(self._on_simulation_finished)

        # Open Progress Window
        self.progress_window = ProgressWindow()
        self.progress_window.show()
        self.close()  # Close the current window
        
        self.simulation_thread.start()


    def _on_progress_update(self, value):
        if hasattr(self, 'progress_window'):
            self.progress_window.update_progress(value)


    def _on_simulation_finished(self, message):
        if hasattr(self, 'progress_window'):
            self.progress_window.status_label.setText(message)