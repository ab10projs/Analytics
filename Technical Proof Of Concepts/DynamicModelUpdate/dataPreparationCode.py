##### generate data  #########
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

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

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
actualFactor = [round( random.uniform(.70, 1.30),3) for _ in range(dataCount)]


df = pd.DataFrame( {'coreGlu': coreGlu, 'binder1':binder1 , 'relHum':relHum, 'tempr':tempr,
                    'rpm':rpm, 'rpmSec':rpmSec, 'actualFactor': actualFactor})

df['calccoreGlu']= df['coreGlu'].apply(
    lambda row: (-(row-90)**2 +560 -row**1.1 )/75
)

df['calcbinder1']= df['binder1'].apply(
    lambda x, M=100: (M*(3*(x/12)**2 - 2*(x/12)**3))/100
)

df['calcrelHum']= df['relHum'].apply(
    lambda x, M=100: M * (1 - math.exp(-0.3 * (x - 40)))/50
)

df['calctempr']= df['tempr'].apply(
    lambda x, M=100: M * (1 - math.exp(-0.1 * (x + 100)))/100
)

df['calcrpm']= df['rpm'].apply(

lambda x: (
    (120 - 0.0025 * (x - 1000)**2)/100 if x <= 100
    else (120 - 0.00375 * (x - 1000)**2)/100
)


)

df['calcrpmSec']= df['rpmSec'].apply(

lambda x: (
    (40 + 360 * (
        3 * ((x - 600) / 100)**2
        - 2 * ((x - 600) / 100)**3
    ))/500 if x <= 700
    else (400 + 0.4 * (x - 700)
         - 0.02 * (x - 700)**2)/500
)

)

df['estimate'] = (df['calccoreGlu'] *0.5)+(df['calcbinder1']*1.2)+(df['calcrelHum']*1)+df['calctempr']+(df['calcrpm']*.07)+df['calcrpmSec']

df['actualStrength'] = df['estimate'] *df['actualFactor']

print(df.head(600))
dfpolar= pl.DataFrame(df)
# df.to_csv("C:/GIT_Repo_Analytics/Analytics/Technical Proof Of Concepts/DynamicModelUpdate/dataPrep.csv")
dfpolar.write_csv("C:/GIT_Repo_Analytics/Analytics/Technical Proof Of Concepts/DynamicModelUpdate/dataPrep.csv")


# ##################  individual figures for sanity check ####################
# fig1 = px.scatter(
#     df,
#     x=df['coreGlu'],
#     y=df['calccoreGlu'],
#     title="calccoreGlu",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig1.show()
#
# fig2 = px.scatter(
#     df,
#     x=df['binder1'],
#     y=df['calcbinder1'],
#     title="calcbinder1",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig2.show()
#
# fig3 = px.scatter(
#     df,
#     x=df['relHum'],
#     y=df['calcrelHum'],
#     title="calcrelHum",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig3.show()
#
# fig4 = px.scatter(
#     df,
#     x=df['tempr'],
#     y=df['calctempr'],
#     title="calctempr",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig4.show()
#
# fig5 = px.scatter(
#     df,
#     x=df['rpm'],
#     y=df['calcrpm'],
#     title="calcrpm",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig5.show()
#
# fig6 = px.scatter(
#     df,
#     x=df['rpmSec'],
#     y=df['calcrpmSec'],
#     title="calcrpmSec",
#     labels={"value": "Values", "variable": "Metric", "ser": "Ser"},
# )
# fig6.show()
# ##################  individual figures for sanity check ####################

#################------------------------------------------------------------------
# ## equation
# df = pl.read_csv("BaseData.csv")
# names = df.columns
# print(names)
# pressure = f"54 + pow({names[0]},1.67) + 2* pow({names[1]},1.22) - pow({names[2]},0.88) \
#  - pow(({names[3]}/{names[4]}),.77) + 1.33* ({names[5]}/{names[6]})"
# print(pressure)
