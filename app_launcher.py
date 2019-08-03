#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:11:11 2019
@author: max
"""

import base64
import datetime
import io
import time
import numpy as np
from PIL import Image
import cv2
import urllib

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import imageio
import json
import flask
from natsort import natsorted
#from flask_caching import Cache

import pandas as pd
import sys
import os
import re


sys.path.append(os.path.realpath(__file__))
import graph_definitions as GD
import menu_definitions as MD
import algorythm_definitions as AD



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.title='Visualisation_of_Data'

'''
Holds interface and callback definitions for the app. This is the script that
launches it
Dependencies:
menus and buttons are defined in the file menu_definitions.py
graphs are defined in the file graph_definitions.py
other functions for calculations on data are defined in algorythm_definitions.py
'''


#%% caching


#%% app upload
global df
df=pd.DataFrame({'flags':[1, 2]})

#%%
    
app.layout = html.Div([
    html.P('Upload the csv file holding your data:'),
    dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=True), 
    html.P('Upload a single image for troubleshooting'),
    MD.Upload_images(),
    MD.Image_folder(),
    MD.Folder_submit(),
    html.P('Do you have other channels that you want to merge?'),
    MD.Image_selector(),
    #calling menus
    html.Hr(),
    html.Div(
        [html.Div([dcc.Markdown('''**Data organization**'''),
        html.P('How is your data formatted?'),
        MD.datatype_selector(),
        html.P('Select the columns that hold your data, if x,y coordinates, first selected is treated as x coordinate:'),
        MD.data_selector(df),
        html.P('Select the column which holds the classifier of your groups:'),
        MD.classifier_choice(df),
        html.P('Select the column which holds the identifier for each unique item:'),
        MD.identifier_selector(df),
        html.P('Select the column which holds the timepoints:'),
        MD.timepoint_selector(df)], className= 'six columns'),
    
        html.Div([dcc.Markdown('''**Data filtering**'''), 
        MD.RadioItems(),
        html.P('Select the minimum track length'),
        MD.track_length_selector(),
        html.Div(id='track_length_output', style={'margin-top': 20} ),
        html.Div([
        html.Div([
        html.P('Select the minimum travelled distance'),
        MD.distance_filter(),
                ], className='three columns'),
        html.Div([
                html.P('Select which flags to exclude from the Graphs'),
                MD.flag_filter()
                ], className='three columns')
        ], className='row'),
        html.P('Do you want to reuse a previously created instance of the graph, if available?'),
        MD.graph_reuse(),
        MD.plot_button()], className='six columns'
    )], className='row'),


#tabs section start
    dcc.Tabs(id='tabs', children=[
             dcc.Tab(label='Table', 
                     children= [html.Table(id='output-data-upload'),
                                    html.A(
                                            'Download Data',
                                            id='download-link',
                                            download="rawdata.csv",
                                            href="",
                                            target="_blank"
                                            ),
                                            MD.save_button()]),
                     #calling the table
                             
             dcc.Tab(label='Graph',
                     #calling the graph 
                     children= [html.Div([
                                     #graph for showing data
                                     html.Div([dcc.Graph(id='migration_data'),
                                               #MD.save_button()
                                               ],
                                          className= 'six columns'),
                                               #graph for showing the image
                                     html.Div([dcc.Graph(id='image-overlay'),
                                               #slider for selection of image
                                               MD.image_slider(),
                                               
                                               html.Div(id='image_slider_output', style={'margin-top': 20},),
                                               html.Img(id='test_image',
                                                        style={
                                                            'height': '75%',
                                                            'width': '75%',
                                                            'float': 'fixed',
                                                            'position': 'relative',
                                                            'margin-top': 20,
                                                            'margin-right': 20,
                                                            
                                                                }
                                                        
                                                        ),
                                               html.Div(id='image_name',
                                                        ),
                                               html.Div([
                                                    dcc.Markdown(("""
                                                        **Click Data**
                                        
                                                        Click on points in the graph.
                                                    """)),
                                                    html.Pre(id='click-data', style={
                                                'border': 'thin lightgrey solid',
                                                'overflowX': 'scroll'
                                            })]),
                                                MD.track_comment(),
                                                MD.comment_submit(),
                                                html.P('Do you want to flag all, or a single timepoint?'),
                                                MD.flag_options(),
                                                  ],className='six columns', )
                                          
                                               
                                 ], className='row')]
                                 
                     )
            ]),
#tabs section end    
           
                                 

 
                             
                    


#html.Img(id='test_image')

    html.Div(id='output-image-upload', style={'display':'none'}),
     #hidden divs for storing data
    html.Div(id='shared_data', style={'display':'none'}),
    html.Div(id='shared_data2', style={'display':'none'}),
    #holding the type of the uploaded images
    html.Div(id='image_type', style={'display':'none'}),
    #holding the uploaded images
    html.Div(id='image_list', style={'display':'none'}),
    #holds graphs after they have been created for faster access
    html.Div(id='graph_storage', style={'display':'none'}),
    html.Div(id='encoded_img_storage', style={'display':'none'})
])
    

#%%layouts
#table layout



#%% upload function
def parse_contents(contents, filename, date):
    '''
    parses contents of spreadsheath
    '''

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        global df
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    #selection of graphs
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        MD.generate_table(df),
        #horizontal line
        html.Hr() ])
    
    
def parse_images(contents, filename, date):
    '''
    parses content of the images
    '''
    #print(filename)
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
        
    ])


#%% update after data upload
         
@app.callback(Output('output-data-upload', 'children'),
              
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
#calls the upload function, updating the global variable df and also storing 

def update_output(list_of_contents, list_of_names, list_of_dates):
    print(list_of_names)
    print(list_of_dates)
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children#, df.to_json(date_format='iso', orient='split')
#%% update after image folder got parsed 
@app.callback(Output('image_list', 'component'),
              [Input('Folder_submit', 'n_clicks')],
              [State('Image_folder', 'value'),])
#calls the upload function, updating the global variable df and also storing 
def update_images(n_clicks, folder):
    find_dir='overlays'
    #finding only png files
    png_find=re.compile('.png')
    image_dict={}
    print(folder)
    print('uploading...')
    key_pattern=re.compile('W[A-Z][0-9]_S[0-9]+_T[0-9]+')
    for root, dirs, files in os.walk(folder):
        #print(dirs)
    #looks in each folder from given path
    #if folder is matching the KD pattern, the find_dir pattern and
    #if there are csv files
        if find_dir in root and len([x for x in files if re.search(png_find, x)])!=0:
            #print(find_dir)
            #finds the csv files in the folder and adds them to a list
            image_files=[x for x in files]
            for img in image_files:
                #print(img)
                #print(type(img))
                #join image and full path
                img_path=os.path.join(root, img)
                #open and encode the image with base64 encoding
                #encoded=base64.b64encode(open(img_path, 'rb').read())
                #update the dictionary
                img_key=re.search(key_pattern, img).group()
                #image_dict.update({img_key:encoded})     
                image_dict.update({img_key:img_path})
                #i_dirs.append(os.path.join(root, img)) 
                
    #print(image_dict)
    print(AD.take(5, image_dict.items()))
    print('images uploaded')
    return image_dict


#%%
#updating image upload of upload button
@app.callback([Output('output-image-upload', 'children'),
              Output('output-image-upload', 'component'),
              Output('image_type', 'children')],
              [Input('upload-image', 'contents')],
              [State('upload-image', 'filename'),
               State('upload-image', 'last_modified')])
def update_images_output(list_of_contents, list_of_names, list_of_dates):
    print(list_of_names)
    patterns=[re.compile('\.tiff$'), re.compile('\.png$'), re.compile('\.tif$'), re.compile('\.TIF$'), re.compile('\.jpeg$'), re.compile('\.jpg$')]

    
    images={}
    if list_of_contents is not None:
        for p in patterns:
            children = [
            parse_images(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        for n, c in zip(list_of_names, list_of_contents):
            #stores images in a dictionary with the filename as a key to the image
            images.update({n:c})
        for p in patterns:
            if re.search(p, n)!=None:
                filetype=re.search(p, n).group()
                break
        #print(images)
        return children, images, filetype
@app.callback(Output('test_image', 'src'),
               [Input('output-image-upload', 'component')],
               [State('upload-image', 'filename')])
def display_image(component, filename):
    print('displaying image')
    print(filename)
    return component[filename[0]]
    
#%% updating dropdown menus
#gets called when data is uploaded. It does not actually use the input
#from the upload, but gets the column names from the global variable df which is
#updated by the data upload. Outputs the column names as options ot the three
#dropdown menus
@app.callback([Output('classifier_choice', 'options'),
               Output('identifier_selector', 'options'),
               Output('timepoint_selector', 'options'),
               Output('data_selector', 'options'),],
              [Input('output-data-upload', 'children')])

def update_dropdown(contents):
    columns=df.columns
    col_labels=[{'label' :k, 'value' :k} for k in columns]
    identifier_cols=col_labels
    timepoint_cols=col_labels
    data_cols=col_labels
    #print(col_labels)

    return col_labels, identifier_cols, timepoint_cols, data_cols

#is called once you select a column from the timepoint_selector dropdown menu
@app.callback([Output('track_length_selector', 'max'),
             Output('track_length_selector', 'marks'),
             Output('track_length_selector', 'value')],
             [Input('timepoint_selector', 'value')])
#gets the minimum and maxium value of the timepoint column as selected
#and adjusts min and max values of the track_length_selector slider as first output
#and the marks on the slider as second output
def get_max_timepoints(timepoint_selector):
    min_timepoint=df[timepoint_selector].min()
    max_timepoint=df[timepoint_selector].max()
    marks={}
    value=0
    for m in range(min_timepoint, max_timepoint, 5):
        marks.update({m:str(m)})
    return max_timepoint, marks, value

#gets called when you select a value on the track_length_selector slider
@app.callback([Output('track_length_output', 'children'),
              Output('shared_data', 'children'),
              Output('flag_filter', 'options')],
              [Input('track_length_selector', 'value'),
               Input('comment_submit', 'n_clicks')],
              [State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('track_comment', 'value'),
               State('migration_data', 'clickData'),
               State('flag_options', 'value'),
               State('flag_filter', 'options'),
               State('shared_data', 'children')
               ])


#displays the selected value below the slider
#and filters the data by the minimal track length as picked in the slider
def filter_graph(track_length_selector, n_clicks, identifier_selector, timepoint_selector, 
                 track_comment, clickData, flag_options, flag_filter, shared_data):
    display_string='Minimum track length: {} {}'.format(track_length_selector, 'timepoints')
    #dff=pd.read_json(shared_data, orient='split')
    
    #grouping the data by the identifier
    track_lengths=pd.DataFrame(df.groupby(identifier_selector)[timepoint_selector].count())
    #filtering the track lengths by only selecting those with a track length higher,
    #then the one chosen in the slider
    thresholded_tracks=track_lengths[track_lengths[timepoint_selector]>track_length_selector]
    track_ids=thresholded_tracks.index.tolist()
    if shared_data==None:
        dff=df.loc[df[identifier_selector].isin(track_ids)]
    else:
        dff=pd.read_json(shared_data, orient='split').loc[df[identifier_selector].isin(track_ids)]
    #flag_filter=[{'label': 'None', 'value':'None'}]
    print(track_comment)
    #flagging framework
    if clickData!=None:
        print(clickData['points'][0]['hovertext'])
        #read previously filtered data frame
        #create a new column and fill it
        try:
            dff['flags']
        except KeyError:
            dff['flags']='None'
            print('flags resetted')
        #get the unique ID from the hovertext
        ID=clickData['points'][0]['hovertext']
        
        #check flag options. If single, add the submitted comment only to 
        #the selected timepoint
        if flag_options=='single':
            dff.loc[dff['unique_time']==ID, 'flags']=track_comment
            print('single')
        #if 'all' remove the timepoint component from the string and add the comment
        #to all datapoints with that ID
        if flag_options=='all':
           print('all')
           pattern=re.compile('_T.+')
           try:
               ID=ID.replace(re.search(pattern, ID).group(),'')
               dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment
           except AttributeError:
               pass

        flags=list(dff['flags'].unique())
        flag_filter=[{'label' :k, 'value' :k} for k in flags]
        print(flags)

        #print(dff.loc[dff[identifier_selector]==ID, 'flags'])
           #print(dff[dff[identifier_selector]==ID])
    dff=dff.to_json(date_format='iso', orient='split') 
    print(flag_filter)
    return display_string, dff, flag_filter
#%% update graph 

#creates a figure when the display plots button is pressed.
#also takes the states of the dropdown menus: classifier_choice, identifier_selector
#and timepoint_selector and feeds it as options to the graph.
#it takes the data from the hidden div 'shared_data' as input data for the graph
@app.callback([Output('migration_data', 'figure'),
               Output('graph_storage', 'component')],
              [Input('plot_button', 'n_clicks')],
              [State('graph_selector', 'value'),
               State('shared_data', 'children'),
               State('classifier_choice', 'value'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('data_selector', 'value'),
               State('distance_filter', 'value'),
               State('graph_storage', 'component'),
               State('graph_reuse', 'value'),
               State('flag_filter', 'value')])

def plot_graph(n_clicks, graph_selector, shared_data, classifier_choice,
               identifier_selector, timepoint_selector, data_selector, distance_filter, 
               graph_storage, graph_reuse, flag_filter):
    #if the graph storage is empty an empty dictionary will be created
    if graph_storage==None or graph_reuse=='no':
        graph_storage={}
    #data is read from the shared data div
    dff=pd.read_json(shared_data, orient='split')
    print(flag_filter)
    print(type(flag_filter))
    
    if flag_filter is not None:
        for i in flag_filter:
            dff=dff[dff['flags']!=i]
    #if the current graph option is already stored in the graph storage, 
    #the stored graph will be displayed
    if graph_selector in graph_storage.keys():
        return graph_storage[graph_selector], graph_storage
    #oherwise the graph will be picked from the graph options dictionary, the figure will be created,
    #the graph_storage dictionary will be updated and the figure and updated dictionary will be returned
    else:
        graph_options={'lineplot':GD.lineplot, 'migration_distance':GD.migration_distance, 'time_series':GD.time_series}
        fig=graph_options[graph_selector](dat=dff, classifier_column=classifier_choice, 
                            identifier_column=identifier_selector,
                            timepoint_column=timepoint_selector, data_column=data_selector, distance_filter=distance_filter, testmode=True)
        graph_storage.update({graph_selector:fig})
        return fig, graph_storage

#%% atm changing to click data showing full video 
@app.callback([Output('image_list', 'children'),
               Output('image_name', 'children')],
              [Input('migration_data', 'clickData')],
              [State('image_list','component'),
               State('image_type', 'children'),
               State('Image_selector', 'value'),
               State('shared_data', 'children')])
def update_image_overlay(hoverData, image_dict, image_type, image_selector, shared_data):
    #start_time=time.time()
    #Error message if no images have been uploaded
    if len(image_dict)==0:
        print('No images have been uploaded')
    data=pd.read_json(shared_data, orient='split')
    #getting hovertext from hoverdata and removing discrepancies between hover text and filenames
    #(stripping of track_ID)
    try:
        #exclusion criterium if timepoint is already there
        exclusion=re.compile('_E+.*')
        track_pattern=re.compile('_E.+?(?=\_)')
        #taken from hovertext should be something like 'WB2_S1324_E4'
        ID_or=hoverData['points'][0]['hovertext']
        
        #getting the track ID of the individual cell. Something like '_E4'
        track_ID=re.search(track_pattern, ID_or).group()

        
        print('track_ID: ', track_ID)
        #getting the ID to the images by stripping off extensions
        #something like 'WB2_S1324
        ID=ID_or.replace(re.search(exclusion, ID_or).group(),'')
        print('ID_or: ', ID_or)
        print('ID: ', ID)
    except AttributeError:        
        #exclusion criterium if timepoint isnot in hovertext
        exclusion_nt=re.compile('_E+.*')
        ID_or=hoverData['points'][0]['hovertext']
        
        #getting the track ID of the individual cell. Something like '_E4'
        track_ID=re.search(exclusion, ID_or).group()

        
        print('track_ID: ', track_ID)
        #getting the ID to the images by stripping off extensions
        #something like 'WB2_S1324
        ID=ID_or.replace(re.search(exclusion, ID_or).group(),'')
        print('ID_or: ', ID_or)
        print('ID: ', ID)
        #hovertext in graph needs to be changed back to uniqe time when region should be marked
        ID=hoverData['points'][0]['hovertext'].replace(re.search(exclusion_nt, hoverData['points'][0]['hovertext']).group(),'')
        print('ID: ',ID)
    #searching the dictionary for keys fitting the hovertext   
    imagelist=[i for i in image_dict.keys() if ID in i]
    if len(imagelist)==0:
        print('Key Error, no images associated with {} found.'.format(ID))
    
    #sort images 
    imagelist=natsorted(imagelist)
    #getting dimensions of image
    img_size=imageio.imread(image_dict[imagelist[0]]).shape
    #inidiate a dictionary to coordinates for images. Including image shape
    loaded_dict={'shape':img_size}
    for i in imagelist:
        #adding the unoque ID of the cell back into the key of the image
        #to get X, Y coordinates. Something like 'WB2_S1324_E4_T1'
        tracking_ID=i.replace(re.search('_T', i).group(), track_ID+'_T')
        print('tracking_ID: ',tracking_ID)
        img=image_dict[i]
        try:
            x_coord=int(data[data['unique_time']==tracking_ID]['Location_Center_X'].values)
            y_coord=int(data[data['unique_time']==tracking_ID]['Location_Center_Y'].values)
            #img[y_coord-5:y_coord+5, x_coord-5:x_coord+5]=[255, 0, 0]
       #if no data for timepoint is found print error message
        except TypeError:
            print('no segmentation found for', i)
        
        loaded_dict.update({img:[x_coord, y_coord]})
    print(type(loaded_dict))
    print(loaded_dict)    
    print('encoding complete')
    return json.dumps(loaded_dict), ID_or
    #return 'data:video/mp4;base64,{}'.format(temp_avi.decode()), ID_or

#%% flagging framework
@app.callback(Output('click-data', 'children'),
              [Input('migration_data', 'clickData')])    
def display_click_data(clickData):
    '''getting click data from graph and displaying it
    '''
    return json.dumps(clickData, indent=2)



#%% scrollable images
@app.callback([Output('image_slider', 'max'),
             Output('image_slider', 'marks'),
             Output('image_slider_output', 'value')],
             [Input('image_list', 'children')])
#gets the minimum and maxium value of the timepoint column as selected
#and adjusts min and max values of the track_length_selector slider as first output
#and the marks on the slider as second output
def get_image_timepoints(image_dict):
    image_dict=json.loads(image_dict)
    max_timepoint=len(image_dict.keys())-1
    marks={}
    for m in range(0, max_timepoint, 5):
        marks.update({m:str(m)})
    image_slider_output='Image{} selected'.format(image_dict)
    return max_timepoint, marks, image_slider_output  
#updating image graph
@app.callback(Output('image-overlay', 'figure'),
              [Input('image_slider', 'value')],
              [State('image_list', 'children')])

def update_image_graph(value, image_dict):
    image_dict=json.loads(image_dict)
    print(AD.take(5, image_dict.items()))
    img=list(image_dict.keys())[value+1]
    print(img)
    #retrieving image shape from dictionary
    x=image_dict['shape'][0]
    y=image_dict['shape'][1]
   
# =============================================================================
#     temp=Image.fromarray(img)
#     temp.save('temp.png')
# =============================================================================
    
    with open(img, 'rb') as f:
        encoded=base64.b64encode(f.read())
    print('encoding complete')

    return GD.image_graph('data:image/png;base64,{}'.format(encoded.decode()), x_C=x, y_C=y, 
                          X_S=image_dict[img][0], Y_S=image_dict[img][1])

#%% Download csv file
@app.callback(Output('download-link', 'href'),
              [Input('save_df', 'n_clicks')],
              [State('shared_data', 'children')],               )
def update_download_link(shared_data):
    data=pd.read_json(shared_data, orient='split')
    csv_string = data.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
    return csv_string
    
# =============================================================================
# @app.callback(Output('shared_data2', 'children'),
#                 [Input('comment_submit', 'n_clicks')],
#                 [State('shared_data', 'children'),
#                 State('track_comment', 'value'),
#                 State('migration_data', 'clickData'),
#                 State('identifier_selector', 'value'),
#                 State('flag_options', 'value')],)
# def flag_data(n_clicks, shared_data, track_comment, click_data, identifier_selector, flag_options):
#     '''
#     gets the click data and allows you to add a comment to a new copy of the data frame
#     You have the option to either add that comment to the individual timepoint selected, or to
#     all timepoints of the track ID
#     '''
# 
#     print(click_data['points'][0]['hovertext'])
#     #read previously filtered data frame
#     dff=pd.read_json(shared_data, orient='split')
#     #create a new column and fill it
#     dff['flags']=float('nan')
#     #get the unique ID from the hovertext
#     ID=click_data['points'][0]['hovertext']
#     
#     #check flag options. If single, add the submitted comment only to 
#     #the selected timepoint
#     if flag_options=='single':
#         dff.loc[dff['unique_time']==ID, 'flags']=track_comment
#     #if 'all' remove the timepoint component from the string and add the comment
#     #to all datapoints with that ID
#     if flag_options=='all':
#        pattern=re.compile('_T.+')
#        try:
#            ID=ID.replace(re.search(pattern, ID).group(),'')
#        except AttributeError:
#            dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment
#        #print(dff[dff[identifier_selector]==ID])
#         
#     dff=dff.to_json(date_format='iso', orient='split')
#   
#     return dff
# =============================================================================

#%% Display image overlay, revert to this option until image manipulation is stable
# =============================================================================
# @app.callback(Output('image-overlay', 'src'),
#               [Input('migration_data', 'hoverData')],
#               [State('image_list','component'),
#                State('image_type', 'children'),
#                State('Image_selector', 'value'),])
# def update_image_overlay(hoverData, image_dict, image_type, image_selector):
#     start_time=time.time()
# 
#     #exclusion criterium if timepoint is already there
#     exclusion=re.compile('_E.+?(?=\_)')
#     #print(image_type)
#     
#     #exclusion criterium if timepoint isnot in hovertext
#     exclusion_nt=re.compile('_E+.*')
#     #getting hovertext from hoverdata and removing discrepancies between hover text and filenames
#     try:
#         ID=hoverData['points'][0]['hovertext'].replace(re.search(exclusion, hoverData['points'][0]['hovertext']).group(),'')
#     except AttributeError:
#         ID=hoverData['points'][0]['hovertext'].replace(re.search(exclusion_nt, hoverData['points'][0]['hovertext']).group(),'')
#         ID=ID+'_T1'
#     #if re.search('_T[0-9]+', ID)==None:
#         
#     print(ID)
#     #searching the dictionary for keys fitting the hovertext
#  
#    
#     image=image_dict[ID]
#     #base64 encode the image
#     with open(image, 'rb') as f:
#         encoded=base64.b64encode(f.read())
#     #update the dictionary with the encoded image
#     image_dict.update({ID:encoded})
#     print(type(image))
#     #return the encoded image
#     print("--- %s seconds ---" % (time.time() - start_time))
#     return 'data:image/png;base64,{}'.format(encoded.decode())  
# =============================================================================

  
#%%    
    
    #update the dictionary with the encoded image
    #image_dict.update({ID:encoded})
    #print(type(image))
    #return the encoded image
    #print("--- %s seconds ---" % (time.time() - start_time))
    #return 'data:image/png;base64,{}'.format(encoded.decode())  
       
# =============================================================================
#         
#         if encoded_images==None:
#         encoded_images={}
# 
#     if ID in encoded_images.keys():
#         print("--- %s seconds ---" % (time.time() - start_time))
#         encoded=encoded_images[ID][0]
#         return 'data:image/png;base64,{}'.format(encoded.decode()), encoded_images
#     else:
#         image=image_dict[ID]
#         #base64 encode the image
#         encoded=base64.b64encode(open(image, 'rb').read())
#         #update the dictionary with the encoded image
#         encoded_images.update({ID:[encoded]})
#         print(type(image))
#         #return the encoded image
#         print("--- %s seconds ---" % (time.time() - start_time))
#         return 'data:image/png;base64,{}'.format(encoded.decode()), encoded_images 
# =============================================================================
    
# =============================================================================
#     if type(image)==bytes:
#         print("--- %s seconds ---" % (time.time() - start_time))
#         print(type(image))
#         return 'data:image/png;base64,{}'.format(image.decode()) 
#     if type(image)==str: 
#         #base64 encode the image
#         encoded=base64.b64encode(open(image, 'rb').read())
#         #update the dictionary with the encoded image
#         image_dict.update({ID:encoded})
#         print(type(image))
#         #return the encoded image
#         print("--- %s seconds ---" % (time.time() - start_time))
#         return 'data:image/png;base64,{}'.format(encoded.decode())    
# =============================================================================
    
    
# =============================================================================
#         if re.search(ID, k) !=None:           
#             #image_name=k.replace(re.search(exclusion, k).group(), '')
#             print(k)
#             print(ID)
#             #getting the image from the dictionary by using it's name as the key
#             image=image_dict[k]
#             #base 64 encode the image
#             encoded=base64.b64encode(open(image, 'rb').read())
#             #return the encoded image
#             print("--- %s seconds ---" % (time.time() - start_time))
#             return 'data:image/png;base64,{}'.format(encoded.decode())
#             #break out of the loop once the first image is found 
#             break
# =============================================================================




#%%
if __name__ == '__main__':
    app.run_server(debug=True)