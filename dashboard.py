import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

from loader.load_openflight_data import load_locations, load_routes_join

app = dash.Dash('Openflights')

loc_df = load_locations('./data/airports.dat')
route_df = load_routes_join('./data/routes.dat', loc_df)

floor_marks = list(range(0, len(route_df), 500))
ceil_marks = list(range(500, len(route_df), 500)) + [len(route_df) - 1]
slider_marks = {f: f'{f} to {c}'  for f, c in zip(floor_marks, ceil_marks)}

app.layout = html.Div(children=[
    html.H1(children='Openflights data'),

    dcc.Graph(id='world-map-graph'),
    dcc.Slider(
        id='flights-slider',
        min=100,
        max=len(route_df),
        value=500,
        marks=slider_marks,
        step=None
    )
])

@app.callback(Output('world-map-graph', 'figure'),
              [Input('flights-slider', 'value')])
def update_world_map(num_routes):
    fig = go.Figure()

    # plot the locations
    fig.add_trace(go.Scattergeo(
        lon=loc_df['longitude'],
        lat=loc_df['latitude'],
        hoverinfo='text',
        text=loc_df['name'],
        mode='markers',
        marker=dict(size=2, color='rgb(255, 0, 0)')
    ))

    # plot the flights
    r_df = route_df.iloc[num_routes: num_routes + 500]
    lons = np.empty(3 * len(r_df))
    lons[::3] = r_df['longitude']
    lons[1::3] = r_df['longitude_destination']
    lons[2::3] = None

    lats = np.empty(3 * len(r_df))
    lats[::3] = r_df['latitude']
    lats[1::3] = r_df['latitude_destination']
    lats[2::3] = None

    fig.add_trace(go.Scattergeo(
        lon=lons,
        lat=lats,
        mode='lines',
        line=dict(width=1, color='green'),
        opacity=.3
    ))

    fig.update_layout(geo=dict(landcolor='rgb(243, 243, 243)',
                               countrycolor='rgb(204, 204, 204)'),
                      margin=dict(l=0, r=0, b=0, t=0))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
