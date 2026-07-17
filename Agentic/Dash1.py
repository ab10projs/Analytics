import dash
import polars as pl
import pandas as pd
import time
from dash import Dash, Input, Output, html
import dash_core_components as dcc
import dash_bootstrap_components as dbc



df = pl.read_csv(f'C:/data/concreteStrength/Concrete Strenght DataSet/Concrete Compressive Strength.csv')


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout= html.Div([
    html.H3("Start")
])

if __name__ == '__main__':
    app.run(debug=True)
