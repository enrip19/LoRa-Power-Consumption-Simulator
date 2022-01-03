# Functional power model. To use it read readme.md file

# IMPORTS
# File managing
import glob
import csv
import os
import gc

from IPython import get_ipython

# Arguments parser
import sys
import getopt
from distutils.util import strtobool

# Math and data analysis
import numpy as np
import sklearn.metrics as sk

# Signal processing
import scipy as scy
import scipy.signal as sig
import scipy.ndimage as ndimg

# Variable managing
from uncertainties import ufloat
from uncertainties.umath import *

# Execution control
import papermill as pm
import pickle

# Tables formatter
import pandas as pd

# Plot
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.lines import Line2D
from matplotlib.ticker import (
    MultipleLocator, FormatStrFormatter, AutoMinorLocator, EngFormatter)

r_folder = './../vars/'
w_folder = './../results/' 

startup = True
vcc = True
val_vcc = 'on'
rfo = True
val_rfo = 'rfo'
x = 0 #dBm
DRin = 10 #bps
T_val = 15 #min
bytes_packet = 222  # [bytes] --- bytes per packet

# command parser
argv = sys.argv[1:]
# print(argv) # debugging
error_msg = "SEMTECH SX1267 LoRa Power Model Usage: \n\n power_model_script.py [options] [value]  \n \nOptions: \n-s, --startup  \t\t Include Startup? If False startup not included. Else, startup included. \n-v, --vcc \t\t Power is enabled during sleep mode? If 'ON' sleep mode is 0A current consumption. If 'OFF', the module is enabled in ultra-low-power mode. \n-r, --rfo \t\t Power of antenna power mode: If 'RFO', RFO mode enabled [0 to 14dBm]. If 'PABOOST', PA_BOOST enabled [2 to 20dBm]. Only accepts natural input. \n-x, -power \t\t Antenna Power output [dBm]: If rfo = PABOOST, only accepts from 2 to 20 dBm. If rfo = RFO, only accepts from 0 to 14 dBm. \n-d, --DRin \t\t Data Rate input [bps]: Number of data in bits per second which enters to the system to send by LoRa module. Max = 10bps. \n-t,-T --T \t\t Period of sending [min]. Time between 2 sending routines. Only accepts natural number input. \n-b, --Bytes \t\t Number of bytes per packet. Only accepts a natural input. \n\nIf no parameter is set, it will catch default params: \n startup = True \n vcc = True \n rfo = True \n x = 0 dBm \n DRin = 10 bps \n T = 15 min \n b = 222 bytes \n\nFor more information about SEMTECH SX1267 LoRa module, please refer to it's datasheet.\n\n------------------------------------------------------------------------------------------------------\nFOXES is a project funded  by the European Union’s Horizon 2020 Research and Innovation Programme, under grant agreement Nr. 951774. \n\nUniversitat de Barcelona  \nhttps://www.foxes-project.eu/ \n------------------------------------------------------------------------------------------------------"
try:
    options, args = getopt.getopt(argv, 's:v:r:x:d:t:T:b:h:',['startup=','vcc=','rfo=','power=','DRin=','T=', 'Bytes=''help='])

    for name, value in options:
        if name in ['-h','--help']:
            print('hola')
            print(error_msg)
            # sys.exit(2)
        elif name in ['-s', '--startup']:
            startup = bool(strtobool(value))
            # print('startup:',startup)
        elif name in ['-v','--vcc']:
            val_vcc = value.lower()
            if(val_vcc == 'on'): 
                vcc = True
                # print('vcc:', val_vcc.upper() ,'(',vcc,')')
            elif (val_vcc == 'off'): 
                vcc = False
                # print('vcc:', val_vcc.upper() ,'(',vcc,')')
            else:
                print('### ERROR: Please answer on or off. Please check help below ### \n\n\n')
                sys.exit()
        elif name in ['-r','--rfo']:
            val_rfo = value.lower()
            if(val_rfo == 'paboost' or val_rfo == 'pa_boost'):
                rfo = False
                # print('rfo:', val_rfo.upper() ,'(',rfo,')')
            elif(val_rfo == 'rfo' or val_rfo == 'rfo'):
                rfo = True
                # print('vcc:', val_rfo.upper() ,'(',vcc,')')
            else:
                print('### ERROR: Please answer paboost or rfo. Please check help below ### \n\n\n')
                sys.exit()
            # print('rfo:', rfo)
        elif name in ['-x','--power']:
            val = int(value)
            if(rfo == False):
                if(val<2 or val>20):
                    print('### ERROR: Power is not in PABOOST range. Please check help below ### \n\n\n')
                    sys.exit()
                else:
                    x = val
                    # print('x: ',x)
            else:
                if(val<0 or val>14):
                    print('### ERROR: Power is not in PABOOST range. Please check help below ### \n\n\n')
                    sys.exit()
                else:
                    x = val
                    # print('x: ',x)
        elif name in ['-d','--DRin']:
            val = float(value)
            if(val<=10):
                DRin = val
                # print('DRin:',DRin)
            else:
                print('### ERROR: DRin exceed max value. Please check help below. ### \n\n\n')
                sys.exit()
        elif name in ['-t','-T','--T']:
            T_val = int(value)
            # print('T:',T_val)
            
except Exception as e:
    # print(e)
    print(error_msg)
    sys.exit()
# except 
    
# print(startup, vcc, rfo)
# Reading data
#Startup
t_startup = pickle.load(open(r_folder + 't_startup','rb'))
i_startup = pickle.load(open(r_folder + 'i_startup','rb'))

t_rx = pickle.load(open(r_folder + 't_rx','rb'))
i_rx = pickle.load(open(r_folder + 'i_rx','rb'))

t_tx_start_paboost = pickle.load(open(r_folder + 't_tx_start_paboost','rb'))
i_tx_start_paboost = pickle.load(open(r_folder + 'i_tx_start_paboost','rb'))

t_tx_start_rfo = pickle.load(open(r_folder + 't_tx_start_rfo','rb'))
i_tx_start_rfo = pickle.load(open(r_folder + 'i_tx_start_rfo','rb'))

t_tx_peak_paboost = pickle.load(open(r_folder + 't_tx_peak_paboost','rb'))
t_tx_peak_rfo = pickle.load(open(r_folder + 't_tx_peak_rfo','rb'))

t_tx_wait_paboost = pickle.load(open(r_folder + 't_tx_wait_paboost','rb'))
i_tx_wait_paboost = pickle.load(open(r_folder + 'i_tx_wait_paboost','rb'))

t_tx_wait_rfo = pickle.load(open(r_folder + 't_tx_wait_rfo','rb'))
i_tx_wait_rfo = pickle.load(open(r_folder + 'i_tx_wait_rfo','rb'))

fTrend_txPeak_paboost_best = pickle.load(open(r_folder + 'fTrend_txPeak_paboost_best','rb'))
fTrend_txPeak_paboost_center = pickle.load(open(r_folder + 'fTrend_txPeak_paboost_center','rb'))
fTrend_txPeak_paboost_worst = pickle.load(open(r_folder + 'fTrend_txPeak_paboost_worst','rb'))

fTrend_txPeak_rfo_best = pickle.load(open(r_folder + 'fTrend_txPeak_rfo_best','rb'))
fTrend_txPeak_rfo_center = pickle.load(open(r_folder + 'fTrend_txPeak_rfo_center','rb'))
fTrend_txPeak_rfo_worst = pickle.load(open(r_folder + 'fTrend_txPeak_rfo_worst','rb'))

# Variable definition
points = 1000000  # number of points for the simulation

bits_packet = bytes_packet*8  # [bits] --- Numero de bits per packet

print('STARTING SIMULATION...')
if(vcc == False):
    vcc_mode_case = 'VccOFF'
else:
    vcc_mode_case = 'VccON'

# Times and intensity definitions 
## SLEEP ##
# t_sleep will be calculated in function of period of sending
if(vcc == False):
    i_sleep = 0
else:
    i_sleep = 1.7715347532000003E-05 #[A] It is hardcoded because it was measured by 1000 iteration averaging method to avoid measurement noise

pickle.dump(i_sleep, open("./../vars/i_sleep",'wb'))

## STARTUP ##
# t_startup is constant, so variable is already generated
if(startup == False):
    i_startup = 0

## TX ##
### tx start ###
if(rfo==False):
    t_tx_start = t_tx_start_paboost
    i_tx_start = i_tx_start_paboost
else:
    t_tx_start = t_tx_start_rfo
    i_tx_start = i_tx_start_rfo

### tx peak ###
if(rfo == False):
    t_tx_peak = t_tx_peak_paboost
    i_tx_peak = fTrend_txPeak_paboost_center
    i_tx_peak_best = fTrend_txPeak_paboost_best
    i_tx_peak_worst = fTrend_txPeak_paboost_worst
else:
    t_tx_peak = t_tx_peak_rfo
    i_tx_peak = fTrend_txPeak_rfo_center
    i_tx_peak_best = fTrend_txPeak_rfo_best
    i_tx_peak_worst = fTrend_txPeak_rfo_worst

### tx wait ###
if(rfo == False):
    t_tx_wait = t_tx_wait_paboost
    i_tx_wait = i_tx_wait_paboost
else:
    t_tx_wait = t_tx_wait_rfo
    i_tx_wait = i_tx_wait_rfo

# Power Model
time_sleep_min = T_val  # sleep time [min] = sending period
time_sleep = time_sleep_min * 60  # conversion to seconds

time_sim = time_sleep + 60 # give to simulation time 60secs more for ensuring to not overflow arrays

dataRate_in = DRin  # [bits/seconds] --- Data Rate input
seconds_packet = bits_packet/dataRate_in  # [seconds/packet]

packet_count = time_sleep/seconds_packet # [packets] --- number of packets calculation

k_packets = int(np.ceil(packet_count)) # [packets] --- rounding number of packets (all packets are same length)

# calculation of t_sleep
t_sleep = time_sleep


# calculation of full tx
i_tx = (i_tx_start*t_tx_start + (i_tx_peak(x)*t_tx_peak + i_tx_wait*t_tx_wait)* k_packets)*(((t_tx_start + (t_tx_peak + t_tx_wait)*k_packets))**(-1))
i_tx_best = (i_tx_start*t_tx_start + (i_tx_peak_best(x)*t_tx_peak + i_tx_wait*t_tx_wait)* k_packets)*(((t_tx_start + (t_tx_peak + t_tx_wait)*k_packets))**(-1))
i_tx_worst = (i_tx_start*t_tx_start + (i_tx_peak_worst(x)*t_tx_peak + i_tx_wait*t_tx_wait)* k_packets)*(((t_tx_start + (t_tx_peak + t_tx_wait)*k_packets))**(-1))
t_tx = (t_tx_start + (t_tx_peak + t_tx_wait)*k_packets)


# Power calculation from intensity
p_startup = i_startup*3.3
p_rx = i_rx*3.3
p_sleep = i_sleep*3.3
p_tx = i_tx*3.3
p_tx_best = i_tx_best*3.3
p_tx_worst = i_tx_worst*3.3

# Power Calculation
power = (p_startup*t_startup + p_tx*t_tx + p_rx*t_rx + p_sleep*t_sleep) * (((t_startup + t_tx + t_rx + t_sleep))**(-1))
power_best = (p_startup*t_startup + p_tx_best*t_tx + p_rx*t_rx + p_sleep*t_sleep) * (((t_startup + t_tx + t_rx + t_sleep))**(-1))
power_worst = (p_startup*t_startup + p_tx_worst*t_tx + p_rx*t_rx + p_sleep*t_sleep) * (((t_startup + t_tx + t_rx + t_sleep))**(-1))

# Saving data 
if not os.path.exists(w_folder):
    os.makedirs(w_folder)
    print("Results folder missing. Created")
    
pickle.dump(power, open(w_folder + "power", "wb"))
pickle.dump(power_best, open(w_folder + "power_best", "wb"))
pickle.dump(power_worst, open(w_folder + "power_worst", "wb"))

pow_formatter = EngFormatter(unit='')

pow_format =  pow_formatter(power.nominal_value)
pow_best_format =  pow_formatter(power_best.nominal_value)
pow_worst_format =  pow_formatter(power_worst.nominal_value)


if(pow_format[-1] == 'µ'): 
    std_format = power.std_dev * 100000
    std_best_format = power_best.std_dev * 100000
    std_worst_format = power_worst.std_dev * 100000
elif(pow_format[-1] == 'm'): 
    std_format = power.std_dev * 1000
    std_best_format = power_best.std_dev * 100
    std_worst_format = power_worst.std_dev * 100
else: 
    std_format = power.std_dev
    std_best_format = power_best.std_dev
    std_worst_format = power_worst.std_dev

print('\nSimulation conditions: \n \tStartup\t\t= ', startup, ' \n\tVcc\t\t= ', val_vcc.upper(), ' \n\tMode\t\t= ', val_rfo.upper(), '\n\tAntenna power\t= ', x, ' \n\tDRin\t\t= ', DRin, '\n\tT\t\t= ', T_val, ' \n\tBytes/packet\t= ', bytes_packet,'\n')
print('-------------------------------------------------- RESULTS ---------------------------------------------------')
print('Power: (', pow_formatter(power.nominal_value)[:-1], '+/-', round(std_format,4),')', pow_format[-1]+'W')
print('Best case power: (', pow_formatter(power_best.nominal_value)[:-1], '+/-', round(std_best_format,4),')', pow_format[-1]+'W')
print('Worst case power: (', pow_formatter(power_worst.nominal_value)[:-1],'+/-', round(std_worst_format,4),')', pow_format[-1]+'W')
print('--------------------------------------------------------------------------------------------------------------')