from operator import index
import pandas as pd
import numpy as np
import polars as pl
import math
import plotly
import dash
import random
import statistics
import statsmodels.api as sm
import json
import plotly.express as px


# Prevent columns from collapsing into '...'
pl.Config.set_fmt_str_lengths(100)
pl.Config.set_tbl_width_chars(10000)

pd.set_option('display.float_format','{:.2f}'.format)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


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

--------------------
The factors that can not be controlled are as below:
1) relHum : Relative Humidity is natural
2) tempr  : Temperature is natural
3) coreGlue : The raw material is supplied by vendors and can not be guaranteed to be of same 
composition resulting in same strength
4) binder1 :  The raw material is supplied by vendors and can not be guaranteed to be of same 
composition resulting in same strength
-------------------

-------------------
Factors that can be controlled
1) rpm: The machine's rpm can be controlled
2) rpmSec : machine running at a certain rpm for desired seconds can be controlled 
3) coreGlue and binder1 ratio: The ration in which the two ingradient can be mixed can be controlled   
-------------------

------------------- Design of Experient ----------------------
Once a lot of coreGlue and binder material is received, there is no guarantee that the old mixture ratio will
produce same strength. The other variable factors like relative humidity and temperature also has impact on
strength, which are out of control.
Before deciding the mix and processing (ratio, rpm etc.) samples are taken and strength is checked 


Regular monitoring is needed as the relative humidity and temperature keeps changing. Alert needs to be 
generated whenever due to temperature and humidity the rpm and rpmSec needs to be adjusted     
------------------- Design of Experient ----------------------

------------------- Approach ---------------------------
1) save the prepared data (40 rows), only variable columns and actual strength and not calculated.
2) use statics model and fit the data to find the estimation equation
3) publish the statistics and relation -- (store in json)
4) use AI to explain the impact of variables. -- (store in json)
5) from mean and sd, publish the strength that can be expected at 5% significance OR 95% confidence level  -- (store in json)
6) generate next 10 rows and consider it as sample
7) calculate standard error, and z score to confirm if the sample of 10 and initial sample of 30 have
significant difference  -- (store in json)
8) If the difference is significant, alert is raised and a commentary from AI is shown to suggest what
process changes in mix, rpm rpmSec should be done. -- (store in json)
9) generate new samples after altering process (rpm,mix, rpmSec) and perform hypothesis testing
10) Ask agent recommendations for optimization on rpm, rpmSec and the ingradiant

------------------- Approach ---------------------------
"""

###  About data  --- end

####--- config ----
N= 50
min_val = 1
max_val =10

var1 = [ round(random.uniform(1,10),4) for _ in range(N) ]
var2 = [ round(random.uniform(25,125),4) for _ in range(N) ]
var3 = [ round(random.uniform(500,1200),4) for _ in range(N) ]
var4 = [ round(random.uniform(700,1500),4) for _ in range(N) ]
var5 = [ round(random.uniform(1000,2000),4) for _ in range(N) ]
var6 = [ round(random.uniform(100,200),4) for _ in range(N) ]
var7 = [ round(random.uniform(1,20),4) for _ in range(N) ]

# print(var1,var2,var3,var4,var5,var6,var7)
print(var1)
df = pd.DataFrame({
                    'var1': var1,
                    'var2': var2,
                    'var3': var3,
                    'var4': var4,
                    'var5': var5,
                    'var6': var6,
                    'var7': var7,
                   })

print(df)

design = pd.DataFrame(
    {
        "const":1,
        "var1Rel": df['var1'].apply(lambda val: pow(val,1.83)/10),
        "var2Rel": df['var2'].apply(lambda val: pow(val,1.3)/292),
        "var3Rel": df['var3'].apply(lambda val: pow(val, .13) / 1.7),
        "var45Rel": df[['var4','var5']].apply(lambda val: pow(val['var4']/val['var5'], 1.44) / 1.4, axis=1),
        "var67Rel": df[['var6','var7']].apply(lambda val: pow(val['var6']*val['var7'], .14) / 2.2, axis=1),
    }
)
print(design)


