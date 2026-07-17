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

STREAM_NAME = "stocks_stream"

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
deqDate = deque(maxlen=400)
deqDateTop10 = deque(maxlen=10)
deqCloseScrip1 = deque(maxlen=5000)
deqCloseScrip2 = deque(maxlen=5000)
deqCloseScrip3 = deque(maxlen=5000)
deqCloseScrip4 = deque(maxlen=5000)

counter = 0

# ----------------------------------------------------
# Stream Reader Thread
# ----------------------------------------------------

def stream_reader():

    last_id = "$"

    # print("Subscriber started")

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

                df = pl.DataFrame(rows)

                buffer.append(df)
                deqDate.append(df['DATE1'][0])
                deqDateTop10.append(df['DATE1'][0])
            

threading.Thread(
    target=stream_reader,
    daemon=True
).start()



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


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)


BG_WHITE = "#ffffff"
TEXT_BLACK = "#000000"
GRID_GREY = "#e6e6e6"


#-------------------------------------------------------------------------- Start
app.layout = html.Div([
    dbc.Row(
        dbc.Col(
            html.H3("Near Realtime Data Analytics", className="text-center"),
            width=12
        )
    ),
    dbc.Container(
        fluid=True,
        className="p-3",
        children=[
            dbc.Container(
                [
                    dbc.Row(
                        children=[
                            dbc.Row([
                                dbc.Col([
                                # dbc.Row(
                                #     html.H3("Tab1", className="mb-0")
                                # ),
                                dbc.Row(
                                    dcc.Graph(id='scatter-chart',
                                              style={"height": "250px"}),
                                )
                            ], width=3),

                            dbc.Col([
                                # dbc.Row(
                                #     html.H3("Top Gainer H3", className="mb-0")
                                # ),
                                dbc.Row(
                                    dcc.Graph(id='bar1',
                                              style={"height": "250px"}),
                                )
                            ], width=3),

                            dbc.Col([
                                # dbc.Row(
                                #     html.H3("Top Losers H3", className="mb-0")
                                # ),
                                dbc.Row(
                                    dcc.Graph(id='bar2',
                                              style={"height": "250px"}),
                                )
                            ], width=3),


                            dbc.Col([
                                # dbc.Row(
                                #     html.H3("Top Mv Avg", className="mb-0")
                                # ),
                                dbc.Row(
                                    dcc.Graph(id='bar3',
                                              style={"height": "250px"}),
                                )
                            ], width=3),

                            ])
                    ]),
                    dbc.Row([
                                dbc.Col([
                                html.P(" "),
                                html.P("Business Case:"),
                                html.Ul([
                                    html.Li("Better decision-making"),
                                    html.Li("Proactive approach"),
                                    html.Li("Competitive Advantage "),
                                    html.Li("Greater Operational Efficiency")
                                ], style={'fontSize': '80%'})
                            ], width=3 ),

                            dbc.Col([
                                html.P(" "),
                                html.P("Technical Considerations Required:"),
                                html.Ul([
                                    html.Li("Asynchronous data ingestion"),
                                    html.Li("Vectorized dataframe processing"),
                                    html.Li("Thread-safe shared memory"),
                                    html.Li("Fault-tolerant Redis buffering"),
                                    html.Li("Efficient in-memory analytics"),
                                ], style={'fontSize': '80%'})
                            ], width=3),

                            dbc.Col([
                                # html.P("Features of this dashboard:"),
                                dbc.Row(
                                    dcc.Graph(id='fig5',
                                              style={"height": "250px"}),
                                )
                            ], width=3),

                            dbc.Col([
                                # html.P("Features of this dashboard:"),
                                dbc.Row(
                                    dcc.Graph(id='fig6',
                                              style={"height": "250px"}),
                                )
                            ], width=3),

                             ])
                ]
            ),

        ]),
    # dcc.Graph(id='scatter-chart'),

    dcc.Interval(
        id='interval-component',
        interval=400,
        n_intervals=0
    )
])

@app.callback(
    Output('scatter-chart', 'figure'),
    Output('bar1', 'figure'),
    Output('bar2', 'figure'),
    Output('bar3', 'figure'),
    Output('fig5', 'figure'),
    Output('fig6', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_scatter_chart(n_intervals):
    fig1 = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()
    fig5 = go.Figure()
    fig6 = go.Figure()
    # print('counter', counter)
    # print('n_intervals', n_intervals)
    # print('deqDate', list(deqDate))
    global buffer
    global deqDateTop10
    if len(buffer)>0:
        df = buffer[-1]
        frames = list(buffer)
        dfMerged = pl.concat(frames, how="vertical_relaxed")

        df = df.with_columns(((pl.col('CLOSE_PRICE')- pl.col('PREV_CLOSE'))/pl.col('PREV_CLOSE')).alias('percentChange'))
        dfTop = df.select([pl.col('SYMBOL'), pl.col('percentChange')]).sort(by = pl.col('percentChange'))
        dfTopGainers = dfTop.tail(5)
        dfTopGainers = dfTopGainers.sort(by = pl.col('percentChange'), descending = True)
        dfTopLosers = dfTop.head(5)
        # print('Losers')
        # print(dfTopLosers)
        #
        # print("deqDateTop10")
        # print(deqDateTop10)
        # print(df.head(1))
        #
        # print('Gainers')
        # print(dfTopGainers)
        # print(dfMerged.shape)
        # print(dfTop.head(4))
        dfMergedGp = dfTop.sort(['SYMBOL', 'percentChange']).group_by('SYMBOL').agg(
            pl.col('percentChange').tail(10).mean().alias('AvgLastTen')
        )
        # print(dfMergedGp.sort(by = pl.col('AvgLastTen'), descending=True).head(5))
        dfTopMvAvg =dfMergedGp.sort(by = pl.col('AvgLastTen'), descending=True).head(5)


        fig1 = go.Figure(
            go.Scattergl(
                x=df['SYMBOL'],
                y=df['CLOSE_PRICE'],
                mode='markers',
                marker=dict(size=1,
                            color= df["CLOSE_PRICE"],
                            colorscale="Viridis",
                            opacity=0.8,
                            line=dict(width=0.8)
                            )
            )
        ).update_yaxes(range=[0, 500]
                            ).update_xaxes(tickfont=dict(size=1)
                            ).update_layout(
                                title= dict(
                                    # text='Your Custom Title',
                                    xanchor='center',
                                    x=0.5
                                ),
                                xaxis= dict(
                                tickangle=-45,
                                title='Stocks',
                                gridcolor='white',
                                ), yaxis= dict(
                                    title='Live Stock Prices',
                                    showgrid=True,
                                    gridcolor='white',
                                    gridwidth=1
                                ),
                                paper_bgcolor='white',
                                plot_bgcolor='white'
                            )
        fig1.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            template="plotly_white",
        )

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=dfTopGainers["SYMBOL"].to_list(),
                y=dfTopGainers["percentChange"].to_list(),
                name="Top Gainers",
                marker=dict(
                    color=dfTopGainers["percentChange"].to_list(),
                    colorscale=[
                                    [0.0, "#81C784"],   # light green (not white)
                                    [0.3, "#66BB6A"],
                                    [0.6, "#43A047"],
                                    [1.0, "#1B5E20"]    # dark green
                                ],
                )
            )

        )
        fig2.update_layout(
            title="Top Advancing Stocks",
            # xaxis_title="Stocks",
            yaxis_title="Percent Change",
            template="plotly_white",
            xaxis= dict(tickangle=45, tickfont=dict(size=10))
        )

        fig3 = go.Figure()
        fig3.add_trace(
            go.Bar(
                x=dfTopLosers["SYMBOL"],
                y=dfTopLosers["percentChange"],
                name="Top Losers",
                marker=dict(
                color=dfTopLosers["percentChange"].to_list(),
                colorscale=[
                    [0.0, "#EF9A9A"],  # light red
                    [0.3, "#E57373"],
                    [0.6, "#EF5350"],
                    [1.0, "#B71C1C"]  # dark red
                ])
            )
        )
        fig3.update_layout(
            title="Top Declining Stocks",
            # xaxis_title="Stocks",
            yaxis_title="Percent Change",
            template="plotly_white",
            xaxis=dict(tickangle=45, tickfont=dict(size=10))
        )


        fig4.add_trace(
            go.Bar(
                x=dfTopMvAvg["SYMBOL"],
                y=dfTopMvAvg["AvgLastTen"],
                name="10MvAvg",
                marker_color=dfTopMvAvg["AvgLastTen"],
            )
        )
        fig4.update_layout(
            title="Top Moving Average",
            # xaxis_title="Stocks",
            yaxis_title="Moving Avg",
            template="plotly_white",
            xaxis=dict(tickangle=45, tickfont=dict(size=10))
        )

        #--------------------- Fig 5 multicharts start here

        dfScrip1= dfMerged.filter(pl.col('SYMBOL')=='ICICIBANK')
        # dfScrip2 = dfMerged.filter(pl.col('SYMBOL') == 'RELIANCE')
        dfScrip3 = dfMerged.filter(pl.col('SYMBOL') == 'BHEL')

        fig5.add_trace(
            go.Scatter(
                x=dfScrip1["DATE1"].to_list(),
                y=dfScrip1["CLOSE_PRICE"].to_list(),
                mode="markers",
                marker=dict(size=2,
                            color=dfScrip1["CLOSE_PRICE"],
                            colorscale="Viridis",
                            opacity=0.8,
                            line=dict(width=0.8)
                            ),
                name="ICICI"
            )
        )

        fig5.update_layout(
            title={
                'text': "ICICI",
                'font': {'family': "Arial", 'size': 14},
                'x': 0.5,  # Centers the title (0 = left, 0.5 = center, 1 = right)
                'xanchor': 'center'
            },
            # xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            template="plotly_white"
        )

        fig6.add_trace(
            go.Scatter(
                x=dfScrip3["DATE1"].to_list(),
                y=dfScrip3["CLOSE_PRICE"].to_list(),
                mode="markers",
                marker=dict(size=2,
                            color=dfScrip3["CLOSE_PRICE"],
                            colorscale="Viridis",
                            opacity=0.8,
                            line=dict(width=0.8)
                            ),
                name="BHEL"
            )
        )

        fig6.update_layout(
                title={
                    'text': "BHEL",
                    'font': {'family': "Arial", 'size': 14},
                    'x': 0.5,  # Centers the title (0 = left, 0.5 = center, 1 = right)
                    'xanchor': 'center'
                },
            # xaxis_title="Date",
            yaxis_title="Price",
            hovermode="x unified",
            template="plotly_white"
        )

        # --------------------- Fig 5 multicharts end here

    return fig1, fig2, fig3, fig4, fig5, fig6
#-------------------------------------------------------------------------- Start

if __name__ == "__main__":
    app.run(debug=True)
