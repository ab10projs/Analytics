########################## import and setup section starts ############################################################################################################### 1
import dash
import polars as pl
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import numpy as np
import json
import plotly.graph_objs as go
import plotly.colors as pc
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import datetime

colorsRed = pc.n_colors('rgb(255,200,200)', 'rgb(150,0,0)', 15, colortype='rgb') # used in pie red shades
colorsGreen = pc.n_colors('rgb(200,255,200)', 'rgb(0,100,0)', 15, colortype='rgb') # used in pie red shades

import time
import re
# Configure Polars for better performance
pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_width_chars(1000)
pl.Config.set_tbl_rows(1000)
pl.Config.set_float_precision(4)

# Configure Pandas
pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option("display.max_rows", 1000)
desired_width = 5000000
pd.set_option('display.width',desired_width )
pd.set_option('display.max_columns', 50)

######################### import and setup section end     ############################################################################################################### 1

path= "C:/GIT_Repo_Analytics/Analytics/Visualizations/Dash/data/"
df = pl.read_csv(f"{path}ConcreteCompressiveStrength.csv")
print(df.head(1))


fig1 = go.Figure()
fig1.update_layout(
    margin=dict(l=5, r=5, t=5, b=5),   # reduces whitespace
)



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
 dbc.Row([
     html.H2("Actionable Insights Analytics Dashboard",className="text-center" )
 ]),
 dbc.Row([
  dbc.Col([dcc.Dropdown(style={"marginBottom": "4px"}),
                   dcc.Dropdown(style={"marginBottom": "4px"}),
                   dcc.Dropdown(style={"marginBottom": "4px"}),
                   dcc.Dropdown(style={"marginBottom": "40px"}),
                   dbc.Col(dcc.Graph(id='gp7', figure=fig1, style={"height": "300px"}, config={"displayModeBar": False})),

           ], width= 2, className="ms-5" ),
  dbc.Col([html.Div([
                                dbc.Row(
                                    [
                                        dbc.Col(dcc.Graph(id='gp1', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                                        dbc.Col(dcc.Graph(id='gp2', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                                        dbc.Col(dcc.Graph(id='gp3', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                                        dbc.Col(dcc.Graph(id='gp4', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                                    ],
                                    className="gx-1"   # <— reduces horizontal space between graphs
                                ),

                        ]),
                      dbc.Row(
                          [
                              dbc.Col(dcc.Graph(id='gp5', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                              dbc.Col(dcc.Graph(id='gp6', figure=fig1, style={"height": "250px"}, config={"displayModeBar": False})),
                          ],
                          className="gx-1",  # <— reduces horizontal space between graphs
                      ),
                    ],width= 9),

 ]),
])

if __name__ == "__main__":
    app.run(debug=True)




