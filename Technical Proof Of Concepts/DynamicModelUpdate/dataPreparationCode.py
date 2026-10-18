#####  create dummy equation and generate data  #########
import pandas as pd
import numpy as np
import polars as pl
import math
import statsmodels.api as sm
import json
import plotly.express as px


# Remove the limit on the number of displayed columns
pl.Config.set_tbl_cols(-1)

# Prevent columns from collapsing into '...'
pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_width_chars(10000)

###  About data --- start
"""
The company performs an industrial process in which metalic parts are joint in extreme temperature and 
humidity. There are two main ingradiants (coreGlu and binder),which are procured from multiple vendors
and hence the exact chemical property of these ingradiants is not assumed to be fixed. There is impact
of external factors like temperature and relative humidity. The company perfoms processing of these 
indradiants and mix the material at different rpms and different time as this process also impacts the 
bonding strength of adhesive. Past data has shown that the strength of adhesive ranges from 3.45 to 6.6
pounds/sq inch. The industrial process requires the bond strength to be >5.2 pounds/sq inch to be acceptable.
lesser strength than this will cause the parts to fail, and hence not acceptable. A stronger material than 6.2
becomes very expensive.    
 
1) coreGlue : range (80 - 90) percent -- impact (increate, then flat)
2) binder1  : range (10 - 20) percent  -- impact (increase, then dip flat)
3) relativeHumididty  : range (40 - 60) percent  -- impact (increase, then dip sharp)
4) temperatue  : range (-100  -50) F  -- impact (increasse, then dip )
5) rpm      : range (800 - 1400)      -- impact (increase, then dip slow)
6) rpmSec   : range (600 - 800)       -- impact (increase, then dip flat)
7) pressure kg/sqinc: (3.45 - 6.6)    -- (acceptable 5.2 onwards)
"""

###  About data  --- end

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


# ### random data generation -- start
# import random
# x = 10
# low = 1.5
# high = 10.5
# lst = [round( random.uniform(low, high),4) for _ in range(x)]
# print(lst)
# ### random data generation -- end

## random data generation
import random
dataCount = 400
factor = [round( random.uniform(.01, .2),3) for _ in range(dataCount)]
binder1 = [round( (i)*100, 3) for i in factor]
coreGlu = [round( (1-i)*100, 3) for i in factor]
relHum = [round( random.uniform(40, 60),3) for _ in range(dataCount)]
tempr = [round( random.uniform(-100, -50),3) for _ in range(dataCount)]
rpm = [round( random.uniform(800, 1400),3) for _ in range(dataCount)]
rpmSec = [round( random.uniform(600, 800),3) for _ in range(dataCount)]
actualFactor = [round( random.uniform(.88, 1.15),3) for _ in range(dataCount)]

print(factor)
print(coreGlu)
print(binder1)
##

df = pd.DataFrame( {'coreGlu': coreGlu, 'binder1':binder1 , 'relHum':relHum, 'tempr':tempr,
                    'rpm':rpm, 'rpmSec':rpmSec, 'actualFactor': actualFactor})

df['calccoreGlu']= df['coreGlu'].apply(
    # lambda row: (-(row-90)**2 +560 -row**1.1 )/75
    lambda row: (-(row-90)**2 +560 -row**1.1 )/100
)

df['calcbinder1']= df['binder1'].apply(
# lambda x, M=100: 0 if x <= 0 else (M*(3*(x/12)**2 - 2*(x/12)**3))/75 if x < 12 else M/100
    lambda x, M=100: 0 if x <= 0 else (M*(3*(x/12)**2 - 2*(x/12)**3))/100 if x < 12 else M/150
)

df['calcrelHum']= df['relHum'].apply(
    lambda x, M=100: M * (1 - math.exp(-0.3 * (x - 40)))/50
)

df['calctempr']= df['tempr'].apply(
    lambda x, M=100: M * (1 - math.exp(-0.1 * (x + 100)))/100
)

df['calcrpm']= df['rpm'].apply(
# lambda x: (
#     (120 - 0.0025 * (x - 1000)**2)/100 if x <= 1000
#     else (120 - 0.000375 * (x - 1000)**2)/100
# )

lambda x: (
    (120 - 0.0025 * (x - 1000)**2)/50 if x <= 1000
    else (120 - 0.000375 * (x - 1000)**2)/50
)


)


df['calcrpmSec']= df['rpmSec'].apply(
lambda x: (
    (40 + 360 * (
        3 * ((x - 600) / 100)**2
        - 2 * ((x - 600) / 100)**3
    ))/500 if x <= 700
    else (400 + 0.4 * (x - 700)
         - 0.002 * (x - 700)**2)/500
)
)

df['estimate'] = df['calccoreGlu']+df['calcbinder1']+df['calcrelHum']+df['calctempr']+df['calcrpm']+df['calcrpmSec']

df['actualStrength'] = df['estimate'] *df['actualFactor']

print(df.head(300))



fig = px.scatter(
    df,
    x=df['rpmSec'],
    y=df['calcrpmSec'],
    title="calcrpmSec",
    labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
)


# This will open a new tab in your default web browser
fig.show()



#################------------------------------------------------------------------
# ## equation
# df = pl.read_csv("BaseData.csv")
# names = df.columns
# print(names)
# pressure = f"54 + pow({names[0]},1.67) + 2* pow({names[1]},1.22) - pow({names[2]},0.88) \
#  - pow(({names[3]}/{names[4]}),.77) + 1.33* ({names[5]}/{names[6]})"
# print(pressure)
