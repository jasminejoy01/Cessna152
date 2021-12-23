# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 20:56:07 2021

@author: jasmi
"""
import re
import time
import datetime
from datetime import date
import numpy as np

def convert(hour, minute, am):
    if am == 'PM':
        hour = hour + 12
        minute = minute + 12
    return hour, minute
 
def time_input():
    year = date.today().year
    month = date.today().month
    day = date.today().day
    zulu = 5
            
    start_hour = int(input("Start Hour: ")) 
    start_min = int(input("Start Minute: "))
    start_am = int(input("AM? If yes, type 1, else 0: "))
    
    end_hour = int(input("End Hour: ")) 
    end_min = int(input("End Minute: "))
    end_am = int(input("AM? If yes, type 1, else 0: "))
    
    starttime = convert(start_hour, start_min, start_am)
    startH = starttime[0] + zulu
    startM = starttime[1]
    endtime = convert(end_hour, end_min, end_am)
    endH = endtime[0] + zulu
    endM = endtime[1]
    
    print("----------------------------------")
    start = datetime.time(startH, startM, 0, 0)
    print("start =", start)
    
    end = datetime.time(endH, endM, 0, 0)
    print("end =", end)
    print("----------------------------------")
    return start, end
   
def solo(rwy, wind, hwind, xwind, pa, t, to_grd_roll, to_50, land_grd_roll, land_50,to_grd_roll_soft, to_50_soft, land_grd_roll_soft, land_50_soft):
    print("\nNormal\n------")
    print("Rwy\t Wind\t Hwind\t XWind\t PA\t T\t T.O.Grd.Roll\t T.O.50'\t Ldg.Grd.Roll\t Ldg.50'")
    print("{0}\t {1}\t {2}\t {3}\t {4}\t {5}\t {6}\t {7}\t {8}\t {9}".format(rwy, wind, hwind, xwind, pa, t, to_grd_roll, to_50, land_grd_roll, land_50))
    
    print("Soft Field\n----------")
    print("Rwy\t Wind\t Hwind\t XWind\t PA\t T\t T.O.Grd.Roll\t T.O.50'\t Ldg.Grd.Roll\t Ldg.50'")
    print("{0}\t {1}\t {2}\t {3}\t {4}\t {5}\t {6}\t {7}\t {8}\t {9}".format(rwy, wind, hwind, xwind, pa, t, to_grd_roll_soft, to_50_soft, land_grd_roll_soft, land_50_soft))

def note_Z(df, DST):
    df_name = df.split(" ")[0]
    time = [(m.start(0), m.end(0)) for m in re.finditer("Z", df)]
    fromtime = [(m.start(0), m.end(0)) for m in re.finditer("FM", df)]
    #print(time)
    
    for each in time:
        zulu = (df[each[0]-7:each[1]]).strip()
        if " " in zulu:
            pass
        else:
            taf_time = (zulu)
            taf_time = taf_time[:len(taf_time)-1]
            day = taf_time[:2]
            hour_UTC = taf_time[2:4]
            min_UTC = taf_time[4:]
            if DST == 0 :
                hour_ET = str(int(hour_UTC) - 4)
            elif DST == 1:
                hour_ET = str(int(hour_UTC) - 5)
            minute_ET = min_UTC
        print("{0} Date {1}, {2}UTC, Time ET {3}:{4} hours.".format(df_name, day, taf_time, hour_ET, minute_ET))
        #return taf_time, day, hour_UTC, hour_ET, min_UTC
            
    for each in fromtime:
        FM = (df[each[0]+2:each[1]+7]).strip()
        day = FM[:2]
        hour_UTC = FM[2:4]
        min_UTC = FM[4:]
        #print(FM, day, hour_UTC, min_UTC)
        if DST == 0 :
            hour_ET = str(int(hour_UTC) - 4)
        elif DST == 1:
            hour_ET = str(int(hour_UTC) - 5)
            minute_ET = min_UTC
        print("{0} Date {1}, {2}UTC, Time ET {3}:{4} hours.".format(df_name, day, FM, hour_ET, minute_ET))

def knots_KT(df):
    KT = [(m.start(0), m.end(0)) for m in re.finditer("KT", df)]
    #print(time)
        
    for each in KT:
        string = df[each[0]-8: each[1]]
        if 'G' in string:
            G = [(m.start(0), m.end(0)) for m in re.finditer("G", string)]
            for value in G:
                gust = (string[value[1]: value[1] + 2])
                wind = (string[:-2])
                direction = (wind[:3])
                wind = (string[value[0]-2:value[0]])
                print("Direction {0}, Wind {1}KT, Gust {2}KT.".format(direction, wind, gust))
        else:
            new_string = (string.split(" ")[-1])
            gust = 0
            wind = (new_string[:-2])
            direction = (wind[:3])
            wind = (string[value[0]-2:value[0]])
            print("Direction {0}, Wind {1}KT, Gust {2}KT.".format(direction, wind, gust))
        return direction, wind, gust
       
def temperature(df):
    temp = [(m.start(0), m.end(0)) for m in re.finditer("/", df)]
    temperature = (df[temp[0][0] - 3 : temp[0][0] ])
    if 'M' in temperature:
        temperature =  temperature.replace('M', '')
        temperature = -1*int(temperature)
    else:
        temperature = int(temperature)
    dewpoint = (df[temp[0][1] :temp[0][1] +2 ])
    if 'M' in dewpoint:
        dewpoint =  dewpoint.replace('M', '')
        dewpoint = -1*int(dewpoint)
    else:
        dewpoint = int(dewpoint)
    print("\nTemperature {0}, Dewpoint {1}.".format(temperature, dewpoint))
    return temperature, dewpoint

def altimeter(df):
    temp = [(m.start(0), m.end(0)) for m in re.finditer(" A", df)]
    for each in temp:
        string = (df[each[1]:each[1]+5]).strip()
        if " " in string:
            pass
        else:
            string = int(string)/100.0
            print("\nAltimeter: {0}".format(str(string)))
            return string


def wind_comps(datafr, temperature, PA, HWC, XWC, factor):
    data = (list(datafr.columns)[1:])
    data_array = np.zeros(len(data))
    for i in range(0, len(data)):
        data_array[i] = int(data[i])
    
    #print(data_array)
    #print(temperature)
    if temperature <= 0:
        temperature = 0
    
    for i in range(0, len(data_array)):
        if (temperature >= data_array[i]) and (temperature<=data_array[i+1]):
            #print(data[i] ,data[i+1] )
            min_val = data[i] 
            max_val = data[i+1]
            
    dataframe = datafr[[ 'PA__', min_val, max_val]]
    #print(dataframe)
    min_PA = int(round(PA-500, -2))
    max_PA = int(round(PA+500, -2))
    #print(min_PA, max_PA, PA)
    frame = dataframe.query('PA__ >= @min_PA and PA__ <= @max_PA')
    #print(frame)
    
    a = frame[max_val] - frame[min_val]
    b = frame[min_val] + a*(temperature/int(max_val))
    #print(b[1], b[0])
    t_adjust = (b[1] - b[0])
    
    ground_roll = round(b[0] + t_adjust*(PA/max_PA), 0)
    soft_field = round(ground_roll + ground_roll * factor, 0)
    
    wind_correction = round(ground_roll - ground_roll*(((10*HWC)/9)/100), 0)
    soft_wind_correction = round(soft_field - ground_roll*(((10*HWC)/9)/100), 0)
    
    #print(ground_roll, soft_field, wind_correction, soft_wind_correction)
    return ground_roll, soft_field, wind_correction, soft_wind_correction 