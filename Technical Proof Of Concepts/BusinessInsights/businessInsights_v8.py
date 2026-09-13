import datetime

import polars as pl
import pandas as pd

import dash
from click import style
import time

pd.set_option('display.max_columns', None)
pl.Config.set_fmt_float("full")
from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, ctx
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

###################################### Process ####################################### start

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.server.df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")

# --------------------  function to update figures ------------------------- start
def figUpdate(df):
    # dfPortfolioPl = app.server.df.select(pl.col(['Portfolio', 'profitLoss'])).group_by(
    dfPortfolioPl = df.select(pl.col(['Portfolio', 'profitLoss'])).group_by(
        pl.col('Portfolio')).agg(
        pl.col('profitLoss').sum()
    ).sort(by='profitLoss', descending= True)

    # dfStrategyPl = app.server.df.select(pl.col(['Strategy', 'profitLoss'])).group_by(
    dfStrategyPl = df.select(pl.col(['Strategy', 'profitLoss'])).group_by(
        pl.col('Strategy')).agg(
        pl.col('profitLoss').sum()
    ).sort(by='profitLoss', descending= True)

    # dfPortStraSer = app.server.df.select(pl.col(['Portfolio', 'Strategy', 'SERIES', 'profitLoss'])).group_by(
    dfPortStraSer = df.select(pl.col(['Portfolio','Strategy', 'SERIES', 'profitLoss'])).group_by(
        pl.col(['Portfolio', 'Strategy', 'SERIES'])).agg(
        pl.col('profitLoss').sum()
    ).sort(by='profitLoss', descending= True)


    dfPortfolioPl , dfStrategyPl , dfPortStraSer= pl.collect_all(
        [dfPortfolioPl, dfStrategyPl, dfPortStraSer]
    )

    ##############  pie charts ###################### start

    portfolioSeries = dfPortfolioPl.select(pl.col('Portfolio')).to_series()
    strategySeries = dfStrategyPl.select(pl.col('Strategy')).to_series()


    # #------------------------- Portfolio Pie Fig ------------------------# Start
    piePortfolio = go.Figure()
    # #------------------------- Portfolio Pie Fig ------------------------# End

    # #------------------------- Strategy Pie Fig ------------------------# Start
    pieStrategy = go.Figure()
    # #------------------------- Strategy Pie Fig ------------------------# End
    ##############  pie charts ###################### end


    # #############  3 d Scatter ############# Start
    dfPortStraSer = dfPortStraSer.filter([(pl.col('profitLoss')<15000)
                                          & (pl.col('profitLoss')>-15000)])
    portfolios = dfPortStraSer["Portfolio"].unique().to_list()
    portfolio_map = {
        portfolio: i
        for i, portfolio in enumerate(portfolios)
    }
    color_values = [
        portfolio_map[p]
        for p in dfPortStraSer["Portfolio"].to_list()
    ]
    pl_values = dfPortStraSer["profitLoss"].to_list()
    pl_abs = dfPortStraSer["profitLoss"].abs().to_list()
    fig_3d = go.Figure()
    fig_3d.add_trace(
        go.Scatter3d(
            x=dfPortStraSer["Portfolio"].to_list(),
            y=dfPortStraSer["SERIES"].to_list(),
            z=pl_values,
            mode="markers",
            marker=dict(
                size=pl_abs,
                sizemode="area",
                sizeref=2 * max(pl_abs) / (20 ** 2),
                sizemin=4,
                color=color_values,
                colorscale="Viridis",
                cmin=0,
                cmax=len(portfolios) - 1,
                showscale=False,
                colorbar=dict(
                    title="Portfolio",
                    tickmode="array",
                    tickvals=list(range(len(portfolios))),
                    ticktext=portfolios
                ),
                opacity=1
            ),
            hovertemplate=(
                "Portfolio: %{x}<br>"
                "Strategy: %{y}<br>"
                "P/L: %{z:,.2f}"
                "<extra></extra>"
            )
        )
    )

    fig_3d.update_layout(
        title=dict(
            text="Portfolio Strategy Series",
            x=0.5,
            xanchor="center"
        ),
        scene=dict(
            xaxis=dict(title="Portfolio"),
            yaxis=dict(title="Series"),
            zaxis=dict(title="Profit/Loss")
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    # #############  3 d Scatter ############# End
    return piePortfolio, pieStrategy, fig_3d, portfolioSeries, strategySeries, dfPortStraSer

# --------------------  function to update figures ------------------------- end
df = app.server.df
piePortfolio,pieStrategy, fig_3d, portfolioSeries, strategySeries, dfPortStraSer = figUpdate(df)

print("dfPortStraSer.head(3)")
print(dfPortStraSer.head(3))

### mouse hover tip ### start
txtTechnicalChallenges =  dbc.Container([
    html.H5("Technical Challenges", id="tipTechnicalChallenges" , style={"fontSize": "14px"}),
    dbc.Tooltip(
        html.Div(
    [
        html.B("Common Issues", style={"fontSize": "14px"}),
        html.Hr(style={"margin": "4px 0"}),
        html.Ul(
            [
                html.Div("1. Slow response"),
                html.Div("2. Drill-down and drill-through are slow"),
                html.Div("3. Filters freeze"),
                html.Div("4. Reports time out"),
                html.Div("5. Business calculations become difficult"),
                html.Div("6.Performance degrades quickly"),
                html.Div("7. Lacks flexibility"),
                html.Div("8. Limited custom algorithms"),
                html.Div("9. Cost escalation"),
                html.Div("10. Limited interactivity"),
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
        target="tipTechnicalChallenges",
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


### mouse hover tip  Solution Architecture  ### start
txtSolutionArchitecture =  dbc.Container([
    html.H5(" Solution Architecture", id="tipSolutionArchitecture" , style={"fontSize": "14px"}),
    dbc.Tooltip(
        html.Div(
    [
        html.B("Design Considerations", style={"fontSize": "14px"}),
        html.Hr(style={"margin": "4px 0"}),
        html.Ul(
            [
                html.Div("1. Intelligent Cache"),
                html.Div("2. Reduced I/O"),
                html.Div("3. Control Latency"),
                html.Div("4. Concurrent Users"),
                html.Div("5. Vectorized processing"),
                html.Div("6. Scalable to Petabytes"),
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
        target="tipSolutionArchitecture",
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



app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title> </title>   <!-- force empty title -->
        {%css%}
        <link rel="icon" href="data:;base64,iVBORw0KGgo="> <!-- blank favicon -->
        
        <style>
        /* =================================================
           GLOBAL
           ================================================= */
        * {

            box-sizing: border-box;
        }
        
        html,
        body {

            margin: 0;

            padding: 0;

            width: 100%;

            height: 100%;

            overflow: hidden;

            font-family: Arial, sans-serif;
        }
        
                /* =================================================
           PAGE
           ================================================= */

        .page {

            width: 100vw;

            height: 100vh;

            overflow: hidden;

            display: flex;

            flex-direction: column;
        }
        
                /* =================================================
           MAIN DASHBOARD

           Columns:

               20% | 40% | 40%

           Rows:

               55% | 45%

           Total height:

               100% of remaining viewport
           ================================================= */

        .dashboard {

            display: grid;

            grid-template-columns:

                20%
                40%
                40%;

            grid-template-rows:

                55%
                45%;

            width: 100vw;

            height: calc(100vh - 50px);

            overflow: hidden;

            min-width: 0;

            min-height: 0;
        }
        
                /* =================================================
           LEFT COLUMN
           ================================================= */

        .left-column {

            grid-column: 1;

            grid-row: 1 / 3;

            display: flex;

            flex-direction: column;

            gap: 5px;

            padding: 5px;

            border-right: 1px solid #cccccc;

            overflow: hidden;

            min-width: 0;

            min-height: 0;
        }


        /* =================================================
           DROPDOWNS
           ================================================= */

        .dropdown {
            width: 100%;
            flex-shrink: 0;
        }
        
        /* =================================================
           TEXT BOXES
           ================================================= */

        .text-box {

            height: 32px;

            min-height: 32px;

            width: 100%;

            padding: 7px 10px;

            border: 1px solid #cccccc;

            border-radius: 4px;

            background: #f7f7f7;

            font-weight: bold;

            flex-shrink: 0;
        }
        
        /* =================================================
           SMALL BAR CHART ROWS
           ================================================= */

        .small-chart-row {

            display: grid;

            grid-template-columns: 1fr 1fr;

            width: 100%;
            
            height: 25%;

            flex: 1 1 0;

            min-height: 0;

            overflow: hidden;
        }


        .small-chart {
            width: 65% !important;
            height: 65% !important;
        
            min-width: 0;
            min-height: 0;
        
            overflow: hidden;
        }
        
        /* Plotly container */

        .small-chart .js-plotly-plot,
        .small-chart .plot-container {
            width: 100% !important;
            height: 100% !important;
        }
        
        
        /* =================================================
        MIDDLE COLUMN
        ================================================= */

        .middle-column {

            grid-column: 2;

            grid-row: 1;

            padding: 3px;

            border-right: 1px solid #cccccc;

            overflow: hidden;

            min-width: 0;

            min-height: 0;
        }
        
          /* =================================================
           TOP CHART ROW
           ================================================= */

        .top-chart-row {

            display: grid;

            grid-template-columns: repeat(3, 25%);

            width: 100%;
            
            gap: 10%;

            height: 70%;

            min-width: 0;

            min-height: 0;

            overflow: hidden;
        }


        .top-chart {

            width: 100% !important;

            height: 100% !important;

            min-width: 0;

            min-height: 0;
        }


        /* =================================================
           RIGHT COLUMN
           ================================================= */

        .right-column {

            grid-column: 3;

            grid-row: 1;

            padding: 3px;

            overflow: hidden;

            min-width: 0;

            min-height: 0;
        }


        /* =================================================
           3D SCATTER
           ================================================= */

        .scatter3d {

            width: 100% !important;

            height: 100% !important;

            min-width: 0;

            min-height: 0;
        }


        /* =================================================
           BOTTOM SCATTER

           Spans:

               Middle 40%
                   +
               Right 40%

               = 80%
           ================================================= */

        .bottom-scatter {

            grid-column: 2 / 4;

            grid-row: 2;

            padding: 0;

            border-top: 1px solid #cccccc;

            overflow: hidden;

            min-width: 0;

            min-height: 0;
        }


        .scatter5 {

            width: 100% !important;

            height: 100% !important;

            min-width: 0;

            min-height: 0;
            
            margin: 0 !important;
        }


        /* =================================================
           PLOTLY CONTAINER
           ================================================= */

        .js-plotly-plot,
        .plot-container {

            width: 100% !important;

            height: 100% !important;
        }


        .dash-graph {

            width: 100%;

            height: 100%;
        }


        /* =================================================
           PREVENT CHILDREN FROM CAUSING OVERFLOW
           ================================================= */

        .left-column > *,
        .middle-column > *,
        .right-column > *,
        .bottom-scatter > * {

            max-width: 100%;

            min-width: 0;
        }


        /* =================================================
           MOBILE / SMALL SCREEN

           On a small screen, one-page desktop layout
           cannot realistically display all charts.

           Therefore switch to a normal vertical layout.
           ================================================= */

        @media (max-width: 900px) {

            html,
            body {

                overflow: auto;
            }


            .page {

                height: auto;

                overflow: visible;
            }


            .dashboard {

                display: block;

                width: 100%;

                height: auto;

                overflow: visible;
            }


            .left-column,
            .middle-column,
            .right-column,
            .bottom-scatter {

                width: 100%;

                height: 450px;

                border-right: none;
            }


            .dashboard-title {

                position: sticky;

                top: 0;

                z-index: 100;
            }

        }
        
        </style>
        
    
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


app.layout = html.Div(
    className = "page",
    children =[
        # =================================================
        # DASHBOARD TITLE
        # =================================================
        html.Div(

            "MARKET ANALYTICS DASHBOARD",
            className="text-center mb-2",
            style={"fontSize": "24px",
                   "fontWeight": "bold"}
        ),

        # =================================================
        # MAIN DASHBOARD
        # =================================================
        html.Div(
            className="dashboard",
            children=[

                        # =========================================
                        # LEFT COLUMN - 20%
                        # =========================================
                        html.Div(
                            className="left-column",
                            children=[

                            # ---------------------------------
                            # Dropdown 1
                            # ---------------------------------
                            dcc.Dropdown(
                                id="ddPortfolio",
                                options=[
                                    {"label": p, "value": p}
                                    for p in portfolioSeries
                                ],
                                placeholder="Select Portfolio Name",
                                multi=True,
                            ),
                            # ---------------------------------
                            # Dropdown 2
                            # ---------------------------------
                            dcc.Dropdown(
                                id="ddStrategy",
                                options=[
                                    {"label": p, "value": p}
                                    for p in strategySeries
                                ],
                                placeholder="Select Strategy Name",
                                multi=True,
                            ),

                            # ---------------------------------
                            # Dropdown 3
                            # ---------------------------------
                            dcc.Dropdown(
                                id="ddSeries",
                                options=[
                                    {"label": p, "value": p}
                                    for p in
                                    dfPortStraSer
                                    .select(pl.col("SERIES"))
                                    .unique()
                                    .to_series()
                                    .sort()
                                ],
                                placeholder="Select Series Name",
                                multi=True,
                            ),

                            # ---------------------------------
                            # Mouseover Text Business Challenges
                            # ---------------------------------
                            html.H3(
                                txtTechnicalChallenges,
                                className="text-box",
                                style={
                                    "backgroundColor": "white"
                                }
                            ),


                            # ---------------------------------
                            # Mouseover Text txtSolutionArchitecture
                            # ---------------------------------
                            html.H3(
                                txtSolutionArchitecture,
                                className="text-box",
                                style={
                                    "backgroundColor": "white"
                                }
                            ),

                            html.H6(
                                "Metrics 12 Core, 16GB RAM i5",
                                style={
                                    "backgroundColor": "white",
                                    "textAlign": "center",
                                    "fontWeight": "bold"
                                }
                            ),

                            # =================================
                            # BAR 6 + BAR 7
                            # =================================
                            html.Div(


                                children=[
                                        html.H6(
                                            children=[
                                                "Time(sec): ",
                                                html.Span(
                                                    id="processingTimeid",
                                                    children="processingTime"
                                                )
                                            ],
                                            style={"fontSize": "14px"}
                                        ),

                                        html.H6(f"Max Profit Portfolio:",
                                                style={"fontSize": "14px"}),
                                        html.H6(f"Records Filtered:",
                                                style={"fontSize": "14px"}),
                                        html.H6(f"Max Series:",
                                            style={"fontSize": "14px"}),
                                        html.H6(f"Min Series:",
                                            style={"fontSize": "14px"}),
                                        html.H6(f"Max Series Portfolio:",
                                                style={"fontSize": "14px"}),
                                        html.H6(f"Min Series Portfolio:",
                                                style={"fontSize": "14px"}),
                                        html.H6(f"Max Series Profit:",
                                                style={"fontSize": "14px"}),
                                        html.H6(f"Min Series Loss:",
                                                style={"fontSize": "14px"}),
                                ]
                            ),

                            # =================================
                            # BAR 8 + BAR 9
                            # =================================
                            html.Div(
                                className="small-chart-row",
                                children=[

                                    ]
                                )
                            ]
                        ),

                        # =========================================
                        # MIDDLE COLUMN - 40%
                        # =========================================
                        html.Div(
                            className="middle-column",
                            children=[

                                html.H5(
                                    "Portfolio and Strategy Details",
                                    style={
                                        "backgroundColor": "white",
                                        "textAlign": "center",
                                        "fontWeight": "bold",
                                        "fontStyle": "italic"
                                    }
                                ),

                                html.Div(
                                    className="top-chart-row",
                                    children=[
                                        # -------------------------
                                        # Pie Chart 1
                                        # -------------------------

                                        dcc.Graph(

                                            id="piePortfolio1",

                                            figure=piePortfolio,

                                            className="top-chart",

                                            config={
                                                "displayModeBar": False
                                            }
                                        ),
                                        # -------------------------
                                        # Pie Chart 2
                                        # -------------------------

                                        dcc.Graph(

                                            id="pieStrategy1",

                                            figure=pieStrategy,

                                            className="top-chart",

                                            config={
                                                "displayModeBar": False
                                            }
                                        ),

                                        # -------------------------
                                        # Bar Chart 3
                                        # -------------------------
                                        dcc.Graph(

                                            id="barStrategy1",

                                            figure=pieStrategy,

                                            className="top-chart",

                                            config={
                                                "displayModeBar": False
                                            }
                                        )
                                    ]

                                )
                            ]
                        ),

                        # =========================================
                        # RIGHT COLUMN - 40%
                        # =========================================
                        html.Div(
                            className="right-column",
                            children=[

                                html.H5(
                                    "Portfolio and Series Details",
                                    style={
                                        "backgroundColor": "white",
                                        "textAlign": "center",
                                        "fontWeight": "bold",
                                        "fontStyle": "italic"
                                    }
                                ),

                                # -----------------------------
                                # 3D Scatter Chart 4
                                # -----------------------------

                                dcc.Graph(

                                    id="fig_3did",

                                    figure=fig_3d,

                                    className="scatter3d",

                                    config={
                                        "displayModeBar": False
                                    }
                                )
                            ]
                        ),

                        # =========================================
                        # BOTTOM SCATTER
                        #
                        # Spans middle + right columns
                        # =========================================
                        html.Div(

                            className="bottom-scatter",
                            children=[

                                html.H5(
                                    "Drill Down",
                                    style={
                                        "backgroundColor": "white",
                                        "textAlign": "center",
                                        "fontWeight": "bold",
                                        "fontStyle": "italic"
                                    }
                                ),

                                dcc.Graph(
                                    id="gpMultiLine",
                                    figure=go.Figure(
                                             layout=dict(
                                                 paper_bgcolor="white",
                                                 plot_bgcolor="white",
                                                 margin=dict(l=10, r=10, t=10, b=10),
                                             )
                                         ),

                                    className="scatter5",
                                    config={
                                        "displayModeBar": False
                                    },
                                    style={
                                        "height": "350px",
                                        "width": "100%",
                                        "backgroundColor": "white",
                                    }
                                )
                            ]
                        )

                ]
            )

    ]
    )




##-------------- common FILTER function ------------------- ## Start
def get_filtered_df(portfolioName, strategyName, seriesName):

    dfFiltered = app.server.df

    if portfolioName:
        dfFiltered = dfFiltered.filter(
            pl.col("Portfolio").is_in(portfolioName)
        )

    if strategyName:
        dfFiltered = dfFiltered.filter(
            pl.col("Strategy").is_in(strategyName)
        )

    if seriesName:
        dfFiltered = dfFiltered.filter(
            pl.col("SERIES").is_in(seriesName)
        )

    return dfFiltered
##-------------- common FILTER function ------------------- ## end

###########################  callbacks ##########################  start

## ------------------  callback for dropdown -------------------- ## Start
@app.callback(
    Output("ddPortfolio", "options"),
    Output("ddPortfolio", "value"),

    Output("ddStrategy", "options"),
    Output("ddStrategy", "value"),

    Output("ddSeries", "options"),
    Output("ddSeries", "value"),

    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value"),
)
def update_dropdowns(portfolioName, strategyName, seriesName):


    df = app.server.df

    # =====================================================
    # Portfolio options
    # based on Strategy + Series
    # =====================================================

    qPortfolio = df

    if strategyName:
        qPortfolio = qPortfolio.filter(
            pl.col("Strategy").is_in(strategyName)
        )

    if seriesName:
        qPortfolio = qPortfolio.filter(
            pl.col("SERIES").is_in(seriesName)
        )

    qPortfolio = (
        qPortfolio
        .select("Portfolio")
        .unique()
    )


    # =====================================================
    # Strategy options
    # based on Portfolio + Series
    # =====================================================

    qStrategy = df

    if portfolioName:
        qStrategy = qStrategy.filter(
            pl.col("Portfolio").is_in(portfolioName)
        )

    if seriesName:
        qStrategy = qStrategy.filter(
            pl.col("SERIES").is_in(seriesName)
        )

    qStrategy = (
        qStrategy
        .select("Strategy")
        .unique()
    )


    # =====================================================
    # Series options
    # based on Portfolio + Strategy
    # =====================================================

    qSeries = df

    if portfolioName:
        qSeries = qSeries.filter(
            pl.col("Portfolio").is_in(portfolioName)
        )

    if strategyName:
        qSeries = qSeries.filter(
            pl.col("Strategy").is_in(strategyName)
        )

    qSeries = (
        qSeries
        .select("SERIES")
        .unique()
    )


    # =====================================================
    # Collect all 3 queries together
    # =====================================================

    dfPortfolio, dfStrategy, dfSeries = pl.collect_all([
        qPortfolio,
        qStrategy,
        qSeries
    ])


    # =====================================================
    # Convert to lists
    # =====================================================

    portfolioList = sorted(
        dfPortfolio["Portfolio"].to_list()
    )

    strategyList = sorted(
        dfStrategy["Strategy"].to_list()
    )

    seriesList = sorted(
        dfSeries["SERIES"].to_list()
    )


    # =====================================================
    # Dropdown options
    # =====================================================

    portfolioOptions = [
        {"label": x, "value": x}
        for x in portfolioList
    ]

    strategyOptions = [
        {"label": x, "value": x}
        for x in strategyList
    ]

    seriesOptions = [
        {"label": x, "value": x}
        for x in seriesList
    ]


    # =====================================================
    # Remove selections which are no longer valid
    # =====================================================

    portfolioName = [
        x for x in (portfolioName or [])
        if x in portfolioList
    ]

    strategyName = [
        x for x in (strategyName or [])
        if x in strategyList
    ]

    seriesName = [
        x for x in (seriesName or [])
        if x in seriesList
    ]


    return (
        portfolioOptions,
        portfolioName,

        strategyOptions,
        strategyName,

        seriesOptions,
        seriesName
    )
## ------------------  callback for dropdown -------------------- ## End

## ----------------- callback for portfolio pie ------------------## Start
@app.callback(
    Output("piePortfolio1", "figure"),
    Output("processingTimeid", "children"),
    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value"),
)

def updatePortfolioPie(
    portfolioName,
    strategyName,
    seriesName
):
    timeStart = datetime.datetime.now()

    dfFiltered = get_filtered_df(
        portfolioName,
        strategyName,
        seriesName
    )

    print(dfFiltered.collect().head())
    print(dfFiltered.select(pl.col('profitLoss')).sum().collect())

    dfPie = (
        dfFiltered
        .group_by("Portfolio")
        .agg(
            pl.col("profitLoss")
            .sum()
            .alias("pl")
        )
        .sort("pl", descending=True)
        .collect()
    )

    if dfPie.height == 0:
        return go.Figure()

    fig = go.Figure(
        data=[
            go.Pie(
                title= "Portfolio",
                labels=dfPie["Portfolio"].to_list(),
                values=dfPie["pl"].to_list(),
                hole=0.5,
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "P/L: %{value}<br>"
                    "Share: %{percent}"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=5, r=5, t=5, b=5)
    )

    timeEnd = datetime.datetime.now()
    processingTime = str(timeEnd.second - timeStart.second)
    print(f"processingTime {processingTime}")
    return fig, processingTime
## ----------------- callback for portfolio pie ------------------## End

## ------------------ callback for strategy pie chart -----------------## Start
@app.callback(
    Output("pieStrategy1", "figure"),
    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value"),
)
def updateStrategyPie(
    portfolioName,
    strategyName,
    seriesName
):

    dfFiltered = get_filtered_df(
        portfolioName,
        strategyName,
        seriesName
    )

    dfPie = (
        dfFiltered
        .group_by("Strategy")
        .agg(
            pl.col("profitLoss")
            .sum()
            .alias("pl")
        )
        .sort("pl", descending=True)
        .collect()
    )

    if dfPie.height == 0:
        return go.Figure()

    fig = go.Figure(
        data=[
            go.Pie(
                title="Strategy",
                labels=dfPie["Strategy"].to_list(),
                values=dfPie["pl"].to_list(),
                hole=0.5,
                textinfo="none",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "P/L: %{value}<br>"
                    "Share: %{percent}"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=5, r=5, t=5, b=5)
    )

    return fig
## ------------------ callback for strategy pie chart -----------------## End


## ------------------ callback for Third chart -----------------## Start
@app.callback(
    Output("barStrategy1", "figure"),
    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value"),
)
def updateStrategyBar(
    portfolioName,
    strategyName,
    seriesName
):

    dfFiltered = get_filtered_df(
        portfolioName,
        strategyName,
        seriesName
    )

    dfBar = (
        dfFiltered
        .group_by("Strategy")
        .agg(
            pl.col("profitLoss")
            .sum()
            .alias("pl")
        )
        .sort("pl", descending=True)
        .collect()
    )

    if dfBar.height == 0:
        return go.Figure()

    fig = go.Figure(
        data=[
            go.Bar(
                x=dfBar["Strategy"].to_list(),
                y=dfBar["pl"].to_list(),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "P/L: %{y:,.2f}"
                    "<extra></extra>"
                )
            )
        ]
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        xaxis=dict(
            showticklabels=False,
            title= 'Series'
        ),

        yaxis=dict(
            showticklabels=False,
            title=None
        )
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=5, r=5, t=5, b=5)
    )

    return fig
## ------------------ callback for 3rd Chart  chart -----------------## End

## ----------------- 3d Scatter ----------------- Start
@app.callback(
    Output("fig_3did", "figure"),
    Input("ddPortfolio", "value"),
    Input("ddStrategy", "value"),
    Input("ddSeries", "value"),
)
def updateScatter(
    portfolioName,
    strategyName,
    seriesName
):

    dfFiltered = get_filtered_df(
        portfolioName,
        strategyName,
        seriesName
    )

    qPortStrSer = (
        dfFiltered
        .group_by([
            "Portfolio",
            "Strategy",
            "SERIES"
        ])
        .agg(
            pl.col("profitLoss")
            .sum()
            .alias("pl")
        )
        .sort("pl", descending=True)
    )

    dfPortStrSer = qPortStrSer.collect()

    if dfPortStrSer.height == 0:
        return go.Figure()

    # Create your scatter here
    # #############  3 d Scatter ############# Start

    dfPortStraSer = dfPortStrSer.filter([(pl.col('pl')<15000)
                                          & (pl.col('pl')>-15000)])
    portfolios = dfPortStraSer["Portfolio"].unique().to_list()
    portfolio_map = {
        portfolio: i
        for i, portfolio in enumerate(portfolios)
    }
    color_values = [
        portfolio_map[p]
        for p in dfPortStraSer["Portfolio"].to_list()
    ]
    pl_values = dfPortStraSer["pl"].to_list()
    pl_abs = dfPortStraSer["pl"].abs().to_list()
    fig_3d = go.Figure()
    fig_3d.add_trace(
        go.Scatter3d(
            x=dfPortStraSer["Portfolio"].to_list(),
            y=dfPortStraSer["SERIES"].to_list(),
            z=pl_values,
            mode="markers",
            marker=dict(
                size=pl_abs,
                sizemode="area",
                sizeref=2 * 14000 / (20 ** 2),
                sizemin= 4,
                color=color_values,
                colorscale="Viridis",
                cmin=0,
                cmax=len(portfolios) - 1,
                showscale=False,
                colorbar=dict(
                    title="Portfolio",
                    tickmode="array",
                    tickvals=list(range(len(portfolios))),
                    ticktext=portfolios
                ),
                opacity=1
            ),
            hovertemplate=(
                "Portfolio: %{x}<br>"
                "Strategy: %{y}<br>"
                "P/L: %{z:,.2f}"
                "<extra></extra>"
            )
        )
    )
    fig_3d.update_layout(
        title=dict(
            text="Portfolio Strategy Series",
            x=0.5,
            xanchor="center"
        ),

        # Reduce outer margins
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),

        # Overall figure background
        paper_bgcolor="white",
        plot_bgcolor="white",  # 2D plotting area

        # 3D plotting area
        scene=dict(
            xaxis=dict(
                title="Portfolio",
                backgroundcolor="white",
                showbackground=False,
            ),
            yaxis=dict(
                title="Series",
                backgroundcolor="white",
                showbackground=False,
            ),
            zaxis=dict(
                title="Profit/Loss",
                # backgroundcolor="white",
                # showbackground=False,
            ),

            # 3D scene background
            bgcolor="white"
        )
    )

    return fig_3d
    # #############  3 d Scatter ############# End


## ----------------- 3d Scatter ----------------- End


## --------------------Multiline -------------------## Start
@app.callback(
    Output("gpMultiLine", "figure"),
    Input("fig_3did", "clickData")
)
def update_multiline(clickData):

    fig = go.Figure()

    if not clickData:
        fig.update_layout(
            # title="Click a point on the 3D chart"
        )
        return fig

    print(clickData)
    print(clickData['points'][0]['y'])


    series    = clickData['points'][0]['y']

    print( series)

    # Filter original LazyFrame
    q_click = (
        app.server.df
        .filter(

            (pl.col("SERIES") == series)
        )
    )

    df_click = q_click.collect()

    if df_click.is_empty():
        return fig

    # Create one line for each symbol
    symbols = df_click["SYMBOL"].unique().to_list()

    for symbol in symbols:

        df_symbol = (
            df_click
            .filter(pl.col("SYMBOL") == symbol)
            .sort("DATE1")
        )

        fig.add_trace(
            go.Scatter(
                x=df_symbol["DATE1"].to_list(),
                y=df_symbol["profitLoss"].to_list(),
                mode="markers",
                name= "",
                marker = dict(
                    opacity=.8,
                    size = 2,
                ),

            )
        )

    fig.update_layout(
        title=dict(
            text=f" {series}",
            x=0.5
        ),

        xaxis=dict(
            title="Date"
        ),

        yaxis=dict(
            title="Profit / Loss"
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        margin=dict(
            l=40,
            r=20,
            t=50,
            b=40
        ),

        hovermode="x unified"
    )

    return fig
## --------------------Multiline -------------------## End

###########################  callbacks ##########################  end


###################################### Process ####################################### end




if __name__ == "__main__":
    app.run(debug=True)#--------------- Dash App Ends  here --------------------------------