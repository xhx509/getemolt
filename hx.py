# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 15:23:37 2012

@author: Huanxin
"""
import pandas as pd
from dateutil.parser import parse
import math

import matplotlib.pyplot as plt
from matplotlib.dates import num2date,date2num
from matplotlib.dates import  DateFormatter
import datetime as dt

from pydap.client import open_url
import sys
#pydir='/net/home3/ocn/jmanning/py/huanxin/work'
import numpy as np

import pytz
utc = pytz.timezone('UTC')
#sys.path.append(pydir)


def colors(n):
	  """Compute a list of distinct colors, each of which is represented as an RGB 3-tuple."""
	  """It's useful for less than 100 numbers"""
	  if pow(n,float(1)/3)%1==0.0:
	     n+=1 
	  #make sure number we get is more than we need.
	  rgbcolors=[]
	  x=pow(n,float(1)/3)
	  a=int(x)
	  b=int(x)
	  c=int(x)
	  if a*b*c<=n:
	    a+=1
	  if a*b*c<n:
	    b+=1
	  if a*b*c<n:
	    c+=1
	  for i in range(a):
	      r=0.99/(a)*(i)
	      for j in range(b):
	          s=0.99/(b)*(j)
	          for k in range(c):
	              t=0.99/(c)*(k)
	              color=r,s,t
	              rgbcolors.append(color)
	  return rgbcolors


def getemolt_depth(b_mindepth,b_maxdepth,lat_max,lon_max,lat_min,lon_min,site1):
    #According to the conditions to select data from "emolt_sensor"
    url="http://gisweb.wh.whoi.edu:8080/dods/whoi/emolt_site?emolt_site.SITE,emolt_site.BTM_DEPTH,emolt_site.LAT_DDMM,emolt_site.LON_DDMM&emolt_site.BTM_DEPTH<="+str(b_maxdepth)+"&emolt_site.BTM_DEPTH>="+str(b_mindepth)+"&emolt_site.LON_DDMM<="\
    +str(lon_max)+"&emolt_site.LON_DDMM>="+str(lon_min)+"&emolt_site.LAT_DDMM<="+str(lat_max)+"&emolt_site.LAT_DDMM>="+str(lat_min)+site1
    try:   
	           dataset=open_url(url)
    except:
	           print 'Sorry, '+url+' not available' 
	           sys.exit(0)
    emolt_site=dataset['emolt_site']
    try:   
	          sites=list(emolt_site['SITE'])
    except:
	          print "'Sorry, According to your input, here are no value. please check it! ' "
	          sys.exit(0)   
    sites=list(emolt_site['SITE'])
    depth_b=list(emolt_site['BTM_DEPTH'])
    

            
    lat_dd=list(emolt_site['LAT_DDMM'])
    lon_dd=list(emolt_site['LON_DDMM'])
    return sites,depth_b,lat_dd,lon_dd
	
def getemolt_sensor(mindtime1,maxdtime1,i_mindepth,i_maxdepth,site2,mindtime,maxdtime):
	  #According to the conditions to select data from "emolt_sensor"
	 
	  url2="http://gisweb.wh.whoi.edu:8080/dods/whoi/emolt_sensor?emolt_sensor.SITE,emolt_sensor.TIME_LOCAL,emolt_sensor.YRDAY0_LOCAL,emolt_sensor.TEMP,emolt_sensor.DEPTH_I&emolt_sensor.TIME_LOCAL>="+str(mindtime1)+"&emolt_sensor.TIME_LOCAL<="\
        +str(maxdtime1)+"&emolt_sensor.DEPTH_I>="+str(i_mindepth)+"&emolt_sensor.DEPTH_I<="+str(i_maxdepth)+site2
	  try:   
	           dataset1=open_url(url2)
	  except:
	           print 'Sorry, '+url2+' not available' 
	           sys.exit(0)
	  emolt_sensor=dataset1['emolt_sensor']
	  try:   
	          sites2=list(emolt_sensor['SITE'])
	  except:
	          print "'Sorry, According to your input, here are no value. please check it! ' "
	          sys.exit(0) 
	  #sites2=list(emolt_sensor['SITE'])
	  time=list(emolt_sensor['TIME_LOCAL'])
	  yrday0=list(emolt_sensor['YRDAY0_LOCAL'])
	  temp=list(emolt_sensor['TEMP'])
	  depth1=list(emolt_sensor['DEPTH_I'])
	
	
	  time1,temp1,yrday01,sites1,depth=[],[],[],[],[]
	  for m in range(len(time)):
	      #if mindtime<=dt.datetime.strptime(str(time[m]),'%Y-%m-%d')<=maxdtime:
	      if date2num(mindtime)<=yrday0[m]%1+date2num(dt.datetime.strptime(str(time[m]),'%Y-%m-%d'))<=date2num(maxdtime):
	      #if str(time[m])=='2012-01-01':
	        temp1.append(temp[m])
	        yrday01.append(yrday0[m]%1+date2num(dt.datetime.strptime(str(time[m]),'%Y-%m-%d')))
	        sites1.append(sites2[m])
	        time1.append(date2num(dt.datetime.strptime(str(time[m]),'%Y-%m-%d'))) 
	        depth.append(depth1[m])
	  #print len(temp1)     
	  return time1,yrday01,temp1,sites1,depth,
def getobs_tempsalt_bysite(site,input_time,depth):
    """
Function written by Jim Manning and used in "modvsobs" and "getemolt",it was modified by Huanxin.
get data from url, return depth temperature,latitude,longitude, and start and end times.
depth includes bottom depth and surface depth,like:  [80,0].
input_time can either contain two values: start_time & end_time OR one value:interval_days
and they should be timezone aware
example: input_time=[dt(2003,1,1,0,0,0,0,pytz.UTC),dt(2009,1,1,0,0,0,0,pytz.UTC)]
"""
    mintime=input_time[0].strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')  # change time format
    maxtime=input_time[1].strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')    
    i_maxdepth=depth[0];i_mindepth=depth[1];
    url='http://comet.nefsc.noaa.gov:8080/erddap/tabledap/eMOLT.csv?SITE,time,depth,sea_water_temperature,latitude,longitude&time>='\
    +str(mintime)+'&time<='+str(maxtime)+'&depth<='+str(i_maxdepth)+'&depth>='+str(i_mindepth)+'&SITE="'+str(site)+'"&orderBy("depth,time")'
    
    df=pd.read_csv(url,skiprows=[1])
    for k in range(len(df)):
       df.time[k]=parse(df.time[k])

    return df.time.values,df.sea_water_temperature.values,df.depth.values,df.SITE.values,df.latitude.values,df.longitude.values

def getobs_tempsalt_byrange(gbox,depth,input_time):
    """
Function written by Huanxin and used in "getemolt".
get data from url, return depth temperature,latitude,longitude, and start and end times.
gbox includes 4 values, maxlon, minlon,maxlat,minlat, like:  [-69.0,-73.0,41.0,40.82].
depth includes bottom depth and surface depth,like:  [80,0].
input_time can either contain two values: start_time & end_time OR one value:interval_days
and they should be timezone aware
example: input_time=[dt(2003,1,1,0,0,0,0,pytz.UTC),dt(2009,1,1,0,0,0,0,pytz.UTC)]
"""
    i_maxdepth=depth[0];i_mindepth=depth[1];lon_max=gbox[0];lon_min=gbox[1];lat_max=gbox[2];lat_min=gbox[3]
    mintime=input_time[0].strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')  # change time format
    maxtime=input_time[1].strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')
    url='http://comet.nefsc.noaa.gov:8080/erddap/tabledap/eMOLT.csv?SITE,time,depth,sea_water_temperature,latitude,longitude&time>='\
    +str(mintime)+'&time<='+str(maxtime)+'&depth<='+str(i_maxdepth)+'&depth>='+str(i_mindepth)+'&latitude>='\
    +str(lat_min)+'&latitude<='+str(lat_max)+'&longitude>='+str(lon_min)+'&longitude<='+str(lon_max)+'&orderBy("SITE,depth,time")'
    df=pd.read_csv(url,skiprows=[1])
    for k in range(len(df)):
       df.time[k]=parse(df.time[k])
    return df.time.values,df.sea_water_temperature.values,df.depth.values,df.SITE.values,df.latitude.values,df.longitude.values
    


def getemolt_ctl(inputfilename):
   f=open(inputfilename)  
   select=f.readline()
   select=select[0:select.index(']')].strip('[').split(' ')
   select1=select[0]
   select2=select[1]
   select3=select[2]
   select4=select[3]
   select5=select[4]
   if select1 =='1':
       dtime=f.readline()
       dtime=dtime[0:dtime.index(']')].strip('[').split(';')
       mindtime=dt.datetime.strptime(dtime[0],'%Y,%m,%d,%H,%M')
       maxdtime=dt.datetime.strptime(dtime[1],'%Y,%m,%d,%H,%M') 
   else:
       dtime=f.readline()
   input_time=[mindtime,maxdtime]
       
   if select2 =='1':
       idepth=f.readline()
       idepth=idepth[0:idepth.index(']')].strip('[').split(',')
       mindepth=float(idepth[0])
       maxdepth=float(idepth[1])
   else:
       mindepth=0
       maxdepth=2000
       dtime=f.readline()
   depth=[maxdepth,mindepth]
       
   if select3 =='1':
       latlon=f.readline()
       latlon=latlon[0:latlon.index(']')].strip('[').split(',')
       lat_max=float(latlon[0])
       lon_min=float(latlon[1])
       lat_min=float(latlon[2])
       lon_max=float(latlon[3])
   else:
       latlon=f.readline()
       lat_max=47.0
       lon_max=-66.0 
       lat_min=35.0
       lon_min=-76.0
   gbox=[lon_max,lon_min,lat_max,lat_min]    
   if select4 =='1':
       polygon=f.readline()
       polygon=polygon[0:polygon.index(']')].strip('[').split(';')
       polygon=[eval(i) for i in polygon]
   else:
       polygon==''
       
   if select5 =='1':
       site=f.readline()
       site=site[0:site.index(']')].strip('[').split(',') 
   else:
       site=f.readline()
       site=''
       
   return input_time,depth,gbox,polygon,site

def emolt_plotting(yrday,depth,temp,time11,samesites0,ax,k,ave_temp0,rgbcolors):
    #"ax" you can do like fig = plt.figure() ; ax = fig.add_subplot(111)
    #"k" "samesites0" ,this function should be in "for" loop,  for k in range(len(samesites0)): 
    # except "k", all of them should be a list
    #ave_temp0 means every average temperature for every samesites
    #rgbcolors is a color box, we select colors from it for plot
    temp0,yrday0=[],[]
    if temp<>[]:       
      depth111s=min(depth)
      # sorted Temperature by date,time   
      a=zip(yrday,temp)
      b=sorted(a, key=lambda a: a[0])
      for e in range(len(temp)):
        yrday0.append(b[e][0])
        temp0.append(b[e][1])     
      plt.plot(yrday0,temp0,color=rgbcolors[k],label=samesites0[k]+'(s): -'+str(int(depth111s))+','+str(round(ave_temp0[k],1))+'F',lw = 3)         
    plt.ylabel('Temperature')
    plt.title('temp from '+num2date(min(time11)).strftime("%d-%b-%Y")+' to '+num2date(max(time11)).strftime("%d-%b-%Y"))
    plt.legend()

#choose suited unit in x axis
    if max(time11)-min(time11)<5:
      monthsFmt = DateFormatter('%m-%d\n %H'+'h')
    if 5<=max(time11)-min(time11)<366:
      monthsFmt = DateFormatter('%m-%d')
    if max(time11)-min(time11)>366:
      monthsFmt = DateFormatter('%Y-%m')    
    ax.xaxis.set_major_formatter(monthsFmt)

    #ax.set_xlabel(str(num2date(min(time11)).year)+"-"+str(num2date(max(time11)).year),fontsize=17)
    #limit x axis length
    ax.set_xlabel('Notation:(s) means near the surface of sea')
    plt.xlim([min(time11),max(time11)+(max(time11)-min(time11))/2]) 
    plt.savefig('/net/home3/ocn/jmanning/py/huanxin/work/hx/please rename .png')   
    plt.show()
def getemolt_samesites_data(sites1,sites2,temp1,lat_dd,lon_dd):
    samesites=list(set(sites2).intersection(set(sites1)))
    if samesites==[]:
      print "Can not find eligible data, please re-enter the conditions"
      sys.exit(0)
    #get average Temperature, sorted sites by average Temperature
    ave_temp,samesites0,ave_temp0=[],[],[]
    for r in range(len(samesites)):
      temp_a=[]
      for s in range(len(sites1)):
         if sites1[s]==samesites[r]:
            temp_a.append(temp1[s]) 
      temp_ave=np.mean(temp_a)
      ave_temp.append(temp_ave)
    c=zip(samesites,ave_temp)
    d=sorted(c, key=lambda c: c[1])
    for g in range(len(samesites)):
      samesites0.append(d[g][0])
      ave_temp0.append(d[g][1])
    lat,lon=[],[]
    for y in range(len(samesites0)):
      for z in range(len(sites2)):
          if sites2[z]==samesites0[y]:
              lat.append(lat_dd[z])
              lon.append(lon_dd[z])  
    samesites=samesites0
    ave_temp=ave_temp0
    return samesites,ave_temp,lat,lon
    


def nearxy(x,y,x0,y0):
    distance=[]
    for i in range(0,np.size(x)):
      for l in range(0,len(y)):
         distance.append(abs(math.sqrt((x[i]-x0)**2+(y[l]-y0)**2)))
    min_dis=min(distance)
    #len_dis=len(distance)
    for p in range(0,len(x)):
      for q in range(0,len(y)):
          if abs(math.sqrt((x[p]-x0)**2+(y[q]-y0)**2))==min_dis:
              index_x=p
              index_y=q
  

    return min(distance),index_x,index_y
  



def point_in_poly(x,y,poly):  #judge whether a site is in or out a polygon 

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside
