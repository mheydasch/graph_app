#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:45:15 2019

@author: max
Holds the graph definitions for the app.

"""


#import plotly.chart_studio as py
import chart_studio.plotly
import plotly.graph_objects as go

import pandas as pd
from plotly.subplots import make_subplots
import os
import sys
import math
import numpy as np
sys.path.append(os.path.realpath(__file__))
import algorythm_definitions as AD

#%% Plots for the plot dictionary, that are based on data
def lineplot(dat=[], classifier_column='', identifier_column='', timepoint_column='',
             data_column='', distance_filter='', unique_time_selector='', testmode=False):
    '''
    testmode: If testomde is set to True only the first 10 items will be used in the graph
    '''    
    print('creating migration lineplot')
    #print(identifier_column)
    #print(type(identifier_column))
    #cells=list(dat[identifier_column].unique())
    #dat[unique_time_selector]=dat[identifier_column]+'_T'+dat[timepoint_column].astype('str')

    classes=list(dat[classifier_column].unique())
    X_column=data_column[0]
    Y_column=data_column[1]
    #initiating traces as a list
    #getting trace IDs from unique IDs (cells)
    print('looping through cells...')
    #getting the number of rows for suplots based on the amount of classes
    row_n=len(classes)

    rowlist=np.arange(1, row_n+1, 1)

        #defining subplot layout
    fig=make_subplots(rows=row_n, cols=1, subplot_titles=classes)
    r_i=0
    #getting max axis values
    max_x=dat[X_column].max()
    min_x=dat[X_column].min()
    max_y=dat[Y_column].max()
    min_y=dat[Y_column].min()
    #looping through the clases
    for i in classes:
        #subsetting the data by the class
        dat_class=dat.loc[dat[classifier_column]==i]
        #getting only the cells from that class
        cells=list(dat_class[identifier_column].unique())
        print('...of class ', i, '...')
        if testmode==True:        
            cells=cells[50:100]
        #append the current classes name to the titles of the plot


    #looping through the cells
        for c in cells:               
            #appending x, y data based on current cell to the list of traces
            fig.append_trace(trace=go.Scatter(
            #getting x values
            x=dat_class.loc[dat_class[identifier_column]==c][X_column],
            #getting y values
            y=dat_class.loc[dat_class[identifier_column]==c][Y_column],
            #getting unique ID
            hovertext=dat_class.loc[dat_class[identifier_column]==c][unique_time_selector],
            customdata=[dat_class.loc[dat_class[identifier_column]==c][unique_time_selector]],
            name=c,
            ),
            row=int(rowlist[math.floor(r_i)]) , col=1)



            
        #adding 1 to the row indicator, so that every class will be 
        #plottet in a new row
        fig.update_yaxes(range=[min_y*1.05, max_y*1.05], row=int(rowlist[math.floor(r_i)]), col=1)
        fig.update_xaxes(range=[min_x*1.05, max_x*1.05], row=int(rowlist[math.floor(r_i)]), col=1)
        r_i+=1

    fig.update_layout(margin={'l': 40, 'b': 5, 't': 30, 'r': 40},
            height=row_n*375, width=750)
    fig.update_layout({'clickmode':'event+select'})
  

    print('...done')
        
    return fig

def migration_distance(dat=[], classifier_column='', identifier_column='', 
                       timepoint_column='', data_column='', distance_filter='', 
                       unique_time_selector='', testmode=False):
    if testmode==True:
        dat=dat[500:10000]
    print('creating migration boxplots')
    print('calculating distances...')
    #calculating the distances and persistence of migration
    distances=AD.calc_dist(dat=dat, classifier_column=classifier_column, 
                           identifier_column=identifier_column, timepoint_column=timepoint_column,
                           data_column=data_column, unique_time_selector=unique_time_selector)
    #filtering the distances by a minimum cumulative distance
    distances=distances[distances['cumulative_distance']>distance_filter]
    print('...done calculating')
    classes=list(distances['Classifier'].astype('str').unique())
    fig=make_subplots(rows=2, cols=1, subplot_titles=['Cumulative distance','Persistence'])

    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances['Classifier']==i]['cumulative_distance'],
        hovertext=distances.loc[distances['Classifier']==i][unique_time_selector],
        customdata=[distances.loc[distances['Classifier']==i][unique_time_selector]],
        name=i,
        boxpoints='all',
        notched=True), 
        row=1, col=1)


    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances['Classifier']==i]['persistence'],
        hovertext=distances.loc[distances['Classifier']==i][unique_time_selector],
        customdata=[distances.loc[distances['Classifier']==i][unique_time_selector]],

        name=i,
        boxpoints='all',
        notched=True), 
        row=2, col=1)
    fig.update_layout(margin={'l': 40, 'b': 5, 't': 30, 'r': 200},
            height=750, width=750)

    return fig
    

def time_series(dat=[], classifier_column='', identifier_column='', 
                timepoint_column='', data_column='', distance_filter='', 
                unique_time_selector='', testmode=False):
    '''
    testmode: If testomde is set to True only the first 10 items will be used in the graph
    '''  
    print('Creating time series')
    #print(identifier_column)
    #print(type(identifier_column))
    #cells=list(dat[identifier_column].unique())
    dat[unique_time_selector]=dat[identifier_column]+'_T'+dat[timepoint_column].astype('str')

    classes=list(dat[classifier_column].unique())
    Y_column=data_column[0]
    X_column=timepoint_column
    max_x=dat[X_column].max()
    min_x=dat[X_column].min()
    max_y=dat[Y_column].max()
    min_y=dat[Y_column].min()
    #initiating traces as a list
    #getting trace IDs from unique IDs (cells)
    print('looping through cells...')
    #getting the number of rows for suplots based on the amount of classes
    row_n=len(classes)

    rowlist=np.arange(1, row_n+1, 1)

        #defining subplot layout
    fig=make_subplots(rows=row_n, cols=1, subplot_titles=classes)
    r_i=0

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
            #getting x values
            x=dat_class.loc[dat_class[identifier_column]==c][X_column],
            #getting y values
            y=dat_class.loc[dat_class[identifier_column]==c][Y_column],
            #getting unique ID
            hovertext=dat_class.loc[dat_class[identifier_column]==c][unique_time_selector],
            customdata=[dat_class.loc[dat_class[identifier_column]==c][unique_time_selector]],
            name=c,),
            row=int(rowlist[math.floor(r_i)]) , col=1)
    


        fig.update_yaxes(range=[min_y*1.05, max_y*1.05], row=int(rowlist[math.floor(r_i)]), col=1)
        fig.update_xaxes(range=[min_x*1.05, max_x*1.05], row=int(rowlist[math.floor(r_i)]), col=1)    
        #adding 1 to the row indicator, so that every class will be 
        #plottet in a new row
        r_i+=1

    fig.update_layout(margin={'l': 40, 'b': 5, 't': 30, 'r': 40},
            height=row_n*375, width=750)
    fig.update_layout({'clickmode':'event+select'})


    print('...done')
    return fig

#%% plots displaying other things
def image_graph(img, x_C=1024, y_C=1024, image_info=[0, 0, 0], ID=''):
    '''
    this graph is supposed to show an image and mark a point on it.
    '''    
    #print(image_info)
    X_S=image_info[0]
    Y_S=image_info[1]
    ID=image_info[3]
    
    
    #calculate aspect ratio
    aspect_ratio=x_C/y_C  
    fig=go.Figure()
    # Add invisible scatter trace.
    # This trace is added to help the autoresize logic work.
    fig.add_trace(
        go.Scatter(
            x=[0, x_C],
            y=[0, y_C],
            mode="markers",
            marker_opacity=0
        )
            )

    fig.add_trace(go.Scatter(
    hovertext=ID,
    customdata=[ID],
    #name=ID,
    x=[X_S],
    #images start with y0 at the top, graphs with y0 at the bottom
    y=[abs(Y_S-y_C)],
    mode='markers',
    marker_opacity=1,
    marker=dict(color='red')
    ))
    #displaying markers over all other tracked cells
    for i in list(image_info[2]['alt_cells'].keys()):
        fig.add_trace(go.Scatter(
                #name=i,
                hovertext=i,
                customdata=[i],
                x=[image_info[2]['alt_cells'][i][0]],
                y=[abs((image_info[2]['alt_cells'][i][1]-y_C))],
                mode='markers',
                marker_opacity=1,
                marker=dict(color='blue')
                
                )
        )
        
    fig.update_layout(
            showlegend=False,
            images=[
                    go.layout.Image(source=img,
                                    xref='x',
                                    yref='y',
                                    x=0,
                                    y=y_C,
                                    #using input image sizes as the
                                    #axes legnths for the graph
                                    sizex=x_C,
                                    sizey=y_C,
                                    sizing='stretch',
                                    opacity=1,
                                    layer='below')],
            #defining height and width of the graph                        
            height=750,
            width=750*aspect_ratio)
                  
    fig.update_xaxes(visible=False, range=[0, x_C])
    fig.update_yaxes(visible=False, range=[0, y_C])
    fig.update_layout({'clickmode':'event+select'})
    
    #print('image being displayed')
    return fig
#/Volumes/imaging.data/Max/REF52/beta_pix/pix_10/cp.out1/output/    