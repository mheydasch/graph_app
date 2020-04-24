#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:11:11 2019
@author: max
"""
'''

Current rules for pattern:
    The order of the pattern in the column unique_time must be Site_ID, TrackID, Timepoint
    The three IDs must be seperated by underscores (_). These underscores must not be 
    captured by the regular expression.
    
    Each pattern must be precided by a number e.g.: WB2_E3_T5
    
    The patterns for Site_ID and Timepoint must be the same in the images as well as in the
    data frame
    
    The timepoint must be the same in the timepoint column as well as in the pattern, without
    the preceeding letter.
    
    
    
to do:
    currently any 'T' (timepoint indicator) will fuck the image correlation up
    if it does exist anywhere else in the name
    Currently does not work if any other order than Site_ID, TrackID, Timpepoint is used
    currently does not work without x, y coordinates
    Important:
        images with albertos dataset are not containing all cells
        comment adding for albertos dataset does not work
        
    remove seg error from settings file, will cause an error when the dataframe does not have flags column
'''
import base64
import datetime
import io
from PIL import Image
from PIL import ImageEnhance
import urllib.parse
#from flask_caching import Cache
import uuid

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import imageio
import json
import plotly.graph_objects as go

from natsort import natsorted

import pandas as pd
import sys
import os
import re
from pathlib import Path


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
# =============================================================================
# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory',
#     'CACHE_THRESHOLD': 5  # should be equal to maximum number of active users
# })
# =============================================================================



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
    # Allow only one file to be uploaded
    multiple=True), 
    #menus for image uploading
    #needs to be full path to the image folder
    MD.Image_folder(),
    MD.Folder_submit(),
    #menus for pattern uploading of IDs,
    #needs to be a regular expression
    MD.ID_pattern(),
    MD.ID_submit(),
    #calling menus
    html.Hr(),
    html.Div(
        [html.Div([dcc.Markdown('''**Data organization**'''),
        html.P('How is your data formatted?'),
        MD.datatype_selector(),
        html.P('Select the columns that hold your data, if x,y coordinates, first selected is treated as x coordinate:'),
        MD.data_selector(df),
        html.P('Select the column holding your not normalized x,y coordinates'),
        MD.coordinate_selector(df),
        html.P('Select the column which holds the classifier of your groups:'),        
        MD.classifier_choice(df),
        html.P('Select the column which holds the identifier for each unique item:'),
        MD.identifier_selector(df),
        html.P('Select  a column with format \'Wellname_Sitename_TrackID_Timepoint\''),
        MD.unique_time_selector(df),        
        html.P('Select the column which holds the timepoints:'),
        MD.timepoint_selector(df),
        
        dcc.Markdown('''**Data processing**'''),
        html.P('Select which measurement you want to average'),
        MD.average_selector(df),
        html.P('Select by what variable the average should be grouped'),
        MD.average_grouper(df),
        MD.average_button(),], className= 'six columns'),
        
        

        

    
    
        html.Div([dcc.Markdown('''**Data filtering**'''), 
        MD.RadioItems(),
        html.P('Select the minimum track length'),
        MD.track_length_selector(),
        #displays the number selected by track_length selector
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
        MD.plot_button(),
        html.P('Do you want to hide plots?'),
        MD.plot_hider(),
        html.P('Do you want exclude flagged images from the plots?'),
        MD.exclude_seen(),
        ], className='six columns'
        
        
    )], className='row'),


#tabs section start
    dcc.Tabs(id='tabs', children=[
             dcc.Tab(label='Table', 
                     children= [html.Table(id='output-data-upload'),

                                            ]),
                     #calling the table
                             
             dcc.Tab(label='Graph',
                     #calling the graph 
                     children= [html.Div([
                                     #graph for showing data
                                     html.Div([html.P('Graph Display: '),
                                               html.Div([dcc.Graph(id='migration_data', )],
                                                        id='graph_div'),
                                               MD.plot_save_button(),          
                                               ], 
                                          className= 'six columns'),
                                               #graph for showing the image
                                     html.Div([dcc.Graph(id='image-overlay',
                                                         ),
                                               #slider for selection of image
                                               MD.image_slider(),
                                               
                                               html.Div(id='image_slider_output', style={'margin-top': 20},),
                                               html.P('Adjust the brightness of the image'),
                                               MD.brightness_slider(),
                                               html.Div([
                                                    dcc.Markdown(("""
                                                         
                                        
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
                                                MD.save_path(),
                                                MD.save_button(),
# =============================================================================
#                                                 html.A(
#                                                         'Download Data',
#                                                         id='download-link',
#                                                         download="rawdata.csv",
#                                                         href="",
#                                                         target="_blank"
#                                                         ),
# =============================================================================
                                                  ],className='six columns', )
                                          
                                               
                                 ], className='row')]
                                 
                     )
            ]),
#tabs section end    
           
                                 

 
                             
                    



    #hidden divs for storing data
    #holds the dataframe after filtering by track length
    #dcc.Store(id='shared_data', storage_type='local'),
    #holds the unfiltered dataframe with user added flags
    dcc.Store(id='session_id', storage_type='session', data=str(uuid.uuid4())),
    dcc.Store(id='flag_storage', storage_type='memory'),
    #stores the patterns for the ID
    dcc.Store(id='pattern_storage', storage_type='memory'),
    #holding the uploaded images
    dcc.Store(id='image_list', storage_type='memory'),
    #holds graphs after they have been created for faster access
    dcc.Store(id='graph_storage', storage_type='memory'),
    #stores the dictionary of images
    dcc.Store(id='image_dict', storage_type='memory'),
    #stores raw click data to be retrieved by update_flags
    dcc.Store(id='click_data_storage', storage_type='memory'),
    #empty storage for settings sham output
    dcc.Store(id='test_storage', storage_type='memory'),
    #dcc.Store(id='df_storage', storage_type='session'),

])
    


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
            print(len(df), 'rows')
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

        MD.generate_table(df[0:20]),
        #horizontal line
        html.Hr() ])
    
# =============================================================================
#         dcc.Store(id='df_storage', storage_type='session', 
#                   data=df.to_json(date_format='iso', orient='split'))])
# =============================================================================
    


#%% update after data upload
         
@app.callback(Output('output-data-upload', 'children'),
#              
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
        return children



#%% updating dropdown menus
#gets called when data is uploaded. It does not actually use the input
#from the upload, but gets the column names from the global variable df which is
#updated by the data upload. Outputs the column names as options ot the three
#dropdown menus
@app.callback([Output('classifier_choice', 'options'),
               Output('identifier_selector', 'options'),
               Output('timepoint_selector', 'options'),
               Output('data_selector', 'options'),
               Output('unique_time_selector', 'options'),
               Output('coordinate_selector', 'options'),
               Output('average_selector', 'options'),
               Output('average_grouper', 'options')],
              [Input('output-data-upload', 'children'),
               Input('flag_storage', 'data')])

def update_dropdown(contents, flag_storage):
    print('updating menus...')
    ctx= dash.callback_context
    #checking which input was triggeredn
    if ctx.triggered[0]['prop_id']=='output-data-upload.children':
        columns=df.columns

    if ctx.triggered[0]['prop_id']=='flag_storage.data':
        dff=pd.read_csv(flag_storage, index_col='index')
        columns=dff.columns

    col_labels=[{'label' :k, 'value' :k} for k in columns]
    identifier_cols=col_labels
    timepoint_cols=col_labels
    data_cols=col_labels
    unique_time_columns=col_labels
    coordinates=col_labels
    average=col_labels
    grouper=col_labels
    print('... menus updated')

    return (col_labels, identifier_cols, timepoint_cols, data_cols, 
            unique_time_columns, coordinates, average, grouper)

#%% update after image folder got parsed 
@app.callback(Output('image_list', 'data'),
              [Input('Folder_submit', 'n_clicks')],
              [State('Image_folder', 'value'),
              State('pattern_storage', 'data')])
def update_images(n_clicks, folder, pattern_storage):
    find_dir='overlays'
    print('pattern storage: ', pattern_storage)
    #gets the pattern of the trackid from the input pattern
    trackid_pattern=re.compile(r'\(\?P\<TrackID\>.*?(?=\()')
    #removes the trackid pattern from the pattern to find images
    pattern=pattern_storage[0].replace(re.search(trackid_pattern, pattern_storage[0]).group(), '') 
    #finding only png files
    png_find=re.compile('.png')
    image_dict={}
    print(folder)
    print('uploading...')
    key_pattern=re.compile(pattern)
    print(key_pattern)
    #key_pattern=re.compile('W[A-Z][0-9]_S[0-9]+_T[0-9]+')
    for root, dirs, files in os.walk(folder):
        #print(dirs)
    #looks in each folder from given path
    #if folder is matching the KD pattern, the find_dir pattern and
    #if there are csv files
        if find_dir in root and len([x for x in files if re.search(png_find, x)])!=0:
            #print(find_dir)
            #finds the csv files in the folder and adds them to a list
            image_files=[x for x in files if re.search(png_find, x)!=0]
            for img in image_files:
                #print(img)
                #print(type(img))
                #join image and full path
                img_path=os.path.join(root, img)
                #open and encode the image with base64 encoding
                #encoded=base64.b64encode(open(img_path, 'rb').read())
                #update the dictionary
                #gets the Site_ID and timepoint from the images
                try:
                    Site_ID, Timepoint =re.search(key_pattern, img).group('Site_ID', 'Timepoint')
                except AttributeError:
                    break 
                #adds them together as the image key
                img_key=Site_ID+Timepoint
                #img_key=re.search(key_pattern, img).group()
                image_dict.update({img_key:img_path})
                #i_dirs.append(os.path.join(root, img)) 
    if bool(image_dict):            
        print(AD.take(5, image_dict.items()))
        print('images uploaded')
    else:
        print('Error: No images have been found')
    return image_dict
#%% ID pattern recognition
@app.callback([Output('pattern_storage', 'data'),],
              [Input('ID_submit', 'n_clicks')],
              [State('ID_pattern', 'value'),])

#gets triggered when the pattern submit button is pressed and simply
#stores the submitted regex pattern
def update_ID_pattern(n_clicks, value, ):
    print(value, 'submitted')
    
    return [str(value)], 
    


#%%
#gets called when you select a value on the track_length_selector slider
@app.callback(Output('track_length_output', 'children'),
              [Input('track_length_selector', 'value'),
               Input('flag_filter', 'value')],
              [State('flag_storage', 'data'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value')
               ])


#displays the selected value below the slider
#and filters the data by the minimal track length as picked in the slider
def filter_graph(track_length_selector, flag_filter, flag_storage, identifier_selector, timepoint_selector, 
                  ):
    display_string='Minimum track length: {} {}'.format(track_length_selector, 'timepoints')
    #grouping the data by the identifier
    print('tracks with length < {} have been excluded'.format(track_length_selector))

    return display_string

#%% storing flags to flag sotrage once the submit button is pressed
@app.callback([Output('flag_storage', 'data'),
              Output('flag_filter', 'options')],
              [Input('comment_submit', 'n_clicks'),
               Input('average_button', 'n_clicks')],
              [State('identifier_selector', 'value'),
               State('track_comment', 'value'),
               State('migration_data', 'clickData'),
               State('flag_options', 'value'),
               State('flag_filter', 'options'),
               State('flag_storage', 'data'),
               State('click_data_storage', 'data'),
               State('unique_time_selector', 'value'),
               State('pattern_storage', 'data'),
               State('average_selector', 'value'),
               State('average_grouper', 'value'),
               State('classifier_choice', 'value')
               ])
def update_flags(n_clicks, comment_submit, identifier_selector, 
                 track_comment, clickData, flag_options, flag_filter, 
                 flag_storage, click_data_storage, unique_time_selector, pattern_storage,
                 average_selector, average_grouper, classifier_choice):
    #adding average values
    ctx= dash.callback_context
    
    #adding flags
    print(track_comment)
    print('pattern storage: ', pattern_storage)
    #get patterns from user input
    pattern=re.compile(pattern_storage[0])    
    #if flag storage not empty load it
    if flag_storage != None: 
        dff=pd.read_csv(flag_storage, index_col='index')
    #otherwise load global dataframe
    else:
        dff=df
        print('flag_storage empty')
    #if click_data is provided
    print(len(df), 'rows')
    if ctx.triggered[0]['prop_id']=='average_button.n_clicks':
        print('Calculating averages of {} per {} for each class of {}...'.format(average_selector,
              average_grouper, classifier_choice))
        dff=AD.calc_average(dat=dff, classifier_column=classifier_choice, average_column=average_selector,
                        grouping_column=average_grouper)
    print('...done')
        
    #add comments if the comment submit button was pressed
    if ctx.triggered[0]['prop_id']=='comment_submit.n_clicks':
    
        if click_data_storage!=None:
            
            print('clickdata: ',click_data_storage)
            #get relevant click data
            if 'customdata' in click_data_storage['points'][0]:
                ID=click_data_storage['points'][0]['customdata']
            if 'hovertext' in click_data_storage['points'][0]: 
                ID=click_data_storage['points'][0]['hovertext']
    
            print('ID: ', ID)
            #if dataframe does not have the 'flag' column create it
            #create a new column and fill it
            if 'flags' not in dff.columns:
                dff['flags']='None'
                print('flags resetted')
            
            #check flag options. If single, add the submitted comment only to 
            #the selected timepoint
            if flag_options=='single':
                dff.loc[dff[unique_time_selector]==ID, 'flags']=track_comment
                #print('single')
            #if 'all' remove the timepoint component from the string and add the comment
            #to all datapoints with that ID like 'WB2_S1324_E4'
            if flag_options=='all':
               #print('all')
               try:
                   Timepoint=re.search(pattern, ID).group('Timepoint')
                   ID=ID.replace(Timepoint,'')
                   print('Timless ID: ', ID)
                   dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment
               except AttributeError:
                   print('No Timepoint found')  
                   dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment
    
            #create a list of unique flags
            flags=list(dff['flags'].unique())
            #create an options attribute of the flags for the flag_filter dropdwon menu
            flag_filter=[{'label' :k, 'value' :k} for k in flags]
            print('flags', flags)
    #flag_storage=dff.to_dict() 
    print(len(dff), 'rows')
    #getting the path of the app
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #creating a folder 'Cache' if it does not already exist
    AD.createFolder(os.path.join(dir_path, 'Cache'))
    #savint the flagged dataframe as 'temp.csv' in the 'Cache' folder
    flag_storage=os.path.join(dir_path, 'Cache', 'temp.csv')
    dff.to_csv(flag_storage, index_label='index')

    
    print('flag_filter', flag_filter)    
    return flag_storage, flag_filter

#%% update graph 

#creates a figure when the display plots button is pressed.
#also takes the states of the dropdown menus: classifier_choice, identifier_selector
#and timepoint_selector and feeds it as options to the graph.
#it takes the data from the hidden div 'shared_data' as input data for the graph
@app.callback([Output('migration_data', 'figure'),
               Output('graph_storage', 'data')],
              [Input('plot_button', 'n_clicks')],
              [State('graph_selector', 'value'),
               State('classifier_choice', 'value'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('data_selector', 'value'),
               State('distance_filter', 'value'),
               State('graph_storage', 'data'),
               State('graph_reuse', 'value'),
               State('flag_filter', 'value'),
               State('unique_time_selector', 'value'),
               State('flag_storage', 'data'),
               State('track_length_selector', 'value'),
               State('exclude_seen', 'value'),
               State('pattern_storage', 'data')])

def plot_graph(n_clicks, graph_selector, classifier_choice,
               identifier_selector, timepoint_selector, data_selector, distance_filter, 
               graph_storage, graph_reuse, flag_filter, unique_time_selector, flag_storage,
               track_length_selector, exclude_seen, pattern_storage):
    
    
    
    #if the graph storage is empty an empty dictionary will be created
    if graph_storage==None or graph_reuse=='no':
        graph_storage={}
    #data is read from the shared data div
    pattern=re.compile(pattern_storage[0])
    
    #try to read flag sotrage.
    if flag_storage != None:
        dff=pd.read_csv(flag_storage, index_col='index')
    else:
        dff=pd.DataFrame(df)
    #force appropriate datatypes
# =============================================================================
#     dff[classifier_choice]=dff[classifier_choice].astype(str)
#     dff[identifier_selector]=dff[identifier_selector].astype(str)
#     dff[timepoint_selector]=dff[timepoint_selector].astype(int)
#     for i in data_selector:
#         dff[i]=dff[i].astype(float)
#     dff[unique_time_selector]=dff[unique_time_selector].astype(str)
# =============================================================================
    
    
    track_lengths=pd.DataFrame(dff.groupby(identifier_selector)[timepoint_selector].count())
    #filtering the track lengths by only selecting those with a track length higher,
    #then the one chosen in the slider
    thresholded_tracks=track_lengths[track_lengths[timepoint_selector]>track_length_selector]
    track_ids=thresholded_tracks.index.tolist()
    dff=dff.loc[dff[identifier_selector].isin(track_ids)]
    
    exclude=[]
    if exclude_seen=='Yes':
        if 'flags' in dff.columns:
            #for each flag in the data frame that is note None get the unique_time_selector
            for i in dff[dff['flags']!='None'][unique_time_selector]:
                #add the Site_ID to the list
                exclude.append(re.search(pattern, i).group('Site_ID'))
            for i in set(exclude):
                print('excluded{}from the list'.format(i))
                #for each item of the list get all items of the dataframe
                #where i is not part of the unique time column 
                dff=dff[dff[unique_time_selector].str.contains(i)!=True]
        
        
        
    
    print(flag_filter)
    #print(type(flag_filter))
    if flag_filter is not None and 'flags' in dff.columns:
        for i in flag_filter:
            dff=dff[dff['flags']!=i]
    #if the current graph option is already stored in the graph storage, 
    #the stored graph will be displayed
    if graph_selector in graph_storage.keys():
        return graph_storage[graph_selector], graph_storage
    #oherwise the graph will be picked from the graph options dictionary, the figure will be created,
    #the graph_storage dictionary will be updated and the figure and updated dictionary will be returned
    else:
        graph_options={'lineplot':GD.lineplot, 'migration_distance':GD.migration_distance, 'time_series':GD.time_series,
                       'corel_plot': GD.corel_plot, 'flag_count':GD.flag_count, 'boxplot':GD.boxplot}
        fig=graph_options[graph_selector](dat=dff, classifier_column=classifier_choice, 
                            identifier_column=identifier_selector,
                            timepoint_column=timepoint_selector, data_column=data_selector, 
                            distance_filter=distance_filter,
                            unique_time_selector=unique_time_selector, testmode=False)
        graph_storage.update({graph_selector:fig})
        return fig, graph_storage

#saving the graph to svg at same location as specified for datatable
@app.callback(Output('plot_save_button', 'children'),
      [Input('plot_save_button', 'n_clicks')],
      [State('migration_data', 'figure'),
       State('save_path', 'value'),
       State('graph_selector', 'value')],)
                             
def download_svg(n_clicks, migration_data, save_path, graph_selector):
    #print(save_path)
    fig=go.Figure(migration_data)
    #print(fig)
    path=save_path
    prefix=graph_selector
    #if the path dictates a csv file, the filename will be replaced
    #by an appropriate graph name
    if path.endswith('.csv'):
        path=AD.go_one_up(path, mode='file')
        filename=prefix+'.svg'
        path=os.path.join(path, filename)
    #if path does not end in svg, add appropriate filename
    if path.endswith('.svg')!=True:
        filename=prefix+'.svg'
        path=os.path.join(path, filename)
    fig.write_image(path)
    print('file saved under', path)
    return 'Download plot as svg'
#%% 
@app.callback(Output('image_dict', 'data'),
              [Input('migration_data', 'clickData')],
              [State('image_list','data'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('unique_time_selector', 'value'),
               State('coordinate_selector', 'value'),
               State('pattern_storage', 'data'),
               State('flag_storage', 'data'),
               State('track_length_selector', 'value')],)
def update_image_overlay(hoverData, image_dict, 
                         identifier_selector, timepoint_selector, unique_time_selector,
                         coordinate_selector, pattern_storage, flag_storage, track_length_selector):

    print('pattern storage: ', pattern_storage)
    try:
        pattern=re.compile(pattern_storage[0])
    except TypeError:
        print('Error: no pattern has been submitted')
    #Error message if no images have been uploaded
    if type(image_dict)!= None or len(image_dict)==0:
        print('No images have been uploaded')
    #read data from flag_storage if exists    
    if flag_storage != None:
        data=pd.read_csv(flag_storage, index_col='index')
    #else from shared data
    else:
        data=pd.DataFrame(df)
    track_lengths=pd.DataFrame(data.groupby(identifier_selector)[timepoint_selector].count())
    #filtering the track lengths by only selecting those with a track length higher,
    #then the one chosen in the slider
    thresholded_tracks=track_lengths[track_lengths[timepoint_selector]>track_length_selector]
    track_ids=thresholded_tracks.index.tolist()
    data=data.loc[data[identifier_selector].isin(track_ids)]
    #getting hovertext from hoverdata and removing discrepancies between hover text and filenames
    #(stripping of track_ID)
    ID_or=hoverData['points'][0]['hovertext']
    print('ID_or:', ID_or)
    try:
        #getting the different components of the ID. Such as:
        #'WB2' '_S0520' '_E3' '_T40'         
        Site_ID, track_ID, Timepoint =re.search(pattern, ID_or).group(
                 'Site_ID', 'TrackID', 'Timepoint')

        #exclusion criterium if timepoint is already there
        exclusion=track_ID+Timepoint
        #print(Timepoint, track_ID, Wellname, Sitename)
        print('exclusion:', exclusion)
        print('track_ID: ', track_ID)
        #getting the ID to the images by stripping off extensions
        #something like 'WB2_S1324
        ID=ID_or.replace(exclusion,'')
        print('ID_or: ', ID_or)
        print('ID: ', ID)
    except AttributeError:       
        print('Error: unrecognized pattern')
# =============================================================================
#         #exclusion_nt=re.compile('_E+.*')
#         Wellname, Sitename, track_ID =re.search(timeless_pattern, ID_or).group(
#                 'Well', 'Site', 'TrackID')
#                 #exclusion criterium if timepoint isnot in hovertext
#         exclusion=track_ID
#         #getting the track ID of the individual cell. Something like '_E4'
#         #track_ID=re.search(exclusion, ID_or).group()
# 
#         
#         print('track_ID: ', track_ID)
#         #getting the ID to the images by stripping off extensions
#         #something like 'WB2_S1324
#         ID=ID_or.replace(exclusion, '')
#         print('ID_or: ', ID_or)
#         print('ID: ', ID)
#         #hovertext in graph needs to be changed back to uniqe time when region should be marked
#         #ID=hoverData['points'][0]['hovertext'].replace(re.search(exclusion_nt, hoverData['points'][0]['hovertext']).group(),'')
#         #print('ID: ',ID)
# =============================================================================
    #searching the dictionary for keys fitting the hovertext 
    try:
        imagelist=[i for i in image_dict.keys() if ID in i]
    except AttributeError:
        print('No images have been uploaded')
    if len(imagelist)==0:
        print('Key Error, no images associated with {} found.'.format(ID))
    
    #sort images 
    imagelist=natsorted(imagelist)
    #getting dimensions of image
    img_size=imageio.imread(image_dict[imagelist[0]]).shape
    #inidiate a dictionary to coordinates for images. Including image shape
    loaded_dict={'shape':img_size,}
    #time_pattern=re.compile('_T+[0-9]*')
    timenumber_pattern=re.compile('[0-9]+')
   
    
    #getting part of the data that is from the current image
    #gets the image ID, something like  WB2_S1324_T1
    print('imagelist[0]', imagelist[0])
    Image_ID= imagelist[0]
    print('Image_ID', Image_ID)
    #get the time, something like _T1
    #Time_ID= re.search(time_pattern, Image_ID).group()
    print('Timepoint', Timepoint)
    #get the ID only from the Site, something like WB2_S1324
    #Site_ID= Image_ID.replace(Timepoint, '')
    print('Site_ID', Site_ID)
    #gets part of the dataframe that is from the current image
    Site_data=data[data[identifier_selector].str.contains(Site_ID)]
    #gets the part of the timepoint which is not a number
    timeindicator_pattern=re.compile('.*?(?=[0-9])')
    timeindicator=re.search(timeindicator_pattern, Timepoint).group()
    
    #getting all the images for the respective timepoints
    for i in imagelist:
        #print(i)
        #adding the unique ID of the cell back into the key of the image
        #to get X, Y coordinates. Something like 'WB2_S1324_E4_T1'        
        tracking_ID=i.replace(re.search(timeindicator, i).group(), track_ID+timeindicator)
        #print('tracking_ID: ',tracking_ID)
        img=image_dict[i]
        try:
            x_coord=int(data[data[unique_time_selector]==tracking_ID][coordinate_selector[0]].values)
            y_coord=int(data[data[unique_time_selector]==tracking_ID][coordinate_selector[1]].values)
       #if no data for timepoint is found print error message
        except TypeError:
            print('no segmentation found for', i)
            x_coord=0.1
            y_coord=0.1
        if 'flags' in data.columns:
            flag=data[data[unique_time_selector]==tracking_ID]['flags']
        else:
            flag='None'
        
        
        #getting part of the dataframe that is from the current timepoint as well
        #get the time, something like _T1
        #print('i: ', i)
        Time_ID= i.replace(Site_ID, '')
        #print('Time_ID:', Time_ID)
        #gets only the numeric value of the timepoint
        Time= re.search(timenumber_pattern, Time_ID).group()
        #print('Time:', Time)
        timepoint_data=Site_data[Site_data[timepoint_selector]==int(Time)]
        alt_img={}
        for index, row in timepoint_data.iterrows():
            if int(row[coordinate_selector[0]])!=x_coord:
                if 'flags' in data.columns:
                    flag=row['flags']
                else: 
                    flag='None'
                alt_img.update({row[unique_time_selector]:[int(row[coordinate_selector[0]]), int(row[coordinate_selector[1]]), flag]})

        
        loaded_dict.update({img:[x_coord, y_coord, {'alt_cells': alt_img}, tracking_ID, flag]})
 
    print(AD.take(3, loaded_dict.items())) 
    print('encoding complete')
    return loaded_dict

#%% flagging framework
@app.callback([Output('click-data', 'children'),
              Output('click_data_storage', 'data')],
              [Input('migration_data', 'clickData'),
               Input('image-overlay', 'clickData')],)    
def display_click_data(clickData, image_overlay):
    '''getting click data from graph and displaying it
    '''
    ctx= dash.callback_context

    
    if ctx.triggered[0]['prop_id']=='image-overlay.clickData':
        data=image_overlay
    if ctx.triggered[0]['prop_id']=='migration_data.clickData':
        data=clickData
    #print(data)
    return json.dumps(data, indent=2), data



#%% scrollable images
@app.callback([Output('image_slider', 'max'),
             Output('image_slider', 'marks'),
             Output('image_slider_output', 'value')],
             [Input('image_dict', 'data')])
#gets the minimum and maxium value of the timepoint column as selected
#and adjusts min and max values of the track_length_selector slider as first output
#and the marks on the slider as second output
def get_image_timepoints(image_dict):
    #image_dict=json.loads(image_dict)
    max_timepoint=len(image_dict.keys())-1
    marks={}
    for m in range(0, max_timepoint, 5):
        marks.update({m:str(m)})
    image_slider_output='Image{} selected'.format(image_dict)
    return max_timepoint, marks, image_slider_output  
#updating image graph

#updating image graph
@app.callback(Output('image-overlay', 'figure'),
              #Output('histogram', 'figure')],
              [Input('image_slider', 'value'),],
              [State('image_dict', 'data'),
               State('brightness_slider', 'value'),])

def update_image_graph(value, image_dict, brightness):
    '''
    Calls the graph for image display
    Gets the image list from update_image_overlay.
    Based on the value of the image slider it selects an image from
    the dictionary and calls the graph with that image, including
    the X,Y coordinates of all cells in that image 
    It also gets a value from 0-15 from the brightness slider, and adjusts the
    brightness of the image accordingly.
    '''
    
    #image_dict=json.loads(image_dict)
    #print(AD.take(5, image_dict.items()))
    img=list(image_dict.keys())[value+1]
    #retrieving image shape from dictionary
    x=image_dict['shape'][0]
    y=image_dict['shape'][1]
    #retrieving cell ID from dictionary
    #ID=image_dict['ID'] 
    
    #adjust the brightness of the image.
    image=Image.open(img)
    enhancer_object = ImageEnhance.Brightness(image)
    image = enhancer_object.enhance(brightness)
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    encoded=base64.b64encode(imgByteArr.getvalue())

    return GD.image_graph('data:image/png;base64,{}'.format(encoded.decode()), x_C=x, y_C=y, 
                          image_info=image_dict[img]) 

#%% Download csv file
@app.callback(Output('save_path', 'children'),
              [Input('save_button', 'n_clicks')],
              [State('flag_storage', 'data'),
               State('save_path', 'value')],)
                             
def update_download_link(n_clicks, flag_storage, save_area):
    print(save_area)
    data=pd.read_csv(flag_storage, index_col='index')
    data.to_csv(save_area, index_label='index')
    print('file saved under', save_area)
    return 'Download datatable'
    
# =============================================================================
#     csv_string=''
#     try: 
#         data=pd.read_csv(flag_storage)
#         type(flag_storage)
#         csv_string = data.to_csv(index=False, encoding='utf-8')
#         csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#     except Exception as e:
#         print(e)
#     return csv_string
# =============================================================================

@app.callback(Output('graph_div', 'style'),
                [Input('plot_hider' ,'value')])
def hide_graphs(value):
    if value=='Yes':
        return {'display':'none'}
    if value=='No':
        return {'display':'block'}
    
#%% load previous settings
@app.callback([Output('graph_selector', 'value'),
               Output('classifier_choice', 'value'),
               Output('identifier_selector', 'value'),
               Output('timepoint_selector', 'value'),
               Output('data_selector', 'value'),
               Output('distance_filter', 'value'),
               Output('graph_reuse', 'value'),
               Output('flag_filter', 'value'),
               Output('unique_time_selector', 'value'),
               Output('track_length_selector', 'value'),
               Output('exclude_seen', 'value'),
               Output('ID_pattern', 'value'),
               Output('save_path', 'value'),
               Output('Image_folder', 'value'),
               Output('plot_hider' ,'value')],
               [Input('output-data-upload', 'children')])

def load_settings(output_data_upload):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    setting_file=Path(os.path.join(dir_path,'Cache', 'settings.csv'))
    if setting_file.is_file():
        settings=pd.read_csv(setting_file).loc[0]
        settinglist=[]
        for enum, column in enumerate(settings):
            if enum==5:
               column=eval(column)
            if enum >0:
                settinglist.append(column)
        print(settinglist)
        return settinglist

#%% safe current settings
@app.callback(Output('test_storage', 'children'),
              [Input('graph_selector', 'value'),
               Input('classifier_choice', 'value'),
               Input('identifier_selector', 'value'),
               Input('timepoint_selector', 'value'),
               Input('data_selector', 'value'),
               Input('distance_filter', 'value'),
               Input('graph_reuse', 'value'),
               Input('flag_filter', 'value'),
               Input('unique_time_selector', 'value'),
               Input('track_length_selector', 'value'),
               Input('exclude_seen', 'value'),
               Input('ID_pattern', 'value'),
               Input('save_path', 'value'),
               Input('Image_folder', 'value'),
               Input('plot_hider' ,'value')],
               [State('output-data-upload', 'children')])
def safe_settings(graph_selector, classifier_choice, identifier_selector,
                  timepoint_selector, data_selector, distance_filter,
                  graph_reuse, flag_filter, unique_time_selector,
                  track_length_selector, exclude_seen,
                  ID_pattern, save_path,
                  Image_folder, plot_hider, output_data_upload):
    
    if output_data_upload!=None:
        settings=pd.DataFrame(data={'graph_selector': graph_selector, 'classifier_choice': classifier_choice,
                           'identifier_selector':identifier_selector, 'timepoint_selector': timepoint_selector,
                           'data_selector':[data_selector], 'distance_filter': distance_filter,
                            'graph_reuse':graph_reuse,
                           'flag_filter':flag_filter,'unique_time_selector':unique_time_selector,
                           'track_length_selector':track_length_selector, 'exclude_seen':exclude_seen,
                           'ID_pattern': ID_pattern,
                           'save_path': save_path,
                           'Image_folder': Image_folder, 
                           'plot_hider':plot_hider}, index=[1,2])
        dir_path = os.path.dirname(os.path.realpath(__file__))
        AD.createFolder(os.path.join(dir_path, 'Cache'))
        setting_storage=os.path.join(dir_path, 'Cache', 'settings.csv')
        settings.to_csv(setting_storage, index_label='index')
        #print('settings have been saved to {}'.format(setting_storage))
        return 'nothing'


#%%
if __name__ == '__main__':
    app.run_server(debug=False)