# Feasibility Study of a Thermal Energy Storage Integrated Heat Pump

## Overview

This project was developed as part of the master's thesis ***"Feasibility Study of a Thermal Energy Storage Integrated Heat Pump"***, submitted in fulfilment of the requirements for the Master of Science in Aeronautical Engineering at the University of Limerick.

The goal of this work is to:
- Model a steady-state, single-stage high-temperature heat pump.
- Calculate and optimise the sizing of a thermal energy storage (TES) system.

---

## Installation Requirements

You can install all required libraries with the following command:

```bash
pip install numpy matplotlib plotly scipy CoolProp openpyxl sounddevice PyQt5
```

To run this project, the following Python libraries are required:

**Core Dependencies**
- `numpy`
- `math`
- `random`
- `sys`
- `os`
- `time`
- `csv`
- `io`
- `datetime`
- `shutil`

**Plotting and Visualisation**
- `matplotlib`
- `plotly`

**Optimisation and Curve Fitting**
- `scipy`

**Thermodynamic Properties**
- `CoolProp`

**Excel File Handling**
- `openpyxl`

**Audio Playback**
- `sounddevice`

### Graphical User Interface
- `PyQt5`


## How to Use the Program

**Heat Pump (HP) Modelling**

- Fill the input Excel file using the same format as `Excel_Inputs/Inputs.xlsx`.
- Run the script `Main_HP.py`.
- Output results will be saved in the `Excel_Outputs/` directory.

**Thermal Energy Storage (TES) Calculation**

- Enter the input values directly within the script `Main_TES.py`.
- Run the script `Main_TES.py`.

*Note: Detailed instructions for filling inputs and interpreting results can be found in the master's thesis report.*

## Abstract of the master thesis

The industrial sector still relies heavily on fossil fuels for its heating processes. However, with the need to reduce overall greenhouse gas emissions to contain global warming, it is essential to find alternatives to eliminate the use of fossil fuel. A promising solution is the thermal energy storage integrated heat pump (TESIHP), which generates heat using renewable energy. The clean electricity produced is used to power the compressor of a high temperature heat pump (HTHP), which recovers waste heat from the industry and raises its temperature above 100°C to meet the process requirements. A thermal energy storage (TES) is combined with the HTHP to mitigate the intermittency of the renewable energy. The purpose of this study is to verify the feasibility of a TESIHP and identify a viable configuration. Firstly, a steady-state, single-stage heat pump model has been developed in python. The aim is to simulate a HTHP able to supply energy to a typical industrial example: a milk drying process that, at some stage, needs to heat ambient air from 20°C to 170°C. As highlighted in the scientific literature, such heat pumps tend to have low COP that decrease with higher temperature lifts and often use synthetic working fluids. The simulated HTHP uses R1233zd(E) as the working fluid and reaches a COP of approximately 1.8. Secondly, the objective is to find an operating configuration of the TES that minimises its size, even if it requires a larger power plant, as the TES is more challenging to scale up. It is assumed to be an adiabatic stratified water tank. The renewable energy source is a photovoltaic system, as the data are easily accessible on internet. The TES and the solar panel surface should measure 594.85 m³ and 2436.66 m ², respectively. Finally, an estimate of the total capital investment was made: €71,382 for the HTHP and €112,272 for the TES. With the photovoltaic power plant, the total price amounts to 573,519 €, with a payback period estimated at 9.4 years. The power plant accounts for 68% of the total cost, the HTHP 20%, and the TES 12%.

## Information

All scripts have been coded by myself (Mathieu Mercier), except for `HeatPumpInterface.py`, which was generated with the help of AI.

Please note that the formatting of the scripts does not strictly follow official Python style guidelines (e.g. PEP 8), and could benefit from further refactoring and cleanup.

The heat pump model can also be run using the `testX.py` scripts located in the `Model_HTHP` folder.
