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
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from datetime import datetime
from dash import dcc, html, Input, Output, State
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

app.server.df = pl.scan_parquet("C:/Anupam/GIT/base/cursorFolder/tools/BhavData/*.parquet")
print(app.server.df.collect_schema().names())

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
    print(dfPortStraSer.shape)

    ##############  pie charts ###################### start

    portfolioSeries = dfPortfolioPl.select(pl.col('Portfolio')).to_series()
    portfolioPLSeries = dfPortfolioPl.select(pl.col('profitLoss')).to_series()
    strategySeries = dfStrategyPl.select(pl.col('Strategy')).to_series()
    strategyPLSeries = dfStrategyPl.select(pl.col('profitLoss')).to_series()

    #------------------------- Portfolio Pie Fig ------------------------# Start
    piePortfolio = go.Figure(
            data=[go.Pie(labels=portfolioSeries, values= portfolioPLSeries,
                         textinfo="value", textposition="inside", insidetextorientation="radial",
                         marker=dict(colors=['green', 'red']))],
            layout=go.Layout(
                title=dict(
                    text="Profit Loss",
                    font=dict(size=18),
                    x=0.5,  # center
                    xanchor="center",
                    y=1,  # push title down a bit
                    yanchor="top",
                ),
                margin=dict(t=35, b=10, l=10, r=10),
                showlegend=False,
                width=200,  # figure width
                height=200  # figure height
            )
        )
    #------------------------- Portfolio Pie Fig ------------------------# End

    #------------------------- Strategy Pie Fig ------------------------# Start
    pieStrategy = go.Figure(
            data=[go.Pie(labels=strategySeries, values= strategyPLSeries,
                         textinfo="value", textposition="inside", insidetextorientation="radial",
                         marker=dict(colors=['green', 'red']))],
            layout=go.Layout(
                title=dict(
                    text="Profit Loss",
                    font=dict(size=18),
                    x=0.5,  # center
                    xanchor="center",
                    y=1,  # push title down a bit
                    yanchor="top",
                ),
                margin=dict(t=35, b=10, l=10, r=10),
                showlegend=False,
                width=200,  # figure width
                height=200  # figure height
            )
        )
    #------------------------- Strategy Pie Fig ------------------------# End


    ##############  pie charts ###################### end


    #############  3 d Scatter ############# Start
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
        )
    )
    #############  3 d Scatter ############# End
    return piePortfolio, pieStrategy, fig_3d, portfolioSeries, strategySeries, dfPortStraSer

# --------------------  function to update figures ------------------------- end

df = app.server.df
piePortfolio,pieStrategy, fig_3d, portfolioSeries, strategySeries, dfPortStraSer = figUpdate(df)

#########           Layout Section ################### Start
app.layout = dbc.Container([
    dcc.Graph(id = 'piePortfolio1', figure= piePortfolio ),
    dcc.Graph(id = 'pieStrategy1', figure= pieStrategy ),
    dcc.Graph(id= 'fig_3did', figure= fig_3d , style={"width": "100%", "height": "600px"}),
    dcc.Dropdown(
        id='ddPortfolio',
        options=[{"label": p, "value": p} for p in portfolioSeries],
        placeholder="Select Portfolio Name",
        multi=True
    ),
    dcc.Dropdown(
        id='ddStrategy',
        options=[{"label": p, "value": p} for p in strategySeries],
        placeholder="Select Strategy Name",
        multi=True
    ),
    dcc.Dropdown(
        id='ddSeries',
        options=[{"label": p, "value": p} for p in dfPortStraSer.select(pl.col('SERIES')).unique().to_series().sort()],
        placeholder="Select Strategy Name",
        multi=True
    ),
])
#########           Layout Section ################### End

###########################  callbacks ##########################  start
@app.callback(
    Output('ddStrategy', 'value'),
    Input('ddPortfolio', 'value'),
    Input('ddSeries', 'value'),
)
def updateStretgyDropdown(portfolioNames, seriesNames):
    if (not(portfolioNames) and not(seriesNames)):
        print("No Portfolio and Series Fliter")
        dfFiletred = app.server.df



###########################  callbacks ##########################  end

if __name__ == "__main__":
    app.run(debug=True)#--------------- Dash App Ends  here --------------------------------