import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import sys
import numpy as np
import pandas as pd
import regex as re
import requests
from lxml.html.soupparser import fromstring
import geopy.distance
from datetime import date
import sqlite3
from sklearn.ensemble import RandomForestRegressor
exec(open('config.py').read())
pd.options.mode.chained_assignment = None  # default='warn'

def scraper(url):
    req_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'upgrade-insecure-requests': '1',
        'user-agent': 'charlesbarry8895@brown.edu'
    }
    
    with requests.Session() as s:
       response = s.get(url, headers=req_headers)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    list1 = str(soup.find_all('script', {'type': 'application/json'}))[str(soup.find_all('script', {'type': 'application/json'})).find('zpid')-1:].split(",")
    list2 = [i.replace('"', '').split(":") for i in list1]
    
    detailUrl = [i[2].replace('//', '') for i in list2 if i[0] == 'detailUrl']
    unformattedPrice = [i[1] for i in list2 if i[0] == 'unformattedPrice']
    address = [i[1] for i in list2 if i[0] == 'address']
    addressStreet = [i[1] for i in list2 if i[0] == 'addressStreet']
    addressCity = [i[1] for i in list2 if i[0] == 'addressCity']
    addressZipcode = [i[1] for i in list2 if i[0] == 'addressZipcode']
    addressState = [i[1] for i in list2 if i[0] == 'addressState']
    beds = [i[1] for i in list2 if i[0] == 'beds']
    baths = [i[1] for i in list2 if i[0] == 'baths']
    area = [i[1] for i in list2 if i[0] == 'area']
    latitude = [i[1] for i in list2 if i[0] == 'latitude']
    latitude = [latitude[i] for i in range(len(latitude)) if '}' not in str(latitude[i])]
    longitude = [i[1] for i in list2 if i[0] == 'longitude']
    longitude = [longitude[i] for i in range(len(longitude)) if '}' not in str(longitude[i])]
    bathrooms = [i[1] for i in list2 if i[0] == 'bathrooms']
    bedrooms = [i[1] for i in list2 if i[0] == 'bedrooms']
    livingArea = [i[1] for i in list2 if i[0] == 'livingArea']
    homeType = [i[1] for i in list2 if i[0] == 'homeType']
    daysOnZillow = [i[1] for i in list2 if i[0] == 'daysOnZillow']
    zestimate = [i[1] for i in list2 if i[0] == 'zestimate']
    rentZestimate = [i[1] for i in list2 if i[0] == 'rentZestimate']
    isPreforeclosureAuction = [i[1] for i in list2 if i[0] == 'isPreforeclosureAuctio']
    priceForHDP = [i[1] for i in list2 if i[0] == 'priceForHDP']
    taxAssessedValue = [i[1] for i in list2 if i[0] == 'taxAssessedValue']
    lotAreaValue = [i[1] for i in list2 if i[0] == 'lotAreaValue']
    lotAreaUnit = [i[1] for i in list2 if i[0] == 'lotAreaUnit']
    
    print(f'{len(longitude)} Records found at {url}')
    
    ### - Array Length Checks
    bool_value = (len(detailUrl) == len(unformattedPrice) == len(address) == len(addressStreet) ==
                  len(addressCity) == len(addressZipcode) == len(addressState) == len(beds) ==
                  len(baths) == len(area) == len(latitude) == len(longitude))
    
    if bool_value:
        df = pd.DataFrame({'detailUrl':detailUrl,
                           'unformattedPrice':unformattedPrice, 'address':address, 'addressStreet':addressStreet,
                           'addressCity':addressCity, 'addressZipcode':addressZipcode, 'addressState':addressState,
                           'beds':beds, 'baths':baths, 
                           'area':area, 
                           'latitude':latitude, 'longitude':longitude
    #                        'rentZestimate':rentZestimate, 'zestimate':zestimate
                          })

        return df
    else:
        print(f'Improper Array Lengths for {url}')

def spider(url_list, pois):
    
    ### - Build Out initial dataframe via web-scraping small geographical blocks
    i=0
    for url in url_list:
        if i==0:
            df = scraper(url)
        else:
            df = pd.concat([df, scraper(url)])
        print(f'Scraped url # {i}')
        i=i+1
    
    ### - Read in Reference Data
    os.chdir(user_directory + '\\denver_real_estate\\source_data')
    edu_scores = pd.read_csv("Education_Scores_Colorado.csv").groupby('County').mean().reset_index()[['County', 'Rank score (2022)']].rename({'Rank score (2022)':'edu_rank_score_2022'}, axis=1)
    co_zips = pd.read_csv('colorado_zip_codes.csv')[['zip', 'county']]
    property_characteristics = pd.read_csv('real_property_residential_characteristics.csv')
    prop_char = property_characteristics.groupby('OWNER_CITY').agg({'TOTAL_VALUE': 'mean'}).reset_index()

    os.chdir(user_directory + '\\denver_real_estate')
    
    ### - DataFrame Standardization
    df.addressZipcode = df.addressZipcode.astype(int)
    property_characteristics.OWNER_CITY = property_characteristics.OWNER_CITY.str.upper()
    df.addressCity = df.addressCity.str.upper()
    df['dist_to_downtown'] = np.nan
    df['dist_to_ski'] = np.nan
    df['dist_to_red_rocks'] = np.nan
    
    ### - Merge with Reference Data
    edu_final = pd.merge(co_zips, edu_scores, how='left', left_on='county', right_on='County')[['zip', 'county', 'edu_rank_score_2022']].drop_duplicates()
    edu_final.zip = edu_final.zip.astype(int)
    df = pd.merge(df, edu_final, how='left', left_on='addressZipcode', right_on = 'zip')
    df = pd.merge(df, prop_char, how='left', left_on='addressCity', right_on = 'OWNER_CITY').rename({'TOTAL_VALUE':'average_home_value'}, axis=1)
    
    ### - Distance Calculations
    for i in range(len(df.beds)):
        coords_downtown = (float(pois['RiNo (River North Arts District)'][0]), float(pois['RiNo (River North Arts District)'][1]))
        coords_ski = (float(pois['Breckenridge Ski Resort'][0]), float(pois['Breckenridge Ski Resort'][1]))
        coords_redrocks = (float(pois['Red Rocks Park & Ampitheatre'][0]), float(pois['Red Rocks Park & Ampitheatre'][1]))
        coords_2 = (float(df.latitude[i]), float(df.longitude[i]))

        df['dist_to_downtown'][i] = geopy.distance.geodesic(coords_downtown, coords_2).miles
        df['dist_to_ski'][i] = geopy.distance.geodesic(coords_ski, coords_2).miles
        df['dist_to_red_rocks'][i] = geopy.distance.geodesic(coords_redrocks, coords_2).miles
        
    ### - Date Stamp
    df['date_stamp'] = str(date.today())
    
    cursor = sqlite3.connect("denver_real_estate.db")
    
    df2 = pd.read_sql_query(
    f'''
        SELECT *
        FROM denver_active_listings
    ''', cursor).drop(columns=['index'])
    
    j=0
    for i in range(len(df.beds)):
        if df.address[i] not in set(df2.address):
            df2 = pd.concat([df2, df.iloc[[i]][df2.columns]])
            j=j+1
            
    if j!=0:
        print(f'{j} New Records added to denver_active_listings database')
        df2.to_sql("denver_active_listings", cursor, if_exists="replace")
    else:
        print('No new records Added.')
        
    cursor.close()
    
    return df2

def build_model():
    #Pull Test Data
    cursor = sqlite3.connect("denver_real_estate.db")
    test = pd.read_sql_query(
        f'''
            SELECT *
            FROM test_df
        ''', cursor)
    cursor.close()
    
    #Format data for model
    test.unformattedPrice = test.unformattedPrice.astype(float)
    test.beds = test.beds.replace('null', 0).astype(int)
    test.baths = test.baths.replace('null', 0).astype(float).astype(int)
    test.area = test.area.replace('null', 0).astype(float)
    test.addressCity = test.addressCity.astype("category")
    test.dist_to_downtown = test.dist_to_downtown.astype(float)
    test.dist_to_ski = test.dist_to_ski.astype(float)
    test.dist_to_red_rocks = test.dist_to_red_rocks.astype(float)
    test.edu_rank_score_2022 = test.edu_rank_score_2022.astype(float)
    test.average_home_value = test.average_home_value.astype(float)

    x = test[['unformattedPrice', 'beds', 'area', 'addressCity',
             'dist_to_downtown', 'dist_to_ski', 'dist_to_red_rocks',
             'edu_rank_score_2022', 'average_home_value']]
    x = pd.get_dummies(x)
    
    y = test.rank_score
    
    # Instantiate model with 1000 decision trees
    rf = RandomForestRegressor(n_estimators = 1000, random_state = 49)
    # Train the model on training data
    rf.fit(x.fillna(0), y.fillna(0));
    
    # Use the forest's predict method on the test data
    predictions = rf.predict(x.fillna(0))
    # Calculate the absolute errors
    errors = abs(predictions - y)
    # Print out the mean absolute error (mae)
    print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
    
    cols=list(x.columns)

    x2 = test[['beds', 'baths', 'area', 'addressCity',
             'dist_to_downtown', 'dist_to_ski', 'dist_to_red_rocks',
             'edu_rank_score_2022', 'average_home_value']]

    x2 = pd.get_dummies(x2)
    
    y2 = test.unformattedPrice.astype(int)
    
    # Instantiate model with 1000 decision trees
    rf2 = RandomForestRegressor(n_estimators = 1000, random_state = 49)
    # Train the model on training data
    rf2.fit(x2.fillna(0), y2.fillna(0));
    
    # Use the forest's predict method on the test data
    predictions2 = rf2.predict(x2.fillna(0))
    # Calculate the absolute errors
    errors = abs(predictions2 - y2)
    # Print out the mean absolute error (mae)
    print('Mean Absolute Error:', round(np.mean(errors), 2), 'degrees.')
    
    cols2=list(x2.columns)
    
    return rf, cols, rf2, cols2

def score_data(rf, cols):
    cursor = sqlite3.connect("denver_real_estate.db")
    df = pd.read_sql_query(
        f'''
            SELECT *
            FROM denver_active_listings
            WHERE address NOT IN (SELECT address FROM denver_prediction_values)
        ''', cursor)
    
    try:
        df.unformattedPrice = df.unformattedPrice.astype(float)
        df.beds = df.beds.replace('null', 0).astype(int)
        df.baths = df.baths.replace('null', 0).astype(float).astype(int)
        df.area = df.area.replace('null', 0).astype(float)
        df.addressCity = df.addressCity.astype("category")
        df.dist_to_downtown = df.dist_to_downtown.astype(float)
        df.dist_to_ski = df.dist_to_ski.astype(float)
        df.dist_to_red_rocks = df.dist_to_red_rocks.astype(float)
        df.edu_rank_score_2022 = df.edu_rank_score_2022.astype(float)
        df.average_home_value = df.average_home_value.astype(float)

        # y = df.rank_score
        x = df[['unformattedPrice', 'beds', 'area', 'addressCity',
                'dist_to_downtown', 'dist_to_ski', 'dist_to_red_rocks',
                'edu_rank_score_2022', 'average_home_value']]
        x = pd.get_dummies(x)
        
        for col in cols:
            if col not in set(list(x.columns)):
                x[col] = 0
                
        x = x[cols].fillna(0)
        
        df['predictions'] = rf.predict(x)
        
        df = df[['address', 'predictions']]
        
        df.to_sql("denver_prediction_values", cursor, if_exists="append")
        cursor.close()
    except:
        print('No New Records For Scoring')

def score_data_price(rf, cols):
    cursor = sqlite3.connect("denver_real_estate.db")
    df = pd.read_sql_query(
        f'''
            SELECT *
            FROM denver_active_listings
            WHERE address NOT IN (SELECT address FROM denver_prediction_values_price)
        ''', cursor)
    
    try:
        df.unformattedPrice = df.unformattedPrice.astype(float)
        df.beds = df.beds.replace('null', 0).astype(int)
        df.baths = df.baths.replace('null', 0).astype(float).astype(int)
        df.area = df.area.replace('null', 0).astype(float)
        df.addressCity = df.addressCity.astype("category")
        df.dist_to_downtown = df.dist_to_downtown.astype(float)
        df.dist_to_ski = df.dist_to_ski.astype(float)
        df.dist_to_red_rocks = df.dist_to_red_rocks.astype(float)
        df.edu_rank_score_2022 = df.edu_rank_score_2022.astype(float)
        df.average_home_value = df.average_home_value.astype(float)

        # y = df.rank_score
        x = df[['beds', 'baths', 'area', 'addressCity',
                'dist_to_downtown', 'dist_to_ski', 'dist_to_red_rocks',
                'edu_rank_score_2022', 'average_home_value']]
        x = pd.get_dummies(x)
        
        for col in cols:
            if col not in set(list(x.columns)):
                x[col] = 0
                
        x = x[cols].fillna(0)
        
        df['predictions_price'] = rf.predict(x)
        
        df = df[['address', 'predictions_price']]
        
        df.to_sql("denver_prediction_values_price", cursor, if_exists="append")
        cursor.close()
    except:
        print('No New Records For Scoring')