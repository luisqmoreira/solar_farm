import plotly.graph_objects as go  # or plotly.express as px
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output


# ------------------------------------------------------------------------------

elevation = pd.read_csv("/Users/luismoreira/Desktop/Final_project/Databases/matrix.csv")

matrix = elevation.copy()

matrix.set_index('x', inplace=True)

matrix.columns = [float(i) for i in matrix.columns]

display(matrix)

lat_search = list(matrix.columns)

long_search = list(matrix.index)

lat_search = [float(item) for item in lat_search]

long_search = [float(item) for item in long_search]


# ------------------------------------------------------------------------------


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

app = dash.Dash()

app.layout = html.Div([
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
    ])
], style={'background-color': '#0E1012'})


@app.callback(
    Output('graph', 'figure'),
    [Input('select_lat', 'value'),
     Input('select_long', 'value')])
def search(lat, long):
    data = matrix[search_lat(lat)].loc[search_long(long)]

    z_data = data

    fig = go.Figure(data=[go.Surface(z=z_data.values)])

    fig.update_layout(title='Topometry', autosize=False,
                      width=600,
                      height=600,
                      margin=dict(l=65, r=50, b=65, t=90),
                      paper_bgcolor='#0E1012')

    return fig


if __name__ == '__main__':
    app.run_server()
