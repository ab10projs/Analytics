import redis
import polars as pl 
import json 
from collections import deque 
import datetime
import time

df = pl.read_csv("C://GIT_Repo_Analytics//Analytics//Technical Proof Of Concepts//DynamicModelUpdate//css.csv",
                 infer_schema_length= 600)

stream_name = "prediction_model_data"
r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)



groups = df.partition_by("Serl", maintain_order=True)

# print(groups[2])

for a,b in enumerate(groups, start=0):
    dfJson = b.write_json()
    r.xadd(stream_name,{'date':str(b['Serl'][0]),'data':dfJson})
    print('Published Batch for Serl:', b['Serl'][0])
    time.sleep(2)
