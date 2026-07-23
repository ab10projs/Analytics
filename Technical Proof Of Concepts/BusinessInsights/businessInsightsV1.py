import polars as pl
import pandas as pd
import numpy as np
import datetime
import dash
import plotly


pd.set_option('display.max_columns', None)
pl.Config.set_fmt_float("full")

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



import polars as pl

# Remove the limit on the number of displayed columns
pl.Config.set_tbl_cols(-1)

# Prevent columns from collapsing into '...'
pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_width_chars(10000)

lstPortfolio =['Apex Wealth', 'Zenith Capital', 'Vista Wealth', 'Nexus Advisors', 'Propel Capital']
lstStrategy = ['Stochastic', 'bollinger', 'Trend Reversal', 'Parabolic SAR', 'Relative Streangth']
probabilitiesPortfolio = [0.52, 0.23, 0.15, 0.07, 0.03]
probabilitiesStrategies = [0.42, 0.18, 0.19, 0.08, 0.13]

# #-------------------------------------------  Parquet Data Preperation starts ----------------------
# exposure = 10000
# df = pl.read_csv("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/dfMerged.csv")
#
# df = df.with_columns(pl.col("DATE1").str.to_date(format="%Y-%m-%d"),
#                       pl.col("DELIV_QTY").cast(pl.Float64, strict= False),
#                       pl.col("DELIV_PER").cast(pl.Float64, strict= False)
#                     )
#
#
# dfFiltered = df.filter((pl.col('DATE1').dt.year() == 2021))
# dfFiltered = dfFiltered.with_columns(pl.col('DATE1').dt.offset_by("1y").alias("DATE1"))
# dfFiltered = dfFiltered.with_columns(
#     pl.col(pl.Float64, pl.Float32).map_elements(
#         lambda col: col * np.random.uniform(0.93, 1.07),
#         return_dtype=pl.Float64
#     )
# )
#
# dfFiltered = dfFiltered.with_columns(
#     Portfolio=pl.Series(
#         np.random.choice(
#             lstPortfolio,
#             size=dfFiltered.height,
#             p=probabilitiesPortfolio
#         )
#     )
# )
#
# dfFiltered = dfFiltered.with_columns(
#     Strategy=pl.Series(
#         np.random.choice(
#             lstStrategy,
#             size=dfFiltered.height,
#             p=probabilitiesStrategies
#         )
#     )
# )
#
# dfFiltered = dfFiltered.with_columns(pl.when((pl.col('DATE1').dt.weekday()>=2)
#                               & (pl.col('DATE1').dt.weekday()<=5)).then(pl.lit(1)
# ).otherwise(None).alias('LongStatus'))
#
# dfFiltered = dfFiltered.with_columns( pl.when(pl.col('LongStatus')==1).then(
#     (pl.lit(exposure)/pl.col('CLOSE_PRICE'))* (pl.col('OPEN_PRICE')- pl.col('CLOSE_PRICE'))
# ).otherwise(pl.lit(0)).alias('profitLoss')
# )
# dfFiltered.write_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/dfYear23.parquet")
# #-------------------------------------------  Parquet Data Preperation done here ----------------------



# #------------------------------------- Processing Starts Here --------------------------------
# df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")
# print(df.collect().shape)
# print(df.collect().head())
#
# dfGp = df.group_by([pl.col('DATE1').dt.year().alias('year'),
#                     pl.col('DATE1').dt.month().alias('month')
#                     , pl.col('SYMBOL')
#                     , pl.col('SERIES')
#                     , pl.col('Portfolio')
#                     , pl.col('Strategy')
#                     ]).agg(pl.col('profitLoss').sum().alias('pl'))
# print(dfGp.collect().shape)
# print(dfGp.sort(by='pl').collect().head())
#
# dfGp2 = dfGp.group_by([pl.col('Strategy')]).agg(pl.col('pl').sum().alias('pl')).collect()
#
# v = dfGp2['pl'].to_list()
# l= dfGp2['Strategy'].to_list()
# fig1 = go.Figure(
#     data=[go.Pie(labels=l, values=v)]
# )
# fig1.show()
#
# dfGp2 = dfGp.group_by([pl.col('Portfolio')]).agg(pl.col('pl').sum().alias('pl')).collect()
#
# v = dfGp2['pl'].to_list()
# l= dfGp2['Portfolio'].to_list()
# fig2 = go.Figure(
#     data=[go.Pie(labels=l, values=v)]
# )
# fig2.show()
# # #------------------------------------- Processing Ends Here --------------------------------

#--------------- Dash App Starts here --------------------------------
BG_WHITE = "#ffffff"
TEXT_BLACK = "#000000"
GRID_GREY = "#e6e6e6"

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title> </title>   <!-- force empty title -->
        {%css%}
        <link rel="icon" href="data:;base64,iVBORw0KGgo="> <!-- blank favicon -->
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")
print(df.collect().head())

dfPortfolio = df.group_by([pl.col('Portfolio')]).agg(pl.col('profitLoss').sum().alias('pl')).collect()
lportfolio = dfPortfolio['Portfolio'].to_list()
vportfolio = dfPortfolio['pl'].to_list()

dfStrategy = df.group_by([pl.col('Strategy')]).agg(pl.col('profitLoss').sum().alias('pl')).collect()
lStrategy = dfStrategy['Strategy'].to_list()
vStrategy = dfStrategy['pl'].to_list()



dropdown =  dcc.Dropdown(
        id='portfolioId',
        options=[{"label": p, "value": p} for p in lstPortfolio],
        placeholder="Select Portfolio",
        style={'fontSize': '12px'},
        multi=True
    ),
dropdown1 =  dcc.Dropdown(
        id='portfolioId1',
        options=[{"label": p, "value": p} for p in lstPortfolio],
        placeholder="Select Portfolio",
        style={'fontSize': '12px'},
        multi=True
    ),

fig1= dcc.Graph(id='gpStrategy1',
                                style={"height": "150px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lStrategy, values=vStrategy
                                                            , showlegend=False
                                                            , hole=0.5, )]).update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
))


fig2= dcc.Graph(id='gpStrategy2',
                                style={"height": "150px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lStrategy, values=vStrategy
                                                            , showlegend=False
                                                            , hole=0.5,)]).update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
))

fig3= dcc.Graph(id='gpStrategy3',
                                style={"height": "150px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lStrategy, values=vStrategy
                                                            , showlegend=False
                                                            , hole=0.5,)]).update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
))

fig4= dcc.Graph(id='gpStrategy4',
                                style={"height": "150px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lStrategy, values=vStrategy
                                                            , showlegend=False
                                                            , hole=0.5,)]).update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
))


txtAboutPlatform = "Technical concepts"
app.layout = dbc.Container(
    fluid=True,
    style={"backgroundColor": BG_WHITE},
    className="p-2",
    children=[
            dbc.Row([
            dbc.Col([
                    dbc.Row(dropdown),
                    dbc.Row(dropdown1),
                    dbc.Row(html.P(txtAboutPlatform), style={'fontSize': '16px'}),
                    ],md=3,className="text-left border p-3"),
            dbc.Col([
                    dbc.Row(html.H4("Analytics Platform"),className="text-center"),
                    dbc.Row([ dbc.Col(fig1,md=3,className="px-1"), dbc.Col(fig2,md=3,className="px-1"),
                              dbc.Col(fig3,md=3,className="px-1"), dbc.Col(fig4,md=3,className="px-1")], className="g-1"),

                     ],md=9,className="text-center border p-3")
            ])
])
if __name__ == "__main__":
    app.run(debug=True)
#--------------- Dash App Ends  here --------------------------------