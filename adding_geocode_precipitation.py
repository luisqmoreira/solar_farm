import pandas as pd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

data = pd.read_csv('/Users/luismoreira/Desktop/Final_project/final_project/missing_cloud_cover.csv')

data = data.drop('Unnamed: 0', axis = 1)

precipitation = pd.read_csv('/Users/luismoreira/Documents/PyCharm/solar_farm/precipitation.csv')

locator = Nominatim(user_agent="myGeocoder", timeout=20)
rgeocode = RateLimiter(locator.reverse, min_delay_seconds=0.001)

precipitation['coordinates'] = precipitation['lat'].map(str) + ',' + precipitation['long'].map(str)

precipitation['Address'] = precipitation['coordinates'].apply(rgeocode)