#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:11:11 2019
@author: max
"""

import base64
import datetime
import io
from PIL import Image
from PIL import ImageEnhance
import urllib.parse

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import imageio
import json

from natsort import natsorted

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
        MD.timepoint_selector(df)], className= 'six columns'),


    
    
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
                                               html.Div([dcc.Graph(id='migration_data')],
                                                        id='graph_div'),
                                               ], 
                                          className= 'six columns'),
                                               #graph for showing the image
                                     html.Div([dcc.Graph(id='image-overlay'),
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
                                                html.A(
                                                        'Download Data',
                                                        id='download-link',
                                                        download="rawdata.csv",
                                                        href="",
                                                        target="_blank"
                                                        ),
                                                  ],className='six columns', )
                                          
                                               
                                 ], className='row')]
                                 
                     )
            ]),
#tabs section end    
           
                                 

 
                             
                    



     #hidden divs for storing data
    #holds the dataframe after filtering by track length
    dcc.Store(id='shared_data', storage_type='local'),
    #holds the unfiltered dataframe with user added flags
    dcc.Store(id='flag_storage', storage_type='session'),
    #stores the patterns for the ID
    dcc.Store(id='pattern_storage', storage_type='local'),
    #holding the uploaded images
    dcc.Store(id='image_list', storage_type='session'),
    #holds graphs after they have been created for faster access
    dcc.Store(id='graph_storage', storage_type='session'),
    #stores the dictionary of images
    dcc.Store(id='image_dict', storage_type='memory'),
    #stores raw click data to be retrieved by update_flags
    dcc.Store(id='click_data_storage', storage_type='memory'),


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
               Output('coordinate_selector', 'options')],
              [Input('output-data-upload', 'children')])

def update_dropdown(contents):
    columns=df.columns
    col_labels=[{'label' :k, 'value' :k} for k in columns]
    identifier_cols=col_labels
    timepoint_cols=col_labels
    data_cols=col_labels
    unique_time_columns=col_labels
    coordinates=col_labels
    #print(col_labels)

    return col_labels, identifier_cols, timepoint_cols, data_cols, unique_time_columns, coordinates

#%% update after image folder got parsed 
@app.callback(Output('image_list', 'data'),
              [Input('Folder_submit', 'n_clicks')],
              [State('Image_folder', 'value'),])
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
                
    print(AD.take(5, image_dict.items()))
    print('images uploaded')
    return image_dict
#%% ID pattern recognition
@app.callback([Output('pattern_storage', 'data'),],
              [Input('ID_submit', 'n_clicks')],
              [State('ID_pattern', 'value'),])

#gets triggered when the pattern submit button is pressed and simply
#stores the submitted regex pattern
def update_ID_pattern(n_clicks, value, ):
    #print(value, 'submitted')
    
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
              [Input('comment_submit', 'n_clicks')],
              [State('identifier_selector', 'value'),
               State('track_comment', 'value'),
               State('migration_data', 'clickData'),
               State('flag_options', 'value'),
               State('flag_filter', 'options'),
               State('flag_storage', 'data'),
               State('click_data_storage', 'data'),
               State('unique_time_selector', 'value'),
               State('pattern_storage', 'data')
               ])
def update_flags(n_clicks, identifier_selector, 
                 track_comment, clickData, flag_options, flag_filter, 
                 flag_storage, click_data_storage, unique_time_selector, pattern_storage):
    print(track_comment)
    print('pattern storage: ', pattern_storage)
    pattern=re.compile(pattern_storage[0])    
    if flag_storage != None: 
        flag_storage=pd.DataFrame.from_dict(flag_storage)
    else:
        dff=pd.DataFrame(df)
        print('flag_storage empty')
    
    #flagging framework
    if click_data_storage!=None:
        
        print('clickdata: ',click_data_storage)
        
        if 'customdata' in click_data_storage['points'][0]:
            ID=click_data_storage['points'][0]['customdata']
        if 'hovertext' in click_data_storage['points'][0]: 
            ID=click_data_storage['points'][0]['hovertext']

        print('ID: ', ID)
        #read previously filtered data frame
        #create a new column and fill it
        try:
            dff['flags']
        except KeyError:
            dff['flags']='None'
            print('flags resetted')
        #get the unique ID from the hovertext
        #ID=clickData['points'][0]['hovertext']
        
        #check flag options. If single, add the submitted comment only to 
        #the selected timepoint
        if flag_options=='single':
            dff.loc[dff[unique_time_selector]==ID, 'flags']=track_comment
            #print('single')
        #if 'all' remove the timepoint component from the string and add the comment
        #to all datapoints with that ID like 'WB2_S1324_E4'
        if flag_options=='all':
           #print('all')
           #pattern=re.compile('_T.*')
           try:
               Timepoint=re.search(pattern, ID).group('Timepoint')
               ID=ID.replace(Timepoint,'')
               dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment
           except AttributeError:
               dff.loc[dff[identifier_selector]==ID, 'flags']=track_comment


        flags=list(dff['flags'].unique())
        flag_filter=[{'label' :k, 'value' :k} for k in flags]
        print('flags', flags)
    flag_storage=dff.to_dict() 
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
               State('track_length_selector', 'value')])

def plot_graph(n_clicks, graph_selector, classifier_choice,
               identifier_selector, timepoint_selector, data_selector, distance_filter, 
               graph_storage, graph_reuse, flag_filter, unique_time_selector, flag_storage,
               track_length_selector):
    #if the graph storage is empty an empty dictionary will be created
    if graph_storage==None or graph_reuse=='no':
        graph_storage={}
    #data is read from the shared data div
    
    
    #try to read flag sotrage.
    if flag_storage != None:
        dff=pd.DataFrame.from_dict(flag_storage)
    else:
        dff=pd.DataFrame(df)
    track_lengths=pd.DataFrame(dff.groupby(identifier_selector)[timepoint_selector].count())
    #filtering the track lengths by only selecting those with a track length higher,
    #then the one chosen in the slider
    thresholded_tracks=track_lengths[track_lengths[timepoint_selector]>track_length_selector]
    track_ids=thresholded_tracks.index.tolist()
    dff=dff.loc[dff[identifier_selector].isin(track_ids)]
    
    print(flag_filter)
    #print(type(flag_filter))
    
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
                            timepoint_column=timepoint_selector, data_column=data_selector, 
                            distance_filter=distance_filter, unique_time_selector=unique_time_selector, testmode=True)
        graph_storage.update({graph_selector:fig})
        return fig, graph_storage

#%% 
@app.callback(Output('image_dict', 'data'),
              [Input('migration_data', 'clickData')],
              [State('image_list','data'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('unique_time_selector', 'value'),
               State('coordinate_selector', 'value'),
               State('pattern_storage', 'data'),
               State('flag_storage', 'data')],)
def update_image_overlay(hoverData, image_dict, 
                         identifier_selector, timepoint_selector, unique_time_selector,
                         coordinate_selector, pattern_storage, flag_storage):

    print('pattern storage: ', pattern_storage)
    pattern=re.compile(pattern_storage[0])
    #Error message if no images have been uploaded
    if len(image_dict)==0:
        print('No images have been uploaded')
    #read data from flag_storage if exists    
    if flag_storage != None:
        data=pd.DataFrame.from_dict(flag_storage)
    #else from shared data
    else:
        data=pd.DataFrame(df)
    #getting hovertext from hoverdata and removing discrepancies between hover text and filenames
    #(stripping of track_ID)
    ID_or=hoverData['points'][0]['hovertext']
    try:
        #getting the different components of the ID. Such as:
        #'WB2' '_S0520' '_E3' '_T40'         
        Site_ID, track_ID, Timepoint =re.search(pattern, ID_or).group(
                 'Site_ID', 'TrackID', 'Timepoint')

        #exclusion criterium if timepoint is already there
        exclusion=track_ID+Timepoint
        #print(Timepoint, track_ID, Wellname, Sitename)
        
        #print('track_ID: ', track_ID)
        #getting the ID to the images by stripping off extensions
        #something like 'WB2_S1324
        ID=ID_or.replace(exclusion,'')
        #print('ID_or: ', ID_or)
        #print('ID: ', ID)
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
    imagelist=[i for i in image_dict.keys() if ID in i]
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
    
    #getting all the images for the respective timepoints
    for i in imagelist:
        #adding the unique ID of the cell back into the key of the image
        #to get X, Y coordinates. Something like 'WB2_S1324_E4_T1'        
        tracking_ID=i.replace(re.search('_T', i).group(), track_ID+'_T')
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
            flag='none'
        
        
        #getting part of the dataframe that is from the current timepoint as well
        #get the time, something like _T1
        #print('i: ', i)
        Time_ID= i.replace(Site_ID, '')
        #gets only the numeric value of the timepoint
        Time= re.search(timenumber_pattern, Time_ID).group()
        timepoint_data=Site_data[Site_data[timepoint_selector]==int(Time)]
        alt_img={}
        for index, row in timepoint_data.iterrows():
            if int(row[coordinate_selector[0]])!=x_coord:
                if 'flags' in data.columns:
                    flag=row['flags']
                alt_img.update({row[unique_time_selector]:[int(row[coordinate_selector[0]]), int(row[coordinate_selector[1]]), flag]})

        
        loaded_dict.update({img:[x_coord, y_coord, {'alt_cells': alt_img}, tracking_ID, flag]})
 
    #print(AD.take(5, loaded_dict.items())) 
    print('encoding complete')
    return json.dumps(loaded_dict)

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
    image_dict=json.loads(image_dict)
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
    It also gets a value from 0-2 from the brightness slider, and adjusts the
    brightness of the image accordingly.
    '''
    
    image_dict=json.loads(image_dict)
    #print(AD.take(5, image_dict.items()))
    img=list(image_dict.keys())[value+1]
    print(img)
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
    #saving and opening
# =============================================================================
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     img_path=os.path.join(dir_path, 'temp.png')
#     image.save(img_path)
#    
#     
#     with open(img_path, 'rb') as f:
#         encoded=base64.b64encode(f.read())
#     #print('encoding complete')
# =============================================================================

    return GD.image_graph('data:image/png;base64,{}'.format(encoded.decode()), x_C=x, y_C=y, 
                          image_info=image_dict[img]) 

#%% Download csv file
@app.callback(Output('download-link', 'href'),
              [Input('flag_storage', 'data')],)
                             
def update_download_link(shared_data):
    csv_string=''
    try: 
        data=pd.read_json(shared_data, orient='split')
        type(shared_data)
        csv_string = data.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    except Exception as e:
        print(e)
    return csv_string

@app.callback(Output('graph_div', 'style'),
                [Input('plot_hider' ,'value')])
def hide_graphs(value):
    if value=='Yes':
        return {'display':'none'}
    if value=='No':
        return {'display':'block'}
    




#%%
if __name__ == '__main__':
    app.run_server(debug=True)