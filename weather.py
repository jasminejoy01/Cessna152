# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 01:43:30 2021

@author: jasmi
"""


import re

# taf = '''TAF CYHM 120541Z 18012KT P6SM -RA SCT008 OVC040 TEMPO
# 1206/1208 3SM -RA BR BKN007 OVC015 PROB30 1206/1208 2SM RA BR
# OVC004
# FM120800 24010G20KT 5SM -SHRA BR SCT004 OVC025 TEMPO 1208/1210
# 3SM BR BKN008 OVC012 PROB30 1208/1210 2SM -DZ BR OVC005
# FM121000 22012KT P6SM SCT020
# FM121300 24012G22KT P6SM FEW025
# FM121800 22012G22KT P6SM -SHRA SCT020 BKN040
# BECMG 1222/1224 22012KT'''

#metar = '''METAR CYHM 120600Z 24009KT 15SM -RA OVC043 12/11 A2970 RMK SC8 SLP060 DENSITY ALT 900FT='''

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
    temperature = (df[temp[0][0] - 2 : temp[0][0] ])
    dewpoint = (df[temp[0][1] :temp[0][1] +2 ])
    print("\nTemperature {0}, Dewpoint {1}.".format(temperature, dewpoint))
    return temperature, dewpoint

def altimeter(df):
    temp = [(m.start(0), m.end(0)) for m in re.finditer(" A", df)]
    for each in temp:
        string = (df[each[1]:each[1]+5]).strip()
        if " " in string:
            pass
        else:
            print("\nAltimeter Setting {0}.".format(string))
            return string

#(note_Z(taf, 0))
# (note_Z(metar,0))
# print('\n')
#string = '''FM121000 22012KT P6SM SCT020
# FM121300 24012G22KT P6SM FEW025
# '''
#knots_KT(string)
# temperature(metar)
# altimeter(metar)