####################  import section #################  start
import polars as pl
import pandas as pd
import numpy as np
import datetime
import dash
import plotly
import plotly.colors as pc
from click import style

from businessInsights_v5 import qStrategy, qSeries

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
from dash import dcc, html, Input, Output, callback, ctx

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

############## lazy frame ##################### start
df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")
############## lazy frame ##################### end

############# on start the dropdown should have all values ######### start
qPortfolioValues = df.select(pl.col('Portfolio').unique().sort())
qStrategyValues = df.select(pl.col('Strategy').unique().sort())
qSeriesValues = df.select(pl.col('SERIES').unique().sort())
dPortfolioValues, dStrategyValues, dSeriesValues = pl.collect_all(
    [
        qPortfolioValues,
        qStrategyValues,
        qSeriesValues
    ]
)
portfolio_values = ["All"] + dPortfolioValues["Portfolio"].to_list()
strategy_values = ["All"] + dStrategyValues["Strategy"].to_list()
series_values = ["All"] + dSeriesValues["SERIES"].to_list()
############# on start the dropdown should have all values ######### end

########### helper fn for dropdown ############ start
def make_options(values):
    return  [
        {
        "label" : str(value),
        "value" : value
        }
        for value in values
    ]
########### helper fn for dropdown ############ end

########## filter function ########### start
def apply_filters(
    q,
    portfolio,
    strategy,
    series
):

    if portfolio != "All":
        q = q.filter(
            pl.col("Portfolio") == portfolio
        )

    if strategy != "All":
        q = q.filter(
            pl.col("Strategy") == strategy
        )

    if series != "All":
        q = q.filter(
            pl.col("SERIES") == series
        )

    return q
########## filter function ########### end


# ######### 3d scatter ########### start
# def create_3d_scatter(d):
#
#     # Convert categorical values to numeric positions
#     portfolios = d["Portfolio"].unique().to_list()
#     strategies = d["Strategy"].unique().to_list()
#     series = d["SERIES"].unique().to_list()
#
#     portfolio_map = {
#         value: i
#         for i, value in enumerate(portfolios)
#     }
#
#     strategy_map = {
#         value: i
#         for i, value in enumerate(strategies)
#     }
#
#     series_map = {
#         value: i
#         for i, value in enumerate(series)
#     }
#
#     x = [
#         portfolio_map[v]
#         for v in d["Portfolio"].to_list()
#     ]
#
#     y = [
#         strategy_map[v]
#         for v in d["Strategy"].to_list()
#     ]
#
#     z = d["pl"].to_list()
#
#     series_num = [
#         series_map[v]
#         for v in d["SERIES"].to_list()
#     ]
#
#     sizes = [
#         max(5, min(30, abs(v) / 1000))
#         for v in z
#     ]
#
#     fig = go.Figure(
#         data=[
#             go.Scatter3d(
#                 x=x,
#                 y=y,
#                 z=z,
#
#                 mode="markers",
#
#                 marker=dict(
#                     size=sizes,
#                     color=series_num,
#                     colorscale="Turbo",
#                     showscale=True,
#                     colorbar=dict(
#                         title="Series"
#                     ),
#
#                     opacity=0.8
#                 ),
#
#                 customdata=[
#                     [
#                         p,
#                         s,
#                         se,
#                         pl
#                     ]
#                     for p, s, se, pl in zip(
#                         d["Portfolio"].to_list(),
#                         d["Strategy"].to_list(),
#                         d["SERIES"].to_list(),
#                         z
#                     )
#                 ],
#
#                 hovertemplate=(
#                     "Portfolio: %{customdata[0]}<br>"
#                     "Strategy: %{customdata[1]}<br>"
#                     "Series: %{customdata[2]}<br>"
#                     "P/L: %{customdata[3]:,.0f}"
#                     "<extra></extra>"
#                 )
#             )
#         ]
#     )
#
#     fig.update_layout(
#         margin=dict(
#             l=0,
#             r=0,
#             t=30,
#             b=0
#         ),
#
#         scene=dict(
#             xaxis=dict(
#                 title="Portfolio",
#                 tickmode="array",
#                 tickvals=list(range(len(portfolios))),
#                 ticktext=portfolios
#             ),
#
#             yaxis=dict(
#                 title="Strategy",
#                 tickmode="array",
#                 tickvals=list(range(len(strategies))),
#                 ticktext=strategies
#             ),
#
#             zaxis=dict(
#                 title="Profit / Loss"
#             )
#         )
#     )
#
#     return fig
# ######### 3d scatter ########### end

#### 3d #### start


#---- 3d
def create_3d_scatter(d):

    # 1. Define the 3D Scatter Figure

    # Create numeric positions for categorical axes
    x_categories = d["SYMBOL"].unique().to_list()
    y_categories = d["Portfolio"].unique().to_list()

    x_map = {v: i for i, v in enumerate(x_categories)}
    y_map = {v: i for i, v in enumerate(y_categories)}

    x_num = [x_map[v] for v in d["SYMBOL"].to_list()]
    y_num = [y_map[v] for v in d["Portfolio"].to_list()]

    z = d["pl"].to_list()

    # --------------------------------------------------
    # Create a unique numeric color value for X + Y
    # --------------------------------------------------

    xy_pairs = list(
        zip(
            d["SYMBOL"].to_list(),
            d["Portfolio"].to_list()
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
            d["SYMBOL"].to_list(),
            d["Portfolio"].to_list()
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

                x = d['Portfolio'].to_list(),
                y = d['SYMBOL'].to_list(),
                z = d['pl'].to_list(),
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
                title="SYMBOL"
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
    return fig_3d
#### 3d #### end


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

app.layout = dbc.Container(
    [

        dbc.Row(
            [

                dbc.Col(
                    [
                        html.Label("Portfolio"),

                        dcc.Dropdown(
                            id="ddPortfolio",
                            options=make_options(portfolio_values),
                            value="All",
                            clearable=False
                        )
                    ],
                    md=4
                ),

                dbc.Col(
                    [
                        html.Label("Strategy"),

                        dcc.Dropdown(
                            id="ddStrategy",
                            options=make_options(strategy_values),
                            value="All",
                            clearable=False
                        )
                    ],
                    md=4
                ),

                dbc.Col(
                    [
                        html.Label("Series"),

                        dcc.Dropdown(
                            id="ddSeries",
                            options=make_options(series_values),
                            value="All",
                            clearable=False
                        )
                    ],
                    md=4
                )

            ],
            className="g-2"
        ),

        html.Br(),

        dbc.Row(
            [

                dbc.Col(
                    dcc.Graph(
                        id="gpPortfolio1",
                        style={
                            "height": "120px",
                            "width": "100%"
                        },
                        config={
                            "displayModeBar": False
                        }
                    ),
                    md=4
                ),

                dbc.Col(
                    dcc.Graph(
                        id="gpStrategy1",
                        style={
                            "height": "120px",
                            "width": "100%"
                        },
                        config={
                            "displayModeBar": False
                        }
                    ),
                    md=4
                ),

                dbc.Col(
                    dcc.Graph(
                        id="gpSeries1",
                        style={
                            "height": "120px",
                            "width": "100%"
                        },
                        config={
                            "displayModeBar": False
                        }
                    ),
                    md=4
                ),
            ],
            className="g-1"
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="gpPortStratSer",
                        style={
                            "height": "500px",
                            "width": "100%"
                        },
                        config={
                            "displayModeBar": False
                        }
                    ),
                    md=12
                )
            ],
            className="g-1"
        )

    ],
    fluid=True
)

#################### layout ###################################### end

################### callback section ################## start
############# dropdown update ########### start
@callback(
    Output("ddPortfolio", "options"),
    Output("ddStrategy", "options"),
    Output("ddSeries", "options"),

    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value")
)
def update_dropdowns(
    portfolio,
    strategy,
    series
):

    # -----------------------------------------------------
    # Portfolio options
    #
    # Apply Strategy + Series filters
    # DO NOT apply Portfolio filter
    # -----------------------------------------------------

    qPortfolio = df

    if strategy != "All":
        qPortfolio = qPortfolio.filter(
            pl.col("Strategy") == strategy
        )

    if series != "All":
        qPortfolio = qPortfolio.filter(
            pl.col("SERIES") == series
        )

    qPortfolio = (
        qPortfolio
        .select(
            pl.col("Portfolio").unique().sort()
        )
    )


    # -----------------------------------------------------
    # Strategy options
    #
    # Apply Portfolio + Series filters
    # DO NOT apply Strategy filter
    # -----------------------------------------------------

    qStrategy = df

    if portfolio != "All":
        qStrategy = qStrategy.filter(
            pl.col("Portfolio") == portfolio
        )

    if series != "All":
        qStrategy = qStrategy.filter(
            pl.col("SERIES") == series
        )

    qStrategy = (
        qStrategy
        .select(
            pl.col("Strategy").unique().sort()
        )
    )


    # -----------------------------------------------------
    # Series options
    #
    # Apply Portfolio + Strategy filters
    # DO NOT apply Series filter
    # -----------------------------------------------------

    qSeries = df

    if portfolio != "All":
        qSeries = qSeries.filter(
            pl.col("Portfolio") == portfolio
        )

    if strategy != "All":
        qSeries = qSeries.filter(
            pl.col("Strategy") == strategy
        )

    qSeries = (
        qSeries
        .select(
            pl.col("SERIES").unique().sort()
        )
    )


    # -----------------------------------------------------
    # Execute all 3 queries together
    # -----------------------------------------------------

    dPortfolio, dStrategy, dSeries = pl.collect_all(
        [
            qPortfolio,
            qStrategy,
            qSeries
        ]
    )


    # -----------------------------------------------------
    # Convert to lists
    # -----------------------------------------------------

    portfolio_options = (
        ["All"] +
        dPortfolio["Portfolio"].to_list()
    )

    strategy_options = (
        ["All"] +
        dStrategy["Strategy"].to_list()
    )

    series_options = (
        ["All"] +
        dSeries["SERIES"].to_list()
    )


    # -----------------------------------------------------
    # IMPORTANT:
    #
    # Make sure currently selected value remains in its
    # own dropdown options.
    #
    # This prevents Dash from resetting it.
    # -----------------------------------------------------

    if portfolio != "All" and portfolio not in portfolio_options:
        portfolio_options.append(portfolio)

    if strategy != "All" and strategy not in strategy_options:
        strategy_options.append(strategy)

    if series != "All" and series not in series_options:
        series_options.append(series)


    return (
        make_options(portfolio_options),
        make_options(strategy_options),
        make_options(series_options)
    )
############# dropdown update ########### end

######### pie function ########### start
def create_pie(d, category):

    fig = go.Figure(
        data=[
            go.Pie(
                labels=d[category].to_list(),
                values=d["pl"].to_list(),

                showlegend=False,

                hole=0.5,

                textinfo="percent",
                textposition="inside"
            )
        ]
    )

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig
######### pie function ########### end

######## pie callback start
@callback(
    Output("gpPortfolio1", "figure"),
    Output("gpStrategy1", "figure"),
    Output("gpSeries1", "figure"),
    Output("gpPortStratSer", "figure"),

    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value")
)
def update_pies(
    portfolio,
    strategy,
    series
):

    # -----------------------------------------------------
    # Apply ALL current filters
    # -----------------------------------------------------

    qFiltered = apply_filters(
        df,
        portfolio,
        strategy,
        series
    )


    # -----------------------------------------------------
    # Create 4 LAZY aggregations
    #
    # Nothing has been collected yet.
    # -----------------------------------------------------

    qPortfolio = (
        qFiltered
        .group_by("Portfolio")
        .agg(
            pl.col("profitLoss")
              .sum()
              .alias("pl")
        )
        .sort("pl", descending=True)
    )


    qStrategy = (
        qFiltered
        .group_by("Strategy")
        .agg(
            pl.col("profitLoss")
              .sum()
              .alias("pl")
        )
        .sort("pl", descending=True)
    )


    qSeries = (
        qFiltered
        .group_by("SERIES")
        .agg(
            pl.col("profitLoss")
              .sum()
              .alias("pl")
        )
        .sort("pl", descending=True)
    )

    qPortStratSer = (
        qFiltered
        .group_by(["Portfolio", "Strategy", "SYMBOL"])
        .agg(
            pl.col("profitLoss")
            .sum()
            .alias("pl")
        )
        .sort("pl", descending=True)
    )

    # -----------------------------------------------------
    # Execute the three queries together
    # -----------------------------------------------------

    dPortfolio, dStrategy, dSeries, dPortStratSer= pl.collect_all(
        [
            qPortfolio,
            qStrategy,
            qSeries,
            qPortStratSer
        ]
    )


    # -----------------------------------------------------
    # Create Plotly figures
    # -----------------------------------------------------

    figPortfolio = create_pie(
        dPortfolio,
        "Portfolio"
    )

    figStrategy = create_pie(
        dStrategy,
        "Strategy"
    )

    figSeries = create_pie(
        dSeries,
        "SERIES"
    )

    fig3D = create_3d_scatter(
        dPortStratSer
    )




    return (
        figPortfolio,
        figStrategy,
        figSeries,
        fig3D
    )
######## pie callback end

################### callback section ################## end


if __name__ == "__main__":
    app.run(debug=True)#--------------- Dash App Ends  here --------------------------------

