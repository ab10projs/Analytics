import polars as pl
import pandas as pd
import statsmodels.api as sm
import json
import json
import threading
from collections import deque
import time

import dash
from click import style
from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.express as px

import redis
import polars as pl

STREAM_NAME = "prediction_model_data"

# ----------------------------------------------------
# Redis
# ----------------------------------------------------

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# ----------------------------------------------------
# Shared Buffer
# ----------------------------------------------------

buffer = deque(maxlen=400)
counter = 0

df = pl.read_csv("C://GIT_Repo_Analytics//Analytics//Technical Proof Of Concepts//DynamicModelUpdate//BaseData.csv",
                 infer_schema_length= 600)
dfCollect = df.clear()

# ----------------------------------------------------
# Stream Reader Thread
# ----------------------------------------------------
def stream_reader():
    global dfCollect
    last_id = "$"
    while True:
        messages = r.xread(
            {STREAM_NAME: last_id},
            block=100
        )
        if not messages:
            continue
        for stream_name, records in messages:
            for msg_id, values in records:
                last_id = msg_id
                rows = json.loads(values["data"])
                dfLatest = pl.DataFrame(rows)
                # print(dfCollect)
                buffer.append(dfLatest)
                dfCollect = dfCollect.vstack(dfLatest)
                # print("--------")

threading.Thread(
    target=stream_reader,
    daemon=True
).start()
#
# while True:
#     print(dfCollect)
#     time.sleep(1)

##---------------------Dash App--------------------- Start Here---------------------
import polars as pl
import numpy as np
import time
import pandas as pd
import os
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import date
import plotly.graph_objects as go
from datetime import datetime
from dash import dcc, html, Input, Output
import polars as pl

######## Sample scatter ############## Start
import plotly.express as px
import pandas as pd

# 1. Create a quick sample dataset
data = {
    "X_Axis": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Y_Axis": [10, 15, 13, 17, 22, 18, 25, 29, 24, 30],
    "Category": ["A", "A", "A", "A", "A", "B", "B", "B", "B", "B"]
}
df = pd.DataFrame(data)

# 2. Build the scatter plot
fig = px.scatter(
    df,
    x="X_Axis",
    y="Y_Axis",
    color="Category",  # Automatically colors points by group
    # title="Sample Scatter Chart",
    labels={"X_Axis": "X Values", "Y_Axis": "Y Values"}
)
fig.update_layout(
    showlegend=False,
    margin=dict(t=0, b=0, l=0, r=0), # 't=30' reduces the overall top canvas spacing
    title={
        'y': 0.95,                       # Pushes the title down closer to the chart canvas
        'x': 0.5,                        # Centers the title horizontally
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

# 3. View the figure

######## Sample scatter ############## end


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

BG_WHITE = "#ffffff"
TEXT_BLACK = "#000000"
GRID_GREY = "#e6e6e6"

app.layout = html.Div([
    dbc.Row(
        children=[
        dbc.Col(
            html.H3("Prediction Model", className="text-center"),
            width=12
        ),
        html.H4(id='iddfcount', children="Initial State"),
    ]
    ),

    dbc.Row(
        [
          dbc.Col(
              [
                html.H6("This column which be 20% of page width"),
            ],
                className="border",
                style={"width": "20%", "flex": "0 0 20%", "maxWidth": "20%"}
          ),
          dbc.Col([
                html.H6("This column which be 80% of page width"),
              dbc.Row(
                    html.H6("Row1"),
                    className="border",
              ),
              dbc.Row(
                  [
                    html.H6("Row2"),
                      dbc.Col([
                          html.H6("Col1"),
                            dcc.Graph(figure=fig,
                                      style={"height": "250px", "width": "300px"}),
                          ],
                          className="border p-0",
                        style={"width": "33%", "flex": "0 0 33%", "maxWidth": "33%"}
                      ),
                      dbc.Col(
                          html.H6("Col2"),
                          className="border",
                          style={"width": "33%", "flex": "0 0 33%", "maxWidth": "33%"}
                      ),
                      dbc.Col(
                          html.H6("Col3"),
                          className="border",
                          style={"width": "33%", "flex": "0 0 33%", "maxWidth": "33%"}
                      ),
                  ],
                  className="border",
              )

          ],
            className="border",
            style={"width": "80%", "flex": "0 0 80%", "maxWidth": "80%"}
          )
        ],
    ),

    dcc.Interval(
        id='interval-component',
        interval=500,
        n_intervals=0
    )
])


#------------------------ callbacks-----

@app.callback(
    Output('iddfcount','children' ),
    Input('interval-component', 'n_intervals')
)
def updateTxt(n_intervals):
    return str(dfCollect.shape[0]) + str(dfCollect.tail(1))

if __name__ == "__main__":
    app.run(debug=True)
