########################## Trading Analysis Dashboard - Visualizations ##########################
import polars as pl
import pandas as pd
import datetime
import sys
import os

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure Polars
pl.Config.set_tbl_cols(100)
pl.Config.set_tbl_width_chars(1000)
pl.Config.set_tbl_rows(1000)
pl.Config.set_float_precision(4)

# Dash imports
from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

# Redis Integration
try:
    import redis
    import json
    import pickle

    REDIS_AVAILABLE = True
    # Initialize Redis connection
    try:
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=False  # We'll handle encoding manually for pickle
        )
        # Test connection
        redis_client.ping()
        print("✓ Redis connection established")
    except (redis.ConnectionError, redis.TimeoutError) as e:
        print(f"⚠ Redis connection failed: {e}")
        print("   Continuing without Redis caching...")
        REDIS_AVAILABLE = False
        redis_client = None
except ImportError:
    REDIS_AVAILABLE = False
    redis_client = None
    print("Redis not available. Install with: pip install redis")
    print("   Continuing without Redis caching...")

ite = redis_client.scan_iter("*")

for i in ite:
    print(redis_client.get(i.decode()).decode())