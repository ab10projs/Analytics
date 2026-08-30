import polars as pl
import pandas as pd
import numpy as np
import datetime
import dash
import plotly
import plotly.colors as pc

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

df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")
print(df.collect().head())

dfPortfolio = df.group_by([pl.col('Portfolio')]).agg(pl.col('profitLoss').sum().alias('pl')).collect()
lportfolio = dfPortfolio['Portfolio'].to_list()
vportfolio = dfPortfolio['pl'].to_list()

dfStrategy = df.group_by([pl.col('Strategy')]).agg(pl.col('profitLoss').sum().alias('pl')).collect()
lStrategy = dfStrategy['Strategy'].to_list()
vStrategy = dfStrategy['pl'].to_list()

dfSeries = (df.group_by("SERIES").agg(pl.col("profitLoss").sum().alias("pl")).sort("pl", descending=True).head(5).collect())
lSeries = dfSeries['SERIES'].to_list()
vSeries = dfSeries['pl'].to_list()


# dfPortStrSer = (df.group_by([pl.col('Portfolio'), pl.col('Strategy'), pl.col('SYMBOL'), pl.col('SERIES'), pl.col('DATE1')]).agg(pl.col('profitLoss').sum().alias('pl'))).collect()
# df = df.filter(pl.col('SERIES')=='EQ')
df = df.filter(  pl.col("profitLoss").is_between(-50000, 50000))
dfPortStrSer = (df.group_by([pl.col('Portfolio'), pl.col('Strategy'), pl.col('SYMBOL')]).agg(pl.col('profitLoss').sum().alias('pl'))).collect()

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


fig2= dcc.Graph(id='gpStrategy2',
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

figSeries1= dcc.Graph(id='gpSeries1',
                                style={"height": "120px", "width": "100%"},
                                config={"displayModeBar": False},
                                figure=go.Figure(data=[go.Pie(labels=lSeries, values=vSeries
                                                            , showlegend=False
                                                            , hole=0.5
                                                            , textinfo="percent"
                                                            # , hovertemplate="<b>%{label}</b>: %{value} (%{percent})<extra></extra>"
                                                            ,  textposition="inside")]).update_layout(

                                    margin=dict(l=0, r=0, t=0, b=0)
))


#---- 3d
# 1. Define the 3D Scatter Figure

# Create numeric positions for categorical axes
x_categories = dfPortStrSer["SYMBOL"].unique().to_list()
y_categories = dfPortStrSer["Portfolio"].unique().to_list()

x_map = {v: i for i, v in enumerate(x_categories)}
y_map = {v: i for i, v in enumerate(y_categories)}

x_num = [x_map[v] for v in dfPortStrSer["SYMBOL"].to_list()]
y_num = [y_map[v] for v in dfPortStrSer["Portfolio"].to_list()]

z = dfPortStrSer["pl"].to_list()

# --------------------------------------------------
# Create a unique numeric color value for X + Y
# --------------------------------------------------

xy_pairs = list(
    zip(
        dfPortStrSer["SYMBOL"].to_list(),
        dfPortStrSer["Portfolio"].to_list()
    )
)

xy_map = {
    pair: i
    for i, pair in enumerate(dict.fromkeys(xy_pairs))
}

color_values = [xy_map[pair] for pair in xy_pairs]

# --------------------------------------------------
# Marker size based on absolute P&L
# --------------------------------------------------

abs_z = np.abs(np.array(z))

# Scale sizes so they remain visually useful
if abs_z.max() > 0:
    marker_size = 5 + 20 * abs_z / abs_z.max()
else:
    marker_size = np.full(len(abs_z), 5)

xy_pairs = list(
    zip(
        dfPortStrSer["SYMBOL"].to_list(),
        dfPortStrSer["Portfolio"].to_list()
    )
)

unique_pairs = list(dict.fromkeys(xy_pairs))

# Plotly qualitative colors
palette = (
    pc.qualitative.Plotly
    + pc.qualitative.D3
    + pc.qualitative.G10
    + pc.qualitative.Safe
    + pc.qualitative.Dark24
)

color_map = {
    pair: palette[i % len(palette)]
    for i, pair in enumerate(unique_pairs)
}

point_colors = [
    color_map[pair]
    for pair in xy_pairs
]




fig_3d = go.Figure(
    data=[
        go.Scatter3d(


            x = dfPortStrSer['Portfolio'].to_list(),
            y = dfPortStrSer['SYMBOL'].to_list(),
            z = dfPortStrSer['pl'].to_list(),
            mode="markers",
            marker=dict(
                # size=marker_size,
                size = 1.5,
                color= point_colors,  # Sets color based on a variable
                colorscale="Viridis",  # Choose a color palette
                opacity=0.9,
                showscale=False,
            ),
        )
    ]
)

# 2. Update Layout for Titles and Component Sizing
fig_3d.update_layout(
    title=dict(
        text="Portfolio-Scrip-PL",
        y=.85,  # Move title higher up (closer to 1.0 is top edge)
        x=0.5,
        xanchor="center",
        yanchor="top",
    ),
    margin=dict(l=0, r=0, b=0, t=0),  # Tight margins to maximize graph area
    scene=dict(
        xaxis=dict(
            title="Symbol"
        ),
        yaxis=dict(
            title="Portfolio"
        ),
        zaxis=dict(
            title="Profit / Loss",
            range=[-50000, 50000],
            dtick=10000
        )
    )
,
)



# 3. Assign it to your dcc.Graph component


scatter3d_1 = dcc.Graph(
    id="scatter3d_1",
    figure=fig_3d,  # or your second figure
    style={
        "height": "400px",
        "width": "100%"
    },
    config={"displayModeBar": False}
)

scatter3d_2 = dcc.Graph(
    id="scatter3d_2",
    figure=fig_3d,  # or your second figure
    style={
        "height": "750px",
        "width": "100%"
    },
    config={"displayModeBar": False}
)


#---- 3d

mainTitle  = html.Div([ html.H3 ('Analytics Platform')],style={"text-align": "center", "width": "100%"})
# txtAboutPlatform0 = "Technical Challenges"  # txtAboutPlatform0

txtAboutPlatform0 =  dbc.Container([
    html.H4("Technical Challenges", id="tipPlatformForAnalytics"),
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
                "margin": "0",
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

app.layout = dbc.Container(
    fluid=True,
    className="p-2",
    style={"backgroundColor": BG_WHITE, "minHeight": "100vh"},
    children=[
        # TITLE ROW
        dbc.Row(
            dbc.Col(
                html.H3(
                    "Analytics Platform",
                    className="text-center mb-2",
                    style={"fontSize": "22px", "fontWeight": "600"},
                ),
                width=12,
            ),
            className="g-0",
        ),

        # MAIN 3-COLUMN ROW
        dbc.Row(
            [
                # COLUMN 1 — FILTERS (~15%)
                dbc.Col(
                    [
                        html.Div(
                            "FILTERS",
                            style={
                                "fontSize": "13px",
                                "fontWeight": "600",
                                "marginBottom": "8px",
                            },
                        ),
                        dcc.Dropdown(
                            id="portfolioId1",
                            options=[{"label": p, "value": p} for p in lstPortfolio],
                            placeholder="Select Portfolio",
                            style={"fontSize": "12px"},
                            multi=True,
                            className="mb-2",
                        ),
                        dcc.Dropdown(
                            id="strategyId1",
                            options=[{"label": p, "value": p} for p in lstStrategy],
                            placeholder="Select Strategy",
                            style={"fontSize": "12px"},
                            multi=True,
                            className="mb-2",
                        ),
                        dcc.Dropdown(
                            id="seriesId1",
                            options=[{"label": p, "value": p} for p in lSeries],
                            placeholder="Select Series",
                            style={"fontSize": "12px"},
                            multi=True,
                            className="mb-3",
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H5(
                                    "Technical Challenges",
                                    id="tipPlatformForAnalytics",
                                    style={
                                        "fontSize": "14px",
                                        "fontWeight": "600",
                                        "marginBottom": "0",
                                    },
                                ),
                                dbc.Tooltip(
                                    # ... your tooltip content unchanged ...
                                    target="tipPlatformForAnalytics",
                                    placement="right",
                                    style={
                                        "--bs-tooltip-bg": "#ffffff",
                                        "--bs-tooltip-color": "#000000",
                                        "textAlign": "left",
                                        "border": "none",
                                        "boxShadow": "0px 4px 10px rgba(0,0,0,0.1)",
                                    },
                                ),
                            ]
                        ),
                    ],
                    xs=12,
                    md=2,
                    style={
                        "border": "1px solid #ddd",
                        "borderRadius": "6px",
                        "padding": "8px",
                    },
                ),

                # COLUMN 2 — DONUTS + scatter3d_1 (~35%)
                dbc.Col(
                    [
                        # Row 1: 3 donut charts
                        dbc.Row(
                            [
                                dbc.Col(fig1, md=4, className="px-1"),
                                dbc.Col(fig2, md=4, className="px-1"),
                                dbc.Col(figSeries1, md=4, className="px-1"),
                            ],
                            className="g-1 mb-2",
                        ),
                        # Row 2: 3D chart
                        dbc.Row(
                            dbc.Col(scatter3d_1, width=12, className="px-1"),
                            className="g-0",
                        ),
                    ],
                    xs=12,
                    md=6,
                    style={
                        "border": "1px solid #ddd",
                        "borderRadius": "6px",
                        "padding": "5px",
                    },
                ),

                # COLUMN 3 — scatter3d_2 only (~50%)
                dbc.Col([
                    # dbc.Row([
                    #     dbc.Col(fig1, md=2, className="px-1"),
                    #     dbc.Col(fig2, md=2, className="px-1"),
                    #     dbc.Col(figSeries1, md=2, className="px-1"),
                    # ]),
                    # dbc.Row([
                    #     dbc.Col(fig1, md=2, className="px-1"),
                    #     dbc.Col(fig2, md=2, className="px-1"),
                    #     dbc.Col(figSeries1, md=2, className="px-1"),
                    # ]),
                ],
                    xs=12,
                    md=4,
                    style={
                        "border": "1px solid #ddd",
                        "borderRadius": "6px",
                        "padding": "5px",
                    }
                ),
            ],
            className="g-2",
            align="start",
        ),
    ],
)

##-------------------------------- Add the callback here -------------------------## Start

##-------------------------------- Add the callback here -------------------------## End



if __name__ == "__main__":
    app.run(debug=True)#--------------- Dash App Ends  here --------------------------------