# LoRa-Power-Consumption-Simulator
A Semtech SX1276 LoRa Module model to simulate its power-consumption behavior

SEMTECH SX1267 LoRa Power Model Usage:  `power_model_script.py [options] [value] `

> Options: 
>
>    **-s, --startup**
>>Include Startup? If False startup not included. Else, startup included. 
>
>   **-v, --vcc**
>>Power is enabled during sleep mode? If 'ON' sleep mode is 0A current consumption. If 'OFF', the module is enabled in ultra-low-power mode. 
>
>    **-r, --rfo**
>>Power of antenna power mode: If 'RFO', RFO mode enabled [0 to 14dBm]. If 'PABOOST', PA_BOOST enabled [2 to 20dBm]. Only accepts natural input. 
>
>    **-x, -power**
>>Antenna Power output [dBm]: If rfo = PABOOST, only accepts from 2 to 20 dBm. If rfo = RFO, only accepts from 0 to 14 dBm. 
>
 >   **-d, --DRin**
 >>Data Rate input [bps]: Number of data in bits per second which enters to the system to send by LoRa module. Max = 10bps. 
>
 >   **-t,-T --T**
 >>Period of sending [min]. Time between 2 sending routines. Only accepts natural number input. 
>
 >   **-b, --Bytes**
 >>Number of bytes per packet. Only accepts a natural input. 



If no value is set, it will catch default params: 
>
> startup = True 
>
> vcc = True 
>
> rfo = True 
>
> x = 0 dBm 
>
> DRin = 10 bps 
>
> T = 15 min 
>
> b = 222 bytes 



For more information about SEMTECH SX1267 LoRa module, please refer to it's datasheet.



------------------------------------------------------------------------------------------------------

FOXES is a project funded  by the European Union’s Horizon 2020 Research and Innovation Programme, under grant agreement Nr. 951774. 



Universitat de Barcelona   -   Developed by Enric Puigvert Coromina 

https://www.foxes-project.eu/ 

------------------------------------------------------------------------------------------------------
