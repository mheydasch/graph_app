#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 13:11:11 2019

@author: max
"""

import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd
import sys
import os


sys.path.append(os.path.realpath(__file__))
import graph_definitions as GD
import algorythm_defitions as AD


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''
To Dos:
graph needs to be stored and retrieved
add selector for values from dataframe. 
add bar graph for persistance plots data
'''
#%% app upload
global df
df=[]
app.layout = html.Div([
    
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
        multiple=True
    ),
    html.Table(id='output-data-upload'),
    dcc.RadioItems(
    options=[
        {'label': 'lineplot', 'value': 'lineplot'},
        {'label': 'None', 'value' : 'None'}

    ],
    value='None',
    id='graph_selector'),
    dcc.Graph(id='migration_data')
])

#%%layouts
def generate_table(df):
    return dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns],
                fixed_rows={'headers':True, 'data':0},
                style_cell={'width' :'150px'}
            )


#%%
#backup
def parse_contents(contents, filename, date):
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

        generate_table(df),
        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

#%% update after upload
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


#%% update graph picker
# =============================================================================
# path='/Users/max/Desktop/beta_pix_5_data.csv'
# data=pd.read_csv(path)
# =============================================================================
#graph_options={}

graph_options={'None':print(), 'lineplot':GD.lineplot}
@app.callback(Output('migration_data', 'figure'),
              [Input('graph_selector', 'value')])
# =============================================================================
# def get_value(value):
#     print(value)
#     if value=='lineplot':
#         return GD.lineplot(data, testmode=True)
# =============================================================================
def get_value(value):

    return graph_options[value](df, testmode=False)

    #return GD.lineplot(df, testmode=True)
# =============================================================================
# def get_value(value):
#     print(value)
#     if 'df' in globals():
#       if value=='lineplot':
#             print(GD.lineplot(df, testmode=True))
#             return GD.lineplot(df, testmode=True)
# =============================================================================


        

#%%


if __name__ == '__main__':
    app.run_server(debug=True)