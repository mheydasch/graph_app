#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 16:22:28 2019

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
#plotly 3.7.1

#%% legacy plots
#lineplot with two columns instead of one
def lineplot(dat=[], classifier_column='', identifier_column='', timepoint_column='', data_column='', distance_filter='', testmode=False):
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
            #getting x values
            x=dat_class.loc[dat_class[identifier_column]==c][X_column],
            #getting y values
            y=dat_class.loc[dat_class[identifier_column]==c][Y_column],
            #getting unique ID
            hovertext=dat_class.loc[dat_class[identifier_column]==c][identifier_column]),

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

#%% migration plot with two columns
def migration_distance(dat=[], classifier_column='', identifier_column='', timepoint_column='', data_column='', distance_filter='', testmode=False):
    if testmode==True:
        dat=dat[0:1000]
    print('calculating distances...')
    #calculating the distances and persistence of migration
    distances=AD.calc_dist(dat=dat, classifier_column=classifier_column, identifier_column=identifier_column, timepoint_column=timepoint_column, data_column=data_column)
    #filtering the distances by a minimum cumulative distance
    distances=distances[distances['cumulative_distance']>distance_filter]
    print('...done calculating')
    classes=list(distances[classifier_column].unique())
    fig=tools.make_subplots(rows=1, cols=2, subplot_titles=['Cumulative distance','Persistence'])

    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances[classifier_column]==i]['cumulative_distance'],
        hovertext=distances.loc[distances[classifier_column]==i][identifier_column],

        #x=[xpos],
        name=i,
        boxpoints='all'), 
        row=1, col=1)


    for xpos, i in enumerate(classes):
        fig.append_trace(trace=go.Box(
        y=distances.loc[distances[classifier_column]==i]['persistence'],
        hovertext=distances.loc[distances[classifier_column]==i][identifier_column],

        #x=[xpos],
        name=i,
        boxpoints='all'), 
        row=1, col=2)

    return fig
    
#%%
@app.callback(Output('image-overlay', 'src'),
              [Input('migration_data', 'hoverData')],
              [State('image_list','component'),
               State('image_type', 'children'),
               State('Image_selector', 'value'),
               State('shared_data', 'children')])
def update_image_overlay(hoverData, image_dict, image_type, image_selector, shared_data):
    #start_time=time.time()
    data=pd.read_json(shared_data, orient='split')

    #exclusion criterium if timepoint is already there
    exclusion=re.compile('_E.+?(?=\_)')
    #print(image_type)
    
    #exclusion criterium if timepoint isnot in hovertext
    exclusion_nt=re.compile('_E+.*')
    #getting hovertext from hoverdata and removing discrepancies between hover text and filenames
    #(stripping of track_ID)
    try:
        ID_or=hoverData['points'][0]['hovertext']
        ID=ID_or.replace(re.search(exclusion, ID_or).group(),'')
        print(ID_or)
    except AttributeError:
        ID=hoverData['points'][0]['hovertext'].replace(re.search(exclusion_nt, hoverData['points'][0]['hovertext']).group(),'')
        ID=ID+'_T1'
    #searching the dictionary for keys fitting the hovertext   
    image=image_dict[ID]
    #base64 encode the image   
    
    #testcode
    #reading the image as np array
    img=imageio.imread(image)
    #getting x and y coordinates from the data table, using the original ID,
    #which encludes the track ID of the cell
    x_coord=int(data[data['unique_time']==ID_or]['Location_Center_X'].values)
    y_coord=int(data[data['unique_time']==ID_or]['Location_Center_Y'].values)
    #manipulating a range of pixels around the center into being green
    img[x_coord-5:x_coord+5, y_coord-5:y_coord+5]=[0, 255, 0]
    img=Image.fromarray(img)
    #base64 encoding the image
    encoded=base64.b64encode(img)
        
    
    #update the dictionary with the encoded image
    #image_dict.update({ID:encoded})
    #print(type(image))
    #return the encoded image
    #print("--- %s seconds ---" % (time.time() - start_time))
    return 'data:image/png;base64,{}'.format(encoded.decode()) 