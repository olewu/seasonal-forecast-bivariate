from dash import html, dcc, Dash
from dash.dependencies import Input, Output

import plotly.express as px
import numpy as np
import os
import xarray as xr
from datetime import datetime, date, timedelta

dpath = '/Users/owul/Library/CloudStorage/OneDrive-NORCE/data/'

city_coords_lalo = {
    'Bergen'    : [60.389, 5.33],
    'Oslo'      : [59.913,10.739],
    'Trondheim' : [63.43, 10.393],
    'Tromsø'    : [69.683,18.943]
}

MONTH_NAMES_long = ['January','February','March','April','May','June','July','August','September','October','November','December']

opts_dict = [{'label':ci,'value':ci} for ci in city_coords_lalo.keys()]

td = datetime.today()

app = Dash(__name__)

@app.callback(
    Output('scatter',
           'figure'),
    [Input('city-dropdown', 'value'),
     Input('init-date','date'),
     Input('lead-month','value')],
)
def scatter_plot(city,init_date,lead_month):
    
    init_date_dt = date.fromisoformat(str(init_date))
    
    init_year,init_month = init_date_dt.year,init_date_dt.month
    
    if lead_month > 5:
        lead_month = 5
    elif lead_month < 1:
        lead_month = 1
        
    displ_month = MONTH_NAMES_long[(init_month + lead_month)%12 - 1]
    
    tp_file = os.path.join(dpath,'forecast_production_detailed_total_precipitation_{0:d}_{1:d}.nc4'.format(init_year,init_month))
    t2_file = os.path.join(dpath,'forecast_production_detailed_2m_temperature_{0:d}_{1:d}.nc4'.format(init_year,init_month))

    lalo = city_coords_lalo[city]
    
    title = '{0:s} {1:s}'.format(city,displ_month)
    
    with xr.open_dataset(tp_file) as ds_tp, xr.open_dataset(t2_file) as ds_t2:

        tp_data = ds_tp.sel(lat=lalo[0],lon=lalo[-1],lead_month=lead_month, method='nearest')
        t2_data = ds_t2.sel(lat=lalo[0],lon=lalo[-1],lead_month=lead_month, method='nearest')
            
        tp_stdzd = ((tp_data.forecast - tp_data.climatology)/tp_data.sd).values
        t2_stdzd = ((t2_data.forecast - t2_data.climatology)/t2_data.sd).values
        
        fig = px.scatter(
            x=t2_stdzd,
            y=tp_stdzd,
            range_x = [-3.5,3.5],
            range_y = [-3.5,3.5],
            labels={'x':'2m temperature (stdzd)','y':'total precipitation (stdzd)'},
            title=title,
            width = 700,
            height = 700
        )
        
#     fig.update_layout(
#         margin=dict(l=20, r=20, t=20, b=20),
#         paper_bgcolor='LightSteelBlue',
#     )
    
    return fig

app.layout = html.Div(
    children=[
        html.H1(children="2m Temperature vs. Precipitation"),
        html.Div(
            children=[
                html.H2("Choose place and lead time"),
                html.Div(
                    children=[
                        html.P("City"),
                        dcc.Dropdown(
                            id="city-dropdown",
                            options = opts_dict,
                            value='Bergen',
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.P("Initialization Date"),
                        dcc.DatePickerSingle(
                            id = "init-date",
                            placeholder = "Initialization Date",
                            initial_visible_month = datetime.today().date() - timedelta(days=15),
                            min_date_allowed = datetime.now().strftime('2022-08'),
                            max_date_allowed = datetime.today().date(),
                            display_format='YYYY-MM',
                            first_day_of_week = 1
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.P("Lead Month"),
                        dcc.Input(
                            id = "lead-month",
                            placeholder = "Lead Month",
                            type = "number",
                            value = 1,
                        ),
                    ],
                ),
            ],
            # can use CSS formatting with `style`
            style = {
                "backgroundColor": "#DDDDDD",
                "maxWidth": "800px",
                "padding": "10px 20px",
            },
        ),
        html.Div(
            children=[
                html.H2("Scatter"),
                dcc.Graph(id="scatter"),
            ],
            style={
                "backgroundColor": "#DDDDDD",
                "maxWidth": "800px",
                "marginTop": "10px",
                "padding": "10px 20px",
            },
        ),
    ]
)

if __name__ == "__main__":
    app.run_server()