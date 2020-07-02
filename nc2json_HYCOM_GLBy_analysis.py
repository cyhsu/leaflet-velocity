import os, sys, json
import numpy as np
import xarray as xr
from glob import glob
from datetime import datetime
from netCDF4 import Dataset, num2date, date2num
from scipy.interpolate import griddata


#- HYCOM GLBv0.08/latest (daily-mean) present + forecast
#- Detail info: https://www.hycom.org/dataserver/gofs-3pt1/analysis
#- Horizontal Resolution 
slice_index = 5 
dx, dy = 0.08 * slice_index, 0.04 * slice_index

link = 'http://tds.hycom.org/thredds/dodsC/GLBy0.08/latest'
df = xr.open_dataset(link, decode_times=False)
df['time'] = num2date(df['time'].data, df['time'].units)

Current_Time = np.datetime64('now','h')
#df = df.sel(time=Current_Time,
df = df.sel(time='2020-07-01T21:00:00',
            lon=slice(None,None,slice_index),
            lat=slice(None,None,slice_index),
           )[['water_u','water_v']].isel(depth=0).squeeze().drop({'depth','time_run'}).persist()

output = open('hycom_surface_current.json','r').read()
json_templete = json.loads(output)
json_templete[0]['header']['dx'] = dx  #- dx of eastward-current
json_templete[0]['header']['dy'] = dy  #- dy of eastward-current
json_templete[1]['header']['dx'] = dx  #- dx of northward-current
json_templete[1]['header']['dy'] = dy  #- dy of northward-current

u0 = df.fillna(0).water_u.data
v0 = df.fillna(0).water_v.data

json_templete[0]['header']['la1']=df.lat.data[-1]
json_templete[0]['header']['la2']=df.lat.data[0]
json_templete[0]['header']['lo1']=df.lon.data[0]
json_templete[0]['header']['lo2']=df.lon.data[-1]
json_templete[0]['header']['nx']=df.lon.size
json_templete[0]['header']['ny']=df.lat.size
json_templete[0]['header']['refTime']=str(df.time.data)
json_templete[0]['data'] = u0.flatten().tolist()

json_templete[1]['header']['la1']=df.lat.data[-1]
json_templete[1]['header']['la2']=df.lat.data[0]
json_templete[1]['header']['lo1']=df.lon.data[0]
json_templete[1]['header']['lo2']=df.lon.data[-1]
json_templete[1]['header']['nx']=df.lon.size
json_templete[1]['header']['ny']=df.lat.size
json_templete[1]['header']['refTime']=str(df.time.data)
json_templete[1]['data'] = v0.flatten().tolist()





with open('hycom_surface_current.json', 'w') as outfile:  
	outfile.write('[')            
	json.dump(json_templete[0], outfile) 
	outfile.write(',')            
	json.dump(json_templete[1], outfile) 
	outfile.write(']')           
