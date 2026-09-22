import polars as pl
import pandas as pd
# from polars.dataframe.frame import P
import statsmodels.api as sm
import json


# Prevent columns from collapsing into '...'
pl.Config(tbl_cols=-1)

dfTrng1 = pl.read_csv("cssTrng1.csv")

print(dfTrng1.head())
x_cols = ['Cem', 'BFurSlg', 'FlyA', 'Wtr', 'Super', 'Coar', 'FAgg', 'Age']
y_col = 'Strg'


pdf = dfTrng1.select(x_cols + [y_col]).to_pandas()
X = pdf[x_cols]
y = pdf[y_col]

X_with_constant = sm.add_constant(X)
print("  X_with_constant ")
print(X_with_constant)
print(y)

model = sm.OLS(y, X_with_constant).fit()
const = model.params["const"]
print(const)
slopes = [model.params[x_cols]]

slopes = model.params[x_cols]

print(slopes)

intercept = model.params["const"]

def create_equation(model, x_cols, y_name="Y", tolerance=1e-6):

    params = model.params

    intercept = params.get("const", 0.0)

    equation = f"{y_name} = {intercept:.8g}"

    for col in x_cols:
        slope = float(params[col])

        # Ignore extremely small coefficients
        if abs(slope) < tolerance:
            continue

        if slope >= 0:
            equation += f" + {slope:.8g}*{col}"
        else:
            equation += f" - {abs(slope):.8g}*{col}"

    return equation



equation = create_equation(
    model,
    x_cols,
    y_name="DependentVariable"
)

print(equation)


def calculate_y(row, model, x_cols):

    params = model.params

    y = float(params.get("const", 0.0))

    for col in x_cols:
        y += float(params[col]) * float(row[col])

    return y

pdf["predicted_y"] = pdf.apply(
    lambda row: calculate_y(row, model, x_cols),
    axis=1
)

dfPolar = pl.DataFrame(pdf)
print(dfPolar.head)
