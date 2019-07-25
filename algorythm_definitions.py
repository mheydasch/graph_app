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
#%%
def calc_dist(dat=[], classifier_column='Classifier', identifier_column='unique_id', timepoint_column='Metadata_Timepoint', data_column=['Location_Center_X_Zeroed','Location_Center_Y_Zeroed']):
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
        #calculating x and y step sizes over the whole timecourse
        xd=single_track[X_column][0:].reset_index()-single_track[X_column][1:].reset_index()
        yd=single_track[Y_column][0:].reset_index()-single_track[Y_column][1:].reset_index()
        #calculating 2D stepsize over the whole time course
        stepsize=np.sqrt(xd[X_column]**2+yd[Y_column]**2)
        #last number wil always be nan, so drop it
        stepsize=stepsize.dropna()
        #summing up stepsize to get cumulative distance
        cumulative_distance=sum(stepsize)
        #calculating the distance between start and end point
        net_distance=np.sqrt((single_track[X_column].iloc[-1]-
                                single_track[Y_column].iloc[0])**2)
        #adding the calculated values to a dictionary
        temp={'unique_id':n, 'cumulative_distance':cumulative_distance, 'net_distance':net_distance, 'Classifier':single_track.loc[0][classifier_column]}
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