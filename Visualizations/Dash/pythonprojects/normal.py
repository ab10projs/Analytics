import numpy as np
import plotly.graph_objects as go

mu = 5
sigma = 2

x = np.linspace(mu - 4*sigma, mu + 4*sigma, 500)
y = 1/(sigma*np.sqrt(2*np.pi)) * np.exp(-((x-mu)**2)/(2*sigma**2))

print(x)
print("-----------------")
print(y)
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Normal PDF"))
fig.update_layout(title="Normal Distribution (Mean=5, SD=2)",
                  xaxis_title="x", yaxis_title="Density")
fig.show()
