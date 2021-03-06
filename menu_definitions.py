
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 12:06:05 2019

@author: max

Holds the menu definition, such as buttons and dropdown menus
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_table


#%% data
def Upload_data():
    return dcc.Upload(
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
        multiple=False
    )
    
#The following functions define several menus and are called in the initial
#layout when the app is launched
#radio item layout
def RadioItems():
    return dcc.RadioItems(
    options=[
        {'label': 'lineplot', 'value': 'lineplot'},
         {'label':'migration_distance', 'value': 'migration_distance'},
         {'label':'time_series', 'value':'time_series'},
         {'label':'corel plot', 'value': 'corel_plot'},
         {'label':'flag_count', 'value':'flag_count'},
         {'label':'boxplot', 'value':'boxplot'}],
    value='lineplot',
    id='graph_selector')
def graph_reuse():
    return dcc.RadioItems(
    options=[
            {'label':'yes', 'value' : 'yes'},
             {'label':'no', 'value' : 'no'}],
             value='yes',
             id='graph_reuse')
#table layout
def generate_table(df):
    '''
    called when data is uploaded
    '''
    return dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={'headers':True, 'data':0},
                style_cell={'width' :'150px'}
            )
    
def plot_button():
    return html.Button(id='plot_button', n_clicks=0, children='Display plots')

def plot_save_button():
    return html.Button(id='plot_save_button', n_clicks=0, children='Download plot as svg')
#dropdown layout
def classifier_choice(df):
    '''
    dropdown menu to select which column should be used as the classifier
    '''
    columns=df.columns
    classifieroptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            #label='Classifier Column',
            id='classifier_choice',
            options=classifieroptions,
            placeholder='select the classifier column',
            value='Classifier')
def identifier_selector(df):
    '''
    dropdown menu to select the column which identifies individual cells
    '''
    columns=df.columns
    identifieroptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='identifier_selector',
            options=identifieroptions,
            placeholder='select the identifier column',
            value='unique_id')
def unique_time_selector(df):    
    '''
    dropdown menu to select which column contains the information about timepoints
    '''
    columns=df.columns
    timepointoptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='unique_time_selector',
            options=timepointoptions,
            placeholder='select a column where the value is unique for timepoint and cell',
            value='unique_time')

   
def timepoint_selector(df):    
    '''
    dropdown menu to select which column contains the information about timepoints
    '''
    columns=df.columns
    timepointoptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='timepoint_selector',
            options=timepointoptions,
            placeholder='select the timepoint column',
            value='Metadata_Timepoint')
    
def data_selector(df):
    columns=df.columns
    data_options= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='data_selector',
            options=data_options,
            multi=True,
            value=['Location_Center_X_Zeroed', 'Location_Center_Y_Zeroed'])
    
def coordinate_selector(df):
    columns=df.columns
    data_options= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='coordinate_selector',
            options=data_options,
            multi=True,
            value=['Location_Center_X', 'Location_Center_Y'])
def average_button():    
    return html.Button(id='average_button', n_clicks=0, children='Calculate Average')
    
    
def average_selector(df):    
    '''
    dropdown menu to select which column you want to average
    '''
    columns=df.columns
    timepointoptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='average_selector',
            options=timepointoptions,
            placeholder='select the column which you want to average',
            value='None'
            )
def average_grouper(df):
    '''
    dropdown menu to select which measurement you want to group the average by
    '''
    columns=df.columns
    timepointoptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='average_grouper',
            options=timepointoptions,
            placeholder='select the column which you want to average',
            value='None'
            )

#%% Filters
def track_length_selector():
    '''
    input box for minimum track length
    '''
    return dcc.Input(placeholder='Enter a value...',
                     type='number',
                     value=20,
                     id='track_length_selector')
# =============================================================================
# def track_length_selector():
#     
#     '''
#     slider to select data cleaning method
#     '''
#     return dcc.Slider(
#             id='track_length_selector',
#             min=0,
#             max=10,
#             step=1,
#             value=7,
#             marks={0:'0',
#                    5:'5',
#                    10:'10'})
# =============================================================================
def distance_filter():
    '''
    input box for minum travelled distance
    '''
    return dcc.Input(placeholder='Enter a value...',
                     type='number',
                     value=30,
                     id='distance_filter')
    
def custom_filter_dropdown(df):
    '''
    dropdown menu to select which data type to filter by 
    '''
    columns=df.columns
    identifieroptions= [{'label' :k, 'value' :k} for k in columns]
    identifieroptions.append({'label':'none', 'value':'none'})
    return dcc.Dropdown(
            id='custom_filter_dropdown',
            options=identifieroptions,
            placeholder='select a column as filter',
            value='none')
def custom_filter_numeric():
    '''
    input box for custom filter
    '''
    return dcc.Input(placeholder='Enter a value...',
                     type='number',
                     value=0,
                     id='custom_filter_numeric')  
    
def datatype_selector():
    return dcc.RadioItems(options=[
        {'label': 'X, Y coordinates', 'value': 'xy'},
        {'label': 'individual features', 'value' : 'features'}],
    value='xy',
    id='datatype_selector')
    

#%% Patterns    
def ID_pattern():
    return dcc.Textarea(
            value='(?P<Site_ID>W[A-Z][0-9]+_S[0-9]{4})(?P<TrackID>_E[0-9]+)(?P<Timepoint>_T[0-9]+)',
            style={'width':'100%'},
            id='ID_pattern',
            )   
def timeless_ID_pattern():
    return dcc.Textarea(
            value='(?P<Well>W[A-Z][0-9]+)(?P<Site>_S[0-9]{4})(?P<TrackID>_E[0-9]+)',
            style={'width':'100%'},
            id='timeless_ID_pattern',
            )  
def ID_submit():
    return html.Button(id='ID_submit', n_clicks=0, children='Submit pattern')
    
def save_path():
    return dcc.Textarea(
            placeholder='save the datatable at the following location',
            value='/Users/max/Desktop/Office/Phd/pythoncode/graph_app/flagged_datatable.csv',
            style={'width':'100%'},
            id='save_path')    

def save_button():
    return html.Button(id='save_button', n_clicks=0, children='Download datatable')

#%% images

def Image_folder():
    return dcc.Textarea(
            placeholder='Enter the path to your images',
            value='enter full path to your image',
            style={'width':'100%'},
            id='Image_folder')

def Folder_submit():
    return html.Button(id='Folder_submit', n_clicks=0, children='upload images')
    

def Image_selector():
    return dcc.RadioItems(options=[
        {'label' : 'Yes', 'value': 'Yes'}, 
        {'label': 'No', 'value' : 'No'}], 
        value='No', 
        id='Image_selector')
def image_slider():
    
    '''
    slider to select image to display
    '''
    return dcc.Slider(
            id='image_slider',
            min=0,
            max=10,
            step=1,
            value=0,
            marks={0:'0',
                   5:'5',
                   10:'10'},
           updatemode='drag')
def brightness_slider():
    '''
    slider to adjust brightness of image
    '''
    return dcc.Slider(
            id='brightness_slider',
            min=0,
            max=15,
            step=None,
            value=1,
            marks={0:'0',                     
                  0.5:'0.5',
                  1:'1',
                  1.5:'1.5',
                  2:'2',
                  3: '3',
                  4:'4',
                  5:'5',
                  6: '6',
                  7: '7',
                  8: '8',
                  10: '10',
                  15: '15',})
    
#%% track filtering
def track_comment():
    return dcc.Textarea(
            placeholder='Do you want to flag the track',
            value='enter a comment to the track',
            style={'width':'100%'},
            id='track_comment',
            )
def comment_submit():
    return html.Button(id='comment_submit', n_clicks=0, children='Add Comment')    
def flag_options():
    return dcc.RadioItems(
    options=[
            {'label':'all', 'value' : 'all'},
             {'label':'single', 'value' : 'single'}],
             value='all',
             id='flag_options')
def flag_filter():
    return dcc.Dropdown(
            id='flag_filter',
            options=[{'label':'placeholder', 'value':'placeholder'}],
            multi=True,
            )
def plot_hider():
        return dcc.RadioItems(options=[
        {'label' : 'Yes', 'value': 'Yes'}, 
        {'label': 'No', 'value' : 'No'}], 
        value='No', 
        id='plot_hider')
def exclude_seen():
        return dcc.RadioItems(options=[
        {'label' : 'Yes', 'value': 'Yes'}, 
        {'label': 'No', 'value' : 'No'}], 
        value='No', 
        id='exclude_seen')