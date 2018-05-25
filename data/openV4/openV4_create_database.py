#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 16 21:57:32 2018
[ filename for filename in filenames if filename.endswith( suffix ) ] short writting of a list
@author: prunetruong

# downloads and extracts the openimages bounding box annotations and image path files
cd /Users/prunetruong/Desktop/Blind_project/dataset/openV4/
mkdir data
wget http://storage.googleapis.com/openimages/2017_07/images_2017_07.tar.gz
tar -xf images_2017_07.tar.gz
mv 2017_07 data/images
rm images_2017_07.tar.gz

wget http://storage.googleapis.com/openimages/2017_07/annotations_human_bbox_2017_07.tar.gz
tar -xf annotations_human_bbox_2017_07.tar.gz
mv 2017_07 data/bbox_annotations
rm annotations_human_bbox_2017_07.tar.gz

wget http://storage.googleapis.com/openimages/2017_07/classes_2017_07.tar.gz
tar -xf classes_2017_07.tar.gz
mv 2017_07 data/classes
rm classes_2017_07.tar.gz
https://blog.algorithmia.com/deep-dive-into-object-detection-with-open-images-using-tensorflow/

Classes we are interested in: 
/m/01bjv,Bus

/m/07jdr,Train

/m/07r04,Truck

coordinates of the box, in normalized image coordinates. XMin is in [0,1], 
where 0 is the leftmost pixel, and 1 is the rightmost pixel in the image. 
Y coordinates go from the top pixel (0) to the bottom pixel (1).



to write
--path_coco_database '/Users/prunetruong/Desktop/Blind_project/dataset/openV4/'
--step_val_train_test train
--path_text_file '/Users/prunetruong/Desktop/Blind_project/dataset/category_classes_openV4.txt'
    

"""

import csv
import os
import urllib.request
from PIL import Image
import argparse
import sys

def make_json_file(text, categories_path):
    '''from the Text file containing the informations on the categories we want to 
    download in the database, creates a list information + a vector classes_to_download
    input: path to the text_file
    Also, for the label name given, finds the corresponding id in categories_path'''
    
    print('checking for existence of category...')
    categories=[]
    classes_to_download=[]
 
    for x in open('{}'.format(text)).readlines():
        row=x.split(",")
        label_exist=0
        with open(categories_path, 'r') as file: 
            for line in csv.reader(file):
                if (line[1].lower()==row[0]):
                    category={'label_number': line[0], 'label': row[0], 'label_id': row[1]}
                    categories.append(category)
                    classes_to_download.append(line[0])
                    label_exist=1
                    print('category {} exists'.format(row[0]))
                    continue
            if label_exist==0: 
                sys.exit('warning: {} is not a valid category name. Please change it. Stop execution'.format(row[0]))
                
            
    return(categories, classes_to_download)

def format_annotations(annotation_path, trainable_classes, categories):
    '''trainable_classes_path contains a list of the category we are interested in, 
    annotation_path contains all the annotations for bounding box for all images. 
    
    output:  annotation_bbx: a list containing the bounding box informations of the
    images of the categories in "trainable_classes".
    ids: the list of the corresponding image ids
    
    ex: ids= ['ibeineodn', 'bcienocnen']
    annotations_bbx[{'id': row[0], 'label': row[2], 'confidence': row[3], 'x0': row[4],
                          'x1': row[5], 'y0': row[6], 'y1': row[7]}]
    '''
    
    annotations_bbx = []
    ids = []
  
    with open(annotation_path, 'r') as annofile:
        for row in csv.reader(annofile):
            label_number_dataset=row[2]
            if label_number_dataset in trainable_classes:
                
                for line in categories: 
                    #line each time contains {{'label_number': line[0], 'label': row[0], 'label_id': row[1]}}
                    #we get the information on the category
                    if line['label_number']==label_number_dataset:
                        label=line['label']
                        label_id=line['label_id']
                        
                annotation = {'id': row[0], 'label_number': row[2],'label':label, 'label_id':label_id,
                              'confidence': row[3], 'xmin': row[4],'xmax': row[5], 'ymin': row[6], 'ymax': row[7]}
                annotations_bbx.append(annotation)
                if not row[0] in ids:
                    #here we exclude the name of images that appear several times (the ones that have several annotations)
                    ids.append(row[0])

    print('there are {} images of {}'.format(len(ids), ' '.join(trainable_classes)))
    print('there are {} annotations'.format(len(annotations_bbx)))

    return annotations_bbx, ids

def list_image_to_download(path_to_download, ids):
    '''check if there are already images from the ids list that are downloaded. 
    Otherwise, lists the image_id that need to be downloaded'''
    
    image_to_download=[]
    for name in ids:
        if not os.path.exists('{}/{}.jpg'.format(path_to_download, name)):
            image_to_download.append(name)
    return image_to_download

def format_image_index(images_path, ids):
    '''finds the corresponding url for a list of ids images
    input: images_path is the annotation file of all the images in the database
    ids is the list of image_ids of which we want to retrieve url
    output: images is a list containing image_id, url '''
    
    
    images = []
    with open(images_path, 'r') as f:
        print('getting url for images /n this may take a while... ')
        
        reader = csv.reader(f)
        dataset = list(reader)
        print('ok')
        i=0
        for row in dataset:
            image = {'id': row[0], 'url': row[2]}    
            if image['id'] in ids:
                images.append(image)
                i+=1
                if (i%1000==0):
                    print('found {} images'.format(i))
                
        
    print('we have {} images to download'.format(len(images)))
    return images

def download_images(path_to_download, list_images, number): 
    '''download images from a url list'''
    
    print('start downloading {}'.format(number))
    i=0
    for name in list_images:
        file_name=name['id']
        try: 
            urllib.request.urlretrieve(name['url'],
                                       '{}/{}.jpg'.format(path_to_download,file_name)) 
            i+=1
            print('downloaded {}.jpg, {}/{}'.format(file_name, i, number))
        except:
            print('error downloading {}.jpg: skipping'.format(file_name))
    print('end of download')
    
    
def create_csv(name_csv, directory, annotations_bbx):
    print('creating a csv file ...')
    with open('{}/{}.csv'.format(directory, name_csv), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvfile.write('img_name;category;category_idx;height;width;x_min;y_min;x_max;y_max  \n')
        for image in annotations_bbx: 
            image_id=image['id']
            Image_to_describe = Image.open('{}/{}.jpg'.format(directory, image_id))
            width, height = Image_to_describe.size
            writer.writerow([image_id, image['label'], image['label_id'], height, width, image['xmin'],image['ymin'],image['xmax'],
                             image['ymax']])
        print('csv file created in {}'.format(directory))
    


parser = argparse.ArgumentParser()
parser.add_argument('--path_V4_database', dest='path', required=True)
parser.add_argument('--step_val_train_test', dest='step', required=True)
parser.add_argument('--path_text_file', dest='fichier_text', required=True)

if __name__ == '__main__':

    args = parser.parse_args()
    path= args.path
    step = args.step
    fichier_text = args.fichier_text
    
    bbox_annotation_path='{}/annotations/bbox_annotations/{}/annotations-human-bbox.csv'.format(path, step)
    images_annotation_path='{}/annotations/images/{}/images.csv'.format(path,step)
    classes_description_path='{}/annotations/classes/class-descriptions.csv'.format(path)
    
    path_to_download='{}/images/dataset_{}'.format(path,step)
    
    categories_information, list_classes=make_json_file(fichier_text, classes_description_path )
    annotations, list_image_ids = format_annotations(bbox_annotation_path, list_classes, categories_information)
    list_image_id_to_download=list_image_to_download(path_to_download, list_image_ids)
    list_images_url=format_image_index(images_annotation_path, list_image_id_to_download)
    download_images(path_to_download, list_images_url, len(list_images_url))
    create_csv('label_{}'.format(step), path_to_download, annotations)
        