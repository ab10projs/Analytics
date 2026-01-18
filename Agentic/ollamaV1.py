import requests
from dash import Dash, html, dcc, Input, Output, State

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

app = Dash(__name__)

app.layout = html.Div(
    style={"maxWidth": "800px", "margin": "auto", "padding": "20px"},
    children=[
        html.H2("Local AI (Ollama + Dash)"),

        dcc.Textarea(
            id="prompt",
            placeholder="Ask something...",
            style={"width": "100%", "height": "120px"}
        ),

        html.Br(),
        html.Button("Ask AI", id="ask_btn"),

        html.Hr(),
        html.Div(
            id="response",
            style={
                "whiteSpace": "pre-wrap",
                "background": "#f4f4f4",
                "padding": "15px",
                "borderRadius": "5px"
            }
        )
    ]
)

@app.callback(
    Output("response", "children"),
    Input("ask_btn", "n_clicks"),
    State("prompt", "value"),
    prevent_initial_call=True
)
def query_ollama(n_clicks, prompt):
    if not prompt:
        return "Please enter a prompt."

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()

    return r.json()["response"]

if __name__ == "__main__":
    app.run(debug=True)
