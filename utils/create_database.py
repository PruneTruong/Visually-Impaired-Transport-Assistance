#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 17:06:09 2018

@author: ptruong
"""

'''create database with images coming from coco database. 
prerequisite: download the json file "annotations", put the folder "annotations" in the dataDir. 
'''
#requirements: list
from pycocotools.coco import COCO
import numpy as np
import os
import csv
from glob import glob
#import argparse

'''in the dataDir directory is located the "annotations" file containing json file/info on images'''
dataDir='/Users/prunetruong/Desktop/Blind_project/coco_image'
dataType='val2017'
annFile='{}/annotations/instances_{}.json'.format(dataDir,dataType)
coco=COCO(annFile)

def display_max_number(category):
    '''display the number of images contained in the coco database for a category. 
    corresponds to the maximum number of images possible to download'''
    catIds = coco.getCatIds(catNms=category);
    nbr_img=len(coco.getImgIds(catIds=catIds))
    nbr_img=int(nbr_img)
    return nbr_img

def create_categorie(category, directory, label, label_id, number):
    '''input: category= name of the category of object to download and put in the database
              directory= where to create the database
              This function creates a folder named like the category (if doesn't already exist)
              containing all images corresponding to this category from coco_image. 
              it also creates a csv file containing a list of all images_id, 
              corresponding label, height, width and bounding box dimensions of the category object.
              '''
    print('creating category {}...'.format(category))
    max_number=display_max_number(category)
    if (number>max_number):
        print('attention, the number you chose for the category {} is above the limit allowed. The default number is {}'.format(category,max_number) )
        number=max_number
   # if number=: 
      #  number=max_number
   # except 
    catIds = coco.getCatIds(catNms=[category]);
    imgIds = coco.getImgIds(catIds=catIds );
    todownload=[]

    path='{}/{}'.format(directory,category)
    if not os.path.exists(path):
        os.makedirs(path)
        
    with open('{}/{}.csv'.format(directory, category), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for ids in imgIds[0:number]:
            image=coco.loadImgs(ids)[0]
            
            file_name=image['file_name'] #contains .jpg
            print(file_name)
            height=image['height']
            width=image['width']
            annIds = coco.getAnnIds(ids, catIds=catIds)
            if not os.path.exists('{}/{}'.format(path,file_name)):
                todownload.append(ids)
                print('for category {} need to download image {}'.format(category,file_name))
            for i in np.arange(len(annIds)):
                annotation=coco.loadAnns(annIds[i])[0]
                bbox=annotation['bbox']
                writer.writerow([file_name.strip('.jpg'), label, label_id, height, width, bbox[0], bbox[1], bbox[2], bbox[3]])

    if not (len(todownload)==0):
        coco.download('{}'.format(path), todownload)

    print('category {} : preparation finished'.format(category))
    
def merge_csv(directory, name_merged_file): 
    '''merges all csv file contained into directory into one, and prints the number of lines
    in the csv file'''
    print('merging the csv files present in {}....'.format(directory) )
    i=0
    os.chdir('{}'.format(directory))
    if os.path.exists('{}.csv'.format(name_merged_file)):
        os.remove('{}.csv'.format(name_merged_file))
    with open('{}.csv'.format(name_merged_file), 'a') as singleFile:
        for csvs in glob('*.csv'):
            if csvs == '{}.csv'.format(name_merged_file):
                pass
            else:
                for line in open(csvs, 'r'):
                    singleFile.write(line)
                    i+=1
                print('end of document {} '.format(csvs))
                print('document {} contains {} elements'.format(csvs,i))
                i=0
    print('document {}.csv is ready'.format(name_merged_file))
    
    
    with open('{}.csv'.format(name_merged_file), 'r') as f:
        count = len(f.read().split('\n')) - 1
    print('verification : document {}.csv contains {} elements'.format(name_merged_file,count))

def number_image_cat(categories, directory): 
    '''input=vector containing the names of the categories we want ex: ['train', 'person']
             directory where to find the folder containing the database images
    number of element in a folder category in the directory'''
    
    number_files=[]
    for i,j in enumerate(categories):
        list = os.listdir('{}/{}'.format(directory,j))
        number_files= len(list)
        print('catefory {} has {} images '.format(j, number_files))




'''user has to define the directory in which to create the database. He must also choose what categories 
he wants to download, the label and label_id corresponding to this category. Also, numbers corresponds to 
the number of images to download for the corresponding category. If this number is higher than the 
maximum number of images in coco_database, this maximum number is taken as default. 
==> user needs to change directory and categories, labels, label_id, numbers'''


directory='/Users/prunetruong/Desktop/Blind_project/coco_image/dataset_val'

categories=['bus', 'train', 'bicycle', 'car', 'truck']
labels= ['bus', 'train', 'transport', 'transport', 'transport']
label_id=[1, 2, 3, 3, 3]
numbers=[4000, 4000, 1000, 1000, 1000]

#is no number is given, the default will be all the images in the database

a=display_max_number(categories)
for i,j,label_ids, number in zip(categories, labels, label_id, numbers): 
    create_categorie(i, directory, j, label_ids, number)
number_image_cat(categories, directory)
merge_csv(directory, 'label')