# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 21:30:18 2021

@author: jasmi
"""
import replit
replit.clear()

import os
os.system('clear')

import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import weather
#import re
import warnings
warnings.filterwarnings('ignore')

'''User Input '''
#airport = 'CYHM'
airport = input('Airport (CYHM, CFC8):')
turf = 'soft'
print()

taf = '''TAF AMD CYHM 120831Z 1208/1306 26012G22KT P6SM BKN040 BKN080 TEMPO
1208/1210 5SM BR BKN008 OVC012 PROB30 1208/1210 2SM -DZ BR
OVC005
FM121000 25012G22KT P6SM SCT020
FM121300 24012G22KT P6SM FEW025
FM121800 22012G22KT P6SM -SHRA SCT020 BKN040
BECMG 1222/1224 22012KT
FM130500 25010KT P6SM SCT050'''

metar = '''METAR CYHM 121100Z 23009KT 12SM FEW015 FEW250 06/05 A2982 RMK SC1CI1 SLP104=
'''
string = '''
FM121000 25012G22KT P6SM SCT020
FM121300 24012G22KT P6SM FEW025
'''

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

''' Aerodomes '''
def _airport(name):
    for index, row in df_aerodomes.iterrows():
        if row['aerodome'] == name:
            print( row['Description'])
            rwy = (row['Rwys'])
            ground_elev = row['ground_elevation_ft']
            var = row['variation']
            var_dir = row['var_dir']
            rwy_disp = (row['Displacement'])
            rwy_len = (row['RwyLength'])
            if row['RwyType'] != 'asphalt':
                rwy_type = 'soft'
            else:
                rwy_type = 'asphalt'
    print(rwy, ground_elev, var, var_dir, rwy_type, rwy_disp, rwy_len, "\n")
    return rwy, ground_elev, var, var_dir, rwy_type, rwy_disp, rwy_len

#aerodome	ground_elevation_ft	variation	var_dir	Description	RwyType	Rwys	Displacement	RwyLength
aerodome_values = _airport(airport)
ground_elevation = int(aerodome_values[1])
#turf = aerodome_values[4]
rwys = aerodome_values[0]
rwy_len = aerodome_values[-1]
rwy_disp = aerodome_values[-2]
if aerodome_values[3] == 'W':
    variation = round(int(aerodome_values[2]), 2)
elif aerodome_values[3] == 'E':
    variation = -1*round(int(aerodome_values[2]), 2)

#print(ground_elevation, turf)

class Calculation:
    def __init__(self, pa = None,  temperature = None, df = None):
        self.pa = pa
        self.max_val = df.shape[-1]
        self.temperature = temperature
        self.df = df
        self.x_val = df['PA__']
    
    def calculate(self):
        # Lists
        gr_temp = []
                
        # Process
        i = 1
        while i < self.max_val:
            j = (i-1)*10
            #print(i-1, j)
            Y = (self.df[str(j)])
            #print(Y)
            #print(self.x_val)
            #plt.plot(X, Y)
            fit = (np.polyfit(self.x_val, Y, 2, False))
            #print(fit)
            a = fit[0]
            b = fit[1] 
            c = fit[2]
            #print(a, b, c)
            temp = (a*np.power(self.pa,2) + b*self.pa + c)
            #print(temp)
            gr_temp.append(temp)
            i = i + 1
            
        gr_final = np.array(gr_temp) 
        x = (np.arange(0,(self.max_val-1)*10,10))
        #print(x)
        gr_final_fit = (np.polyfit(x, gr_final, 1, False))
        #print(gr_final_fit)
        
        # Final Values
        roll_raw = gr_final_fit[0]*self.temperature+gr_final_fit[1] ## rem: fit quality
        #print(take_off_roll_raw)
        return roll_raw

class WindCorrection:
    def __init__(self, windtype=None , wind=None, gust=None, roll=0):
        self.windtype = windtype
        self.wind = wind
        self.gust = gust
        self.groundroll = roll
    
    def windfactor(self):
        if self.windtype == 'h':
            ## 10 % for 9 knots
            factor = (9/100)*self.wind
            #print(self.windtype, self.wind, self.gust, self.groundroll)
            #factor = self.wind*factor 
            #print(self.groundroll*factor)
            return self.groundroll*factor
    
class Calculations50:
    def __init__(self, roll=0, windcorrected=0 , turf=None, leg=None):
        self.groundroll = roll
        self.turf = turf
        self.leg = leg
        self.windcorrected = windcorrected
        #print(self.groundroll, self.turf ,   self.leg,   self.windcorrected )
        
    def turf_factor(self):
        if self.turf != "asphalt":
            if self.leg == "landing":
                ## 45% add to ground roll
                factor = 0.45*self.groundroll
                turf_correction = factor + self.windcorrected
            elif self.leg == "takeoff":
                ## 15% add to ground roll
                factor = 0.15*self.groundroll
                turf_correction = factor + self.windcorrected
                #print(turf_correction)
        else:
            factor = 0
            turf_correction = factor + self.windcorrected
        return turf_correction
    
#PA = 723.0
#T = 10
#wind = 10
#gust = 20
#ground_elevation = 813
#variation = 10


rwy = np.zeros(len(rwys.split()))
i = 0
for each in rwys.split():
    each = each.replace('[', '')
    each = each.replace(']', '')
    each = each.replace(',', '')
    rwy[i] = int(each)
    i = i + 1

rwylen = np.zeros(len(rwy_len.split()))
i = 0
for each in rwy_len.split():
    #print(each)
    each = each.replace('[', '')
    each = each.replace(']', '')
    each = each.replace(',', '')
    rwylen[i] = int(each)
    i = i + 1

rwydisplacement = np.zeros(len(rwy_len.split()))
i = 0
for each in rwy_disp.split():
    #print(each)
    #each = each.replace(each,"[" )
    each = each.replace('[', '')
    each = each.replace(']', '')
    each = each.replace(',', '')
    rwydisplacement[i] = int(each)
    i = i + 1

weather.note_Z(taf, 0)

altimeter = (int(weather.altimeter(metar))/100)
PA = round(ground_elevation + ((29.92 - altimeter)*1000),2)
print("PA: ", PA,"\n")

knots = weather.knots_KT(string)
direction = int(knots[0])
wind = int(knots[1])
gust = int(knots[-1])
magnetic_dir = direction+variation
print("Magnetic: ", magnetic_dir, wind, gust)

rwy_calc = np.abs(rwy*10 - magnetic_dir)
print(rwy*10, rwy_calc, min(rwy_calc))

result = np.where(rwy_calc == min(rwy_calc))
idx = (result[0][0])
print(rwy[idx])

temp_dewpt = weather.temperature(metar)
print(temp_dewpt, "\n")
T = int(temp_dewpt[0])
#print(T)

''' T.O. Ground Roll '''
print("Use Rwy {0} of length {1} with displacement of {2} \n".format(rwy[idx],rwylen[idx], rwydisplacement[idx]))

TO_ground_roll = Calculation(PA, T, df_gr)
TO_groundroll = round(TO_ground_roll.calculate(), 0)

TO_WindCorrection = WindCorrection('h', wind, gust, TO_groundroll)
TO_windcorrected = round((TO_WindCorrection.windfactor()), 0)

TO_Calculation50 = Calculations50(TO_groundroll, TO_windcorrected, turf, 'takeoff')
TO_Calculation50 = round(TO_Calculation50.turf_factor(), 0)
#print(TO_groundroll, TO_windcorrected, TO_Calculation50)

''' T.O. 50 Feet '''
TO_50 = Calculation(PA, T, df50_landgr)
TO50 = round(TO_50.calculate(), 0)

TO50_WindCorrection = WindCorrection('h', wind, gust, TO50)
TO50_wind = round((TO50_WindCorrection.windfactor()), 0)

TO50_Calculation = Calculations50(TO_windcorrected, TO50_wind, turf, 'takeoff')
TO50_Calculation = round(TO50_Calculation.turf_factor(), 0)
#print(TO50, TO50_wind, TO50_Calculation)

''' landing Ground Roll '''
Land_ground_roll = Calculation(PA, T, df_land)
Land_groundroll = round(Land_ground_roll.calculate(), 0)

Land_WindCorrection = WindCorrection('h', wind, gust, Land_groundroll)
Land_windcorrected = round((Land_WindCorrection.windfactor()), 0)

Land_Calculation50 = Calculations50(Land_groundroll, Land_windcorrected, turf, 'landing')
Land_Calculation50 = round(Land_Calculation50.turf_factor(), 0)
#print(Land_groundroll, Land_windcorrected, Land_Calculation50)

''' landing 50 Feet'''
Land_50 = Calculation(PA, T, df50_landgr)
Land50 = round(Land_50.calculate(), 0)

Land50_WindCorrection = WindCorrection('h', wind, gust, Land50)
Land50_wind = round((Land50_WindCorrection.windfactor()), 0)

Land50_Calculation = Calculations50(Land_windcorrected, Land50_wind, turf, 'landing')
Land50_Calculation = round(Land50_Calculation.turf_factor(), 0)
#print(Land50, Land50_wind, Land50_Calculation)

"Output"
print("TO Ground Roll: {0} \nTO 50': {1} ".format(TO_Calculation50, TO50_Calculation)) 
print("Landing Ground Roll: {0} \nLanding 50': {1} ".format(Land_Calculation50, Land50_Calculation)) 

print("\n ------------ End of Report ------------- \n")

