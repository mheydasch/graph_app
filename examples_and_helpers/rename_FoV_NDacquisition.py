#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 14:41:01 2020

@author: max
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 15:17:03 2018
Renames the files from the microscope into pattern: Well, Date, FoV, channel.
It replaces the well name by a random string of length 8 and creates a csv
file memorizing which string belongs to which well.
To be used before growth cone analyzer crops images to exclude personal bias
in picking the growth cones for each conditions.
@author: max
"""

import os
from os.path import isfile, join
import re
import sys
import string
import random
import pandas as pd
import argparse
#%%
def parseArguments():
  # Define the parser and read arguments
  parser = argparse.ArgumentParser(description='collect segmentation files into one directory')
  parser.add_argument('-d', '--dir', type=str, help='The directory where the files are', required=True)
  parser.add_argument('-i', '--identifier', nargs='+', type=str, help='A list of possible identifier for the files', required=True)

  args = parser.parse_args()
  return(args)

def rename_files(path, identifier):  
    #identifierpattern=re.compile('[A-Z]{3,}', flags=re.IGNORECASE) #identifyimg tif files with a channelname
    os.chdir(path)    
    os.listdir(path)
    onlyfiles=[f for f in os.listdir(path) if isfile(join(path, f))]    
    

   
        

    fovpattern=re.compile('XY[0-9]*') #identifying each pattern
    #wellpattern=re.compile('_[A-Z][0-9]_')
    #datepattern=re.compile('[0-9]{4}_[0-9]{2}_[0-9]{2}')
    #timepattern=re.compile('^t[0-9]+')
    
    
    new_fovs_list={'placeholder':'F'}
    new_fov='F'
    
    #recompiling names in the required order and saving them to new folder
    for i in onlyfiles:
        for iden in identifier:
           
            if iden in i:
                
                print(i, 'renamed to:')
                #identifier=re.search(identifierpattern, i).group().strip('.tif') 
                fov = re.search(fovpattern, i).group().replace('XY', '')
                #date = re.search(datepattern, i).group().replace("_", "")
# =============================================================================
#                 if int(fov) < 11:
#                     well='B3'
#                 if int(fov) >10 and int(fov) < 21:
#                     well='B4'
#                 if int(fov) >20 and int(fov) < 31:
#                     well='C3'
#                 if int(fov) >30 and int(fov) < 41:
#                     well='C4'
#                 if int(fov) >40 and int(fov) < 51:
#                     well='D3'
#                 if int(fov) >50 and int(fov) < 61:
#                     well='D4'
#                 if int(fov) >60 and int(fov) < 71:
#                     well='E3'
#                 if int(fov) >70 and int(fov) < 81:
#                     well='E4'
# =============================================================================
                if int(fov) < 11:
                    well='exclude'
                if int(fov) >11 and int(fov) < 20:
                    well='B2'
                if int(fov) >20 and int(fov) < 31:
                    well='C2'
                if int(fov) >30 and int(fov) < 41:
                    well='B3'
                if int(fov) >40 and int(fov) < 41:
                    well='C3'
                if int(fov) >50 and int(fov) < 61:
                    well='B4'
                if int(fov) >60 and int(fov) < 71:
                    well='C4'
                if int(fov) >70: 
                    well='exclude'
# =============================================================================
#                 try:
#                     well
#                 except NameError:
#                     well=None
#                 if well is None:
#                     well='XY'+fov
# =============================================================================
                #time=re.search(timepattern, i).group()
                file = os.path.join(path, i)
                #creates a 3 characters long random string of uppercase letters and digits and replaces the wellname with it
                if fov in new_fovs_list:
                    new_fov=new_fovs_list[fov]
                else:
                    while new_fov in new_fovs_list.values():
                        new_fov=''.join(random.choices(string.digits, k=4))
                        new_fov='F'+new_fov
                new_fovs_list.update({fov: new_fov})
                oldlocation=os.path.join(path, i)
                newname=new_fov+'_'+iden+'_'+well+'.tif'
                newlocation=os.path.join(path, newname) 
                print(newname)  
                os.rename(oldlocation, newlocation)

if __name__ == '__main__':
    args=parseArguments()
    path=args.dir
    identifier=args.identifier
    print(args)

    rename_files(path, identifier)
