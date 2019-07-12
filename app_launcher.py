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
#from flask_caching import Cache

import pandas as pd
import sys
import os


sys.path.append(os.path.realpath(__file__))
import graph_definitions as GD
import menu_definitions as MD



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True

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
df=pd.DataFrame({'col1':[1, 2]})
#%%
    
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
    #calling menus
    html.Hr(),
    dcc.Markdown('''**Data organization**'''),
    html.P('How is your data formatted?'),
    MD.datatype_selector(),
    html.P('Select the columns that hold your data, if x,y coordinates, first selected is treated as x coordinate:'),
    MD.data_selector(df),
    html.P('Select the column which holds the classifier of your groups:'),
    MD.classifier_choice(df),
    html.P('Select the column which holds the identifier for each unique item:'),
    MD.identifier_selector(df),
    html.P('Select the column which holds the timepoints:'),
    MD.timepoint_selector(df),  
    html.Hr(),
    dcc.Markdown('''**Data filtering**'''), 
    MD.RadioItems(),
    html.P('Select the minimum track length'),
    MD.track_length_selector(),
    html.Div(id='track_length_output', style={'margin-top': 20} ),
    html.P('Select the minimum travelled distance'),
    MD.distance_filter(),
    MD.plot_button(),
    dcc.Tabs(id='tabs', children=[
             dcc.Tab(label='tab one', 
                     children= [html.Table(id='output-data-upload')]),    #calling the table
                             
             dcc.Tab(label='tab two',
                     #calling the graph 
                     children= dcc.Graph(id='migration_data'),)]),

    #hidden divs for storing data
    html.Div(id='shared_data', style={'display':'none'})
])

#%%layouts
#table layout



#%% upload function

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

        MD.generate_table(df),
        #horizontal line
        html.Hr() ])

#%% update after upload
@app.callback(Output('output-data-upload', 'children'),
              
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
#calls the upload function, updating the global variable df and also storing 
#the same dataframe in the hidden Div 'shared_data'
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children#, df.to_json(date_format='iso', orient='split')
#%% updating dropdown menus
#gets called when data is uploaded. It does not actually use the input
#from the upload, but gets the column names from the global variable df which is
#updated by the data upload. Outputs the column names as options ot the three
#dropdown menus
@app.callback([Output('classifier_choice', 'options'),
               Output('identifier_selector', 'options'),
               Output('timepoint_selector', 'options'),
               Output('data_selector', 'options')],
              [Input('output-data-upload', 'children')])

def update_dropdown(contents):
    columns=df.columns
    col_labels=[{'label' :k, 'value' :k} for k in columns]
    identifier_cols=col_labels
    timepoint_cols=col_labels
    data_cols=col_labels
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
              Output('shared_data', 'children')],
              [Input('track_length_selector', 'value')],
              [
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value')])


#displays the selected value below the slider
#and filters the data by the minimal track length as picked in the slider
def display_value(track_length_selector,  identifier_selector, timepoint_selector):
    display_string='Minimum track length: {} {}'.format(track_length_selector, 'timepoints')
    #dff=pd.read_json(shared_data, orient='split')
    
    #grouping the data by the identifier
    track_lengths=pd.DataFrame(df.groupby(identifier_selector)[timepoint_selector].count())
    #filtering the track lengths by only selecting those with a track length higher,
    #then the one chosen in the slider
    thresholded_tracks=track_lengths[track_lengths[timepoint_selector]>track_length_selector]
    track_ids=thresholded_tracks.index.tolist()
    thresholded_data=df.loc[df[identifier_selector].isin(track_ids)]

    return display_string, thresholded_data.to_json(date_format='iso', orient='split')
#%% update graph 

#creates a figure when the display plots button is pressed.
#also takes the states of the dropdown menus: classifier_choice, identifier_selector
#and timepoint_selector and feeds it as options to the graph.
#it takes the data from the hidden div 'shared_data' as input data for the graph
@app.callback(Output('migration_data', 'figure'),
              [Input('plot_button', 'n_clicks')],
              [State('graph_selector', 'value'),
               State('shared_data', 'children'),
               State('classifier_choice', 'value'),
               State('identifier_selector', 'value'),
               State('timepoint_selector', 'value'),
               State('data_selector', 'value'),
               State('distance_filter', 'value')])

def plot_graph(n_clicks, graph_selector, shared_data, classifier_choice, identifier_selector, timepoint_selector, data_selector, distance_filter):
    dff=pd.read_json(shared_data, orient='split')
    graph_options={'None':print(), 'lineplot':GD.lineplot, 'migration_distance':GD.migration_distance}
    return graph_options[graph_selector](dat=dff, classifier_column=classifier_choice, 
                        identifier_column=identifier_selector,
                        timepoint_column=timepoint_selector, data_column=data_selector, distance_filter=distance_filter, testmode=False)





#%%
if __name__ == '__main__':
    app.run_server(debug=True)