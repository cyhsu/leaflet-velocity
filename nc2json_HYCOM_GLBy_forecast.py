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

#- Pre-processing.
Start_Date, End_Date = np.datetime64('today','h'), np.datetime64('today','h') + np.timedelta64(1,'D')
Start_Date, End_Date = np.datetime64('2020-06-29T00:00:00'), np.datetime64('2020-06-30T00:00:00')
link = 'http://tds.hycom.org/thredds/dodsC/GLBy0.08/latest'
nc = Dataset(link); 
tm = nc.variables['time']
tim= num2date(tm[:], tm.units)
nc.close()
tid,= np.where((tim>=Start_Date) & (tim<=End_Date))


link = link + '?'\
       + 'time[{:d}:1:{:d}],'.format(tid[0],tid[-1]+1)\
       + 'lat[2200:{:d}:3001],'.format(slice_index)\
       + 'lon[3200:{:d}:4000],'.format(slice_index)\
       + 'water_u[{:d}:1:{:d}][0][2200:{:d}:3001][3200:{:d}:4000],'.format(tid[0],tid[-1]+1,slice_index,slice_index)\
       + 'water_v[{:d}:1:{:d}][0][2200:{:d}:3001][3200:{:d}:4000]'.format(tid[0],tid[-1]+1,slice_index,slice_index) 

df = xr.open_dataset(link, decode_times=False).squeeze().persist()
df['time'] = num2date(df['time'].data, df['time'].units)


output = open('hycom_GLBy0p08_surface_current.json','r').read()
json_templete = json.loads(output)
json_templete[0]['header']['dx'] = dx  #- dx of eastward-current
json_templete[0]['header']['dy'] = dy  #- dy of eastward-current
json_templete[1]['header']['dx'] = dx  #- dx of northward-current
json_templete[1]['header']['dy'] = dy  #- dy of northward-current

u0 = df.fillna(0).water_u.mean('time').data[::-1]
v0 = df.fillna(0).water_v.mean('time').data[::-1]

json_templete[0]['header']['la1']=df.lat.data[-1]
json_templete[0]['header']['la2']=df.lat.data[0]
json_templete[0]['header']['lo1']=df.lon.data[0]
json_templete[0]['header']['lo2']=df.lon.data[-1]
json_templete[0]['header']['nx']=df.lon.size
json_templete[0]['header']['ny']=df.lat.size
json_templete[0]['header']['refTime']=str(df.time.mean('time').data)
json_templete[0]['data'] = u0.flatten().tolist()

json_templete[1]['header']['la1']=df.lat.data[-1]
json_templete[1]['header']['la2']=df.lat.data[0]
json_templete[1]['header']['lo1']=df.lon.data[0]
json_templete[1]['header']['lo2']=df.lon.data[-1]
json_templete[1]['header']['nx']=df.lon.size
json_templete[1]['header']['ny']=df.lat.size
json_templete[1]['header']['refTime']=str(df.time.mean('time').data)
json_templete[1]['data'] = v0.flatten().tolist()

with open('hycom_surface_current.json', 'w') as outfile:  
	outfile.write('[')            
	json.dump(json_templete[0], outfile) 
	outfile.write(',')            
	json.dump(json_templete[1], outfile) 
	outfile.write(']')           
