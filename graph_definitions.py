#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:45:15 2019

@author: max
"""
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import re
import pandas as pd
#%%
def lineplot(dat=[], classifier_column='', identifier_column='', timepoint_column='', testmode=False):
    '''
    testmode: If testomde is set to True only the first 10 items will be used in the graph
    '''     
    print(identifier_column)
    print(type(identifier_column))
    cells=list(dat[identifier_column].unique())
    
    if testmode==True:
        
        cells=cells[0:100]
   


    #initiating traces as a list
    traces=[]
    #getting trace IDs from unique IDs (cells)
    print('looping through cells...')
    
    #looping through the cells
    for c in cells:   
        #appending x, y data based on current cell to the list of traces
        traces.append(go.Scatter(
        x=dat.loc[dat[identifier_column]==c]['Location_Center_X_Zeroed'],        
        y=dat.loc[dat[identifier_column]==c]['Location_Center_Y_Zeroed']
        )
    )
    print('...done')

    return {'data' :traces}
#%%
def whiskerplot(dat, testmode=False):
    print()
    

