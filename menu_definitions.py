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
        {'label': 'None', 'value' : 'None'},
         {'label':'migration_distance', 'value': 'migration_distance'},],
    value='None',
    id='graph_selector')
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

def track_length_selector():
    
    '''
    slider to select data cleaning method
    '''
    return dcc.Slider(
            id='track_length_selector',
            min=0,
            #for the future add a timepoint column selector for dynamic max lenght
            max=10,
            step=1,
            value=0,
            marks={0:'0',
                   5:'5',
                   10:'10'})
def distance_filter():
    return dcc.Input(placeholder='Enter a value...',
                     type='number',
                     value=0,
                     id='distance_filter')
def datatype_selector():
    return dcc.RadioItems(options=[
        {'label': 'X, Y coordinates', 'value': 'xy'},
        {'label': 'individual features', 'value' : 'features'}],
    value='xy',
    id='datatype_selector')
    
def data_selector(df):
    columns=df.columns
    data_options= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='data_selector',
            options=data_options,
            multi=True,
            value=['Location_Center_X_Zeroed', 'Location_Center_Y_Zeroed'])
#%% images
def Image_folder():
    return dcc.Textarea(
            placeholder='Enter the path to your images',
            value='enter full path to your image',
            style={'width':'100%'},
            id='Image_folder')
def Folder_submit():
    return html.Button(id='Folder_submit', n_clicks=0, children='upload images')
    
def Upload_images():
    return dcc.Upload(
        id='upload-image',
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
        multiple=True
    )
def Image_selector():
    return dcc.RadioItems(options=[
        {'label' : 'Yes', 'value': 'Yes'}, 
        {'label': 'No', 'value' : 'No'}], 
        value='No', 
        id='Image_selector')