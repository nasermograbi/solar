import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain

# Define location
location = Location(latitude=42.676, longitude=23.368, tz='Europe/Sofia', altitude=10, name='Sofia')

# Define PV system parameters with complete module parameters
module_parameters = {
    'pdc0': 3000,  # DC power at STC
    'gamma_pdc': -0.004,  # Temperature coefficient of power
    'I_L_ref': 8.0,  # Light-generated current at STC
    'I_o_ref': 1e-10,  # Diode saturation current at STC
    'R_s': 0.5,  # Series resistance
    'R_sh_ref': 100,  # Shunt resistance at STC
    'a_ref': 1.5,  # Modified ideality factor
    'EgRef': 1.121,  # Bandgap energy in eV
    'cells_in_series': 60,  # Number of cells in series
    'alpha_sc': 0.004,  # Short-circuit current temperature coefficient (required for singlediode)
}

system = PVSystem(
    surface_tilt=30,
    surface_azimuth=180,
    module_parameters=module_parameters,
    inverter_parameters={'pdc0': 3000, 'eta_inv_nom': 0.96},
    temperature_model_parameters={'a': -3.56, 'b': -0.075, 'deltaT': 3}  # SAPM temperature model params
)

# Define ModelChain with explicit DC model
modelchain = ModelChain(
    system,
    location,
    aoi_model='physical',
    spectral_model='no_loss',
    temperature_model='sapm',
    dc_model='singlediode'  # Explicitly set the DC model
)

# Simulate for a specific day
times = pd.date_range('2024-01-23', periods=24, freq='h', tz=location.tz)
weather = location.get_clearsky(times)

# Run the model
modelchain.run_model(weather)

# Debugging: Print intermediate results
print("Solar Position:")
print(modelchain.results.solar_position)

print("Irradiance:")
print(modelchain.results.irradiance)

print("Cell Temperature:")
print(modelchain.results.cell_temperature)

# Check if 'p_mp' exists in the results
print("Available DC keys:", modelchain.results.dc.keys())

if 'p_mp' in modelchain.results.dc:
    dc_power = modelchain.results.dc['p_mp']
else:
    print("Warning: 'p_mp' not found in modelchain results. Using zeros instead.")
    dc_power = pd.Series(0, index=times)  # Default to zero power

# Get AC power (if available)
ac_power = modelchain.results.ac if modelchain.results.ac is not None else pd.Series(0, index=times)

# Create DataFrame and plot
df = pd.DataFrame({'dc_power': dc_power, 'ac_power': ac_power}, index=times)
df.plot(style=['--', '-'], title='Simulated Inverter Output')
plt.ylabel('Power (W)')
plt.xlabel('Time')
plt.grid(True)
plt.tight_layout()
plt.savefig('inverter_output_simulated.png')
plt.show()