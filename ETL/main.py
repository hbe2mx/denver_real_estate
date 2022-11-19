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
import datetime
from datetime import date
import sqlite3
from sklearn.ensemble import RandomForestRegressor
import logging
exec(open('ETL\\config.py').read())
os.chdir(user_directory + '\\denver_real_estate\\Logs')
logging.basicConfig(filename=f"denver_real_estate_ETL_{str(datetime.datetime.now()).replace('.', '').replace(':', '_').replace('-', '_')}.log", encoding='utf-8', level=logging.DEBUG, force=True)
logging.debug('Log Debug: ')
logging.info('Log Info: ')
logging.warning('Log Warning: ')
logging.error('Log Error: ')

# logging.basicConfig(filename=f"Logs\\denver_real_estate_ETL_{str(datetime.datetime.now()).replace('.', '')}.log", filemode='w', encoding='utf-8', level=logging.DEBUG, force=True)
os.chdir(user_directory + '\\denver_real_estate\\ETL')



import helper_functions
from helper_functions import scraper, spider, build_model, score_data, score_data_price

os.chdir(user_directory + '\\denver_real_estate')
#Add New Records to Database and pull dataframe of latest data
df = spider(url_list, pois)

#Build Random Forest Model for Use in Scoring
rf, cols, rf2, cols2 = build_model()

#Score new data with Model
score_data(rf, cols)

score_data_price(rf2, cols2)