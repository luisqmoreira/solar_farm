import pandas as pd
import plotly_express as px

data = pd.read_csv('/Users/luismoreira/Desktop/Final_project/final_project/table.csv')


def find_spain(x):
    """
    :param x: dataframe column
    :return: boolean flag for whether the word 'Espana' is in the specified columns
    """
    if 'España' in x[0]:
        return 1
    else:
        return 0


data['esp_or_not'] = data['Address'].apply(find_spain)


px.imshow(px.scatter_mapbox(data, lat='lat_leftend', lon='long_leftend', zoom=4, mapbox_style="carto-positron"))

#print(type(data['lat_leftend'][0]))
print(data['long_leftend'].dtypes)
