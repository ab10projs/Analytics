import redis
import polars as pl 
import json 
from collections import deque 
import datetime
import time

df = pl.read_csv("C://Anupam//GIT//base//cursorFolder//tools//BhavData//dfMerged.csv") 

stream_name = "stocks_stream"
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

df = df.with_columns(pl.col("DATE1").cast(pl.Date)).sort("DATE1")

groups = df.partition_by("DATE1", maintain_order=True)

# print(groups[2])

for a,b in enumerate(groups, start=0):
    dfJson = b.write_json()
    r.xadd(stream_name,{'date':str(b['DATE1'][0]),'data':dfJson})
    print('Published Batch for date:', b['DATE1'][0])
    time.sleep(.7)
