import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Get the Data
data = pd.read_csv("DataSet_Natal_Final.csv")

### Perform EDA
print(data.head(50))
print(data.info())
print(data.describe())
print(data.type.value_counts())

# histogram
data.hist(figsize=(12, 6))
plt.tight_layout()
#plt.show()

# Quantiles for each column
quantiles_99 = data.quantile(0.995, axis=0)

# Add margins
quantiles_99['area'] *= 1.15
quantiles_99['bathrooms'] *= 1.15
quantiles_99['bedrooms'] *= 1.15
quantiles_99['condo'] *= 1.15
quantiles_99['parking_spots'] *= 1.15
quantiles_99['price'] *= 1.15
quantiles_99['suites'] *= 1.15
# Outliers for each column
data_out = data[(data['area'] > quantiles_99['area']) | (data['area'] > quantiles_99['area']) |
                (data['bathrooms'] > quantiles_99['bathrooms']) | (data['bedrooms'] > quantiles_99['bedrooms']) | 
                (data['condo'] > quantiles_99['condo']) | (data['parking_spots'] > quantiles_99['parking_spots']) |
                (data['price'] > quantiles_99['price']) | (data['suites'] > quantiles_99['suites'])
                ]
# Outliers
data_out.head()

# Remove Outliers
data = pd.concat([data, data_out]).drop_duplicates(keep=False)
data.describe()

# Quantiles
area_quantiles_0005 = data['area'].quantile(0.005)
print(area_quantiles_0005)

# Filter data percentile + 20%
data_out = data[(data['area'] < area_quantiles_0005 * 1.2)]

# Remove Outliers
data = pd.concat([data, data_out]).drop_duplicates(keep=False)
data.describe()

# Statistics
# data.hist(bins=10, figsize=(12, 6))
# data.describe()
# plt.tight_layout()

from sklearn.model_selection import train_test_split

# Divided data
train_set, test_set = train_test_split(data, 
                                       test_size=0.2, 
                                       random_state=35)

print("data has {} instances\n {} train instances\n {} test instances".
      format(len(data),len(train_set),len(test_set)))

# Exploring data
train = train_set.copy()

import folium

# 
m = folium.Map(location=[-5.812757, -35.255127], zoom_start=6)

locations = train[['lat', 'lon']].values.tolist()

for point in locations:
    folium.Marker( location=[ obs['lat'], obs['lon'] ], fill_color=obs['price'], radius=obs['bedrooms'] ).add_to(m)


#mapit.save( 'map.html')