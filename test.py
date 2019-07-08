import dash_html_components as html
import dash_core_components as dcc
import dash

import plotly
from dash.dependencies import Input, Output, State

import pandas as pd
import numpy as np

import json
import datetime
import operator
import os
import sys

import base64
import io


sys.path.append(os.path.realpath(__file__))
import dash_table_experiments as dte


#%%
#df=pd.read_csv('/Volumes/imaging.data/Max/REF52/beta_pix/pix_5/beta_pix_5_data.csv')
# =============================================================================
# def generate_table(dataframe, max_rows=10):
#     try:
#         return html.Table(
#             # Header
#             [html.Tr([html.Th(col) for col in dataframe.columns])] +
#             # Body
#             [html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))])
#     except Exception as e:
#         print(e)
# =============================================================================
#%%
#file upload
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return None

    return df

app = dash.Dash()

app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.H5("Upload Files"),
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
        multiple=False),
    html.Br(),
    html.Button(
        id='propagate-button',
        n_clicks=0,
        children='Propagate Table Data'
    ),


    html.Br(),
    html.H5("Filter Column"),
    dcc.Dropdown(id='dropdown_table_filterColumn',
        multi = False,
        placeholder='Filter Column'),


    html.Br(),
    html.H5("Updated Table"),
    html.Div(html.Table(id='table'))


])




# callback table creation
@app.callback(Output('table', 'data'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
    
# =============================================================================
# def update_table(contents, filename):
#     if contents is not None: 
#         df=parse_contents(contents, filename)
#         return generate_table(df)
# =============================================================================
def generate_table(contents, filename):
    if contents is not None:
        dataframe=parse_contents(contents, filename)
        max_rows=10
        try:
            return html.Table(
                # Header
                [html.Tr([html.Th(col) for col in dataframe.columns])] +
                # Body
                [html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))])
        except Exception as e:
            print(e)
    
# =============================================================================
# def update_output(contents, filename):
#     if contents is not None:
#         df = parse_contents(contents, filename)
#         if df is not None:
#             return df.to_dict('records')
#             
#         else:
#             return [{}]
#     else:
#         return [{}]
# 
# =============================================================================

#callback update options of filter dropdown
@app.callback(Output('dropdown_table_filterColumn', 'options'),
              [Input('propagate-button', 'n_clicks'),
               Input('table', 'rows')])
def update_filter_column_options(n_clicks_update, tablerows):
    if n_clicks_update < 1:
        print("df empty")
        return []

    else:
        dff = pd.DataFrame(tablerows) # <- problem! dff stays empty even though table was uploaded

        print (dff.head()), dff.empty #result is True, labels stay empty

        return [{'label': i, 'value': i} for i in sorted(list(dff))]


# =============================================================================
# app.css.append_css({
#     "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
# })
# =============================================================================

if __name__ == '__main__':
    app.run_server(debug=True)
