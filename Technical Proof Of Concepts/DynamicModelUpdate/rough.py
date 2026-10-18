# #######################  generate random values between twp numbers #####################
# import pandas as pd
# import  numpy as np
#
# import random
#
# numbers = [random.uniform(66, 80) for _ in range(20)]
# for i in numbers:
#     print(i)
# #######################  generate random values between twp numbers #####################

# ####################  equation  ######################
# import polars as pl
# import pandas as pd
# # from polars.dataframe.frame import P
# import statsmodels.api as sm
# import json
#
#
# # Prevent columns from collapsing into '...'
# pl.Config(tbl_cols=-1)
#
# dfTrng1 = pl.read_csv("BaseDataTrng1.csv")
# dfConfermation1 = pl.read_csv("BaseDataTrng2.csv")
#
#
# # print(dfTrng1.head())
# x_cols = ['coreGlue', 'binder1', 'binder2', 'binder3', 'rpm', 'layerThickness', 'cooling', 'setting']
# y_col = 'pressure'
#
# pdf = dfTrng1.select(x_cols + [y_col]).to_pandas()
#
# X = pdf[x_cols]
# y = pdf[y_col]
#
# X_with_constant = sm.add_constant(X)
# # print("  X_with_constant ")
# # print(X_with_constant)
# # print(y)
#
# model = sm.OLS(y, X_with_constant).fit()
#
# const = model.params["const"]
# # print(const)
#
# # slopes = [model.params[x_cols]]
# slopes = model.params[x_cols]
#
# # print(slopes)
#
# intercept = model.params["const"]
#
# def create_equation(model, x_cols, y_name="Y", tolerance=1e-6):
#
#     params = model.params
#
#     intercept = params.get("const", 0.0)
#
#     equation = f"{y_name} = {intercept:.8g}"
#
#     for col in x_cols:
#         slope = float(params[col])
#
#         # Ignore extremely small coefficients
#         if abs(slope) < tolerance:
#             continue
#
#         if slope >= 0:
#             equation += f" + {slope:.8g}*{col}"
#         else:
#             equation += f" - {abs(slope):.8g}*{col}"
#
#     return equation
#
#
#
# equation = create_equation(
#     model,
#     x_cols,
#     y_name="DependentVariable"
# )
#
# # print(equation)
#
#
# def calculate_y(row, model, x_cols):
#
#     params = model.params
#
#     y = float(params.get("const", 0.0))
#
#     for col in x_cols:
#         y += float(params[col]) * float(row[col])
#
#     return y
#
#
# pdf = pl.read_csv("BaseData.csv", infer_schema_length=500).select(x_cols + [y_col]).to_pandas() # ****************************
#
# pdf["predicted_y"] = pdf.apply(
#     lambda row: calculate_y(row, model, x_cols),
#     axis=1
# )
#
# dfPolar = pl.DataFrame(pdf)
# dfPolar = dfPolar.with_columns(pl.Series([i for i in range(len(dfPolar))]).alias('ser'))
# # dfPolar = dfPolar.head(21)
# print(dfPolar.head)
# # print(dfPolar.shape)
#
#
# import plotly.express as px
# import polars as pl
#
# # Assuming your Polars DataFrame is named 'df'
# fig = px.scatter(
#     dfPolar,
#     x="ser",
#     y=["pressure", "predicted_y"],
#     # y=["Strg"],
#     title="Actual Strg vs Predicted Y",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
#
# # This will open a new tab in your default web browser
# fig.show()
# ####################  equation  ######################


#####  create dummy equation and generate data  #########
import pandas as pd
import polars as pl
import math
import statsmodels.api as sm
import json
import plotly.express as px
# read df and take 40 for training and basic equation creation ---- start

###  About data --- start
"""
The company makes adhesive. The raw material is purchased and then processed. 
There are 4 main ingradiants. First is the core binder, which is then mixed with three
different binders. Then the it is mixed at different PRM and rotated for some minutes.
Then certain thickness of mixture is applied on surface and then clamped   
1) air density range : .9 -- 1.25  kg/m cube ... less strength..better when less dense.
2) atmospheric pressure : 990 -- 1025 hectopascals ... high is better
3) humidity: 60 to 90 %   , where strength increases from less humid to high and then drops when very high
"""
###  About data  --- end

df = pl.read_csv("BaseDataTrng1.csv")
df = df.with_columns(pl.Series([i for i in range(len(df))]).alias('ser'))
df = df.to_pandas().head(30)
print(df.head())
# dfX = df['coreGlue'].to_pandas()
# print(dfX.head())
# dfX = pd.DataFrame({"x": [1,2,3,4,5,6,1.2,2.2,3.4,4.5,5,6,7,8,9,11,14,15,20]})
df['calccoreGlue'] = df['coreGlue'].apply(
    # lambda row: -row**2.1 +12*row +1
    # lambda row: (-10* row**2.1 + 120*row +1)
    # lambda row: (1* row**4.1 - 12*row +1)
    lambda row: (-row**0.876 + 2*row +1)
)
df['calcbinder1'] = df['binder1'].apply(
    # lambda row: -row**2.1 +12*row +1
    # lambda row: (-10* row**2.1 + 120*row +1)
    lambda row: (1* row**1.1 - 12*row +1)
)
df['calcbinder2'] = df['binder2'].apply(
    # lambda row: -row**2.1 +12*row +1
    # lambda row: (-10* row**2.1 + 120*row +1)
    lambda row: (-1* row**1.3 - 7*row +1)
)

df["strength"] = df['calcbinder1'] + df['calcbinder2']+  +df['calccoreGlue']

print(df.head())

fig = px.scatter(
    df,
    x="ser",
    y=["strength", "calccoreGlue", "calcbinder1", "calcbinder2"],
    # y=["Strg"],
    title="Actual Strg vs Predicted Y",
    labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
)

# This will open a new tab in your default web browser
fig.show()

### get all independent cols in a list x_cols


# read df and take 40 for training and basic equation creation ---- end

#####  create dummy equation and generate data  #########
