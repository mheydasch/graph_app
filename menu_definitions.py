#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 12:06:05 2019

@author: max
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_table


#The following functions define several menus and are called in the initial
#layout when the app is launched
#radio item layout
def RadioItems():
    return dcc.RadioItems(
    options=[
        {'label': 'lineplot', 'value': 'lineplot'},
        {'label': 'None', 'value' : 'None'},
         {'label':'whiskerplot', 'value': 'whiskerplot'}],
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
            placeholder='select the classifier column')
def identifier_selector(df):
    '''
    dropdown menu to select the column which identifies individual cells
    '''
    columns=df.columns
    identifieroptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='identifier_selector',
            options=identifieroptions,
            placeholder='select the identifier column')
   
def timepoint_selector(df):    
    '''
    dropdown menu to select which column contains the information about timepoints
    '''
    columns=df.columns
    timepointoptions= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='timepoint_selector',
            options=timepointoptions,
            placeholder='select the timepoint column')

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
def datatype_selector():
    return dcc.RadioItems(options=[
        {'label': 'X, Y coordinates', 'value': 'xy'},
        {'label': 'individual features', 'value' : 'features'}

    ],
    value='xy',
    id='datatype_selector')
    
def data_selector(df):
    columns=df.columns
    data_options= [{'label' :k, 'value' :k} for k in columns]
    return dcc.Dropdown(
            id='data_selector',
            options=data_options,
            multi=True)