import pandas as pd
import numpy as np
import math
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
import matplotlib.pyplot as plt
from time import sleep


def address2coord(address):
    """
    Return the latitude and longitude from given address. Uses Free Nomatim OpenStreetMap API.
    OBS.: Super slow...zZz
    > address: string with the address.
    < (lat, lon): tuple with latitude and longitude of the address.
    """
    # Organize address
    address = address.replace(' ', '+')   

    # Nominatim API
    api_url = "https://nominatim.openstreetmap.org/search?&format=json&q="
    
    # 'requests' retry features 
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(20, backoff_factor=.5))
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Get the response
    r = session.get(api_url + address)
    
    # Load as json
    try:
        json_as_list = json.loads(r.content)
    except:
        print("API blocked. Message: {}".format(r.content))
    
    # Consider only the first result
    try:
        json_as_dict = json_as_list[0]
    # If no result is found
    except:
        json_as_dict = {'lat':0, 'lon':0}

    # Retrieve 'lat' and 'lon' from json dictionary
    latitude = float(json_as_dict['lat'])
    longitude = float(json_as_dict['lon'])

    return (latitude, longitude)

# adr = "Rua Desembargador Hemetério Fernandes, 1162 - Tirol, Natal - RN"
# print(address2coord(adr))

def clean_improve_df(file="DataSet_Natal.csv"):
    """
    Apply address2coord to every entry in 'address' and append results to a new column of the DataFrame.
    Briefly, this function cleans the data performing the following steps:
    1 - Remove duplicates
    3 - Remove empty entries of columns 'price','address', 'area' and 'type'.
    4 - Add 'lat' and 'lon' columns
    5 - Drop 'address' column

    > file:name of the .csv  file  or df object.
    < multiple .csv files with cleaned dataframes, added 'lat' and 'lon' columns
    and removed 'address' column.
    OBS.: The conversion of addres in coordenates is supper slow. Took ~3 hours 
    for ~8000 addresses conversions.
    """
    
    # Load DataFrame from file
    if not isinstance(file, pd.DataFrame):
        df = pd.read_csv(file)
    else:
        df = file
    
    # Remove duplicates and reindex
    df.drop_duplicates(inplace=True)
    df = df.reset_index(drop=True)

    # Remove entries with missing values from prices , area, type and address
    df = df.dropna(subset=['price','address', 'area','type'])
        
    #df.to_csv("DataSet_Natal_Clean.csv", index=False)

    # Split df in n parts of maximum 1000 observations due to API limit 
    n = math.ceil(len(df) / 1000)
    df_splitted = np.array_split(df, n)
    
    for i, df_piece in enumerate(df_splitted): 
        # Get latitude and longitude
        coord_series = df_piece['address'].apply(address2coord) # Series
        df_piece['lat'] = coord_series.apply(lambda x: x[0])    # Lat column
        df_piece['lon'] = coord_series.apply(lambda x: x[1])    # Lon column
        
        # Remove entries with missing values from prices , area, type, lat, lon and address
        df_piece = df_piece.dropna(subset=['lat', 'lon'])

        # Replace missing values from bathrooms, bedrooms, condo, parking_spots, suites, condo with zero
        fill_cols = ['bathrooms', 'bedrooms', 'condo', 'parking_spots', 'suites', 'condo']
        df_piece[fill_cols] = df_piece[fill_cols].fillna(0)

        # Drop address column
        df_piece = df_piece.drop(['address'], axis=1)

        #print(df_piece.head(50))

        # Reset index again         
        df_piece = df_piece.reset_index(drop=True)

        # Save partial df
        df_piece.to_csv("DataSet_Natal_Clean_" + str(i) +".csv", index=False)

        # Wait for next acquisition - 3 min
        sleep(180)
    
    # Join results dataframes
    return join_dataframes("DataSet_Natal_Clean_", n)

def join_dataframes(file_static, n):
    """
    Join multiple .cvs files created previously, removing unsuccessful 'lat' and 'lon' coordenates.  
    > file: begin of the .csv file name.
    > n: number of files.
    < one .csv file with the final DataFrame and dataframe itself.
    """
    # Placeholder
    df = pd.DataFrame()
    # Read all files and append them together
    for i in range(n):
        df_piece = pd.read_csv(file_static + str(i) + ".csv")
        df_piece = df_piece[(df_piece.lat != 0) & (df_piece.lon != 0)]
        df = df.append(df_piece)
    
    # Save result
    df.to_csv("DataSet_Natal_Final.csv", index=False)

    return df

df_clean = clean_improve_df()



