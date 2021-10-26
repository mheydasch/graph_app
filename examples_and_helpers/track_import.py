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
import statistics
from pandas.io.parsers import ParserError
#%%

class Experiment_data() :
    def __init__(self, path, Experimentname, double_header=False, time_series=False, classifier='numeric'):
        self.exp_path=path
        self.double_header=double_header #either True or False
        self.time_series=time_series #either True or False
        self.classifier=classifier
        self.Experimentname=Experimentname#either numeirc or nominal
    def find_csv(self):
        '''
        returns a list with all csv files in the KD folder
        '''
        #pattern: must end with '.csv'
        #csv_find=re.compile('REF52nuc1line.*tracks\.csv$')
        csv_find=re.compile('REF52cell.csv')

        #finds the directory with that specific name
        #find_dir='trackXY'
        find_dir='out'

        self.i_dirs=[]
        #Knockdown pattern, must match inserted variable self.__KD followed by '/'
        #and one or more digits
        for root, dirs, files in os.walk(self.exp_path):
            #print (root)
            #looks in each folder from given path
            #if folder is matching the KD pattern, the find_dir pattern and
            #if there are csv files
            if find_dir in root and len([x for x in files if re.search(csv_find, x)])!=0:
                #finds the csv files in the folder and adds them to a list
                csv_files=[x for x in files if re.search(csv_find, x)]
                for csv in csv_files:
                    #each csv file is added to the path and appended to a list
                    self.i_dirs.append(os.path.join(root, csv))     
        #print(self.i_dirs)
        return self.i_dirs
   
    #distances.loc[distances.unique_id.str.contains('C'), 'Classifier']='Ctrl'

    def load_tracks(self):
        track_list=[]
        image_list=[]
        for i in self.i_dirs:
            if 'REF' in i:
                #header needs to be changed depending on the amount of headers in each csv file.
                try:
                    temp=pd.read_csv(i, header=0, sep= ',')
                except ParserError as e:
                    print(e)
                    temp=pd.read_csv(i, header=0, sep= ',', error_bad_lines=False)

    # =============================================================================
                #removing unwanted prefixes from column names
                #if time_series==True:
                for i in temp.columns:
                     ir=i.replace('Image_', '')
                     ir=ir.replace('nuc_', '')
                     ir=ir.replace('cell_', '')
                     try:
                         ir=ir.replace(re.search('cells[0-9]?_', ir), '')
                     except:
                         pass
                     temp=temp.rename(columns={i:ir})

                track_list.append(temp)
# =============================================================================
#             if 'Image' in i:
#                 temp=pd.read_csv(i, header=0)
#                 image_list.append(temp)  
#         if 'Image' in i:        
#             image_data=pd.concat(image_list, axis=0, sort=True)
# =============================================================================
        self.tracks = pd.concat(track_list, axis=0, sort=True)
        self.tracks=self.tracks.reset_index()
        self.track_list=track_list
        #in case of time series
        try:
            self.tracks=self.tracks.rename(columns={'ObjectNumber':'track_id'})
        except:
            pass
        if self.time_series==True:
            self.tracks['Metadata_Timepoint']+=1
            if self.classifier=='nominal':
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
            if self.classifier=='numeric':
                for enum, i in enumerate(self.tracks['Metadata_Site'].astype('str')):
                    while len(i)<4:
                        i='0'+i
                    self.tracks.loc[enum, 'Metadata_Site']=i
                    self.tracks['unique_id']='_S'+self.tracks['Metadata_Site'].astype('str')+'_E'+self.tracks['track_id'].astype('str')
                    self.tracks['unique_time']=self.tracks['unique_id']+'_T'+self.tracks['Metadata_Timepoint'].astype('str')
                for line, i in enumerate(self.tracks['Location_Center_X']):
                    self.tracks.loc[line, 'unique_id']='S'+str(self.tracks.loc[line, 'Metadata_Site'])+'_'+'E'+str(self.tracks.loc[line, 'track_id'])
                
        #in case of double columns
        #double_header=False
        if self.double_header==True:
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
# =============================================================================
#         if 'Image' in i:    
#             self.image_data=image_data
#             #self.tracks['background'][self.tracks['Image_Metadata_Site']==image_data['Metadata_Site']]=image_data['Intensity_LowerQuartileIntensity_DLC']
#             
#             #data.tracks['background'][self.tracks['Image_Metadata_Site']==data.image_data['Metadata_Site']]=data.image_data['Intensity_LowerQuartileIntensity_DLC']
#             self.tracks=self.tracks.merge(self.image_data[['Metadata_Site', 'Intensity_LowerQuartileIntensity_DLC']], how='left', on='Metadata_Site')
# =============================================================================
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
                else:
                    continue
                if np.isnan(self.tracks.loc[line-1, 'Location_Center_X'])==False and line-1>=0 \
                and self.tracks.loc[line-1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    lower=self.tracks.loc[line-1, 'Location_Center_X']
                else:
                    continue
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
                else:
                    continue
                if np.isnan(self.tracks.loc[line-1, 'Location_Center_Y'])==False and line-1>=0 \
                and self.tracks.loc[line-1, 'unique_id']==self.tracks.loc[line, 'unique_id']:
                    lower=self.tracks.loc[line-1, 'Location_Center_Y']
                else:
                    continue
                self.tracks.loc[line, 'Location_Center_Y']=(upper+lower)/2

    def normalize_tracks(self):
        if self.classifier=='nominal':
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
        if self.classifier=='nominal':
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
        #time_series=False
        
        self.find_csv()
        self.load_tracks()
        
        
# =============================================================================
#         if self.classifier=='numeric':    
#             self.tracks.loc[self.tracks.Metadata_Site <= 5, 'Metadata_Classifier']='4000_CTRL_Chemo'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 5) & (self.tracks['Metadata_Site'] <= 10), 'Metadata_Classifier']=str('4000_KO_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 10) & (self.tracks['Metadata_Site'] <= 15), 'Metadata_Classifier']=str('40000_CTRL_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 15) & (self.tracks['Metadata_Site'] <= 20), 'Metadata_Classifier'] =str('40000_KO_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 20) & (self.tracks['Metadata_Site'] <= 25), 'Metadata_Classifier']=str('40000_CTRL_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 25) & (self.tracks['Metadata_Site'] <= 30), 'Metadata_Classifier']=str('40000_KO_Hapto')
# =============================================================================

        if self.classifier=='numeric':    
            self.tracks.loc[self.tracks.Metadata_Site <= 10, 'Metadata_Classifier']='4000_CTRL_Hapto'
            self.tracks.loc[(self.tracks['Metadata_Site'] > 10) & (self.tracks['Metadata_Site'] <= 20), 'Metadata_Classifier']=str('4000_KO_Hapto')

            self.tracks.loc[(self.tracks['Metadata_Site'] > 20) & (self.tracks['Metadata_Site'] <= 25), 'Metadata_Classifier']=str('20000_CTRL_Hapto')
            self.tracks.loc[(self.tracks['Metadata_Site'] > 25) & (self.tracks['Metadata_Site'] <= 30), 'Metadata_Classifier'] =str('20000_KO_Hapto')
            self.tracks.loc[(self.tracks['Metadata_Site'] > 30) & (self.tracks['Metadata_Site'] <= 35), 'Metadata_Classifier']=str('40000_CTRL_Hapto')
            self.tracks.loc[(self.tracks['Metadata_Site'] > 35) & (self.tracks['Metadata_Site'] <= 40), 'Metadata_Classifier']=str('40000_KO_Hapto')
        
# =============================================================================
#         if self.classifier=='numeric':    
#             self.tracks.loc[self.tracks.Metadata_Site <= 5, 'Metadata_Classifier']='4000_CTRL_Chemo'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 5) & (self.tracks['Metadata_Site'] <= 10), 'Metadata_Classifier']=str('20000_CTRL_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 10) & (self.tracks['Metadata_Site'] <= 15), 'Metadata_Classifier']=str('40000_CTRL_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 15) & (self.tracks['Metadata_Site'] <= 20), 'Metadata_Classifier'] =str('4000_KO_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 20) & (self.tracks['Metadata_Site'] <= 25), 'Metadata_Classifier']=str('20000_KO_Chemo')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 25) & (self.tracks['Metadata_Site'] <= 30), 'Metadata_Classifier']=str('40000_KO_Chemo')
#             
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 30) & (self.tracks['Metadata_Site'] <= 35), 'Metadata_Classifier']=str('4000_CTRL_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 35) & (self.tracks['Metadata_Site'] <= 40), 'Metadata_Classifier']=str('20000_CTRL_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 40) & (self.tracks['Metadata_Site'] <= 45), 'Metadata_Classifier']=str('40000_CTRL_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 45) & (self.tracks['Metadata_Site'] <= 50), 'Metadata_Classifier'] =str('4000_KO_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 50) & (self.tracks['Metadata_Site'] <= 55), 'Metadata_Classifier']=str('20000_KO_Hapto')
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 55) & (self.tracks['Metadata_Site'] <= 60), 'Metadata_Classifier']=str('40000_KO_Hapto')
# =============================================================================
            

   
# =============================================================================
#         if self.classifier=='numeric':    
#             self.tracks.Metadata_Site=pd.to_numeric(self.tracks.Metadata_Site)
#             self.tracks.loc[self.tracks.Metadata_Site <= 10, 'Metadata_Classifier']='1B2_FL_lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 10) & (self.tracks['Metadata_Site'] <= 20), 'Metadata_Classifier']='Ctrl_FL_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 20) & (self.tracks['Metadata_Site'] <= 30), 'Metadata_Classifier']='SiDLC_FL_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 30) & (self.tracks['Metadata_Site'] <= 40), 'Metadata_Classifier'] ='1B2_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 40) & (self.tracks['Metadata_Site'] <= 50), 'Metadata_Classifier']='Ctrl_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 50) & (self.tracks['Metadata_Site'] <= 60), 'Metadata_Classifier']='SiDLC_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 60) & (self.tracks['Metadata_Site'] <= 70), 'Metadata_Classifier']='1B2_Planar'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 70) & (self.tracks['Metadata_Site'] <= 80), 'Metadata_Classifier']='Ctrl_Planar'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 80) & (self.tracks['Metadata_Site'] <= 90), 'Metadata_Classifier']='SiDLC_Planar'
# # # =============================================================================
# =============================================================================
#         if self.classifier=='numeric':    
#             self.tracks.Metadata_Site=pd.to_numeric(self.tracks.Metadata_Site)
#             self.tracks.loc[self.tracks.Metadata_Site <= 10, 'Metadata_Classifier']='1B2_Hapto'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 10) & (self.tracks['Metadata_Site'] <= 20), 'Metadata_Classifier']='Ctrl_Hapto'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 20) & (self.tracks['Metadata_Site'] <= 30), 'Metadata_Classifier']='SiDLC_Hapto'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 30) & (self.tracks['Metadata_Site'] <= 40), 'Metadata_Classifier']='1B2_Chemo'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 40) & (self.tracks['Metadata_Site'] <= 50), 'Metadata_Classifier']='SiDLC_Chemo'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 50) & (self.tracks['Metadata_Site'] <= 60), 'Metadata_Classifier']='Ctrl_Chemo'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 60) & (self.tracks['Metadata_Site'] <= 70), 'Metadata_Classifier']='SiDLC_Chemo'
# =============================================================================
# =============================================================================
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 70) & (self.tracks['Metadata_Site'] <= 80), 'Metadata_Classifier']='SiDLC_Hapto_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 80) & (self.tracks['Metadata_Site'] <= 90), 'Metadata_Classifier']='Ctrl_Hapto_Lines'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 90) & (self.tracks['Metadata_Site'] <= 100), 'Metadata_Classifier']='1B2_Hapto_Planar'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 100) & (self.tracks['Metadata_Site'] <= 110), 'Metadata_Classifier']='SiDLC_Hapto_Planar'
#             self.tracks.loc[(self.tracks['Metadata_Site'] > 110) & (self.tracks['Metadata_Site'] <= 120), 'Metadata_Classifier']='Ctrl_Hapto_Planar'
# =============================================================================

     
        if self.time_series==False:
            self.tracks['Metadata_Experiment']=self.Experimentname    
            self.tracks['unique_id']='S'+self.tracks['Metadata_Classifier'].astype('str')+'_E'+self.tracks['track_id'].astype('str')+'_X'+self.tracks['Metadata_Experiment']            
            #deactivate for u track  
# =============================================================================
#             self.tracks['roundness']=self.tracks['AreaShape_MinorAxisLength']/self.tracks['AreaShape_MajorAxisLength']      
#             self.tracks['unique_time']=self.tracks['unique_id']+'_T'+self.tracks['Metadata_Timepoint'].astype('str')
#             self.tracks['Time_Classifier']=self.tracks['Metadata_Classifier']+'_t'+self.tracks['Metadata_Timepoint'].astype('str')
#             ## Define this one manually everytime!
# 
#             self.tracks['Time_Experiment_Classifier']=self.tracks['Time_Classifier']+'_E'+self.tracks['Metadata_Experiment']
#             self.tracks['Experiment_Classifier']=self.tracks['Metadata_Classifier']+'_E'+self.tracks['Metadata_Experiment']
# =============================================================================
            
        
        

    

#%% For laptack auto merged input
#data=data9
for i in data.columns:
         ir=i.replace('Image_', '')
         ir=ir.replace('nuc_', '')
         ir=ir.replace('cell_', '')
         data=data.rename(columns={i:ir})
#%%         
data.loc[data.Metadata_Site <= 5, 'Metadata_Classifier']='4000_CTRL_Chemo'
data.loc[(data['Metadata_Site'] > 5) & (data['Metadata_Site'] <= 10), 'Metadata_Classifier']=str('4000_KO_Chemo')
data.loc[(data['Metadata_Site'] > 10) & (data['Metadata_Site'] <= 15), 'Metadata_Classifier']=str('40000_CTRL_Chemo')
data.loc[(data['Metadata_Site'] > 15) & (data['Metadata_Site'] <= 20), 'Metadata_Classifier'] =str('40000_KO_Chemo')
data.loc[(data['Metadata_Site'] > 20) & (data['Metadata_Site'] <= 25), 'Metadata_Classifier']=str('40000_CTRL_Hapto')
data.loc[(data['Metadata_Site'] > 25) & (data['Metadata_Site'] <= 30), 'Metadata_Classifier']=str('40000_KO_Hapto')         
        
         
#%%         
data.Metadata_Site=pd.to_numeric(data.Metadata_Site)
data.loc[data.Metadata_Site <= 5, 'Metadata_Classifier']='4000_CTRL'
data.loc[(data['Metadata_Site'] > 5) & (data['Metadata_Site'] <= 10), 'Metadata_Classifier']='4000_KO'
data.loc[(data['Metadata_Site'] > 10) & (data['Metadata_Site'] <= 15), 'Metadata_Classifier']='20000_CTRL'
data.loc[(data['Metadata_Site'] > 15) & (data['Metadata_Site'] <= 20), 'Metadata_Classifier'] ='20000_KO'
data.loc[(data['Metadata_Site'] > 20) & (data['Metadata_Site'] <= 25), 'Metadata_Classifier']='40000_CTRL'
data.loc[(data['Metadata_Site'] > 25) & (data['Metadata_Site'] <= 30), 'Metadata_Classifier']='40000_KO'

#data['unique_id']=str(data['track_id']+'_'+data['Metadata_Classifier'])       

#%%
data.Metadata_Site=pd.to_numeric(data.Metadata_Site)
data.loc[data.Metadata_Site <= 5, 'Metadata_Classifier']='4000_CTRL_Chemo'
data.loc[(data['Metadata_Site'] > 5) & (data['Metadata_Site'] <= 10), 'Metadata_Classifier']=str('20000_CTRL_Chemo')
data.loc[(data['Metadata_Site'] > 10) & (data['Metadata_Site'] <= 15), 'Metadata_Classifier']=str('40000_CTRL_Chemo')
data.loc[(data['Metadata_Site'] > 15) & (data['Metadata_Site'] <= 20), 'Metadata_Classifier'] =str('4000_KO_Chemo')
data.loc[(data['Metadata_Site'] > 20) & (data['Metadata_Site'] <= 25), 'Metadata_Classifier']=str('20000_KO_Chemo')
data.loc[(data['Metadata_Site'] > 25) & (data['Metadata_Site'] <= 30), 'Metadata_Classifier']=str('40000_KO_Chemo')

data.loc[(data['Metadata_Site'] > 30) & (data['Metadata_Site'] <= 35), 'Metadata_Classifier']=str('4000_CTRL_Hapto')
data.loc[(data['Metadata_Site'] > 35) & (data['Metadata_Site'] <= 40), 'Metadata_Classifier']=str('20000_CTRL_Hapto')
data.loc[(data['Metadata_Site'] > 40) & (data['Metadata_Site'] <= 45), 'Metadata_Classifier']=str('40000_CTRL_Hapto')
data.loc[(data['Metadata_Site'] > 45) & (data['Metadata_Site'] <= 50), 'Metadata_Classifier'] =str('4000_KO_Hapto')
data.loc[(data['Metadata_Site'] > 50) & (data['Metadata_Site'] <= 55), 'Metadata_Classifier']=str('20000_KO_Hapto')
data.loc[(data['Metadata_Site'] > 55) & (data['Metadata_Site'] <= 60), 'Metadata_Classifier']=str('40000_KO_Hapto')


#%%
data['unique_id']=data['track_id'].astype(str)+'_'+data['Metadata_Classifier']
   
    




         
#%%         
         
def define_classifier(data):
    #time_series=False


    data.Metadata_Site=pd.to_numeric(data.Metadata_Site)
    data.loc[data.Metadata_Site == 1, 'Metadata_Classifier']='2000_chemo_Ctrl'
    data.loc[data.Metadata_Site == 2, 'Metadata_Classifier']='2000_chemo_KO'
    data.loc[data.Metadata_Site == 3, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 4, 'Metadata_Classifier']='4000_chemo_Ctrl'
    data.loc[data.Metadata_Site == 5, 'Metadata_Classifier']='2000_chemo_KO'
    data.loc[data.Metadata_Site == 6, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 7, 'Metadata_Classifier']='6000_chemo_Ctrl'
    data.loc[data.Metadata_Site == 8, 'Metadata_Classifier']='6000_chemo_KO'
    data.loc[data.Metadata_Site == 9, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 10, 'Metadata_Classifier']='12000_chemo_Ctrl'
    data.loc[data.Metadata_Site == 11, 'Metadata_Classifier']='12000_chemo_KO'
    data.loc[data.Metadata_Site == 12, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 13, 'Metadata_Classifier']='2000_hapto_Ctrl'
    data.loc[data.Metadata_Site == 14, 'Metadata_Classifier']='2000_hapto_KO'
    data.loc[data.Metadata_Site == 15, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 16, 'Metadata_Classifier']='4000_hapto_Ctrl'
    data.loc[data.Metadata_Site == 17, 'Metadata_Classifier']='4000_hapto_KO'
    data.loc[data.Metadata_Site == 18, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 19, 'Metadata_Classifier']='6000_hapto_Ctrl'
    data.loc[data.Metadata_Site == 20, 'Metadata_Classifier']='6000_hapto_KO'
    data.loc[data.Metadata_Site == 21, 'Metadata_Classifier']='ignore'
    data.loc[data.Metadata_Site == 22, 'Metadata_Classifier']='12000_hapto_Ctrl'
    data.loc[data.Metadata_Site == 23, 'Metadata_Classifier']='12000_hapto_KO'
    data.loc[data.Metadata_Site == 24, 'Metadata_Classifier']='ignore'
    return data

#%%
data=data[~data['Metadata_Classifier'].str.contains('ignore')]
#%%


#%%
def count_agg(data):
    count=data.groupby(['Metadata_Classifier', 'Metadata_Timepoint'], as_index=False)['ObjectNumber'].count()
    return count
            
            #%%
            
def count_objects(data):
    data=data
    count_dict={}
    for i in data['Metadata_Well'].unique():
        if i%3 != 0:
            i_count=data['Number_Object_Number'][(data['Metadata_Well']==i) & (data['Metadata_Timepoint']==10)].count()
            count_dict.update({i:i_count})
    counts = pd.concat(pd.DataFrame({'name':k, 'value':v}, index=[range(0-len(count_dict))]) for k, v in count_dict.items())     
    #pd.DataFrame(count_dict, index=[range(0-len(count_dict))])
    return counts

#%%
def count_objects(data):
    data=data
    count=data.groupby(['Metadata_Classifier', 'Metadata_Timepoint'], as_index=False)['track_id'].count()
    return count
#%%            
adjust=[i for i in data3.columns if 'Intensity' in i]
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
data.tracks['Metadata_Experiment']='SiDLC27'
#%%
data.tracks['Time_Experiment_Classifier']=data.tracks['Time_Classifier']+'_E'+data.tracks['Metadata_Experiment']
data.tracks['Experiment_Classifier']=data.tracks['Classifier']+'_E'+data.tracks['Metadata_Experiment']



#%%
combined=pd.read_csv('/Office/Phd/Data/REF52/SiDLC/SiDLC_28/SiDLC_26_27_28.csv')
combined=combined[combined['roundness']<0.65]
data26=combined[combined['Metadata_Experiment']=='SiDLC26']
data27=combined[combined['Metadata_Experiment']=='SiDLC27']
data28=combined[combined['Metadata_Experiment']=='SiDLC28']
data28.dropna(subset = ["Classifier"], inplace=True)
#%% combined tracks z_score

mad26=statistics.median(data26.loc[data26['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])
mad27=statistics.median(data27.loc[data27['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])
mad28=statistics.median(data28.loc[data28['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])

mad26_FL=statistics.median(data26.loc[data26['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])
mad27_FL=statistics.median(data27.loc[data27['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])
mad28_FL=statistics.median(data28.loc[data28['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])


#%%

std26=np.std(data26.loc[data26['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])
std27=np.std(data27.loc[data27['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])
std28=np.std(data28.loc[data28['Classifier']=='Ctrl','AreaShape_MajorAxisLength'])

std26_FL=np.std(data26.loc[data26['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])
std27_FL=np.std(data27.loc[data27['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])
std28_FL=np.std(data28.loc[data28['Classifier']=='Ctrl_FL','AreaShape_MajorAxisLength'])




#%%
data26.loc[~data26['Classifier'].str.contains('FL'),'AreaShape_zscore']=(data26.loc[~data26['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad26)/std26
data27.loc[~data27['Classifier'].str.contains('FL'),'AreaShape_zscore']=(data27.loc[~data27['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad27)/std27
data28.loc[~data28['Classifier'].str.contains('FL'),'AreaShape_zscore']=(data28.loc[~data28['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad28)/std28
data26.loc[data26['Classifier'].str.contains('FL'), 'AreaShape_zscore']=(data26.loc[data26['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad26_FL)/std26_FL
data27.loc[data27['Classifier'].str.contains('FL'), 'AreaShape_zscore']=(data27.loc[data27['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad27_FL)/std27_FL
data28.loc[data28['Classifier'].str.contains('FL'), 'AreaShape_zscore']=(data28.loc[data28['Classifier'].str.contains('FL'), 'AreaShape_MajorAxisLength']-mad28_FL)/std28_FL

#%%
combined=pd.concat([data26, data27, data28])
combined['Time_Experiment_Classifier']=combined['Time_Classifier']+'_E'+combined['Metadata_Experiment']
combined['Experiment_Classifier']=combined['Classifier']+'_E'+combined['Metadata_Experiment']
#%%
combined.to_csv('/Office/Phd/Data/REF52/SiDLC/SiDLC_28/SiDLC_26_27_28_zscore_prefiltered.csv')