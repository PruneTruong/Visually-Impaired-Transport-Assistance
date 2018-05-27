#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 26 09:18:37 2018

@author: prunetruong
"""
path_source_images='/Volumes/PRUNE/Visually-Impaired-Transport-Assistance/mixed/images/dataset_train_openV4'
path_destination_images='/Volumes/PRUNE/Visually-Impaired-Transport-Assistance/mixed/images/dataset_train_down_sampled/'

from PIL import Image
import os

i=0
l=0
width = 600

if not os.path.exists('{}'.format(path_destination_images)):
    os.makedirs('{}'.format(path_destination_images))
    
for file in os.listdir('{}'.format(path_source_images) ):
    
    if file.endswith('.jpg')  and not file.startswith('._'):
        print(file)
        l+=1
        if not os.path.exists('{}/{}'.format(path_destination_images,file)):
            img = Image.open('{}/{}.jpg'.format(path_source_images,file.strip('.jpg')))
            width_rel= (width/float(img.size[0]))
            height = int((float(img.size[1])*float(width_rel)))
            try: 
                img = img.resize((width, height), Image.ANTIALIAS) 
                img.save('{}/{}'.format(path_destination_images,file))
                i+=1
            except: 
                print('could not downsampled image {}'.format(file))
print('downsampled {}'.format(i))
print(l)
