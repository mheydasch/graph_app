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
              data_column=['Location_Center_X_Zeroed','Location_Center_Y_Zeroed']):
    l=[]
    cells=list(dat[identifier_column].unique())
    #looping through each unique cell
    for n in cells:
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
        net_distance=np.sqrt((np.float32(single_track[X_column].iloc[-1])-
                                np.float32(single_track[Y_column].iloc[0]))**2)
        #adding the calculated values to a dictionary
        temp={'unique_id':n, 'cumulative_distance':cumulative_distance, 
              'net_distance':net_distance, 'Speed' :speed, 'Classifier':single_track.loc[0][classifier_column],
              '{}'.format(unique_time_selector):single_track.loc[0][unique_time_selector]}
        #appending the dictionary to a list to keep it over the loops
        l.append(temp)
    
    #making data frame of the dictionaries    
    distances=pd.DataFrame(l)
    #calculating persistence
    distances['persistence']=distances['net_distance']/distances['cumulative_distance']
    distances=distances.dropna()
    return distances

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
    if average_column+'_median' not in dat.columns:
        dat[average_column+'_median']='None'
        med=dat.groupby([grouping_column, classifier_column], as_index=False)[average_column].median()
        
        for n, row in med.iterrows():
            idx=dat[(dat[classifier_column]==row[1]) & (dat[grouping_column]==row[0])].index[0]
            dat[average_column+'_median'].iloc[idx]=row.loc[average_column]
    return dat
    