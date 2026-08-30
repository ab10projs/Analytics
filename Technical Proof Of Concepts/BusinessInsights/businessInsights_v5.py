####################  import section #################  start
import polars as pl
import pandas as pd
import numpy as np
import datetime
import dash
import plotly
import plotly.colors as pc
from click import style

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

####################  import section #################  end
# #-------------------------------------------  Parquet Data Preperation starts ----------------------
# exposure = 10000
# df = pl.read_csv("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/dfMerged.csv")
#
# df = df.with_columns(pl.col("DATE1").str.to_date(format="%Y-%m-%d"),
#                       pl.col("DELIV_QTY").cast(pl.Float64, strict= False),
#                       pl.col("DELIV_PER").cast(pl.Float64, strict= False)
#                     )
#


## Here change .dt.offset_by("1y") to -1y,1y,2y etc. AND dfYear23.parquet in write_parquet to save
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

####################  section to import parquet and grouped ##################### start
df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")

qPortfolio = (df.group_by([pl.col('Portfolio')]).agg(pl.col('profitLoss').sum().alias('pl')))
qStrategy = (df.group_by([pl.col('Strategy')]).agg(pl.col('profitLoss').sum().alias('pl')))
qSeries = (df.group_by("SERIES").agg(pl.col("profitLoss").sum().alias("pl")).sort("pl", descending=True).head(5))
qPortStrSer = (df.group_by([pl.col('Portfolio'), pl.col('Strategy'), pl.col('SYMBOL')]
                            ).agg(pl.col('profitLoss').sum().alias('pl')))

dfPortfolio, dfStrategy, dfSeries, dfPortStrSer = pl.collect_all([qPortfolio,qStrategy,qSeries,qPortStrSer])
dfPortStrSer = dfPortStrSer.filter( pl.col("pl").is_between(-50000, 50000))

lportfolio = dfPortfolio['Portfolio'].to_list()
vportfolio = dfPortfolio['pl'].to_list()
lStrategy = dfStrategy['Strategy'].to_list()
vStrategy = dfStrategy['pl'].to_list()
lSeries = dfSeries['SERIES'].to_list()
vSeries = dfSeries['pl'].to_list()

# print(dfPortfolio.head())
####################  section to import parquet and grouped ##################### start

####################### dropdowns ############################### Start
dropdownPortfolio =  dcc.Dropdown(
        id='portfolioId1',
        options=[{"label": p, "value": p} for p in lstPortfolio],
        placeholder="Select Portfolio",
        style={'fontSize': '12px'},
        multi=True
    ),
dropdownStrategy =  dcc.Dropdown(
        id='strategyId1',
        options=[{"label": p, "value": p} for p in lstStrategy],
        placeholder="Select Strategy",
        style={'fontSize': '12px'},
        multi=True
    ),
dropdownSeries =  dcc.Dropdown(
        id='seriesId1',
        options=[{"label": p, "value": p} for p in lSeries],
        placeholder="Select Series",
        style={'fontSize': '12px'},
        multi=True
    ),
####################### dropdowns ############################### end

###################### pie charts ######################## start




############## fig 1 ############# start
fig1= dcc.Graph(id='gpPortfolio1',
                                style={"height": "120px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lportfolio, values=vportfolio
                                                            , showlegend=False
                                                            , hole=0.5
                                                            , textinfo = "percent"
                                                            # , hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>"
                                                            , textposition = "inside"

)]).update_layout(
    margin=dict(l=0, r=0, t=0, b=0)
))
############## fig 1 ############# end

############## fig 2 ############# start
fig2= dcc.Graph(id='gpStrategy1',
                                style={"height": "120px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lStrategy, values=vStrategy
                                                            , showlegend=False
                                                            , hole=0.5
                                                            , textinfo = "percent"
                                                            # , hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>"
                                                            ,textposition = "inside")]
                                                 ).update_layout(
                                    margin=dict(l=0, r=0, t=0, b=0)
))
############## fig 2 ############# end

############## fig 3 ############# start
fig3= dcc.Graph(id='gpSeries1',
                                style={"height": "120px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lSeries, values=vSeries
                                                            , showlegend=False
                                                            , hole=0.5
                                                            , textinfo="percent"
                                                            ,  textposition="inside")]).update_layout(

                                    margin=dict(l=0, r=0, t=0, b=0)
))
############## fig 3 ############# end


###################### pie charts ######################## end



#################### layout ###################################### start

### main title ### start
mainTitle  = html.Div([ html.H3 ('Analytics Platform')],style={"text-align": "center", "width": "100%"})
### main title ### end

### mouse hover tip ### start
txtAboutPlatform0 =  dbc.Container([
    html.H6("Technical Challenges", id="tipPlatformForAnalytics"),
    dbc.Tooltip(
        html.Div(
    [
        html.B("Common Issues", style={"fontSize": "16px"}),
        html.Hr(style={"margin": "4px 0"}),
        html.Ul(
            [
                html.Li("Slow response"),
                html.Li("Drill-down and drill-through are slow"),
                html.Li("Filters freeze"),
                html.Li("Reports time out"),
                html.Li("Business calculations become difficult"),
                html.Li("Performance degrades quickly"),
                html.Li("Lacks flexibility"),
                html.Li("Limited custom algorithms"),
                html.Li("Cost escalation"),
                html.Li("Limited intractivity"),
            ],
            style={
                "paddingLeft": "18px",
                "margin": "5",
                "fontSize": "14px",
                "lineHeight": "1.3",
            },
        ),
            ],
            style={"text-align": "left", "width": "100%"}
        ),
        "Black text on a white background with no borders!",
        target="tipPlatformForAnalytics",
        placement="bottom",
        # This style block overrides Bootstrap 5 CSS variables directly
        style={
            "--bs-tooltip-bg": "#ffffff",  # Sets background to white
            "--bs-tooltip-color": "#000000",  # Sets text to black
            "text-align": "left",
            "border": "none",  # Removes any outer border
            "box-shadow": "0px 4px 10px rgba(0,0,0,0.1)",  # Optional soft shadow for visibility
        },
    ),

])
### mouse hover tip ### end


app.layout = (dbc.Container
([
 mainTitle,
    dbc.Row([
      dbc.Col([
          dbc.Row(dropdownPortfolio),
          dbc.Row(dropdownStrategy),
          dbc.Row(dropdownSeries),
          dbc.Row(txtAboutPlatform0),
      ], width=2),
        dbc.Col([
            dbc.Row([
                dbc.Col([fig1], md=2),
                dbc.Col([fig2], md=2),
                dbc.Col([fig3], md=2),

            ]),
        ], width=10) # don't change 10

    ])

])
)
#################### layout ###################################### end

################### callback section ################## start


################### callback section ################## end


if __name__ == "__main__":
    app.run(debug=True)#--------------- Dash App Ends  here --------------------------------

