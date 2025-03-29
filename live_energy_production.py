import requests
import time
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
from datetime import datetime

# Define location (latitude, longitude)
LAT = 38.736946  # Lisbon
LON = -9.142685

# PV System Parameters
system_peak_power = 3000  # Watts (3 kW)
surface_tilt = 60  # Tilt angle
surface_azimuth = 90  # South-facing
module_params = {
    'pdc0': system_peak_power,
    'gamma_pdc': -0.004,  # Temperature coefficient
    'material': 'monosi'  # Monocrystalline silicon
}
inverter_params = {
    'pdc0': system_peak_power,
    'eta_inv_nom': 0.96  # Nominal inverter efficiency
}

# Initialize PVSystem and Location
location = Location(latitude=LAT, longitude=LON, tz='Europe/Lisbon', altitude=10, name='Lisbon')
system = PVSystem(
    surface_tilt=surface_tilt,
    surface_azimuth=surface_azimuth,
    module_parameters=module_params,
    inverter_parameters=inverter_params,
    racking_model='open_rack',
    module_type='glass_polymer'
)

# ModelChain with explicit models
modelchain = ModelChain(
    system,
    location,
    aoi_model='physical',
    spectral_model='no_loss', # No spectral losses
    temperature_model='sapm'
)

# Open-Meteo API URL for CURRENT weather (updated ~every 15-30 minutes)
url = "https://api.open-meteo.com/v1/forecast"
params = {
    'latitude': LAT,
    'longitude': LON,
    'current': ['temperature_2m', 'shortwave_radiation', 'direct_radiation', 'diffuse_radiation'],
    'timezone': 'auto'
}

def fetch_live_weather():
    """Fetch live weather data from Open-Meteo (current values)."""
    response = requests.get(url, params=params)
    data = response.json()['current']

    return {
        'ghi': data['shortwave_radiation'],  # Global Horizontal Irradiance (W/m²)
        'dni': data['direct_radiation'],     # Direct Normal Irradiance (W/m²)
        'dhi': data['diffuse_radiation'],    # Diffuse Horizontal Irradiance (W/m²)
        'temp_air': data['temperature_2m'],  # Air temperature (°C)
        'time': pd.Timestamp(data['time'])
    }

def calculate_power(weather_data):
    """Calculate solar power for the current timestamp."""
    # Create a DataFrame with the current time and weather data
    df = pd.DataFrame([weather_data], index=[weather_data['time']])

    # Run the PVLib model
    modelchain.run_model(df)
    # Extract AC power (in Watts)
    ac_power = modelchain.results.ac.iloc[0]
    return ac_power

# Main loop to print live values
try:
    while True:
        # Fetch live weather data
        weather = fetch_live_weather()

        # Calculate power
        power = calculate_power(weather)

        # Print live value with timestamp
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | AC Power: {power:.2f} W")
        time.sleep(60)

except KeyboardInterrupt:
    print("\nStopped.")