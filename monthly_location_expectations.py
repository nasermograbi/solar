import requests
import pandas as pd
import matplotlib.pyplot as plt

# Define location (latitude & longitude)
latitude = 42.676  # Example: Sofia, Bulgaria
longitude = 23.368

pvgis_url = f"https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat={latitude}&lon={longitude}&peakpower=3&loss=14&angle=30&aspect=180&outputformat=json"

response = requests.get(pvgis_url)
data = response.json()

# Debug: Print full API response
# print("Full API Response:", data)

# Extract monthly data correctly
if 'outputs' in data and 'monthly' in data['outputs'] and 'fixed' in data['outputs']['monthly']:
    monthly_data = data['outputs']['monthly']['fixed']

    months = [entry['month'] for entry in monthly_data]
    energy = [entry['E_m'] for entry in monthly_data]

    # Convert to DataFrame
    df = pd.DataFrame({'Month': months, 'Energy (kWh)': energy})

    # Plot results
    df.plot(x='Month', y='Energy (kWh)', kind='bar', title=f'PV Energy Production for ({latitude}, {longitude})')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)
    plt.show()

else:
    print("Error: API response does not contain expected monthly energy data.")
