# Importing libraries

import plotly.graph_objects as go  # or
import plotly.express as px
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# ------------------------------------------------------------------------------
# Importing files and formatting

matrix = pd.read_csv("/Users/luismoreira/Desktop/Final_project/Databases/matrix.csv")

mb_token = 'pk.eyJ1IjoibHVpc3FtIiwiYSI6ImNreDgyYjR3cjJ2M2sycXB6amluaGVxdDcifQ.juWpwJjnuW99RKdeUW7dOg'

maps = pd.read_csv('/Users/luismoreira/Desktop/Final_project/final_project/map_data.csv')

matrix.set_index('x', inplace=True)

matrix.columns = [float(i) for i in matrix.columns]

lat_search = list(matrix.columns)

long_search = list(matrix.index)

lat_search = [float(item) for item in lat_search]

long_search = [float(item) for item in long_search]

# ------------------------------------------------------------------------------

px.set_mapbox_access_token(mb_token)

# Inclination Map
specFig_incline = px.scatter_mapbox(maps,
                                    lat='lat_leftend',
                                    lon='long_leftend',
                                    zoom=4,
                                    mapbox_style="carto-darkmatter",
                                    color='Inclination',
                                    height=500,
                                    title='Inclination')

specFig_incline.update_layout(title_x=0.5,
                              title={'font': {'size': 32.5}},
                              font_family="sans-serif",
                              font_color='white',
                              paper_bgcolor='#0E1012')

# Photovoltaic Potential Map
specFig_phov = px.scatter_mapbox(maps,
                                 lat='lat_leftend',
                                 lon='long_leftend',
                                 zoom=4,
                                 mapbox_style="carto-darkmatter",
                                 color='Phov',
                                 height=500,
                                 title='Photovoltaic Potential')

specFig_phov.update_layout(title_x=0.5,
                           title={'font': {'size': 32.5}},
                           font_family="sans-serif",
                           font_color='white',
                           paper_bgcolor='#0E1012')

# Elevation Map
specFig_elevation = px.scatter_mapbox(maps,
                                      lat='lat_leftend',
                                      lon='long_leftend',
                                      zoom=4,
                                      mapbox_style="carto-darkmatter",
                                      color='Elevation',
                                      height=500,
                                      title='Elevation')

specFig_elevation.update_layout(title_x=0.5,
                                title={'font': {'size': 32.5}},
                                font_family="sans-serif",
                                font_color='white',
                                paper_bgcolor='#0E1012')


# ------------------------------------------------------------------------------

# Filtering dataframe according to lat and long provided

def search_lat(lat):
    lats = []
    for item in lat_search:
        if (item > (lat - 0.5)) & (item < (lat + 0.5)):
            lats.append(item)
        else:
            continue
    return lats


def search_long(long):
    longs = []
    for item in long_search:
        if (item > (long - 0.5)) & (item < (long + 0.5)):
            longs.append(item)
        else:
            continue
    return longs


# ------------------------------------------------------------------------------

# App

app = dash.Dash()

app.layout = html.Div([
    html.H1(id='header',
            children='Solar Farming in Portugal',
            style={'color': 'white', 'fontSize': 40, 'font': 'sans-serif', 'textAlign': 'center'}),
    dcc.Graph(id='graph',
              figure='surface'),
    html.Div([
        dcc.Slider(id='select_lat',
                   min=36.18,
                   max=44,
                   step=0.02,
                   value=38,
                   marks={i: i for i in np.arange(36.2, 44, 0.5)},
                   tooltip={'hover': True}),
        dcc.Slider(id='select_long',
                   min=-9.69,
                   max=-6.1,
                   step=0.02,
                   value=-8,
                   marks={i: i for i in np.arange(-10, -6, 0.5)},
                   tooltip={'hover': True}
                   ),
        html.Div(id='my-div')
    ]),
    html.Div([
        dcc.Graph(id='Inclination',
                  figure=specFig_incline,
                  ),
        dcc.Graph(id='Elevation',
                  figure=specFig_elevation),
        dcc.Graph(id='Phov',
                  figure=specFig_phov)
    ], style={'background-color': '#0E1012'})
], style={'background-color': '#0E1012'})


# ------------------------------------------------------------------------------

@app.callback(
    Output('graph', 'figure'),
    [Input('select_lat', 'value'),
     Input('select_long', 'value')])
def search(lat, long):
    data = matrix[search_lat(lat)].loc[search_long(long)]

    z_data = data

    fig = go.Figure(data=[go.Surface(z=z_data.values)])

    fig.update_layout(title={'text': 'Topometry',
                             'x': 0.5,
                             'font': {
                                 'size': 32.5}},
                      autosize=False,
                      width=600,
                      height=600,
                      margin=dict(l=65, r=50, b=65, t=90),
                      font_family="sans-serif",
                      font_color='white',
                      paper_bgcolor='#0E1012')

    return fig


if __name__ == '__main__':
    app.run_server()
