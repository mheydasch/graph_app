#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:03:10 2019

@author: max
"""
import pandas as pd
import re
import numpy as np
#%%
def calc_dist(dat):
    l=[]
    cells=list(dat['unique_id'].unique())
    #looping through each unique cell
    for n in cells:
        #taking only the data of that cell
        single_track=dat[dat['unique_id']==n]
        print(single_track)
        #sorting the data by time
        single_track=single_track.sort_values(by=['Metadata_Timepoint'])
        #calculating x and y step sizes over the whole timecourse
        xd=single_track['Location_Center_X'][0:].reset_index()-single_track['Location_Center_X'][1:].reset_index()
        yd=single_track['Location_Center_Y'][0:].reset_index()-single_track['Location_Center_Y'][1:].reset_index()
        #calculating 2D stepsize over the whole time course
        stepsize=np.sqrt(xd['Location_Center_X']**2+yd['Location_Center_Y']**2)
        #last number wil always be nan, so drop it
        stepsize=stepsize.dropna()
        #summing up stepsize to get cumulative distance
        cumulative_distance=sum(stepsize)
        #calculating the distance between start and end point
        net_distance=np.sqrt((single_track['Location_Center_X'].iloc[-1]-
                                single_track['Location_Center_X'].iloc[0])**2)
        #adding the calculated values to a dictionary
        temp={'unique_id':n, 'cumulative_distance':cumulative_distance, 'net_distance':net_distance, 'Classifier':single_track.loc[0]['Classifier']}
        #appending the dictionary to a list to keep it over the loops
        l.append(temp)
    
    #making data frame of the dictionaries    
    distances=pd.DataFrame(l)
    #calculating persistence
    distances['persistence']=distances['net_distance']/distances['cumulative_distance']
    distances=distances.dropna()
    return distances

def calc_median(distances):
    median_values=distances.groupby('Well', as_index=False).agg({'persistence' :'median', 'cumulative_distance' : 'median'})    
    low_migration=(distances[distances['cumulative_distance']<1].groupby('Well')['unique_id'].count())/\
    (distances.groupby('Well')['unique_id'].count())
    return median_values, low_migration