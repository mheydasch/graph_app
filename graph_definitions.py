#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:45:15 2019

@author: max
"""
import plotly.plotly as py
import plotly.graph_objs as go
from plotly import tools
import os
import sys
import math
import numpy as np
sys.path.append(os.path.realpath(__file__))
import algorythm_definitions as AD
#%%
def lineplot(dat=[], classifier_column='', identifier_column='', timepoint_column='', data_column='', testmode=False):
    '''
    testmode: If testomde is set to True only the first 10 items will be used in the graph
    '''     
    print(identifier_column)
    print(type(identifier_column))
    #cells=list(dat[identifier_column].unique())
    

    classes=list(dat[classifier_column].unique())
    X_column=data_column[0]
    Y_column=data_column[1]
    #initiating traces as a list
    #getting trace IDs from unique IDs (cells)
    print('looping through cells...')
    #getting the number of rows for suplots based on the amount of classes
    row_n=math.ceil(len(classes)/2)
    col_n=2
        #making a list of the rows and collumns for subplot coordinates
    rowlist=np.arange(1, row_n+1, 2)
    collist=[1, 2]
        #defining subplot layout
    fig=tools.make_subplots(rows=row_n, cols=col_n, subplot_titles=classes)
    r_i=0
    c_i=0
    #looping through the clases
    for i in classes:
        #subsetting the data by the class
        dat_class=dat.loc[dat[classifier_column]==i]
        #getting only the cells from that class
        cells=list(dat_class[identifier_column].unique())
        print('...of class ', i, '...')
        if testmode==True:        
            cells=cells[0:50]
        #append the current classes name to the titles of the plot


    #looping through the cells
        for c in cells:               
            #appending x, y data based on current cell to the list of traces
            fig.append_trace(trace=go.Scatter(
            x=dat_class.loc[dat_class[identifier_column]==c][X_column],
            y=dat_class.loc[dat_class[identifier_column]==c][Y_column]),
            row=int(rowlist[math.floor(r_i)]) , col=int(collist[c_i]))
            #c_i is reset to 0 every time it exceeds one, so that
            #only two columns will be plotted
            if c_i >1:
                c_i=0
            
        #adding 0.5 to the row indicator, so that every second class will be 
        #plottet in a new row
        r_i+=0.5
        c_i+=1

    print('...done')
        
    return fig
#%%
def migration_distance(dat=[], classifier_column='', identifier_column='', timepoint_column='', data_column='', testmode=False):
    if testmode==True:
        dat=dat[0:1000]
    print('calculating distances...')
    distances=AD.calc_dist(dat=dat, classifier_column=classifier_column, identifier_column=identifier_column, timepoint_column=timepoint_column, data_column=data_column)
    print('...done calculating')
    classes=list(distances[classifier_column].unique())
    fig=tools.make_subplots(rows=1, cols=2, subplot_titles=['Cumulative distance','Persistence'])

    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances[classifier_column]==i]['cumulative_distance'],
        #x=[xpos],
        name=i,
        boxpoints='all'), 
        row=1, col=1)


    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances[classifier_column]==i]['persistence'],
        #x=[xpos],
        name=i,
        boxpoints='all'), 
        row=1, col=2)

    return fig
    

