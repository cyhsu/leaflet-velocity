import numpy as np
import os, sys, json
from netCDF4 import Dataset, num2date

#-- This script is transferring the information of HYCOM GoM expt90.1 
#-- model simulation output to GeoJson format which is required by leaflet-velocity.js
#--
#-- Detail information: https://www.hycom.org
#-- Modified by Chuan-Yuan Hsu, 2020-07-01
#--    Updates: 
#--              1. Changed from GLBy0.08 to GoMu0.04
#--              2. Two versions: forecast -- take whole day forecast average
#--                               analysis -- take the analysis time point
#-- Modified by Shinichi Kobara 
#-- Created by Chuan-Yuan Hsu, 2017-10-11

#-- Horizontal Resolution Extract Setup.
slice_index = 3 
dx = 0.040 * slice_index
dy = 0.039 * slice_index
Start_Date, End_Date = np.datetime64('today','h'), np.datetime64('today','h') + np.timedelta64(1,'D')
link = 'https://tds.hycom.org/thredds/dodsC/GOMu0.04/expt_90.1m000/FMRC/GOMu0.04_901m000_FMRC_best.ncd'

nc = Dataset(link); 
tm = nc.variables['time']
tim= num2date(tm[:], tm.units)
tid,= np.where((tim>=Start_Date) & (tim<=End_Date))
ref_time = str(num2date(np.mean(tm[tid]), tm.units))
nc.close()


link = link + '?'\
       + 'time[{:d}:1:{:d}],'.format(tid[0],tid[-1]+1)\
       + 'lat[0:{:d}:345],'.format(slice_index)\
       + 'lon[0:{:d}:540],'.format(slice_index)\
       + 'water_u[{:d}:1:{:d}][0][0:{:d}:345][0:{:d}:540],'.format(tid[0],tid[-1]+1,slice_index,slice_index)\
       + 'water_v[{:d}:1:{:d}][0][0:{:d}:345][0:{:d}:540]'.format(tid[0],tid[-1]+1,slice_index,slice_index)\

import importlib.util
package_name = 'xarray'
spec = importlib.util.find_spec(package_name)
if spec:
#if spec is None:
	print('run on netCDF4')
	nc = Dataset(link)
	lat, lon = nc.variables['lat'][:], nc.variables['lon'][:]
	nx, ny = len(lon), len(lat)
	u0 = np.squeeze(np.nanmean(np.ma.masked_invalid(nc.variables['water_u'][:]).filled(fill_value=0),axis=0))[::-1]
	v0 = np.squeeze(np.nanmean(np.ma.masked_invalid(nc.variables['water_v'][:]).filled(fill_value=0),axis=0))[::-1]
else:
	print('run on Xarray')
	import xarray as xr
	df = xr.open_dataset(link, decode_times=False).squeeze().persist()
	df['time'] = num2date(df['time'].data, df['time'].units)
	lat, lon = df.lat.data, df.lon.data
	nx, ny = len(lon), len(lat)
	u0 = df.fillna(0).water_u.mean('time').data[::-1]
	v0 = df.fillna(0).water_v.mean('time').data[::-1]
	ref_time = str(df.time.mean('time').data)

outputFile = 'hycom_surface_current.json'
output = open(outputFile,'r').read()
json_templete = json.loads(output)
json_templete[0]['header']['dx'] = dx  #- dx of eastward-current
json_templete[0]['header']['dy'] = dy  #- dy of eastward-current
json_templete[1]['header']['dx'] = dx  #- dx of northward-current
json_templete[1]['header']['dy'] = dy  #- dy of northward-current

json_templete[0]['header']['la1']=lat[-1]
json_templete[0]['header']['la2']=lat[0]
json_templete[0]['header']['lo1']=lon[0]
json_templete[0]['header']['lo2']=lon[-1]
json_templete[0]['header']['nx']=nx
json_templete[0]['header']['ny']=ny
json_templete[0]['header']['refTime']=ref_time
json_templete[0]['data'] = u0.flatten().tolist()

json_templete[1]['header']['la1']=lat[-1]
json_templete[1]['header']['la2']=lat[0]
json_templete[1]['header']['lo1']=lon[0]
json_templete[1]['header']['lo2']=lon[-1]
json_templete[1]['header']['nx']=nx
json_templete[1]['header']['ny']=ny
json_templete[1]['header']['refTime']=ref_time
json_templete[1]['data'] = v0.flatten().tolist()

with open(outputFile, 'w') as outfile:  
	outfile.write('[')            
	json.dump(json_templete[0], outfile) 
	outfile.write(',')            
	json.dump(json_templete[1], outfile) 
	outfile.write(']')           
