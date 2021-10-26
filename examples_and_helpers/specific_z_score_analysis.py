#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 15:56:21 2019

@author: max

This is the code used for outgrowth_2 and outgrowth_3 experiments
"""


import os
import sys
#import seaborn as sns
import numpy as np
import pandas as pd
import scipy.stats as stats	
#import matplotlib.pyplot as plt
import argparse
import plotly 
#import plotly.plotly as py
import plotly.graph_objs as go
#init_notebook_mode(connected=True)
#import statsmodels.api as sm
#from xattr import xattr
import time
#import subprocess
from plotly import __version__
#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
print(__version__) # requires version >= 1.9.0
#from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multicomp import MultiComparison
from statsmodels.formula.api import ols
#sys.path.append(os.path.realpath(__file__))
#import load_data as exp
import statistics 
from matplotlib import pyplot
import seaborn as sns
import re
import researchpy as rp
import scipy.stats as stats
#%%
features=['AreaShape_MajorAxisLength']
Ctrl='Ctrl'
def MAD_robust(x, robust=True):
    if robust==True:
        med=np.median(x)
        dif=[np.abs(i-med) for i in x]
        return np.median(dif)
    else:
        return np.std(x)
#either computes the median (robust==True), or the mean (robust==False)
def Mean_robust(x, robust=False):
    if robust==True:
        return np.median(x)
    else:
        return np.mean(x)
def calc_mean_features(data):
    '''
    calculates the mean values of each feature grouped by timepoint and by experiment
    excluding the ctrl
    '''
    mean_features=[]
    for f in features:
        temp=pd.DataFrame()
        temp=data[data['Classifier']!=Ctrl].groupby(['time', 'well'], as_index=False).agg({f:['mad', 'mean']})    
        temp.columns = ["_".join(x) for x in temp.columns.ravel()]
        mean_features.append(temp)
    mean_features = pd.concat(mean_features, join='outer', axis=1, sort=True)
    #mean_features.columns = ["_".join(x) for x in mean_features.columns.ravel()]
    mean_features=mean_features.reset_index(drop=True)
    mean_features=mean_features.fillna(0)
    mean_features = mean_features.loc[:,~mean_features.columns.duplicated()]
    return mean_features

#%%
def calc_mean_ctrl(data):
    '''
    calculates the mean values of each feature grouped by timepoint and by experiment
    excluding the ctrl
    '''
    #custom filter. You need to filter the control before calculating z_score
    data=data[data['roundness']<0.65]
    mean_features=[]
    for f in features:
        temp=pd.DataFrame()
        temp=data[data['Classifier'].str.contains('Ctrl')].groupby(['Metadata_Timepoint'], as_index=False).agg({f:['mad', 'mean']})    
        temp.columns = ["_".join(x) for x in temp.columns.ravel()]
        mean_features.append(temp)
    mean_features = pd.concat(mean_features, join='outer', axis=1, sort=True)
    #mean_features.columns = ["_".join(x) for x in mean_features.columns.ravel()]
    mean_features=mean_features.reset_index(drop=True)
    mean_ctrl=mean_features.fillna(0)
    mean_ctrl = mean_ctrl.loc[:,~mean_ctrl.columns.duplicated()]
    return mean_ctrl

def calc_z_score(data):

        mean_ctrl=calc_mean_ctrl(data)
        #mean_features=calc_mean_features(data)
        #temp_data=mean_features
        temp_data=data#data[data['Classifier']!=Ctrl]
        for row in temp_data.iterrows():
            #print(row)
            for f in features:            
                #temp_data.at[row[0],f+'_z_score']=(row[1][f+'_mean']-mean_ctrl[mean_ctrl['time_']==row[1]['time_']][f+'_mean'].iloc[0])/mean_ctrl[mean_ctrl['time_']==row[1]['time_']][f+'_mad'].iloc[0]
                temp_data.at[row[0],f+'_z_score']=(row[1][f]-mean_ctrl[mean_ctrl['Metadata_Timepoint_']==row[1]['Metadata_Timepoint']][f+'_mean'].iloc[0])/mean_ctrl[mean_ctrl['Metadata_Timepoint_']==row[1]['Metadata_Timepoint']][f+'_mad'].iloc[0]

        return temp_data
    
def calc_z_score_list(data):
    '''
    Split your dataframes in one dataframe per control.
    Input all dataframes as a list to the function
    '''
    z_score_list=[]
    for d in data:
        z_score_list.append(calc_z_score(d))
    combined=pd.concat(z_score_list)
    combined['Time_Experiment_Classifier']=combined['Time_Classifier']+'_E'+combined['Metadata_Experiment']
    combined['Experiment_Classifier']=combined['Classifier']+'_E'+combined['Metadata_Experiment']
    return combined
    
#%%
    
def plot_zscore(data):
    fig, ax=pyplot.subplots(figsize=(11, 8))
    f=features[0]
    feature=f+'_z_score'
    data=data[data['roundness']<0.65]
    #data=data[data['Experiment_Classifier'].str.contains('27')]
    fig=sns.lineplot(x='Metadata_Timepoint', sy=f+'_z_score', hue='Experiment_Classifier', data=data)#[(z_score_all['Classifier'].str.contains('C')) & (z_score_all['roundness']<0.65)])
    return fig
def plot_timeseries(data, feature, exclude='blubb', classifier='Metadata_Classifier', Time='Metadata_Timepoint'):
    fig, ax=pyplot.subplots(figsize=(11, 8))
    data=data.sort_values(by=classifier)
    #pallete_size=len(data[classifier].unique())
    #palette=sns.set_palette('bright', n_colors=pallete_size)
    exclude=str(exclude)
    #ax.set(ylim=(200, 350))
    #matching_c = [s for s in data[classifier].unique() if not any(e in s for e in exclude)]
    
    #fig=sns.lineplot(x=Time, palette=palette, y=feature, hue=classifier, data=data[data[classifier].isin(matching_c)])
    fig=sns.lineplot(x=Time, y=feature, hue=classifier, data=data[~data[classifier].str.contains(exclude)])

    return fig

def plot_bar(data, feature, exclude=['ignore'], classifier='Metadata_Classifier'):
    fig, ax=pyplot.subplots(figsize=(11, 8))
    data=data.sort_values(by=classifier)
    palette_size=len(data[classifier].unique())
    palette=sns.set_palette('bright', n_colors=palette_size)
    #data=data.replace([np.inf, -np.inf], np.nan).dropna()
    #ax.set(ylim=(0, 50))
    pyplot.setp(ax.get_xticklabels(), rotation=45)
    matching_c = [s for s in data[classifier].unique() if not any(e in s for e in exclude)]

    
    fig=sns.boxplot(x=classifier, palette=palette, y=feature, data=data[data[classifier].isin(matching_c)], notch=True)
    #fig=sns.barplot(x=classifier, palette=palette, y=feature, data=data[data[classifier].isin(matching_c)])

    #fig=sns.barplot(x=classifier, palette=palette, y=feature, data=data[~data[classifier].str.contains(exclude)])

    return fig


#%%
figure=fig.get_figure()
figure.savefig('/Office/Phd/Data/REF52/SiAB/diameter.svg', format='svg')   
    
#%%
def calc_z_score_grouped(data):
    mean_ctrl=calc_mean_ctrl(data)
    temp=data[data['well']!=Ctrl]
    for k in temp.groupby('Metadata_Timepoint').groups.keys():
        for f in features:
            temp=(temp.groupby('time')[f].groups[k]-mean_ctrl[mean_ctrl['time_']==k][f+'_mean'].iloc[0])/mean_ctrl[mean_ctrl['time_']==k][f+'_mad'].iloc[0]
            
#%%
z_score_all['well'][z_score_all['well']=='Ctrl']='laminin'
z_score_all['well'][z_score_all['well']=='B6']='glass+DMEM'
z_score_all['well'][z_score_all['well']=='B5']='laminin+PDL'
z_score_all['well'][z_score_all['well']=='B4']='laminin+PDL+DMEM'
z_score_all['well'][z_score_all['well']=='B3']='laminin+DMEM'
z_score_all['well'][z_score_all['well']=='B1']='glass'

#%%

fkbp['Normalized_Intensity']=0
Classifier=[]
Timepoint=[]
Intensity=[]
normalized={}
for i in fkbp.groupby(['Classifier']):
    for enum, value in enumerate(i[1].sort_values('Metadata_timepoint')['Intensity']):
        if enum==0:
            norm=value
        Classifier.append(i[0])
        Timepoint.append(enum)
        Intensity. append(value/norm)
normalized.update({'Timepoint':Timepoint})
normalized.update ({'Classifier':Classifier})
normalized.update({'Intensity':Intensity})
normalized=pd.DataFrame.from_dict(normalized)
#%%
def plot_table(data, y, x):
    fig, ax=pyplot.subplots(figsize=(11, 8))
    #data=data[data['Experiment_Classifier'].str.contains('27')]
    fig=sns.lineplot(x=x, y=y, hue='Classifier', data=data)#[(z_score_all['Classifier'].str.contains('C')) & (z_score_all['roundness']<0.65)])
    return fig

#%%
import statsmodels.api as sm
from statsmodels.formula.api import ols
data=figdata[~figdata['Metadata_Classifier'].str.contains('Ctrl')]
Anova=[]
grouped_data=data.groupby('Metadata_Timepoint')
for name, group in grouped_data:
    model= ols('AreaShape_MajorAxisLength ~ C(Metadata_Classifier)', data=group).fit()
    test=sm.stats.anova_lm(model, typ=2)
    testdf=pd.DataFrame(data={'PR(>F)': test.loc['C(Metadata_Classifier)', 'PR(>F)'], 'Metadata_Timepoint':name}, index=[0])
    Anova.append(testdf)
df=pd.concat(Anova)
df=df.reset_index()
df['index']=df['index'].astype(str)

#%%
def lifegivesyou(text, name='Snizl'):
    text=str(text)
    print ('when life gives you {}, don\'t make {}ade! Make life take the {} back! Get mad! I don\'t want your damn {}! What am I supposed to do with these? Demand to see life\'s manager! Make life rue the day it thought it could give {} {}! Do you know who I am? I\'m the man whose gonna burn your house down - with the {}!'.format(text, text, text, text, name, text, text, text))
    
def saga(name1, spec1, spec2, action):
    print('Did you ever hear the tragedy of Darth {} The Wise? I thought not. \
          It’s not a story the {} would tell you. It’s a {} legend. Darth {} was a Dark Lord of the {}, so powerful and so wise he could use the Force to influence the {} to create life…'.format(name1, spec1, spec2, name1, spec2, action))   
    
    #%%
    pattern=re.compile('.+?(?=Hapto)')
    l12['Hue']=l12.Classifier.apply(lambda x: re.search(pattern, x).group())
     
#%% Anova
stats.f_oneway(l['Lamellasize'][l['Hue']=='REF_NC_'],
               l['Lamellasize'][l['Hue']=='REF_SiDLC_'],
               l['Lamellasize'][l['Hue']=='1B2_NC_'],
               l['Lamellasize'][l['Hue']=='1B2_rescue_']
               )    
    
#%%    
summary, results=rp.ttest(group1=l['Lamellasize'][l['Hue']=='REF_NC_'], group1_name='Ctrl', group2=l['Lamellasize'][l['Hue']=='1B2_NC_'], group2_name='KO')
print(summary)         