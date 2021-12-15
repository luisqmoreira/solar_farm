from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import plotly_express as px
import pandas as pd
from terraincache import TerrainTiles
import georasters as gr
import geopandas as gpd
import geopy
from osgeo import gdal
from matplotlib import pyplot as plt
import rasterio

"""
Define Coordinate Bounds for TerrainTiles
"""
bounds = [-9.888, 36, -6, 43.999]

"""
Initialize with bounds and zoom of interest
"""
tt = TerrainTiles(bounds, 11)

"""
load to numpy array
"""
array = tt.load()

# plot the array directly
# plt.imshow(array, cmap='terrain', extent=bounds)
# plt.show()

"""
Exporting the extracted terrain file to a Tiff file
"""
# tt.save(out_file="dem.tif")

"""
Retrieving the Tiff file
"""
elevation = gr.from_file('/Users/luismoreira/dem.tif')

# elevation.plot()
# plt.show()

"""
Transforming the Tiff file into a pandas dataframe
"""
elevation = elevation.to_pandas()

"""
Filtering out coordinates over the ocean by setting elevation to >0
"""
elevation_filtered = elevation[elevation['value'] >= 0]

"""
Retrieving inclination file
"""
incline = gr.from_file('/Users/luismoreira/Downloads/declives/declives.tif')
# incline.plot()
# plt.show()

"""
Transforming Tiff file to pandas dataframe
"""
incline = incline.copy().to_pandas()
incline['long'] = incline['x'] / 1000
incline['lat'] = incline['y'] / 1000

"""
Filter tables to the same coordinates
"""
incline_filtered = incline[
    (incline['long'] <= -6.0023606557377045) &
    (incline['long'] >= -9.692065573770492) &
    (incline['lat'] <= 43.999) &
    (incline['lat'] >= 36.17707349468713)
    ]

incline_filtered.drop(['x', 'y'], axis=1, inplace=True)

print('1')
# Solar

solar = gr.from_file(
    '/Users/luismoreira/Downloads/Portugal_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF/PVOUT.tif')
# solar.plot()
solar = solar.to_pandas()

"""
Filter tables to the same coordinates
"""

solar_long_filtered = solar[(solar['x'] <= -6.0023606557377045) &
                            (solar['x'] >= -9.692065573770492)
                            ]

solar_lat_filtered = solar_long_filtered[
    (solar_long_filtered['y'] <= 43.999) &
    (solar_long_filtered['y'] >= 36.17707349468713)
    ]

solar_final = solar_lat_filtered.copy()

solar_final["long_position"] = pd.cut(solar_final["x"], 40)
solar_final["lat_position"] = pd.cut(solar_final["y"], 100)

solar_by_square = solar_final.groupby(["long_position", "lat_position"]).agg({"value": 'mean'})

solar_by_square.reset_index(inplace=True)

"""
Removing null values
"""
solar_by_square_clean = solar_by_square.copy().dropna()

""""
Topography
"""
elevation_processed = elevation_filtered.copy()

elevation_processed["long_position"] = pd.cut(elevation_processed["x"], 40)
elevation_processed["lat_position"] = pd.cut(elevation_processed["y"], 100)

elevation_by_square = elevation_processed.groupby(["long_position", "lat_position"]).agg({"value": 'mean'})

elevation_by_square.reset_index(inplace=True)

elevation_by_square_clean = elevation_by_square.copy().dropna()

incline_filtered["long_position"] = pd.cut(incline_filtered["long"], 40)
incline_filtered["lat_position"] = pd.cut(incline_filtered["lat"], 100)
incline_by_square = incline_filtered.groupby(["long_position", "lat_position"]).agg({"value": 'mean'})
incline_by_square.reset_index(inplace=True)

print('Halfway')

"""
Merging Solar and elevation 
"""

test = pd.merge(left=solar_by_square, right=elevation_by_square, left_index=True, right_index=True)
test.columns = ['long_position_solar', 'lat_position_solar', 'value_phov', 'long_position_topo', 'lat_position_topo',
                'elevation']

"""
Further cleaning
"""

test_clean = test.copy().dropna()
test_clean2 = test_clean.copy()

"""
Separating longitude and latitude interval bins and changing type from object to float
"""

"""
Longitude
"""
test_clean2['long_leftend'] = test_clean2['long_position_topo'].apply(lambda x: float(x.left))
test_clean2['long_rightend'] = test_clean2['long_position_topo'].apply(lambda x: float(x.right))
test_clean2['long_leftend'] = test_clean2['long_leftend'].astype('float64')
test_clean2['long_rightend'] = test_clean2['long_rightend'].astype('float64')

"""
Latitude
"""
test_clean2['lat_leftend'] = test_clean2['lat_position_solar'].apply(lambda x: float(x.left))
test_clean2['lat_rightend'] = test_clean2['lat_position_solar'].apply(lambda x: float(x.right))
test_clean2['lat_leftend'] = test_clean2['lat_leftend'].astype('float64')
test_clean2['lat_rightend'] = test_clean2['lat_rightend'].astype('float64')

"""
Merge Solar and elevation with inclination
"""
print(3)
merged = pd.merge(left=test, right=incline_by_square, left_index=True, right_index=True)
merged.dropna(inplace=True)

merged['long_leftend'] = merged['long_position_topo'].apply(lambda x: float(x.left))
merged['long_rightend'] = merged['long_position_topo'].apply(lambda x: float(x.right))
merged['long_leftend'] = merged['long_leftend'].astype('float64')
merged['long_rightend'] = merged['long_rightend'].astype('float64')

merged['lat_leftend'] = merged['lat_position'].apply(lambda x: float(x.left))
merged['lat_rightend'] = merged['lat_position'].apply(lambda x: float(x.right))
merged['lat_leftend'] = merged['lat_leftend'].astype('float64')
merged['lat_rightend'] = merged['lat_rightend'].astype('float64')


def find_plot(longitude, latitude):
    """
    :param longitude:
    :param latitude:
    :return: information about land in specified coordinates
    """
    return merged[(merged['long_leftend'] < longitude) & (merged['long_rightend'] > longitude) & (
            merged['lat_leftend'] < latitude) & (merged['lat_rightend'] > latitude)]


"""
Adding address label to coordinates
"""
print('4')
"""
locator = Nominatim(user_agent="myGeocoder", timeout=20)
geocode = RateLimiter(locator.reverse, min_delay_seconds=0.001)
print('5')
merged2 = merged.copy()
merged2['coordinates'] = merged2['lat_leftend'].map(str) + ',' + merged2['long_leftend'].map(str)
merged2['Address'] = merged2['coordinates'].apply(geocode)
"""

merged2 = pd.read_csv('/Users/luismoreira/Desktop/Final_project/final_project/table.csv')


def find_spain(x):
    """
    :param x: dataframe column
    :return: boolean flag for whether the word 'Espana' is in the specified columns
    """
    if 'España' in x[0]:
        return 1
    else:
        return 0


merged2['esp_or_not'] = merged2['Address'].apply(find_spain)

px.imshow(px.scatter_mapbox(merged2, lat='lat_leftend', lon='long_leftend', zoom=4, mapbox_style="carto-positron"))
