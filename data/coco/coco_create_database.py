#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 17:06:09 2018

@author: ptruong

create database with images coming from coco database. 
prerequisite: download the json file "annotations", put the folder "annotations" 
in the dataDir. 


tolaunch
python coco_create_database.py --path_coco_database 
'/Users/prunetruong/Desktop/Blind_project/Visually-Impaired-Transport-Assistance/data/coco' 
--step_val_train_test train 
--path_text_file '/Users/prunetruong/Desktop/Blind_project/Visually-Impaired-Transport-Assistance/data/coco/category_classes_coco.txt'

"""

import numpy as np
import os
import csv
from glob import glob
import argparse
import sys
from pycocotools import coco
    


def get_parameters(text):
    '''from the Text file containing the informations on the categories we want to 
    download in the database, creates a list information + a vector classes_to_download
    input: path to the text_file'''
    
    label=[]
    label_id=[]
    number=[]
    cats = coco.loadCats(coco.getCatIds())
    nms=[cat['name'] for cat in cats]
    for x in open('{}'.format(text)).readlines():
        row=x.split(",")
        label.append(row[0])
        if not row[0] in nms: 
            sys.exit('warning: {} is not a valid category name. Please change it. Stop execution'.format(row[0]))
        label_id.append(row[1])
        number.append(row[2])

    return(label, label_id, number)


def display_max_number(category):
    '''display the number of images contained in the coco database for a category. 
    corresponds to the maximum number of images possible to download'''
    catIds = coco.getCatIds(catNms=category);
    nbr_img=len(coco.getImgIds(catIds=catIds))
    nbr_img=int(nbr_img)
    return nbr_img

def create_categorie(category,label, label_id, number, path, step):
    '''input: category= name of the category of object to download and put in the database
              directory= where to create the database
              This function creates a folder named like the category 
              (if doesn't already exist) containing all images corresponding 
              to this category from coco_image. 
              it also creates a csv file containing a list of all images_id, 
              corresponding label, height, width and bounding box dimensions of 
              the category object.
              '''
    path_image='{}/images/dataset_{}'.format(path, step)
    path_annotations='{}/annotations'.format(path)
    print('creating category {}...'.format(category))
    max_number=display_max_number(category)
    if (int(number)>max_number):
        print('attention, the number you chose for the category {} is above the limit allowed. The default number is {}'.format(category,max_number) )
        number=max_number

    catIds = coco.getCatIds(catNms=[category]);
    imgIds = coco.getImgIds(catIds=catIds );
    todownload=[]
        
    with open('{}/{}_{}.csv'.format(path_annotations, category, step), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvfile.write('img_name;category;category_idx;height;width;x_min;y_min;x_max;y_max\n')
        
        for ids in imgIds[0:int(number)]:
            image=coco.loadImgs(ids)[0]
            
            file_name=image['file_name'] #contains .jpg
            height=image['height']
            width=image['width']
            annIds = coco.getAnnIds(ids, catIds=catIds)
            if not os.path.exists('{}/{}'.format(path_image,file_name)):
                todownload.append(ids)
                print('for category {} need to download image {}'.format(category,file_name))
            for i in np.arange(len(annIds)):
                annotation=coco.loadAnns(annIds[i])[0]
                #here we convert into relative value, bbox: [x,y,width,height],
                bbox=annotation['bbox']
                xmin=float(bbox[0]/width)
                ymin=float(bbox[1]/height)
                xmax=float((bbox[2]+bbox[0])/width)
                ymax=float((bbox[1]+bbox[3])/height)
                writer.writerow([file_name.strip('.jpg'), label, label_id, height, width, xmin, ymin, xmax, ymax])

    if not (len(todownload)==0):
        os.chdir('{}'.format(path_image))
        coco.download('{}'.format(todownload))

    print('category {} : preparation finished'.format(category))
    
def merge_csv(directory, name_merged_file, step): 
    '''merges all csv file contained into directory into one, and prints the number of lines
    in the csv file'''
    print('merging the csv files present in {}....'.format(directory) )
    i=0
    os.chdir('{}'.format(directory))
    if os.path.exists('{}.csv'.format(name_merged_file)):
        os.remove('{}.csv'.format(name_merged_file))
    with open('{}.csv'.format(name_merged_file), 'a') as singleFile:
        singleFile.write('img_name;category;category_idx;height;width;x_min;y_min;x_max;y_max\n')
        for csvs in glob('*_{}.csv'.format(step)):
            if csvs == '{}.csv'.format(name_merged_file):
                pass
            else:
                for line in open(csvs, 'r').readlines()[1:]:
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
==> user needs to change directory and categories, labels, label_id, numbers

Also depending on train or val need to change the directory and first line


'''
parser = argparse.ArgumentParser()
parser.add_argument('--path_coco_database', dest='path', required=True)
parser.add_argument('--step_val_train_test', dest='step', required=True)
parser.add_argument('--path_text_file', dest='fichier_text', required=True)

if __name__ == '__main__':

    args = parser.parse_args()
    path= args.path
    step = args.step
    fichier_text = args.fichier_text


    '''in the dataDir directory is located the "annotations" file containing json file/info on images'''
    dataType='{}2017'.format(step)
    annFile='{}/annotations/instances_{}.json'.format(path,dataType)
    coco=coco.COCO(annFile)
    #COCO is a class from coco
    
    #categories=['bus', 'train', 'car', 'truck']
    #labels= ['bus', 'train', 'car', 'truck']
    #label_id=[0, 1, 2, 3]
    #numbers=[4000, 4000, 2000, 1000]
    

    labels, label_id, numbers=get_parameters('{}'.format(fichier_text))
    categories=labels
    #is no number is given, the default will be all the images in the database
    #a=display_max_number(categories)
    directory_annotations='{}/annotations'.format(path)
    for i,j,label_ids, number in zip(categories, labels, label_id, numbers): 
        create_categorie(i, j, label_ids, number, path, step)
        print(number)
    
    merge_csv(directory_annotations, 'label_{}'.format(step), step)






