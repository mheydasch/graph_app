#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 11:34:49 2019

@author: max
"""


import os
import re
import functools
import pandas as pd
import numpy as np


class Experiment_data:
    def __init__(self, path):
        self.exp_path=path
    def find_csv(self):
        '''
        returns a list with all csv files in the KD folder
        '''
        #pattern: must end with '.csv'
        csv_find=re.compile('REF52.*\.csv$')
        #finds the directory with that specific name
        find_dir='out'
        self.i_dirs=[]
        #Knockdown pattern, must match inserted variable self.__KD followed by '/'
        #and one or more digits
        for root, dirs, files in os.walk(self.exp_path):
            #looks in each folder from given path
            #if folder is matching the KD pattern, the find_dir pattern and
            #if there are csv files
            if find_dir in root and len([x for x in files if re.search(csv_find, x)])!=0:
                #finds the csv files in the folder and adds them to a list
                csv_files=[x for x in files if re.search(csv_find, x)]
                for csv in csv_files:
                    #each csv file is added to the path and appended to a list
                    self.i_dirs.append(os.path.join(root, csv))            
        return self.i_dirs
   
    #distances.loc[distances.unique_id.str.contains('C'), 'Classifier']='Ctrl'

    def load_tracks(self):
        track_list=[]
        image_list=[]
        time_series=False
        for i in self.i_dirs:
            if 'cells' in i:
                #header needs to be changed depending on the amount of headers in each csv file.
                temp=pd.read_csv(i, header=0)

    # =============================================================================
                #removing unwanted prefixes from column names
                #if time_series==True:
                for i in temp.columns:
                     ir=i.replace('Image_', '')
                     ir=ir.replace('nuc_', '')
                     try:
                         ir=ir.replace(re.search('cells[0-9]?_', ir), '')
                     except:
                         pass
                     temp=temp.rename(columns={i:ir})

                track_list.append(temp)
            if 'Image' in i:
                temp=pd.read_csv(i, header=0)
                image_list.append(temp)  
        if 'Image' in i:        
            image_data=pd.concat(image_list, axis=0, sort=True)
        self.tracks = pd.concat(track_list, axis=0, sort=True)
        self.tracks=self.tracks.reset_index()
        self.track_list=track_list
        #in case of time series

        if time_series==True:
            self.tracks['Metadata_Timepoint']+=1
            for enum, i in enumerate(self.tracks['Metadata_Site'].astype('str')):
                while len(i)<4:
                    i='0'+i
                self.tracks.loc[enum, 'Metadata_Site']=i
            self.tracks['unique_id']='W'+self.tracks['Metadata_Well'].astype('str')+\
            '_S'+self.tracks['Metadata_Site'].astype('str')+'_E'+self.tracks['track_id'].astype('str')
            self.tracks['unique_time']=self.tracks['unique_id']+'_T'+self.tracks['Metadata_Timepoint'].astype('str')
            for line, i in enumerate(self.tracks['Location_Center_X']):
                self.tracks.loc[line, 'unique_id']='W'+self.tracks.loc[line, 'Metadata_Well']+\
                '_'+'S'+str(self.tracks.loc[line, 'Metadata_Site'])+'_'+'E'+str(self.tracks.loc[line, 'track_id'])
        
        #in case of double columns
        double_header=False
        if double_header==True:
            n_exclude=re.compile('\.[0-9]')
            head=self.tracks.columns
            cols=self.tracks.loc[0].values
            l=['index']
            for n, i in enumerate(head):
                if i!='index':
                    try:
                       i=i.replace(re.search(n_exclude, i).group(), '')
                         
                    except: AttributeError
                    
                    l.append(str(i)+'_'+str(cols[n]))  
            self.tracks.columns=l
            self.tracks=self.tracks.drop(0, axis=0)
            self.tracks = self.tracks.loc[:,~self.tracks.columns.duplicated()]
            self.tracks.rename(columns={'Image_Metadata_Site':'Metadata_Site'}, inplace=True)
        if 'Image' in i:    
            self.image_data=image_data
            #self.tracks['background'][self.tracks['Image_Metadata_Site']==image_data['Metadata_Site']]=image_data['Intensity_LowerQuartileIntensity_DLC']
            
            #data.tracks['background'][self.tracks['Image_Metadata_Site']==data.image_data['Metadata_Site']]=data.image_data['Intensity_LowerQuartileIntensity_DLC']
            self.tracks=self.tracks.merge(self.image_data[['Metadata_Site', 'Intensity_LowerQuartileIntensity_DLC']], how='left', on='Metadata_Site')
        return self.tracks
    
    def interpolate_tracks(self):
        #interpolating x
        for line ,i in enumerate(self.tracks['Location_Center_X']):
            #checking if line is nan
            if np.isnan(i):
                #checking if next value is not nan, if the next line is not above df boundaries and if next line is still
                #part of the same cell
                if np.isnan(self.tracks.loc[line+1, 'Location_Center_X'])==False and len(self.tracks)>line+1 \
                    and self.tracks.loc[line+1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    upper=self.tracks.loc[line+1, 'Location_Center_X']
                if np.isnan(self.tracks.loc[line-1, 'Location_Center_X'])==False and line-1>=0 \
                and self.tracks.loc[line-1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    lower=self.tracks.loc[line-1, 'Location_Center_X']
                self.tracks.loc[line, 'Location_Center_X']=(upper+lower)/2
        #interpolating y
        for line ,i in enumerate(self.tracks['Location_Center_Y']):
            #checking if line is nan
            if np.isnan(i):
                #checking if next value is not nan, if the next line is not above df boundaries and if next line is still
                #part of the same cell
                if np.isnan(self.tracks.loc[line+1, 'Location_Center_Y'])==False and len(self.tracks)>line+1 \
                    and self.tracks.loc[line+1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    upper=self.tracks.loc[line+1, 'Location_Center_Y']
                if np.isnan(self.tracks.loc[line-1, 'Location_Center_Y'])==False and line-1>=0 \
                and self.tracks.loc[line-1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    lower=self.tracks.loc[line-1, 'Location_Center_Y']
                self.tracks.loc[line, 'Location_Center_Y']=(upper+lower)/2

    def normalize_tracks(self):
        self.find_csv()
        self.load_tracks()
        self.interpolate_tracks()
        #getting a list of the unique ids
        self.cells=self.tracks['unique_id'].unique()
        #initiating the new column for normalized values
        self.tracks['Location_Center_Y_Zeroed']=0
        self.tracks['Location_Center_X_Zeroed']=0
        #looping through the unique ids
        for name in self.cells:
            single_track=self.tracks[self.tracks['unique_id']==name]
            single_track=single_track.sort_values(by=['Metadata_Timepoint'])
            first_index=single_track.index.values[0]
            first_y=single_track.loc[first_index, 'Location_Center_Y']
            first_x=single_track.loc[first_index, 'Location_Center_X']
            single_track['Location_Center_Y_Zeroed']=single_track['Location_Center_Y']-first_y
            single_track['Location_Center_X_Zeroed']=single_track['Location_Center_X']-first_x
            self.tracks['Location_Center_Y_Zeroed'][self.tracks['unique_id']==name]=single_track['Location_Center_Y_Zeroed']
            self.tracks['Location_Center_X_Zeroed'][self.tracks['unique_id']==name]=single_track['Location_Center_X_Zeroed']
        #self.tracks.loc[self.tracks.unique_id.str.contains('B'), 'Classifier']='pix'
        #self.tracks.loc[self.tracks.unique_id.str.contains('C'), 'Classifier']='Ctrl'
# =============================================================================
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('A1'), 'Classifier']='hapto_pix'
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('A2'), 'Classifier']='chemo_pix'
# =============================================================================
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('B2'), 'Classifier']='hapto_DLC'
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('B3'), 'Classifier']='hapto_DLC'
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('B4'), 'Classifier']='chemo_DLC'
#        self.tracks.loc[self.tracks.Metadata_Well.str.contains('B4'), 'Classifier']='EGF+PDGF_DLC'
# =============================================================================
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('B5'), 'Classifier']='10EGF_DLC'
# =============================================================================
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('C2'), 'Classifier']='hapto_CTRL'
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('C3'), 'Classifier']='chemo_CTRL'
        self.tracks.loc[self.tracks.Metadata_Well.str.contains('C4'), 'Classifier']='chemo_CTRL'
    
#        self.tracks.loc[self.tracks.Metadata_Well.str.contains('C4'), 'Classifier']='EGF+PDGF_CTRL'
# =============================================================================
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('C5'), 'Classifier']='10EGF_CTRL'
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('D1'), 'Classifier']='hapto_Notrans'
#         self.tracks.loc[self.tracks.Metadata_Well.str.contains('D2'), 'Classifier']='chemo_Notrans'        
# =============================================================================
    def define_classifier(self):
        self.tracks.loc[self.tracks.Metadata_Site < 10, 'Classifier']='Ctrl'
        self.tracks.loc[(self.tracks['Metadata_Site'] >= 10) & (self.tracks['Metadata_Site'] < 20), 'Classifier']='1B2'
        self.tracks.loc[(self.tracks['Metadata_Site'] >= 20) & (self.tracks['Metadata_Site'] < 30), 'Classifier']='Ctrl_FL'
        self.tracks.loc[(self.tracks['Metadata_Site'] >= 30) & (self.tracks['Metadata_Site'] < 40), 'Classifier']='1B2_FL'


    

#%%
adjust=[i for i in data3.tracks.columns if 'Intensity' in i]
adjust.remove('Intensity_LowerQuartileIntensity_DLC')
#%%df[~df.Team.str.match('Fin*')]
for i in adjust:
    data3.tracks=data3.tracks[~data3.tracks[i].str.contains('[a-zA-Z]')]
    data3.tracks[i]=data3.tracks[i].astype('float64')-data3.tracks['Intensity_LowerQuartileIntensity_DLC']
    
#%%
for i, row in image1.tracks.iterrows():
    #print(row['Metadata_Site'], combined['Metadata_Site'] )
    combined['image_intensity'][combined['Metadata_Site']==row['Metadata_Site']]=row['Intensity_LowerQuartileIntensity_DLC'] 
#%%
data.tracks['roundness']=data.tracks['AreaShape_MinorAxisLength']/data.tracks['AreaShape_MajorAxisLength']       

#%%
            self.tracks['Metadata_Timepoint']+=1
            for enum, i in enumerate(self.tracks['Metadata_Site'].astype('str')):
                while len(i)<4:
                    i='0'+i
                self.tracks.loc[enum, 'Metadata_Site']=i
            self.tracks['unique_id']='W'+self.tracks['Metadata_Well'].astype('str')+\
            '_S'+self.tracks['Metadata_Site'].astype('str')+'_E'+self.tracks['track_id'].astype('str')
            self.tracks['unique_time']=self.tracks['unique_id']+'_T'+self.tracks['Metadata_Timepoint'].astype('str')
            for line, i in enumerate(self.tracks['Location_Center_X']):
                self.tracks.loc[line, 'unique_id']='W'+self.tracks.loc[line, 'Metadata_Well']+\
                '_'+'S'+str(self.tracks.loc[line, 'Metadata_Site'])+'_'+'E'+str(self.tracks.loc[line, 'track_id'])
#%%
data.tracks['unique_id']='S'+data.tracks['Metadata_Site'].astype('str')+'_E'+data.tracks['index'].astype('str')
data.tracks['unique_time']=data.tracks['unique_id']+'_T'+data.tracks['Metadata_Timepoint'].astype('str')
data.tracks['Time_Classifier']=data.tracks['Classifier']+'_t'+data.tracks['Metadata_Timepoint'].astype('str')
#%%

data.tracks['Metadata_Experiment']='SiDLC26'
data.tracks['Time_Experiment_Classifier']=data.tracks['Time_Classifier']+'_E'+data.tracks['Metadata_Experiment']
data.tracks['Experiment_Classifier']=data.tracks['Classifier']+'_E'+data.tracks['Metadata_Experiment']

#%% combined tracks 
