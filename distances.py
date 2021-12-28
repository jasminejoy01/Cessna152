import utils
import re
from datetime import date
import numpy as np
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")


taf = '''
FM281700 27008KT P6SM BKN160 OVC200
FM282200 VRB03KT P6SM OVC120
FM290100 06005KT 4SM -SN OVC040
FM290300 05010KT 2SM -SN BKN005 OVC030
FM290600 05015KT 1 1/2SM -FZDZ -SN BR OVC004
'''

metar = '''
METAR CZBA 281416Z AUTO 26017G29KT 8SM OVC029 02/M03 A2984 RMK ADVISORY ONLY=
'''
##### Constants - Airport Specific ######
validGuess = False
day = int(input("Date of Search: ")) 
while validGuess is False:
    mth = date.today().month
    yr = date.today().year
    if mth in (1, 3, 5, 7, 8, 10, 12):
        if day > 31 or day < 1:
            day = int(input("Out of Range! Date of Search: "))
        else:
            validGuess = True
    elif mth in (4, 6, 9, 11):
        if day > 30 or day < 1:
            day = int(input("Out of Range! Date of Search: ")) 
        else:
            validGuess = True
    elif mth in (2):
        if yr%4 == 0:
            if day > 29 or day < 1:
                day = int(input("Out of Range! Date of Search: ")) 
            else:
                validGuess = True
        else:
            if day > 28 or day < 1:
                day = int(input("Out of Range! Date of Search: ")) 
            else:
                validGuess = True
    
day = int(day)

## Aerodome Info
aerodomes = pd.read_csv('aerodomes.txt', delimiter="\t")
df_aerodomes = pd.DataFrame(aerodomes)

#ref_airport = input("Reference Airport: ")
ref_airport = 'CYHM'
#home_airport = input("Home Airport: ")
home_airport = 'CZBA'
select = df_aerodomes.loc[df_aerodomes['aerodome'] == ref_airport]
home = df_aerodomes.loc[df_aerodomes['aerodome'] == home_airport]
print("Home Airport: {0} ({1})\nReference Airport: {2} ({3})".format(home['Description'].values[0], home_airport, select['Description'].values[0], ref_airport))

ground_elevation_home = int(home['ground_elevation_ft'].values[0]) #603
ground_elevation_airport = int(select['ground_elevation_ft'].values[0]) #800
magnetic_direction = int(home['variation'].values[0])
direction = home['var_dir'].values[0]
rwys = home['Rwys'].values[0] #[32, 14, 27, 9]
rwys = utils.tolist(rwys)
rwys_len = home['RwyLength'].values[0] #[3950, 3950, 2464, 2464]
rwys_len = utils.tolist(rwys_len)
rwys_displacement =  home['Displacement'].values[0] #[409, 181, 254, 328]
rwys_displacement = utils.tolist(rwys_displacement)

magnetic_direction_airport = select['variation'].values[0]
direction_airport = select['var_dir'].values[0]
rwys_airport = select['Rwys'].values[0]
rwys_airport = utils.tolist(rwys_airport)
rwys_len_airport = select['RwyLength'].values[0]
rwys_len_airport = utils.tolist(rwys_len_airport)
rwys_displacement_airport =  select['Displacement'].values[0]
rwys_displacement_airport = utils.tolist(rwys_displacement_airport)

#########################################

taf_split = taf.split("\n")
timeframe = utils.time_input()
start = timeframe[0]
end = timeframe[1]
regulatory_cloud_ceiling = 500
circuit_height = ground_elevation_home + 500

#year = date.today().year
#month = date.today().month

date = (day*100+start.hour)*100
temp = utils.temperature(metar)
temperature = temp[0]
dewpoint = temp[1]

cloudbase = utils.cloudBase(temperature, dewpoint, 'C')
cloudbase_ham = cloudbase + ground_elevation_airport
print("Cloud Base: ", cloudbase_ham," ASL")
available_ceiling = cloudbase_ham - ground_elevation_home
print("Available Ceiling: ", available_ceiling)
if available_ceiling < circuit_height :
    print("\nWARNING! Available Ceiling is lower than circuit height.")
    input("Press Enter to continue...")

altimeter = utils.altimeter(metar)
PA = round(ground_elevation_home + ((29.92 - altimeter)*1000),2)

# Import CSV
gr_ = pd.read_csv('TO_ground_roll_PA.txt', delimiter="\t")
gr50_ = pd.read_csv('TO_50feet_PA.txt', delimiter="\t")
land_ = pd.read_csv('Landing_ground_roll_PA.txt', delimiter="\t")
land50_ = pd.read_csv('Landing_50feet_PA.txt', delimiter="\t")

# Create Dataframes
df_gr = pd.DataFrame(gr_)
df50_gr = pd.DataFrame(gr50_)
df_land = pd.DataFrame(land_)
df50_landgr = pd.DataFrame(land50_)

lst = []
for each in taf_split:
    if 'TAF' in each and 'Z ' in each:
        each = each.replace("Z", "")
        line0 = (each.split(" ")[2])
        print(line0)
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
    elif 'TEMPO' in each:
        print(line0)
        idx = ((re.search("/", each)).span()[1])
        start = each[idx-5: idx-1]
        start_date = start[:2]
        start_hour = start[-2:]+"00"
        end = each[idx: idx+4]
        end_date = end[:2]
        end_hour = start[-2:]+"00"
        new_input = start_date+start_hour
        lst.append(new_input)

#print(lst)
lst = [x for x in lst if isinstance(x, int)]
i = 0
while i < (len(lst)-1):
    #print(date , int(lst[i]),  int(lst[i+1]))
    if len(lst) == 0:
        print("lst is empty!")
        input("Press Enter to continue...")
    else:
        if date >= int(lst[i]) and date < int(lst[i+1]) :
            note = lst[i]
            print(note)
    i = i + 1

bkn_ = []
ovc_ = []
skc_ = []
sct_ = []
few_ = []

#lst = [261140]
for each in taf_split:
    if len(lst) == 1:
        note = lst[0]
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
        print(lst)
        ## update value
        #sys.exit()

bkn_ = np.array(bkn_)
ovc_ = np.array(ovc_)
skc_ = np.array(skc_)
sct_ = np.array(sct_)
few_ = np.array(few_)

if min((bkn_), (ovc_)) == 0:
    ceiling = 1000000000
else:
    ceiling = min(bkn_, ovc_)
hamilton_ceiling = ground_elevation_airport + ceiling
burlington_ceiling = hamilton_ceiling + 100
available_ceiling = burlington_ceiling - regulatory_cloud_ceiling
available_ceiling = available_ceiling - ground_elevation_home

choose = (input("metar or taf?")).lower()
if choose == 'metar':
    print(metar)
    output = utils.knots_KT(metar)
    heading = output[0]
    wind = output[1]
    gust = output[2]
  
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
    #print(taf_split)
    heading = int(input("Heading: "))
    heading_corrected = heading+magnetic_direction

rwys = (np.array(rwys))
rwys_ = np.abs(rwys*10 - heading_corrected)
#print(rwys_)
idx = (np.where(rwys_ == rwys_.min())[0][0])
print("Rwy: ",rwys[idx])

#print(utils.windcomp(wind, rwys[idx], heading_corrected, gust))
rwy_usable = np.array(rwys_len) - np.array(rwys_displacement)
#print("#########################################")
for i in range(0, len(rwys)):
    print("..............................................................................")
    print("\nRunway ", rwys[i], " Runway Length:", rwys_len[i])
    print("Usable Runway Length (for Landing): ", rwy_usable[i])
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
        
    groundRoll_TO = utils.wind_comps(df_gr, temperature, PA, HWC, XWC, 0.15)
    ft50_TO = utils.wind_comps(df50_gr, temperature, PA, HWC, XWC, 0.15)
    
    groundRoll_land = utils.wind_comps(df_land, temperature, PA, HWC, XWC, 0.45)
    ft50_land = utils.wind_comps(df50_landgr, temperature, PA, HWC, XWC, 0.45)
    
    utils.solo(rwys[i], wind, HWC, XWC, PA, temperature, groundRoll_TO[2], ft50_TO[2], groundRoll_land[2], ft50_land[2], groundRoll_TO[3], ft50_TO[3], groundRoll_land[3], ft50_land[3] )