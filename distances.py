"""

"""

import utils
import re
from datetime import date
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")


taf = '''
TAF CYHM 
FM231300 21007KT P6SM BKN070
FM232300 18010G20KT 3SM -SN OVC020 PROB30
RMK NXT FCST BY 230600Z
'''

metar = '''
METAR CYHM 230400Z 26008KT 15SM -SN SCT038 OVC054 M05/M09 A3002 RMK SC3SC5 SLP180=
'''
##### Constants - Airport Specific ######
day = int(input("Date of Search: ")) 
ground_elevation_home = 603
ground_elevation_airport = 800
magnetic_direction = 10
rwys = [32, 14, 27, 9]
direction = 'W'
#########################################

taf_split = taf.split("\n")
timeframe = utils.time_input()
start = timeframe[0]
end = timeframe[1]
regulatory_cloud_ceiling = 500
circuit_height = 1500

#year = date.today().year
#month = date.today().month

date = (day*100+start.hour)*100
temp = utils.temperature(metar)
temperature = temp[0]
dewpoint = temp[1]

altimeter = utils.altimeter(metar)
PA = round(ground_elevation_home + ((29.92 - altimeter)*1000),2)

lst = []
for each in taf_split:
    if 'TAF' in each and 'Z ' in each:
        each = each.replace("Z", "")
        line0 = (each.split(" ")[2])
        #print(line0)
        lst.append(line0)
    elif 'BECMG' in each:
        each = each.replace("BECMG ", "")
        line0 = (each.split("/")[0])
        line1 = (each.split("/")[1])
        start = int(line0.split(" ")[-1])*100
        end = int(line1.split(" ")[0])*100
        #print(start, end)
        lst.append(start)
        lst.append(end)
    elif 'FM' in each:
        line0 = (each.split(" ")[0])
        line0 = line0.replace("FM", "")
        line0 = int(line0)
        #print(line0)
        lst.append(line0)

#print(lst)
i = 0
while i < (len(lst)-1):
    if date >= int(lst[i]) == False:
        print("Taf not within start date.")
        break
    if date >= int(lst[i]) and date < int(lst[i+1]) :
        note = lst[i]
        #print(note)
    i = i + 1

bkn_ = []
ovc_ = []
skc_ = []
sct_ = []
few_ = []

for each in taf_split:
    #print(note)
    try:
        if str(note) in each:
            print(each)
            w = (re.search("KT", each)).span()[0]
            g = w - 3
            if each[g] == "G":
                #print('here', g)
                gust = int(each[g+1:g+3])
                wind = int(each[g-3:g])
                heading = int(each[g-5:g-2])
            else:
                gust = 0
                wind = int(each[w-2:w])
                heading = int(each[w-5:w-2])
            #print(gust, wind, heading)
            sm = (re.search("SM", each)).span()[0]
            sm = each[sm-2:sm]
            #print("SM ", sm )
            if 'BKN' in each:
                bkn = (re.search("BKN", each)).span()[1]
                bkn = int(each[bkn:bkn+4])*100
                bkn_.append(bkn)
            if 'OVC' in each:
                ovc = (re.search("OVC", each)).span()[1]
                ovc = int(each[ovc:ovc+4])*100
                ovc_.append(ovc)
            if 'SKC' in each:
                skc = (re.search("SKC", each)).span()[1]
                skc = int(each[skc:skc+4])*100
                skc_.append(skc)
            if 'SCT' in each:
                sct = (re.search("SCT", each)).span()[1]
                sct = int(each[sct:sct+4])*100
                sct_.append(sct)
            if 'FEW' in each:
                few = (re.search("FEW", each)).span()[1]
                few = int(each[few:few+4])*100
                few_.append(few)
    except:
        print("\nCheck Date!")        
        print("Taf not within start date!")
        sys.exit()

bkn_ = np.array(bkn_)
ovc_ = np.array(ovc_)
skc_ = np.array(skc_)
sct_ = np.array(sct_)
few_ = np.array(few_)

if min((bkn_), (ovc_)) == 0:
    ceiling = 100000000000000000
else:
    ceiling = min(bkn_, ovc_)
hamilton_ceiling = ground_elevation_airport + ceiling
burlington_ceiling = hamilton_ceiling + 100
available_ceiling = burlington_ceiling - regulatory_cloud_ceiling
available_ceiling = available_ceiling - ground_elevation_home

if available_ceiling >= circuit_height:
    print("\nClear for Circuit Height with", available_ceiling[0], "ft available ceiling.")
    print("Statute Miles: ", sm)
    print("Wind: ", wind)
    print("Wind Gust: ", gust)
    print("Heading: ", heading)
    print("Altimeter Setting: ", altimeter)
    print("PA: ", PA)

try:
    heading_corrected = heading+magnetic_direction
except:
    print(taf_split)
    heading = int(input("Heading: "))
    heading_corrected = heading+magnetic_direction

rwys = (np.array(rwys))
rwys_ = np.abs(rwys*10 - heading_corrected)
#print(rwys_)
idx = (np.where(rwys_ == rwys_.min())[0][0])
print("Rwy: ",rwys[idx])

#print(utils.windcomp(wind, rwys[idx], heading_corrected, gust))
print("#########################################")
for i in range(0, len(rwys)):
    print("\nRunway ", rwys[i])
    degrees = rwys[i]*10 - heading_corrected
    
    ### = COS(degree*(PI()/180))*wind
    #gust = 0
    try:
        if gust == 0:
            XWC = wind*np.sin((np.pi/180)*degrees)
            HWC = wind*np.cos((np.pi/180)*degrees)
        else:
            XWC = gust*np.sin((np.pi/180)*degrees)
            HWC = wind*np.cos((np.pi/180)*degrees)
    except:
        gust = int(input("Gust: "))
        wind = int(input("Wind: "))
        if gust == 0:
            XWC = wind*np.sin((np.pi/180)*degrees)
            HWC = wind*np.cos((np.pi/180)*degrees)
        else:
            XWC = gust*np.sin((np.pi/180)*degrees)
            HWC = wind*np.cos((np.pi/180)*degrees)   
     
    HWC = round(HWC, 0)
    XWC = round(XWC, 0)
    print("HWC: {0}, XWC: {1}, Degrees: {2} ".format(HWC, XWC, degrees))

    ################################################
    print("..........................................")
    
    # Import CSV
    gr_ = pd.read_csv('TO_ground_roll_PA.txt', delimiter="\t")
    gr50_ = pd.read_csv('TO_50feet_PA.txt', delimiter="\t")
    land_ = pd.read_csv('Landing_ground_roll_PA.txt', delimiter="\t")
    land50_ = pd.read_csv('Landing_50feet_PA.txt', delimiter="\t")
    aerodomes = pd.read_csv('aerodomes.txt', delimiter="\t")
    
    # Create Dataframes
    df_gr = pd.DataFrame(gr_)
    df50_gr = pd.DataFrame(gr50_)
    df_land = pd.DataFrame(land_)
    df50_landgr = pd.DataFrame(land50_)
    df_aerodomes = pd.DataFrame(aerodomes)
    
    groundRoll_TO = utils.wind_comps(df_gr, temperature, PA, HWC, XWC, 0.15)
    ft50_TO = utils.wind_comps(df50_gr, temperature, PA, HWC, XWC, 0.15)
    
    groundRoll_land = utils.wind_comps(df_land, temperature, PA, HWC, XWC, 0.45)
    ft50_land = utils.wind_comps(df50_landgr, temperature, PA, HWC, XWC, 0.45)
    
    utils.solo(rwys[i], wind, HWC, XWC, PA, temperature, groundRoll_TO[2], ft50_TO[2], groundRoll_land[2], ft50_land[2], groundRoll_TO[3], ft50_TO[3], groundRoll_land[3], ft50_land[3])