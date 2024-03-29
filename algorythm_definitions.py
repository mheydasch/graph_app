5#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:03:10 2019

@author: max

cHolds definitions for several calculations
"""
import pandas as pd
#import re
import numpy as np
from itertools import islice
import os
#%%
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))
def calc_dist(dat=[], classifier_column='Classifier', identifier_column='unique_id', 
              timepoint_column='Metadata_Timepoint', unique_time_selector='unique_time',
              data_column=['Location_Center_X','Location_Center_Y']):
    l=[]
    cells=list(dat[identifier_column].unique())
    #looping through each unique cell
    for n in cells:
        print(n)
        #taking only the data of that cell
        single_track=dat[dat[identifier_column]==n]
        X_column=data_column[0]
        Y_column=data_column[1]
        #sorting the data by time
        single_track=single_track.sort_values(by=[timepoint_column])
        single_track=single_track.reset_index()
        single_track
        #calculating x and y step sizes over the whole timecourse
        xd=single_track[X_column][0:].reset_index()-single_track[X_column][1:].reset_index()
        yd=single_track[Y_column][0:].reset_index()-single_track[Y_column][1:].reset_index()
        #calculating 2D stepsize over the whole time course
        stepsize=np.sqrt(xd[X_column].astype(np.float32)**2+yd[Y_column].astype(np.float32)**2)
        #last number wil always be nan, so drop it
        stepsize=stepsize.dropna()
        #summing up stepsize to get cumulative distance
        cumulative_distance=sum(stepsize)
        speed=cumulative_distance/len(single_track)
        #calculating the distance between start and end point
        #net_distance=0
        try:
            xd_total=xd.dropna()[X_column].iloc[1]-xd.dropna()[X_column].iloc[-1]
            yd_total=yd.dropna()[Y_column].iloc[1]-yd.dropna()[Y_column].iloc[-1]
            net_distance=np.sqrt(xd_total**2+yd_total**2)
        except IndexError as e:
            print(e, n)
            net_distance=np.NaN
            next
        #adding the calculated values to a dictionary
        temp={'unique_id':n, 'cumulative_distance':cumulative_distance, 
              'net_distance':net_distance, 'Speed' :speed, 'Classifier':single_track.loc[0][classifier_column],
              'Metadata_Timepoint':single_track.loc[0][timepoint_column],
              '{}'.format(unique_time_selector):single_track.loc[0][unique_time_selector]}
        #appending the dictionary to a list to keep it over the loops
        l.append(temp)
    
    #making data frame of the dictionaries    
    distances=pd.DataFrame(l)
    #calculating persistence
    distances['persistence']=distances['net_distance']/distances['cumulative_distance']
    distances=distances.dropna()
    return distances

def calc_speed(dat=[], classifier_column='Metadata_Classifier', identifier_column='unique_id', 
              timepoint_column='Metadata_Timepoint', unique_time_selector='unique_time',
              data_column=['Location_Center_X','Location_Center_Y']):
    #l=[]
    #cells=list(dat[identifier_column].unique())
    
    xd=data_column[0]
    yd=data_column[1]
    dat['dispX']=dat[xd].groupby(dat[identifier_column]).diff()
    dat['dispY']=dat[yd].groupby(dat[identifier_column]).diff()
    
# =============================================================================
#     to_filter=[]
#     for i in dat[identifier_column].unique():
#         if dat[dat[identifier_column]==i].shape[0]>5:
#             to_filter.append(i)
#     dat=dat[dat[identifier_column].isin(to_filter)]
# =============================================================================
    
    dat['dispX']=dat['dispX']**2
    dat['dispY']=dat['dispY']**2
    
    dat['disp']=(dat['dispX']+dat['dispY'])**(1/2)
    dat=dat.dropna()
    
# =============================================================================
#     speed=dat.groupby([classifier_column, identifier_column], as_index=False).agg(disp=pd.NamedAgg(column='disp', aggfunc=sum),
#                persistence=pd.NamedAgg(column='disp',
#                                         aggfunc=lambda x: abs((x.iloc[0]-x.iloc[-1])/x.sum()))).reset_index(drop=True)      #{'disp':'sum'}).reset_index(drop=True)
# =============================================================================

    #speed=dat.groupby([classifier_column, identifier_column], as_index=False).agg({'disp':'sum'}).reset_index(drop=True)
    speed=dat.groupby([classifier_column, identifier_column], as_index=False)
    speed.filter(lambda x: len(x) > 1)
    speed=dat.groupby([classifier_column, identifier_column], as_index=False).agg(disp=pd.NamedAgg(column='disp', aggfunc=sum),
                persistence=pd.NamedAgg(column='disp',
                                         aggfunc=lambda x: abs((x.iloc[0]-x.iloc[-1])/x.sum()))).reset_index(drop=True) 
    speed['disp']=speed['disp']/15
    speed['disp_in_mic']=speed['disp']*0.7692

    
    return speed, dat

def cellcount(data=[], classifier_column='Metadata_Classifier', identifier_column='unique_id', 
              timepoint_column='Metadata_Timepoint', unique_time_selector='unique_time',
              data_column=''):
    #l=[]
    #cells=list(dat[identifier_column].unique())
    
    count=data.groupby(['Metadata_Site', 'Metadata_Timepoint'],as_index=False).agg({'track_id': 'count', 
                      'Metadata_Classifier': lambda x: (x.iloc[0])})

    
    return count


def calc_median(distances,  classifier_column='', identifier_column='', timepoint_column='', data_column=''):
    median_values=distances.groupby(classifier_column, as_index=False).agg({'persistence' :'median', 'cumulative_distance' : 'median'})    
    low_migration=(distances[distances['cumulative_distance']<1].groupby('Well')[identifier_column].count())/\
    (distances.groupby(classifier_column)[identifier_column].count())
    return median_values, low_migration

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)
        
def calc_average(dat=[], classifier_column='Classifier', average_column='AreaShape_Area', grouping_column='Metadata_Timepoint'):
    #if average_column+'_median' not in dat.columns:
    dat[average_column+'_median']='None'
    med=dat.groupby([grouping_column, classifier_column], as_index=False)[average_column].median()
    
    for n, row in med.iterrows():
        idx=dat[(dat[classifier_column]==row[1]) & (dat[grouping_column]==row[0])].index[0]
        dat[average_column+'_median'].iloc[idx]=float(row.loc[average_column])
    return dat
    
def go_one_up(path, mode='folder'):
    '''
    takes one folder upwards of the given input folder
    mode can be either 'folder', or 'file'
    '''
  
    split_path=vars()['path'].split('/')
    one_up='/'+split_path[0]
    if mode=='folder':
        for n, i in enumerate(split_path[:-3]):
            one_up=one_up=os.path.join(one_up, split_path[n+1])  
    if mode=='file':
        for n, i in enumerate(split_path[:-2]):
            one_up=one_up=os.path.join(one_up, split_path[n+1])
    one_up=one_up+'/'
    return one_up