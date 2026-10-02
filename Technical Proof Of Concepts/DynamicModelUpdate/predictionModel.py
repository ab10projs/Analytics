import polars as pl
import pandas as pd
import statsmodels.api as sm
import json
import json
import threading
from collections import deque
import time

import dash
from click import style
from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.express as px

import redis
import polars as pl

STREAM_NAME = "prediction_model_data"

# ----------------------------------------------------
# Redis
# ----------------------------------------------------

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# ----------------------------------------------------
# Shared Buffer
# ----------------------------------------------------

buffer = deque(maxlen=400)
counter = 0

df = pl.read_csv("C://GIT_Repo_Analytics//Analytics//Technical Proof Of Concepts//DynamicModelUpdate//css.csv",
                 infer_schema_length= 600)
dfCollect = df.clear()

# ----------------------------------------------------
# Stream Reader Thread
# ----------------------------------------------------
def stream_reader():
    global dfCollect
    last_id = "$"
    while True:
        messages = r.xread(
            {STREAM_NAME: last_id},
            block=100
        )
        if not messages:
            continue
        for stream_name, records in messages:
            for msg_id, values in records:
                last_id = msg_id
                rows = json.loads(values["data"])
                dfLatest = pl.DataFrame(rows)
                # print(dfCollect)
                buffer.append(dfLatest)
                dfCollect = dfCollect.vstack(dfLatest)
                # print("--------")

threading.Thread(
    target=stream_reader,
    daemon=True
).start()

while True:
    print(dfCollect)
    time.sleep(1)